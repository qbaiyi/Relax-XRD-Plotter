import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import matplotlib.font_manager as fm
from matplotlib import patheffects
import matplotlib.patches as mpatches

COLOR_SCHEMES = {
    "Nature": ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F',
               '#8491B4', '#91D1C2', '#DC0000', '#7E6148', '#B09C85'],
    "Science": ['#0C5DA5', '#00B945', '#FF9500', '#FF2C00',
                '#845B97', '#474747', '#9E9E9E'],
    "Custom": ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
               '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
    "原神-雷电将军": ['#5B2C6F', '#9B59B6', '#D7BDE2', '#2C3E50', '#1A1A2E'],
    "原神-钟离": ['#8B4513', '#D2691E', '#F5DEB3', '#CD853F', '#6B4423'],
    "原神-纳西妲": ['#228B22', '#90EE90', '#32CD32', '#006400', '#98FB98'],
    "原神-芙宁娜": ['#1E90FF', '#87CEEB', '#4169E1', '#000080', '#ADD8E6'],
    "原神-那维莱特": ['#00CED1', '#20B2AA', '#48D1CC', '#008B8B', '#E0FFFF'],
    "原神-散兵": ['#4B0082', '#9400D3', '#DDA0DD', '#8A2BE2', '#9932CC'],
    "原神-胡桃": ['#DC143C', '#FF6B6B', '#FFB6C1', '#8B0000', '#CD5C5C'],
    "原神-甘雨": ['#87CEFA', '#B0E0E6', '#AFEEEE', '#ADD8E6', '#E0FFFF'],
    "原神-申鹤": ['#F5F5F5', '#DCDCDC', '#C0C0C0', '#A9A9A9', '#808080'],
    "原神-神里绫华": ['#4169E1', '#6495ED', '#87CEEB', '#B0C4DE', '#E6E6FA'],
    "原神-希格雯": ['#5184B2', '#AAD4F8', '#F2F5FA', '#F1A7B5', '#D55276'],
    "莫兰迪配色": ['#A8A7A7', '#CCB69B', '#96897B', '#B8B8AA', '#C5C5C5',
                   '#D4C4A8', '#BBA694', '#A69383', '#C4BBA4', '#DAD0C8'],
    "马卡龙配色": ['#FFB5BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF',
                   '#E0BBE4', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE'],
    "赛博朋克": ['#00FFF5', '#FF00FF', '#FFFF00', '#00FF00', '#FF6600',
                 '#FF1493', '#00CED1', '#FFD700', '#FF4500', '#9400D3'],
    "日落渐变": ['#FF6B6B', '#FFE66D', '#4ECDC4', '#45B7D1', '#96CEB4'],
    "海洋深蓝": ['#0077B6', '#00B4D8', '#90E0EF', '#CAF0F8', '#023E8A'],
    "森林绿意": ['#2D6A4F', '#40916C', '#52B788', '#95D5B2', '#D8F3DC'],
    "暖橙金秋": ['#E85D04', '#F48C06', '#FAA307', '#FFBA08', '#FFF3B0'],
    "糖果乐园": ['#FF6B6B', '#4ECDC4', '#FFE66D', '#FF8C42', '#95E1D3',
                   '#F38181', '#AA96DA', '#FCBAD3', '#55E6C1', '#A8D8EA'],
}

PLOT_BACKGROUND = 'white'
PLOT_FOREGROUND = 'black'

# ── 贴图绘制函数：使用 matplotlib 原生 patches，每个贴图接受 (ax, x, y, sx, sy, color) ──
# sx/sy 分别是 x/y 方向 1 个"贴图单位"对应的数据坐标尺度，由 draw_stickers 根据轴范围计算

def _dc(x, y, fx, fy, sx, sy):
    """将贴图坐标 (fx, fy) 转为数据坐标，贴图范围约 [-1, 1] 或更大"""
    return (x + fx * sx, y + fy * sy)


def _circle(ax, cx, cy, r, sx, sy, **kw):
    """绘制视觉上的圆形（数据坐标下是椭圆）"""
    e = mpatches.Ellipse((cx, cy), width=2 * r * sx, height=2 * r * sy, **kw)
    ax.add_patch(e)


def _draw_flower(ax, x, y, sx, sy, color):
    """五瓣小花"""
    petal_colors = ['#FF6B6B', '#FF9A9E', '#FF6B6B', '#FF9A9E', '#FF6B6B']
    for i, angle in enumerate(np.linspace(0, 2 * np.pi, 5, endpoint=False)):
        px, py = _dc(x, y, 0.55 * np.cos(angle), 0.55 * np.sin(angle), sx, sy)
        petal = mpatches.Ellipse((px, py), width=0.35 * sx, height=0.50 * sy,
                                 angle=np.degrees(angle), color=petal_colors[i % 5], zorder=16)
        ax.add_patch(petal)
    _circle(ax, x, y, 0.18, sx, sy, color='#FFD700', zorder=17)


