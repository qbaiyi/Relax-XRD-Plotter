import re
import numpy as np
import pandas as pd
from dataclasses import dataclass
from pathlib import Path


@dataclass
class XRDData:
    two_theta: np.ndarray
    intensity: np.ndarray
    filename: str
    display_name: str
    color: str = '#1f77b4'
    line_width: float = 1.0
    line_style: str = 'solid'
    peak_mark_enabled: bool = False
    peak_mark_mode: str = 'symbol+value'
    peak_count_mode: str = 'manual'
    peak_count: int = 3
    peak_min_distance: float = 0.5
    peak_symbol: str = 'circle'
    peak_symbol_color: str = '#d62728'
    peak_text_color: str = '#1f2937'


def detect_delimiter(line: str) -> str:
    candidates = [',', '\t', ';', ' ']
    counts = [(d, line.count(d)) for d in candidates]
    best = max(counts, key=lambda x: x[1])
    if best[1] == 0:
        return None
    return best[0]


def skip_header_lines(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.replace(',', ' ').replace('\t', ' ').replace(';', ' ').split()
        try:
            [float(p) for p in parts]
            return i
        except ValueError:
            continue
    return 0


def _is_number(value) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def _get_header_tokens(lines: list[str], start: int, delimiter: str) -> list[str] | None:
    for idx in range(start - 1, -1, -1):
        stripped = lines[idx].strip()
        if not stripped:
            continue
        if delimiter:
            parts = stripped.split(delimiter)
        else:
            parts = stripped.split()
        tokens = [p.strip() for p in parts if p.strip()]
        if len(tokens) >= 2 and any(not _is_number(token) for token in tokens):
            return tokens
    return None


def _build_series_name(stem: str, header_tokens: list[str] | None, column_index: int,
                       total_series: int) -> str:
    if header_tokens and column_index < len(header_tokens):
        name = str(header_tokens[column_index]).strip()
        if name:
            return name
    if total_series == 1:
        return stem
    return f"{stem}_{column_index}"


def _build_xrd_dataset(two_theta: np.ndarray, intensity: np.ndarray,
                       filename: str, display_name: str) -> XRDData | None:
    valid = np.isfinite(two_theta) & np.isfinite(intensity)
    x = np.asarray(two_theta[valid], dtype=float)
    y = np.asarray(intensity[valid], dtype=float)
    if len(x) < 2 or len(y) < 2:
        return None
    return XRDData(
        two_theta=x,
        intensity=y,
        filename=filename,
        display_name=display_name,
    )


def _load_text_series(filepath: str, filename: str, stem: str) -> list[XRDData]:
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    start = skip_header_lines(lines)
    data_lines = lines[start:]

    delimiter = None
    for line in data_lines:
        stripped = line.strip()
        if stripped:
            delimiter = detect_delimiter(stripped)
            break

    header_tokens = _get_header_tokens(lines, start, delimiter)
    rows = []
    max_columns = 0
    for line in data_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if delimiter:
            parts = stripped.split(delimiter)
        else:
            parts = stripped.split()
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) < 2:
            continue
        numeric_row = []
        row_valid = True
        for part in parts:
            try:
                numeric_row.append(float(part))
            except ValueError:
                row_valid = False
                break
        if not row_valid or len(numeric_row) < 2:
            continue
        rows.append(numeric_row)
        max_columns = max(max_columns, len(numeric_row))

    if len(rows) < 2 or max_columns < 2:
        raise ValueError(f"无法从文件 {filename} 中解析出有效的XRD数据（至少需要2列、2行数据）")

    matrix = np.full((len(rows), max_columns), np.nan)
    for row_idx, row in enumerate(rows):
        matrix[row_idx, :len(row)] = row

    two_theta = matrix[:, 0]
    total_series = max_columns - 1
    datasets = []
    for col_idx in range(1, max_columns):
        display_name = _build_series_name(stem, header_tokens, col_idx, total_series)
        dataset = _build_xrd_dataset(two_theta, matrix[:, col_idx], filename, display_name)
        if dataset is not None:
            datasets.append(dataset)

    if not datasets:
        raise ValueError(f"文件 {filename} 中没有可用的强度列")
    return datasets


def _find_excel_data_start(df: pd.DataFrame) -> int:
    for i in range(len(df)):
        row = df.iloc[i].tolist()
        numeric_count = sum(1 for value in row if _is_number(value))
        if numeric_count >= 2:
            return i
    return -1


def _get_excel_headers(df: pd.DataFrame, start_row: int) -> list[str] | None:
    for idx in range(start_row - 1, -1, -1):
        row = df.iloc[idx].tolist()
        if all(pd.isna(value) for value in row):
            continue
        tokens = ["" if pd.isna(value) else str(value).strip() for value in row]
        if any(token and not _is_number(token) for token in tokens):
            return tokens
    return None


