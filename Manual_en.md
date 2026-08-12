# Relax XRD Plotter — User Manual

> A desktop tool for plotting X-ray diffraction (XRD) patterns. It supports overlaying / stacking multiple spectra, automatic peak marking, manual annotations, freely positioned legends, project files, and one-click export of high-quality images.

---

## 1. Quick Start

1. **Run the app**
   - Portable build: extract the zip and double-click `Relax XRD Plotter.exe` (no Python install needed).
   - Source build: run `python main.py` in this folder.

2. **Import data** (any one)
   - Click the left 「📂 Open Data File」 button and pick a file;
   - or **drag** a data file onto the left 「Drag data here」 zone;
   - Example data is in the `示例数据\` (Sample Data) folder — just drag it in to try.

3. **Adjust the look** (as needed)
   - On the 「🎨 Plot」 tab set figure size, axis ranges, titles, legend position, etc.;
   - On the right 「✳ Annotate」 panel tick 「Enable peak marking for current spectrum」 to auto-mark diffraction peaks.

4. **Export results**
   - Click 「💾 Export Image」 below the plot and save as PNG / TIFF / SVG / PDF;
   - or click 「📄 Save Project」 to store the current plot together with all edits as an `.xrdproj` project file, which you can reopen to keep editing.

> Most settings refresh automatically; if something does not update, click 「🔄 Refresh Plot」 below the plot.

---

## 2. Interface Overview

The app uses a **three-column layout**:

| Area | Content |
|------|---------|
| Left 「📁 Data」 tab | Data file management, plot mode, color settings |
| Left 「🎨 Plot」 tab | Figure size, axes, titles & labels, legend, border |
| Right 「✳ Annotate」 panel | Auto peak marking, manual markers |
| Button bar below plot | Refresh plot, export image, save project |

The top-right corner switches the **UI theme** (9 themes: Modern Light / Modern Dark / Cartoon Park / Mint Fresh / Deep Space, etc.).

---

## 3. Data Area (📁 Data)

### 1. Data file management
- **📂 Open Data File**: opens a file picker to import data.
- **Drag data here**: drop a data file into this zone to import.
- **File list**: lists imported samples; select one so the controls below act on it.
- **Legend name**: type a name for the selected sample, then click 「Apply」 or press Enter to change its legend label.
- **Current line width**: 0.5–8.0, adjusts the selected curve thickness live.
- **Current line style**: solid / dashed / dash-dot / dotted / loose dashed / loose dash-dot.
- **Add / Delete / ↑ / ↓**: import more files, delete the selected file, reorder samples in the stack (order affects stacked offset and legend order).

### 2. Plot mode
- **Overlay**: all curves share one coordinate system.
- **Stacked**: curves shift upward in turn for easy comparison; the spacing is controlled by the 「Offset factor」 slider/box (larger = wider gap).

### 3. Color settings
- **Preset palettes**: pick a scheme (Nature, Science, Custom, Morandi, Macaron, Cyberpunk, Ocean Deep Blue, Forest Green, Warm Orange, Candy Park, plus several Genshin-themed palettes) and apply to all samples at once.
- **Per-sample color**: each sample has a color swatch; click it to set that curve's color individually.

---

## 4. Plot Area (🎨 Plot)

### 1. Figure size
- Set the **width** and **height** (in inches) — they decide the exported image's aspect ratio.

### 2. Axes
- **X / Y axis min·max**: default shows 「Auto」. Focusing the box auto-selects the word 「Auto」 — **just type a number to override**; leave blank or reset to 「Auto」 to let the app auto-fit.
- **Major tick step**: X / Y major tick step, also supports 「Auto」 + direct number entry.
- **Tick direction**: `in` / `out` / `inout`.
- **Reset to auto**: restore all axis ranges to auto at once.

### 3. Titles & labels
- **Title / X label / Y label**: the on-plot text (X defaults to `2θ (°)`, Y defaults to `Intensity (a.u.)`).
- **Title size / Label size / Tick size**: control each text level's size.
- **Font**: default **Times New Roman**, switchable via the dropdown.
- **Bold title**: default **off** (not bold); tick to bold the title.
- **Show X/Y axis labels**: toggle whether axis titles appear on the plot.

### 4. Legend
- **Show legend**: master switch.
- **Legend layout** (three modes):
  - **Grouped**: traditional single legend box; choose 1 of 9 positions (upper right, upper left, etc.).
  - **Above curves**: each sample name is labeled directly at its curve's **upper right**, colored to match the curve, no separate legend box.
  - **Draggable**: labels start at the curve's upper right and **can be dragged anywhere with the mouse**; positions are remembered and survive refresh.
- **Legend size / Legend font**: legend text size and font (default Times New Roman).
- **Show legend frame**: whether to draw a border around the legend box.

### 5. Border
- **Bold axis border**: tick to thicken axis lines.
- **Border width**: set border thickness.

---

## 5. Annotate Area (✳ Annotate, right panel)

### 1. Peak marking (automatic)
- **Enable peak marking for current spectrum**: when ticked, automatically finds and marks peaks for the **currently selected sample** (select it in the file list first).
- **Mark content**:
  - `symbol + peak position`: draw a symbol at the peak and show its 2θ value;
  - `peak position only`: show only the value;
  - `symbol only`: draw only the symbol.
- **Peak count**:
  - `manual`: mark the fixed top N strongest peaks (set by 「Manual peak count」);
  - `auto`: decide peak count by 「Minimum peak distance」.
- **Minimum peak distance**: in auto mode, the minimum 2θ gap between two peaks, to avoid dense noise being mistaken for peaks.
- **Peak decimals**: decimal places kept for the peak value.
- **Symbol type**: 10 options — circle, square, triangle, inverted triangle, diamond, star, hexagon, pentagon, cross, x.
- **Symbol color / Text color**: color of the peak symbol and the peak value text.

### 2. Manual markers
- **Enable manual markers**: tick to turn on manual annotation.
- **Add marker**: **left-click** on the plot to place a marker using the symbol, color, size, and default text set below.
- **Symbol type**: same 10 symbols as above.
- **Pick color / size**: style of new markers (size 20–300).
- **Default text for new markers**: text auto-attached each time you click to add.
- **Edit current marker text**: select a marker in the list, type text, then click 「Apply text」 (or edit the 「Current marker text」 box).
- **Marker list**: lists all manual markers; with one selected:
  - 「Delete selected」: remove it;
  - 「Undo」: delete the most recently added one;
  - 「Clear」: remove all manual markers;
  - 「↑ ↓ ← →」: nudge the selected marker by a small step.
- **Click an existing marker** to select it; in 「Draggable」 legend mode you drag the legend label, not the marker — the two do not interfere.

---

## 6. Button Bar Below Plot

| Button | Function |
|--------|----------|
| 🔄 Refresh Plot | Apply all settings and redraw the current plot. |
| 💾 Export Image | Export as **PNG / TIFF / SVG / PDF** (choose format and path in the dialog). |
| 📄 Save Project | Save the current work — see 「Project file」 below. |

### Project file (.xrdproj)
The 「Save Project」 dialog offers two kinds of save:

- **XRD project file (*.xrdproj)**: saves **data + all edit info**, including:
  - per sample: legend name, color, line width, line style, peak-mark settings, legend label position;
  - global: plot mode, offset factor, figure size, axes, titles & labels, legend (layout + position), border, peak parameters, manual markers.
  - Next time, just **open** or **drop** the `.xrdproj` file to continue editing — no re-setup needed.
- **CSV / TXT**: exports only the on-plot data (including stacked offset), two columns per sample (2θ + intensity); duplicate sample names get a `_2` suffix automatically.

---

## 7. Themes & Appearance

- The top-right 「UI」 dropdown switches 9 UI themes; all control styles (including dialogs and dropdowns) follow.
- Plot font and palette are controlled by their own settings and are independent of the UI theme.

---

## 8. Supported Data Formats

**Import**:
- Text: `.xy`, `.dat`, `.csv`, `.txt` (auto-detect comma / tab / semicolon / space, auto-skip header)
- **Bruker RAW4.00 / D8 exported `.txt`**: the instrument's native export, with a `;RAW4.00` magic line and `[RawHeader]` / `[Data]` blocks (data like `5.0001, 507,` with trailing commas and space padding). The app auto-detects it and reads the 2θ and intensity columns from the `[Data]` block — no manual cleanup needed.
- Excel: `.xlsx` (first sheet)
- Project file: `.xrdproj` (restores data and all edits)

**Sample data** (in `示例数据\`, drag in to try):
- `sample_data.csv` / `sample_data2.csv`: single-curve standard examples;
- `xrd_multi_column_demo.txt`: multiple spectra in one file (tab-separated, `2theta / Sample_A / Sample_B / Sample_C`) — good for demoing **overlay / stacked** multi-spectra;
- `xrd_multi_column_demo.xlsx`: the same structure as an Excel multi-spectrum example;
- `passivated_ball_Pb.txt` (Bruker RAW export): demonstrates direct reading of Bruker instrument raw data.

**Data requirement**: at least 2 columns (1st = 2θ angle, rest = intensity), at least 2 valid numeric rows; multiple intensity columns are auto-split into separate curves.

**Export**: `.png`, `.tiff`, `.svg`, `.pdf`, plus project `.xrdproj` and data `.csv` / `.txt`.

---

## 9. FAQ & Notes

- **Antivirus false positive**: the portable exe is built with PyInstaller; some antivirus tools may flag it. This is normal — add the app folder to the antivirus allow-list / trust list.
- **Chinese display**: title/label default font is Times New Roman; Chinese sample names fall back to a system font and display fine. To unify Chinese style, change the font in 「Titles & labels」.
- **Axis not applying**: make sure you entered a valid number (focus the box and just type to override 「Auto」); if the plot does not update after editing, click 「Refresh Plot」.
- **Project file won't open**: confirm the extension is `.xrdproj` and it was saved by the same app version; drag it in or use 「Open Data File」.

---

## 10. Author

- Author: qxh
- Affiliation: WIT
- Email: qbaiyi@qq.com