def _draw_grass(ax, x, y, sx, sy, color):
    """三片小草叶"""
    from matplotlib.path import Path
    for base_angle, lean in [(-25, -0.12), (0, 0), (25, 0.12)]:
        rad = np.radians(base_angle)
        tip_x, tip_y = _dc(x, y, 0.5 * np.cos(rad), 0.5 * np.sin(rad), sx, sy)
        ctrl_x, ctrl_y = _dc(x, y, 0.25 * np.cos(rad) + lean, 0.25 * np.sin(rad) + 0.2, sx, sy)
        base_x, base_y = _dc(x, y, 0, -0.2, sx, sy)
        verts = [(base_x, base_y), (ctrl_x, ctrl_y), (tip_x, tip_y)]
        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
        path = Path(verts, codes)
        blade = mpatches.PathPatch(path, facecolor='none', edgecolor=color, lw=2.0,
                                   capstyle='round', zorder=16)
        ax.add_patch(blade)


def _draw_sun(ax, x, y, sx, sy, color):
    """太阳：圆脸 + 射线"""
    for i in range(8):
        angle = i * np.pi / 4
        x1, y1 = _dc(x, y, 0.55 * np.cos(angle), 0.55 * np.sin(angle), sx, sy)
        x2, y2 = _dc(x, y, 0.80 * np.cos(angle), 0.80 * np.sin(angle), sx, sy)
        ax.plot([x1, x2], [y1, y2], color=color, lw=2.5, solid_capstyle='round', zorder=15)
    _circle(ax, x, y, 0.50, sx, sy, color='#FFD700', zorder=16)


def _draw_bird(ax, x, y, sx, sy, color):
    """简笔画小鸟"""
    from matplotlib.path import Path
    # 身体弧线
    verts = [_dc(x, y, fx, fy, sx, sy) for fx, fy in
             [(-0.5, 0), (-0.1, 0.25), (0.3, 0.15), (0.5, -0.05)]]
    codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3, Path.CURVE3]
    body = mpatches.PathPatch(Path(verts, codes), facecolor='none', edgecolor=color,
                              lw=2.0, capstyle='round', zorder=16)
    ax.add_patch(body)
    # 翅膀
    wv = [_dc(x, y, fx, fy, sx, sy) for fx, fy in
          [(-0.05, 0.18), (0.0, -0.05), (0.4, 0.05)]]
    wc = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
    wing = mpatches.PathPatch(Path(wv, wc), facecolor='none', edgecolor=color,
                              lw=1.8, capstyle='round', zorder=16)
    ax.add_patch(wing)
    # 眼睛 & 嘴
    ex, ey = _dc(x, y, 0.3, 0.12, sx, sy)
    _circle(ax, ex, ey, 0.06, sx, sy, color='#333', zorder=17)
    bx1, by1 = _dc(x, y, 0.35, 0.08, sx, sy)
    bx2, by2 = _dc(x, y, 0.52, 0.05, sx, sy)
    ax.plot([bx1, bx2], [by1, by2], color='#FF8C00', lw=1.5, solid_capstyle='round', zorder=17)


def _draw_girl(ax, x, y, sx, sy, color):
    """小女孩"""
    hx, hy = _dc(x, y, 0, 0.35, sx, sy)
    _circle(ax, hx, hy, 0.22, sx, sy, color='#FFDAB9', zorder=16)
    for dx_ in [-0.08, 0.08]:
        tx, ty = _dc(x, y, dx_, 0.55, sx, sy)
        _circle(ax, tx, ty, 0.08, sx, sy, color=color, zorder=15)
    # 裙子
    v = [_dc(x, y, fx, fy, sx, sy) for fx, fy in [(-0.22, -0.05), (0.22, -0.05), (0, -0.55)]]
    ax.add_patch(mpatches.Polygon(v, color=color, zorder=16))
    # 表情
    for dx_ in [-0.06, 0.06]:
        ex, ey = _dc(x, y, dx_, 0.38, sx, sy)
        _circle(ax, ex, ey, 0.03, sx, sy, color='#333', zorder=17)
    sx2, sy2 = _dc(x, y, 0, 0.28, sx, sy)
    ax.add_patch(mpatches.Arc((sx2, sy2), 0.10 * sx, 0.06 * sy, angle=0, theta1=0, theta2=180,
                               color='#333', lw=1.0, zorder=17))