def _load_excel_series(filepath: str, filename: str, stem: str) -> list[XRDData]:
    try:
        df = pd.read_excel(filepath, sheet_name=0, header=None)
    except Exception as e:
        raise ValueError(f"读取Excel文件失败: {e}")

    if df.shape[1] < 2:
        raise ValueError(f"Excel文件 {filename} 至少需要2列数据")

    start_row = _find_excel_data_start(df)
    if start_row < 0:
        raise ValueError(f"Excel文件 {filename} 中没有找到有效的数值数据")

    headers = _get_excel_headers(df, start_row)
    data_df = df.iloc[start_row:].copy()
    data_df = data_df.apply(pd.to_numeric, errors='coerce')
    data_df = data_df.dropna(how='all')

    valid_columns = [idx for idx in range(data_df.shape[1]) if data_df.iloc[:, idx].notna().sum() >= 2]
    if len(valid_columns) < 2:
        raise ValueError(f"Excel文件 {filename} 至少需要1列角度和1列强度数据")

    x_col = valid_columns[0]
    two_theta = data_df.iloc[:, x_col].to_numpy(dtype=float)
    intensity_columns = valid_columns[1:]
    total_series = len(intensity_columns)
    datasets = []
    for col_idx in intensity_columns:
        display_name = _build_series_name(stem, headers, col_idx, total_series)
        dataset = _build_xrd_dataset(two_theta, data_df.iloc[:, col_idx].to_numpy(dtype=float),
                                     filename, display_name)
        if dataset is not None:
            datasets.append(dataset)

    if not datasets:
        raise ValueError(f"Excel文件 {filename} 中没有可用的强度列")
    return datasets


def _looks_like_bruker_raw(lines: list[str]) -> bool:
    """Detect Bruker RAW4.00 / D8 exported text files.

    These files start with a ``;RAWx.xx`` magic line and contain ``[RawHeader]`` /
    ``[RangeHeader]`` / ``[Data]`` INI-style sections. The data block is comma (or
    whitespace) separated with trailing commas, e.g. ``    5.0001,       507,``.
    """
    if not lines:
        return False
    first = lines[0].strip()
    if first.startswith(';RAW'):
        return True
    head = '\n'.join(lines[:300]).lower()
    return '[rawheader]' in head and '[data]' in head


def _parse_bruker_data_block(lines: list[str], start_idx: int):
    """Parse a single ``[Data]`` block starting at ``start_idx``.

    Returns ``(header_tokens, rows, max_cols)`` where ``rows`` is a list of
    numeric lists and ``max_cols`` is the widest row. Stops at the next
    ``[section]`` line or end of file.
    """
    j = start_idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    header_tokens = None
    if j < len(lines):
        header_tokens = [t.strip() for t in re.split(r'[,;\t\s]+', lines[j].strip()) if t.strip()]

    rows = []
    max_cols = 0
    k = j + 1
    while k < len(lines):
        st = lines[k].strip()
        k += 1
        if not st:
            continue
        if st.startswith('['):
            break
        parts = [t.strip() for t in re.split(r'[,;\t\s]+', st) if t.strip()]
        numeric_row = []
        row_valid = True
        for p in parts:
            try:
                numeric_row.append(float(p))
            except ValueError:
                row_valid = False
                break
        if not row_valid or len(numeric_row) < 2:
            continue
        rows.append(numeric_row)
        max_cols = max(max_cols, len(numeric_row))
    return header_tokens, rows, max_cols


def _load_bruker_raw_txt(filepath: str, filename: str, stem: str) -> list[XRDData]:
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    data_indices = [i for i, ln in enumerate(lines) if ln.strip().lower().startswith('[data]')]
    if not data_indices:
        raise ValueError(f"文件 {filename} 中未找到 [Data] 数据区块，可能不是有效的 Bruker RAW 文件")

    datasets = []
    for start in data_indices:
        header_tokens, rows, max_cols = _parse_bruker_data_block(lines, start)
        if len(rows) < 2 or max_cols < 2:
            continue
        matrix = np.full((len(rows), max_cols), np.nan)
        for row_idx, row in enumerate(rows):
            matrix[row_idx, :len(row)] = row
        two_theta = matrix[:, 0]
        total_series = max_cols - 1
        for col_idx in range(1, max_cols):
            # 单序列文件用文件名做图例名更直观（Bruker 强度列通常只叫 PSD/Counts）
            if total_series == 1:
                display_name = stem
            else:
                display_name = _build_series_name(stem, header_tokens, col_idx, total_series)
            dataset = _build_xrd_dataset(two_theta, matrix[:, col_idx], filename, display_name)
            if dataset is not None:
                datasets.append(dataset)

    if not datasets:
        raise ValueError(f"文件 {filename} 中没有可用的强度列")
    return datasets


def load_xrd_files(filepath: str) -> list[XRDData]:
    path = Path(filepath)
    if not path.exists():
        raise ValueError(f"文件不存在: {filepath}")

    ext = path.suffix.lower()
    filename = path.name
    stem = path.stem

    if ext in ('.xy', '.dat', '.csv', '.txt'):
        # Bruker RAW4.00 / D8 导出的 .txt：头部为 INI 区块，数据带尾随逗号
        with open(filepath, 'r', encoding='utf-8', errors='replace') as _f:
            _head = _f.readlines(8000)
        if _looks_like_bruker_raw(_head):
            return _load_bruker_raw_txt(filepath, filename, stem)
        return _load_text_series(filepath, filename, stem)
    elif ext == '.xlsx':
        return _load_excel_series(filepath, filename, stem)
    else:
        raise ValueError(f"不支持的文件格式: {ext}（支持: .xy, .dat, .csv, .txt, .xlsx，"
                         f"以及 Bruker RAW4.00/D8 导出的 .txt）")


def load_xrd_file(filepath: str) -> XRDData:
    datasets = load_xrd_files(filepath)
    return datasets[0]