def _draw_boy(ax, x, y, sx, sy, color):
    """小男孩"""
    hx, hy = _dc(x, y, 0, 0.35, sx, sy)
    _circle(ax, hx, hy, 0.22, sx, sy, color='#FFDAB9', zorder=16)
    bx0, by0 = _dc(x, y, -0.18, -0.55, sx, sy)
    body = mpatches.FancyBboxPatch((bx0, by0), 0.36 * sx, 0.45 * sy,
                                   boxstyle="round,pad=0.02", color=color, zorder=16)
    ax.add_patch(body)
    for dx_ in [-0.06, 0.06]:
        ex, ey = _dc(x, y, dx_, 0.38, sx, sy)
        _circle(ax, ex, ey, 0.03, sx, sy, color='#333', zorder=17)
    sx2, sy2 = _dc(x, y, 0, 0.28, sx, sy)
    ax.add_patch(mpatches.Arc((sx2, sy2), 0.10 * sx, 0.06 * sy, angle=0, theta1=0, theta2=180,
                               color='#333', lw=1.0, zorder=17))


def _draw_rainbow(ax, x, y, sx, sy, color):
    """彩虹"""
    rainbow_colors = ['#FF6B6B', '#FFE66D', '#4ECDC4', '#A8D8EA']
    for i, rc in enumerate(rainbow_colors):
        r = (0.50 - i * 0.08)
        ax.add_patch(mpatches.Arc((x, y), 2 * r * sx, 1.6 * r * sy,
                                   angle=0, theta1=0, theta2=180, color=rc, lw=3.0, zorder=16))


def _draw_star(ax, x, y, sx, sy, color):
    """五角星"""
    outer_r, inner_r = 0.9, 0.35
    vertices = []
    for i in range(10):
        angle = -np.pi / 2 + i * np.pi / 5
        r = outer_r if i % 2 == 0 else inner_r
        vertices.append(_dc(x, y, r * np.cos(angle), r * np.sin(angle), sx, sy))
    star = mpatches.Polygon(vertices, color='#FFD700', zorder=15)
    ax.add_patch(star)
    ax.add_patch(mpatches.Polygon(vertices, facecolor='none', edgecolor=color, lw=2.0, zorder=16))


def _draw_butterfly(ax, x, y, sx, sy, color):
    """蝴蝶"""
    lx, ly = _dc(x, y, -0.15, 0.05, sx, sy)
    rx, ry = _dc(x, y, 0.15, 0.05, sx, sy)
    ax.add_patch(mpatches.Ellipse((lx, ly), 0.4 * sx, 0.55 * sy, angle=-30,
                                   color=color, alpha=0.8, zorder=16))
    ax.add_patch(mpatches.Ellipse((rx, ry), 0.4 * sx, 0.55 * sy, angle=30,
                                   color=color, alpha=0.8, zorder=16))
    bx0, by0 = _dc(x, y, -0.03, -0.4, sx, sy)
    body = mpatches.FancyBboxPatch((bx0, by0), 0.06 * sx, 0.55 * sy,
                                    boxstyle="round,pad=0.01", color='#5A3A20', zorder=17)
    ax.add_patch(body)
    for dx_ in [-0.06, 0.06]:
        a1x, a1y = _dc(x, y, dx_, 0.3, sx, sy)
        a2x, a2y = _dc(x, y, dx_ * 2.5, 0.55, sx, sy)
        ax.plot([a1x, a2x], [a1y, a2y], color='#5A3A20', lw=1.2, solid_capstyle='round', zorder=17)


def _draw_mushroom(ax, x, y, sx, sy, color):
    """蘑菇"""
    ax.add_patch(mpatches.Wedge((x, y + 0.1 * sy), 0.45 * sy, theta1=0, theta2=180,
                                 color=color, zorder=16))
    for dfx, dfy in [(-0.12, 0.25), (0.08, 0.3), (-0.02, 0.15)]:
        dx_, dy_ = _dc(x, y, dfx, dfy, sx, sy)
        _circle(ax, dx_, dy_, 0.06, sx, sy, color='white', zorder=17)
    bx0, by0 = _dc(x, y, -0.12, -0.55, sx, sy)
    stem = mpatches.FancyBboxPatch((bx0, by0), 0.24 * sx, 0.5 * sy,
                                    boxstyle="round,pad=0.02", color='#F5DEB3', zorder=15)
    ax.add_patch(stem)


def _draw_cloud(ax, x, y, sx, sy, color):
    """云朵"""
    offsets = [(0, 0, 0.35), (0.25, 0.08, 0.30), (-0.25, 0.05, 0.28),
               (0.15, -0.10, 0.28), (-0.15, -0.08, 0.26)]
    for ofx, ofy, or_ in offsets:
        cx, cy = _dc(x, y, ofx, ofy, sx, sy)
        _circle(ax, cx, cy, or_, sx, sy, color=color, zorder=16)


def _draw_heart(ax, x, y, sx, sy, color):
    """爱心"""
    t = np.linspace(0, 2 * np.pi, 100)
    hx = 16 * np.sin(t) ** 3
    hy = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    scale_x = sx / 18.0
    scale_y = sy / 18.0
    px = hx * scale_x + x
    py = hy * scale_y + y + 0.1 * sy
    ax.add_patch(mpatches.Polygon(np.column_stack([px, py]), color=color, zorder=16))


# 贴图名称 → 绘制函数的映射
STICKER_DRAWERS = {
    "小花": _draw_flower,
    "小草": _draw_grass,
    "太阳": _draw_sun,
    "小鸟": _draw_bird,
    "小女孩": _draw_girl,
    "小男孩": _draw_boy,
    "彩虹": _draw_rainbow,
    "星星": _draw_star,
    "蝴蝶": _draw_butterfly,
    "蘑菇": _draw_mushroom,
    "云朵": _draw_cloud,
    "爱心": _draw_heart,
}


class XRDPlotter:

    def __init__(self, figure):
        self.figure = figure
        self.axes = figure.add_subplot(111)
        self._lines = []
        self._plotted_series = []
        self._border_width = 1.0
        self._font_family = 'Times New Roman'
        self._legend_font_family = 'Times New Roman'
        self._show_x_ticks = True
        self._show_y_ticks = False
        self._curve_labels = []
        self._label_positions = {}
        self._cartoon_mode = False
        self._cartoon_bg = '#FFF8E7'
        self._cartoon_fg = '#5A3A20'
        self._cartoon_font = 'KaiTi'
        plt.rcParams['axes.unicode_minus'] = False

    def set_cartoon_mode(self, enabled):
        self._cartoon_mode = enabled
        try:
            if enabled:
                self.figure.set_sketch_params(scale=6.0, length=40, randomness=1.2)
            else:
                self.figure.set_sketch_params(None)
        except Exception:
            pass

    def clear(self):
        self.axes.clear()
        bg = self._cartoon_bg if self._cartoon_mode else PLOT_BACKGROUND
        self.axes.set_facecolor(bg)
        self.figure.patch.set_facecolor(bg)
        self._lines = []
        self._plotted_series = []
        self._curve_labels = []

    def set_font_family(self, font_family):
        self._font_family = font_family

    def set_legend_font_family(self, font_family):
        self._legend_font_family = font_family or self._font_family

    def _get_font_family_list(self, primary_family=None):
        if self._cartoon_mode:
            families = [
                primary_family or self._cartoon_font,
                'Comic Sans MS',
                '华文彩云',
                '幼圆',
                'Microsoft YaHei',
                'SimHei',
                'Arial Unicode MS',
                'sans-serif',
            ]
        else:
            families = [
                primary_family or self._font_family,
                'Times New Roman',
                'Microsoft YaHei',
                'SimHei',
                'SimSun',
                'Arial Unicode MS',
                'sans-serif',
            ]
        unique_families = []
        for family in families:
            if not family or family in unique_families:
                continue
            if family and family not in unique_families:
                unique_families.append(family)
        return unique_families

    def _make_font_properties(self, size=None, weight='normal', font_family=None):
        return fm.FontProperties(
            family=self._get_font_family_list(primary_family=font_family),
            size=size,
            weight=weight,
        )

    def set_border_width(self, width):
        self._border_width = width

    def _apply_plot_style(self):
        bg = self._cartoon_bg if self._cartoon_mode else PLOT_BACKGROUND
        fg = self._cartoon_fg if self._cartoon_mode else PLOT_FOREGROUND
        self.figure.patch.set_facecolor(bg)
        self.axes.set_facecolor(bg)
        self.axes.tick_params(colors=fg)
        self._apply_tick_visibility()
        for spine in self.axes.spines.values():
            spine.set_color(fg)
            if self._cartoon_mode:
                spine.set_linewidth(2.0)
                spine.set_capstyle('round')
                spine.set_joinstyle('round')
                spine.set_path_effects([
                    patheffects.withStroke(linewidth=4, foreground='#5A3A20',
                                           capstyle='round', joinstyle='round', alpha=0.15),
                    patheffects.Normal()
                ])
            else:
                spine.set_path_effects([])

    def _apply_tick_visibility(self):
        self.axes.tick_params(
            axis='x', which='both',
            bottom=self._show_x_ticks, top=False, labelbottom=self._show_x_ticks
        )
        self.axes.tick_params(
            axis='y', which='both',
            left=self._show_y_ticks, right=False, labelleft=self._show_y_ticks
        )

    def _resolve_line_style(self, style_key):
        mapping = {
            'solid': 'solid',
            'dashed': 'dashed',
            'dashdot': 'dashdot',
            'dotted': 'dotted',
            'loose_dashed': (0, (8, 5)),
            'loose_dashdot': (0, (8, 4, 2, 4)),
        }
        return mapping.get(style_key, 'solid')

    def _apply_cartoon_line_style(self, line):
        if not self._cartoon_mode:
            return
        base_lw = line.get_linewidth()
        new_lw = max(base_lw * 1.6, 2.0)
        line.set_linewidth(new_lw)
        line.set_solid_capstyle('round')
        line.set_solid_joinstyle('round')
        color = line.get_color()
        # 蜡笔涂抹感：收敛的多层描边，视觉上更细但仍保留手绘质感
        line.set_path_effects([
            patheffects.withStroke(linewidth=new_lw + 5, foreground='#5A3A20',
                                   capstyle='round', joinstyle='round', alpha=0.12),
            patheffects.withStroke(linewidth=new_lw + 2, foreground=color,
                                   capstyle='round', joinstyle='round', alpha=0.45),
            patheffects.Normal()
        ])

    def _hand_drawn_jitter(self, y, seed=42):
        if not self._cartoon_mode or len(y) < 3:
            return y
        rng = np.random.default_rng(seed)
        n = len(y)
        y_range = float(np.max(y) - np.min(y))
        amp = max(y_range * 0.012, np.max(np.abs(y)) * 0.006, 0.5)
        t = np.linspace(0.0, 1.0, n)
        noise = np.zeros(n, dtype=float)
        # 低频大扭曲（模拟手臂抖动）
        for _ in range(5):
            freq = rng.uniform(2.0, 8.0)
            phase = rng.uniform(0.0, 2.0 * np.pi)
            noise += amp * rng.uniform(0.3, 1.0) * np.sin(2.0 * np.pi * freq * t + phase)
        # 中频扭曲
        for _ in range(4):
            freq = rng.uniform(8.0, 20.0)
            phase = rng.uniform(0.0, 2.0 * np.pi)
            noise += amp * rng.uniform(0.1, 0.35) * np.sin(2.0 * np.pi * freq * t + phase)
        # 高频毛刺
        noise += rng.normal(0.0, amp * 0.25, n)
        return y + noise

    def plot_overlay(self, data_list):
        self.clear()
        with plt.style.context('default'):
            for i, data in enumerate(data_list):
                plot_y = self._hand_drawn_jitter(data.intensity, seed=42 + i * 137)
                line, = self.axes.plot(
                    data.two_theta, plot_y,
                    color=data.color, label=data.display_name,
                    linewidth=getattr(data, 'line_width', 1.0),
                    linestyle=self._resolve_line_style(getattr(data, 'line_style', 'solid')),
                )
                self._apply_cartoon_line_style(line)
                self._lines.append(line)
                self._plotted_series.append({
                    'data': data,
                    'x': np.asarray(data.two_theta),
                    'y': np.asarray(data.intensity),
                })
            self._apply_plot_style()
            self.axes.tick_params(direction='in')
            if self._cartoon_mode:
                self.axes.tick_params(width=2.0, length=7)
            self._apply_border()
        return self._lines

    def plot_stacked(self, data_list, offset_factor=0.8):
        self.clear()
        with plt.style.context('default'):
            max_intensities = []
            for data in data_list:
                max_intensities.append(np.max(data.intensity) - np.min(data.intensity))

            offsets = [0.0]
            for i in range(1, len(data_list)):
                offsets.append(offsets[-1] + max_intensities[i - 1] * offset_factor)

            for i, data in enumerate(data_list):
                plotted_y = data.intensity + offsets[i]
                plot_y = self._hand_drawn_jitter(plotted_y, seed=42 + i * 137)
                line, = self.axes.plot(
                    data.two_theta, plot_y,
                    color=data.color, label=data.display_name,
                    linewidth=getattr(data, 'line_width', 1.0),
                    linestyle=self._resolve_line_style(getattr(data, 'line_style', 'solid')),
                )
                self._apply_cartoon_line_style(line)
                self._lines.append(line)
                self._plotted_series.append({
                    'data': data,
                    'x': np.asarray(data.two_theta),
                    'y': np.asarray(plotted_y),
                })

            self.axes.set_yticklabels([])
            self._apply_plot_style()
            self.axes.tick_params(direction='in')
            if self._cartoon_mode:
                self.axes.tick_params(width=2.0, length=7)
            self._apply_border()
        return self._lines

    def _apply_border(self):
        for spine in self.axes.spines.values():
            spine.set_linewidth(self._border_width)

    def set_axis_range(self, x_min=None, x_max=None, y_min=None, y_max=None):
        if x_min is not None and x_max is not None:
            self.axes.set_xlim(x_min, x_max)
        if y_min is not None and y_max is not None:
            self.axes.set_ylim(y_min, y_max)

    def set_axis_ticks(self, x_major=None, y_major=None, tick_direction='in',
                       show_x_ticks=True, show_y_ticks=False):
        self._show_x_ticks = show_x_ticks
        self._show_y_ticks = show_y_ticks
        if x_major is not None:
            self.axes.xaxis.set_major_locator(MultipleLocator(x_major))
        if y_major is not None:
            self.axes.yaxis.set_major_locator(MultipleLocator(y_major))
        self.axes.tick_params(direction=tick_direction)
        self._apply_tick_visibility()

    def _set_text_outline(self, text_obj, fg):
        """给文字添加轻微描边，保证在卡通浅色背景上清晰可见。"""
        text_obj.set_path_effects([
            patheffects.withStroke(linewidth=2.5, foreground=fg, alpha=0.9),
            patheffects.Normal()
        ])

    def set_labels(self, title='', xlabel='2θ (°)', ylabel='Intensity (a.u.)',
                   title_size=14, label_size=12, tick_size=10, title_bold=False,
                   show_xlabel=True, show_ylabel=True):
        fg = self._cartoon_fg if self._cartoon_mode else PLOT_FOREGROUND
        font = self._cartoon_font if self._cartoon_mode else None
        tsize = int(title_size * 1.3) if self._cartoon_mode else title_size
        lsize = int(label_size * 1.2) if self._cartoon_mode else label_size
        tcksize = int(tick_size * 1.2) if self._cartoon_mode else tick_size
        weight = 'bold' if title_bold else 'normal'

        title_text = self.axes.set_title(title, color=fg, fontsize=tsize,
                                         fontweight=weight)
        xlabel_text = self.axes.set_xlabel(
            xlabel if show_xlabel else '', color=fg, fontsize=lsize
        )
        ylabel_text = self.axes.set_ylabel(
            ylabel if show_ylabel else '', color=fg, fontsize=lsize
        )

        title_text.set_fontproperties(self._make_font_properties(size=tsize, weight=weight, font_family=font))
        xlabel_text.set_fontproperties(self._make_font_properties(size=lsize, font_family=font))
        ylabel_text.set_fontproperties(self._make_font_properties(size=lsize, font_family=font))
        self.axes.tick_params(labelsize=tcksize, colors=fg)

        tick_labels = self.axes.get_xticklabels() + self.axes.get_yticklabels()
        for label in tick_labels:
            label.set_fontproperties(self._make_font_properties(size=tcksize, font_family=font))
            label.set_color(fg)

        # 儿童模式下给所有文字加实心描边，防止空心/看不清
        if self._cartoon_mode:
            self._set_text_outline(title_text, fg)
            self._set_text_outline(xlabel_text, fg)
            self._set_text_outline(ylabel_text, fg)
            for label in tick_labels:
                self._set_text_outline(label, fg)

        self._apply_tick_visibility()

    def draw_curve_labels(self, draggable=False, font_size=10, font_family=None):
        """为每条谱图绘制独立文字标签（替代集中图例）。

        默认放在每条曲线最高峰上方；被手动拖动过的标签使用保存的位置。
        draggable=True 时标签可被鼠标拖动。
        """
        fnt = self._cartoon_font if self._cartoon_mode else (font_family or self._legend_font_family)
        self._curve_labels = []
        if not self._plotted_series:
            return
        y_min, y_max = self.axes.get_ylim()
        pad = max((y_max - y_min) * 0.02, 1e-6)
        x_min, x_max = self.axes.get_xlim()
        x_inset = (x_max - x_min) * 0.01
        for series in self._plotted_series:
            data = series['data']
            x = np.asarray(series['x'])
            y = np.asarray(series['y'])
            if len(x) == 0:
                continue
            override = self._label_positions.get(id(data))
            if override is not None:
                tx, ty = override
            else:
                # 默认放在每条谱图的右上方
                tx, ty = float(x[-1]) - x_inset, float(y[-1]) + pad
            text = self.axes.text(
                tx, ty, data.display_name,
                color=data.color, ha='right', va='bottom',
                fontsize=font_size,
                fontproperties=self._make_font_properties(size=font_size, font_family=fnt),
                zorder=11,
            )
            if draggable:
                text.set_picker(True)
            self._curve_labels.append((text, data))

    def save_label_position(self, data, position):
        self._label_positions[id(data)] = (float(position[0]), float(position[1]))

    def set_legend(self, show=True, position='upper right', show_frame=False,
                   font_size=10, font_family=None):
        fg = self._cartoon_fg if self._cartoon_mode else PLOT_FOREGROUND
        fnt = self._cartoon_font if self._cartoon_mode else (font_family or self._legend_font_family)
        fsize = int(font_size * 1.2) if self._cartoon_mode else font_size
        fancy = self._cartoon_mode
        if not show:
            legend = self.axes.get_legend()
            if legend:
                legend.remove()
            return
        if self._lines:
            legend = self.axes.legend(
                handles=self._lines,
                loc=position,
                frameon=show_frame,
                edgecolor=fg if show_frame else 'none',
                fancybox=fancy,
                prop=self._make_font_properties(size=fsize, font_family=fnt)
            )
            for text in legend.get_texts():
                text.set_color(fg)
                text.set_fontproperties(
                    self._make_font_properties(size=fsize, font_family=fnt)
                )
                if self._cartoon_mode:
                    self._set_text_outline(text, fg)
            if legend.get_title():
                legend.get_title().set_color(fg)
                if self._cartoon_mode:
                    self._set_text_outline(legend.get_title(), fg)

    def _find_candidate_peaks(self, x, y):
        if len(x) < 3 or len(y) < 3:
            return np.array([], dtype=int)
        return np.array([
            idx for idx in range(1, len(y) - 1)
            if y[idx] >= y[idx - 1] and y[idx] >= y[idx + 1]
            and (y[idx] > y[idx - 1] or y[idx] > y[idx + 1])
        ], dtype=int)

    def _select_top_peaks(self, x, y, candidates, count_mode, count, min_distance):
        if len(candidates) == 0:
            return np.array([], dtype=int)

        max_count = 10 if count_mode == 'auto' else max(1, min(int(count), 10))
        ordered = sorted(candidates, key=lambda idx: y[idx], reverse=True)
        selected = []
        for idx in ordered:
            if all(abs(x[idx] - x[chosen]) >= min_distance for chosen in selected):
                selected.append(idx)
            if len(selected) >= max_count:
                break
        return np.array(sorted(selected, key=lambda idx: x[idx]), dtype=int)

    def _get_marker_symbol(self, symbol_key):
        mapping = {
            'circle': 'o',
            'square': 's',
            'triangle': '^',
            'triangle_down': 'v',
            'diamond': 'D',
            'star': '*',
            'hexagon': 'h',
            'pentagon': 'p',
            'plus': 'P',
            'x': 'X',
        }
        return mapping.get(symbol_key, 'o')

    def draw_manual_markers(self, markers, selected_index=None):
        if not markers:
            return

        bg = self._cartoon_bg if self._cartoon_mode else PLOT_BACKGROUND
        fnt = self._cartoon_font if self._cartoon_mode else None
        for index, marker in enumerate(markers):
            marker_symbol = self._get_marker_symbol(marker.get('symbol', 'circle'))
            marker_size = float(marker.get('size', 70))
            marker_color = marker.get('color', '#d62728')
            x = marker.get('x')
            y = marker.get('y')
            if x is None or y is None:
                continue

            if index == selected_index:
                self.axes.scatter(
                    [x], [y],
                    s=marker_size * 1.8,
                    marker=marker_symbol,
                    color='none',
                    edgecolors='#111827',
                    linewidths=2.0 if self._cartoon_mode else 1.3,
                    zorder=8,
                )

            scatter_kwargs = dict(
                s=marker_size,
                marker=marker_symbol,
                color=marker_color,
                edgecolors='white',
                linewidths=1.5 if self._cartoon_mode else 0.8,
                zorder=9,
            )
            if self._cartoon_mode:
                scatter_kwargs['linewidths'] = 2.0
            self.axes.scatter([x], [y], **scatter_kwargs)

            marker_text = str(marker.get('text', '') or '').strip()
            if marker_text:
                self.axes.annotate(
                    marker_text,
                    xy=(x, y),
                    xytext=(10, 8),
                    textcoords='offset points',
                    ha='left',
                    va='bottom',
                    color='#111827',
                    fontsize=11 if self._cartoon_mode else 9,
                    fontproperties=self._make_font_properties(size=11 if self._cartoon_mode else 9, font_family=fnt),
                    bbox=dict(
                        boxstyle='round,pad=0.2' if self._cartoon_mode else 'round,pad=0.16',
                        facecolor=bg,
                        edgecolor='none',
                        alpha=0.78,
                    ),
                    zorder=10 if index == selected_index else 9,
                )

    def draw_stickers(self, stickers):
        if not self._cartoon_mode or not stickers:
            return
        # 根据轴数据范围计算贴图缩放，确保不同数据尺度下大小一致
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        x_range = max(abs(xlim[1] - xlim[0]), 1e-6)
        y_range = max(abs(ylim[1] - ylim[0]), 1e-6)
        for sticker in stickers:
            x = sticker.get('x')
            y = sticker.get('y')
            if x is None or y is None:
                continue
            sticker_type = sticker.get('type', '小花')
            size = sticker.get('size', 20)
            color = sticker.get('color', '#FF6B6B')
            # 贴图在视觉上约占轴范围的 size/20 * 5%
            frac = 0.05 * (size / 20.0)
            sx = x_range * frac
            sy = y_range * frac
            drawer = STICKER_DRAWERS.get(sticker_type, _draw_flower)
            drawer(self.axes, x, y, sx, sy, color)

    def _get_peak_offsets(self, total_count, index):
        offset_patterns = [
            (0, 12),
            (0, 22),
            (10, 18),
            (-10, 18),
            (14, 28),
            (-14, 28),
            (18, 14),
            (-18, 14),
            (22, 26),
            (-22, 26),
        ]
        return offset_patterns[index % min(max(total_count, 1), len(offset_patterns))]

    def annotate_peaks(self, data_list, peak_global_cfg):
        mode = peak_global_cfg.get('peak_mark_mode', 'symbol+value')
        count_mode = peak_global_cfg.get('peak_count_mode', 'manual')
        peak_count = peak_global_cfg.get('peak_count', 3)
        min_distance = max(peak_global_cfg.get('peak_min_distance', 0.5), 0.01)
        decimals = max(0, int(peak_global_cfg.get('peak_label_decimals', 2)))
        bg = self._cartoon_bg if self._cartoon_mode else PLOT_BACKGROUND
        fnt = self._cartoon_font if self._cartoon_mode else None
        sym_size = 60 if self._cartoon_mode else 42
        lbl_size = 11 if self._cartoon_mode else 9
        lw = 1.2 if self._cartoon_mode else 0.6

        for series in self._plotted_series:
            data = series['data']
            if not data.peak_mark_enabled:
                continue

            x = np.asarray(series['x'])
            y = np.asarray(series['y'])
            candidates = self._find_candidate_peaks(x, y)
            selected = self._select_top_peaks(x, y, candidates, count_mode, peak_count, min_distance)
            if len(selected) == 0:
                continue

            peak_x = x[selected]
            peak_y = y[selected]

            if mode in ('symbol', 'symbol+value'):
                self.axes.scatter(
                    peak_x,
                    peak_y,
                    s=sym_size,
                    marker=self._get_marker_symbol(data.peak_symbol),
                    color=data.peak_symbol_color,
                    edgecolors='white',
                    linewidths=lw,
                    zorder=6,
                )

            if mode in ('value', 'symbol+value'):
                for idx, peak_idx in enumerate(selected):
                    dx, dy = self._get_peak_offsets(len(selected), idx)
                    self.axes.annotate(
                        f"{x[peak_idx]:.{decimals}f}",
                        xy=(x[peak_idx], y[peak_idx]),
                        xytext=(dx, dy),
                        textcoords='offset points',
                        ha='center',
                        va='bottom',
                        color=data.peak_text_color,
                        fontsize=lbl_size,
                        fontproperties=self._make_font_properties(size=lbl_size, font_family=fnt),
                        bbox=dict(boxstyle='round,pad=0.2',
                                  facecolor=bg,
                                  edgecolor='none',
                                  alpha=0.75),
                        zorder=7,
                    )

    def apply_color_scheme(self, data_list, scheme_name):
        colors = COLOR_SCHEMES.get(scheme_name, COLOR_SCHEMES['Custom'])
        for i, data in enumerate(data_list):
            data.color = colors[i % len(colors)]
        return data_list

    def export_figure(self, filepath, dpi=300, width=8, height=6):
        self.figure.set_size_inches(width, height)
        self.figure.savefig(filepath, dpi=dpi, bbox_inches='tight')

    @staticmethod
    def get_available_fonts():
        fonts = set()
        for font in fm.fontManager.ttflist:
            fonts.add(font.name)
        return sorted(list(fonts))
