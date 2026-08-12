"""i18n —— Relax XRD Plotter 界面国际化（中文 / 英文）。

- 文本类：tr(key) 返回当前语言下的字符串（缺省回退到 key）。
- 下拉选项类：部分下拉的“显示文字”随语言变化，但内部值是稳定的英文键。
  用 choice_items / choice_key / choice_display 在“显示文字 <-> 内部键”之间转换。
- 语言状态：全局 _LANG，由主窗口从 QSettings 读取后 set_language()。
"""

_LANG = 'zh'

# ----------------------------------------------------------------------------
# 纯文本
# ----------------------------------------------------------------------------
_STRINGS = {
    # 标题栏
    'app_title': {'zh': '🔬 Relax XRD Plotter', 'en': '🔬 Relax XRD Plotter'},
    'drag_hint': {'zh': '拖拽数据到这里', 'en': 'Drag data here'},
    'btn_author': {'zh': '👤 作者', 'en': '👤 Author'},
    'language': {'zh': '语言', 'en': 'Language'},

    # 左侧标签页 / 右侧面板头
    'tab_data': {'zh': '📁 数据', 'en': '📁 Data'},
    'tab_plot': {'zh': '🎨 绘图', 'en': '🎨 Plot'},
    'annotation_header': {'zh': '✳ 标注', 'en': '✳ Annotate'},

    # 数据文件区
    'data_files': {'zh': '📁 数据文件', 'en': '📁 Data Files'},
    'btn_open': {'zh': '📂 打开数据文件', 'en': '📂 Open Data'},
    'legend_name': {'zh': '图例名称:', 'en': 'Legend name:'},
    'legend_name_ph': {'zh': '输入当前样品在图例中的名称', 'en': 'Name shown in legend for current sample'},
    'line_width': {'zh': '当前线宽:', 'en': 'Line width:'},
    'line_style': {'zh': '当前线型:', 'en': 'Line style:'},
    'btn_add': {'zh': '添加', 'en': 'Add'},
    'btn_remove': {'zh': '删除', 'en': 'Remove'},
    'btn_up': {'zh': '↑', 'en': '↑'},
    'btn_down': {'zh': '↓', 'en': '↓'},

    # 绘图模式区
    'plot_mode': {'zh': '🎨 绘图模式', 'en': '🎨 Plot Mode'},
    'overlay': {'zh': '单图模式', 'en': 'Overlay'},
    'stacked': {'zh': '堆叠模式', 'en': 'Stacked'},
    'offset': {'zh': '偏移系数:', 'en': 'Offset:'},

    # 颜色区
    'colors': {'zh': '🎭 颜色设置', 'en': '🎭 Colors'},
    'color_scheme': {'zh': '预设配色:', 'en': 'Color scheme:'},

    # 坐标轴
    'axes': {'zh': '📐 坐标轴', 'en': '📐 Axes'},
    'x_min': {'zh': 'X最小值:', 'en': 'X min:'},
    'x_max': {'zh': 'X最大值:', 'en': 'X max:'},
    'y_min': {'zh': 'Y最小值:', 'en': 'Y min:'},
    'y_max': {'zh': 'Y最大值:', 'en': 'Y max:'},
    'x_major': {'zh': 'X主刻度:', 'en': 'X major:'},
    'y_major': {'zh': 'Y主刻度:', 'en': 'Y major:'},
    'tick_dir': {'zh': '刻度方向:', 'en': 'Tick dir:'},
    'show_x_ticks': {'zh': '显示X轴刻度', 'en': 'Show X ticks'},
    'show_y_ticks': {'zh': '显示Y轴刻度', 'en': 'Show Y ticks'},
    'reset_auto': {'zh': '重置为自动', 'en': 'Reset to Auto'},
    'auto': {'zh': '自动', 'en': 'Auto'},

    # 标峰
    'peak_marking': {'zh': '📍 标峰设置', 'en': '📍 Peak Marking'},
    'peak_mode': {'zh': '显示模式:', 'en': 'Display:'},
    'peak_count': {'zh': '峰数量:', 'en': 'Peak count:'},
    'peak_manual_count': {'zh': '手动峰数:', 'en': 'Manual count:'},
    'peak_min_dist': {'zh': '最小峰间距:', 'en': 'Min spacing:'},
    'peak_decimals': {'zh': '数值小数位:', 'en': 'Decimals:'},
    'peak_enable': {'zh': '当前谱图启用标峰', 'en': 'Mark peaks for this curve'},
    'symbol_type': {'zh': '符号类型:', 'en': 'Symbol:'},
    'symbol_color': {'zh': '符号颜色:', 'en': 'Symbol color:'},
    'peak_value_color': {'zh': '峰位颜色:', 'en': 'Label color:'},
    'pick_color': {'zh': '选择颜色', 'en': 'Pick color'},

    # 儿童贴图（隐藏功能，仍翻译以兼容）
    'stickers': {'zh': '🎨 儿童贴图', 'en': '🎨 Kids Stickers'},
    'sticker_enable': {'zh': '启用儿童贴图', 'en': 'Enable stickers'},
    'sticker_type': {'zh': '贴图类型:', 'en': 'Sticker type:'},
    'sticker_color': {'zh': '贴图颜色:', 'en': 'Sticker color:'},
    'size': {'zh': '大小:', 'en': 'Size:'},
    'sticker_hint': {'zh': '勾选“启用儿童贴图”后，在右侧图面上点击即可放置贴图。',
                     'en': 'Enable stickers, then click on the plot to place a sticker.'},
    'btn_up_move': {'zh': '上移', 'en': 'Move up'},
    'btn_down_move': {'zh': '下移', 'en': 'Move down'},
    'btn_delete_selected': {'zh': '删除选中', 'en': 'Delete selected'},
    'btn_clear_all': {'zh': '清空全部', 'en': 'Clear all'},

    # 手动标记
    'manual_markers': {'zh': '✳ 手动标记', 'en': '✳ Manual Markers'},
    'manual_enable': {'zh': '启用手动标记', 'en': 'Enable manual markers'},
    'manual_symbol_color': {'zh': '符号颜色:', 'en': 'Symbol color:'},
    'manual_hint': {'zh': '先勾选“启用手动标记”，再左键点击图面添加符号；点击已有符号可选中，再删除。',
                    'en': 'Enable manual markers, then left-click the plot to add. Click an existing marker to select, then delete.'},
    'default_text': {'zh': '默认文字:', 'en': 'Default text:'},
    'default_text_ph': {'zh': '新加符号默认带上的文字', 'en': 'Text auto-added to new markers'},
    'current_text': {'zh': '当前文字:', 'en': 'Current text:'},
    'current_text_ph': {'zh': '修改当前选中符号的文字', 'en': 'Edit text of selected marker'},
    'btn_apply_text': {'zh': '应用文字', 'en': 'Apply text'},
    'btn_left': {'zh': '左移', 'en': 'Left'},
    'btn_right': {'zh': '右移', 'en': 'Right'},
    'btn_undo_last': {'zh': '撤销最后一个', 'en': 'Undo last'},

    # 图尺寸
    'figure_size': {'zh': '📏 图尺寸', 'en': '📏 Figure Size'},
    'width_in': {'zh': '宽(in):', 'en': 'Width (in):'},
    'height_in': {'zh': '高(in):', 'en': 'Height (in):'},
    'figure_tip': {'zh': '修改后会实时更新右侧预览，导出图片也沿用当前尺寸。',
                   'en': 'Updates the preview live; export uses the same size.'},

    # 标题与标签
    'title_labels': {'zh': '📝 标题与标签', 'en': '📝 Title & Labels'},
    'title': {'zh': '标题:', 'en': 'Title:'},
    'xlabel': {'zh': 'X轴标签:', 'en': 'X label:'},
    'ylabel': {'zh': 'Y轴标签:', 'en': 'Y label:'},
    'title_size': {'zh': '标题字号:', 'en': 'Title size:'},
    'label_size': {'zh': '标签字号:', 'en': 'Label size:'},
    'tick_size': {'zh': '刻度字号:', 'en': 'Tick size:'},
    'font': {'zh': '字体:', 'en': 'Font:'},
    'title_bold': {'zh': '标题加粗', 'en': 'Bold title'},
    'show_xlabel': {'zh': '显示X轴标题', 'en': 'Show X label'},
    'show_ylabel': {'zh': '显示Y轴标题', 'en': 'Show Y label'},

    # 图例
    'legend': {'zh': '📋 图例', 'en': '📋 Legend'},
    'legend_show': {'zh': '显示图例', 'en': 'Show legend'},
    'legend_layout': {'zh': '图例布局:', 'en': 'Legend layout:'},
    'legend_pos': {'zh': '位置:', 'en': 'Position:'},
    'legend_font_size': {'zh': '图例字号:', 'en': 'Legend size:'},
    'legend_font': {'zh': '图例字体:', 'en': 'Legend font:'},
    'legend_frame': {'zh': '显示图例边框', 'en': 'Show legend frame'},
    'legend_hint': {'zh': '“谱图上方”将名称标注在对应曲线右上方；“手动拖动”可用鼠标拖动每个标签。',
                   'en': '"Above plot" puts the name at the top-right of each curve; "Draggable" lets you drag each label.'},

    # 边框
    'border': {'zh': '📦 边框设置', 'en': '📦 Border'},
    'border_bold': {'zh': '外边框加粗', 'en': 'Bold border'},
    'border_width': {'zh': '边框宽度:', 'en': 'Border width:'},

    # 底部按钮
    'btn_refresh': {'zh': '🔄 刷新绘图', 'en': '🔄 Refresh'},
    'btn_export': {'zh': '💾 导出图片', 'en': '💾 Export'},
    'btn_save': {'zh': '📄 保存处理文件', 'en': '📄 Save Project'},
    'btn_apply_name': {'zh': '应用', 'en': 'Apply'},

    # 对话框 / 消息
    'author_title': {'zh': '作者信息', 'en': 'Author Info'},
    'author_body': {'zh': '<p>作者：qxh<br>单位：WIT<br>邮箱：qbaiyi@qq.com</p>'
                          '<p style=\'font-size:18px; font-weight:700; color:{accent};\'>看不懂，也实在卷不动！！</p>',
                      'en': '<p>Author: qxh<br>Affiliation: WIT<br>Email: qbaiyi@qq.com</p>'
                           '<p style=\'font-size:18px; font-weight:700; color:{accent};\'>Can\'t follow it, and honestly can\'t keep up either!!</p>'},
    'msg_hint': {'zh': '提示', 'en': 'Hint'},
    'please_add_data': {'zh': '请先添加XRD数据文件', 'en': 'Please add XRD data files first'},
    'load_failed': {'zh': '加载失败', 'en': 'Load failed'},
    'load_failed_msg': {'zh': '无法加载文件:\n{path}\n\n{err}',
                        'en': 'Failed to load file:\n{path}\n\n{err}'},
    'open_failed': {'zh': '打开失败', 'en': 'Open failed'},
    'open_failed_msg': {'zh': '无法读取工程文件:\n{path}\n\n{err}',
                        'en': 'Cannot read project file:\n{path}\n\n{err}'},
    'name_invalid': {'zh': '名称无效', 'en': 'Invalid name'},
    'name_empty': {'zh': '图例名称不能为空', 'en': 'Legend name cannot be empty'},
    'save_ok': {'zh': '保存成功', 'en': 'Saved'},
    'save_ok_msg': {'zh': '工程文件已保存至:\n{path}\n\n下次直接打开或拖入该文件，即可恢复全部编辑状态。',
                    'en': 'Project saved to:\n{path}\n\nOpen or drop this file next time to restore all edits.'},
    'save_ok_data_msg': {'zh': '处理后的数据已保存至:\n{path}', 'en': 'Processed data saved to:\n{path}'},
    'save_failed': {'zh': '保存失败', 'en': 'Save failed'},
    'save_failed_msg': {'zh': '保存工程文件时出错:\n{err}', 'en': 'Error saving project:\n{err}'},
    'save_failed_data_msg': {'zh': '保存处理文件时出错:\n{err}', 'en': 'Error saving data:\n{err}'},
    'export_ok': {'zh': '导出成功', 'en': 'Exported'},
    'export_ok_msg': {'zh': '图片已保存至:\n{path}', 'en': 'Image saved to:\n{path}'},
    'export_failed': {'zh': '导出失败', 'en': 'Export failed'},
    'export_failed_msg': {'zh': '导出图片时出错:\n{err}', 'en': 'Error exporting image:\n{err}'},
    'save_dialog': {'zh': '保存处理文件', 'en': 'Save project'},
    'open_dialog': {'zh': '选择XRD数据文件', 'en': 'Select XRD data files'},
    'export_dialog': {'zh': '导出图片', 'en': 'Export image'},
    'export_dpi': {'zh': '导出DPI', 'en': 'Export DPI'},
    'export_dpi_msg': {'zh': '请输入导出DPI:', 'en': 'Enter export DPI:'},
    'points_suffix': {'zh': '点', 'en': 'pts'},

    # 文件对话框过滤器
    'filter_xrd': {'zh': 'XRD数据文件', 'en': 'XRD data files'},
    'filter_proj': {'zh': 'XRD工程文件', 'en': 'XRD project'},
    'filter_all': {'zh': '所有文件', 'en': 'All files'},
}

# ----------------------------------------------------------------------------
# 可翻译下拉选项：(内部键, 中文显示, 英文显示)
# ----------------------------------------------------------------------------
SYMBOL_CHOICES = [
    ('circle', '圆形', 'Circle'),
    ('square', '正方形', 'Square'),
    ('triangle', '三角形', 'Triangle'),
    ('triangle_down', '倒三角形', 'Inverted triangle'),
    ('diamond', '菱形', 'Diamond'),
    ('star', '五角星', 'Star'),
    ('hexagon', '六边形', 'Hexagon'),
    ('pentagon', '五边形', 'Pentagon'),
    ('plus', '十字形', 'Plus'),
    ('x', '叉形', 'Cross'),
]

LINESTYLE_CHOICES = [
    ('solid', '实线', 'Solid'),
    ('dashed', '虚线', 'Dashed'),
    ('dashdot', '点划线', 'Dash-dot'),
    ('dotted', '点线', 'Dotted'),
    ('loose_dashed', '稀疏虚线', 'Loose dashed'),
    ('loose_dashdot', '稀疏点划线', 'Loose dash-dot'),
]

LEGEND_LAYOUT_CHOICES = [
    ('grouped', '集中图例', 'Grouped'),
    ('above', '谱图上方', 'Above plot'),
    ('drag', '手动拖动', 'Draggable'),
]

LEGEND_POS_CHOICES = [
    ('upper right', '右上', 'Upper right'),
    ('upper left', '左上', 'Upper left'),
    ('lower left', '左下', 'Lower left'),
    ('lower right', '右下', 'Lower right'),
    ('center left', '左中', 'Center left'),
    ('center right', '右中', 'Center right'),
    ('upper center', '上中', 'Upper center'),
    ('lower center', '下中', 'Lower center'),
    ('center', '居中', 'Center'),
]

PEAK_MODE_CHOICES = [
    ('symbol', '仅符号', 'Symbol only'),
    ('value', '仅峰位', 'Value only'),
    ('symbol+value', '符号+峰位', 'Symbol + value'),
]

COUNT_MODE_CHOICES = [
    ('manual', '手动', 'Manual'),
    ('auto', '自动', 'Auto'),
]

TICK_DIR_CHOICES = [
    ('in', '向内', 'Inward'),
    ('out', '向外', 'Outward'),
    ('inout', '双向', 'Both'),
]

STICKER_CHOICES = [
    ('flower', '小花', 'Flower'),
    ('grass', '小草', 'Grass'),
    ('sun', '太阳', 'Sun'),
    ('bird', '小鸟', 'Bird'),
    ('girl', '小女孩', 'Girl'),
    ('boy', '小男孩', 'Boy'),
    ('rainbow', '彩虹', 'Rainbow'),
    ('star', '星星', 'Star'),
    ('butterfly', '蝴蝶', 'Butterfly'),
    ('mushroom', '蘑菇', 'Mushroom'),
    ('cloud', '云朵', 'Cloud'),
    ('heart', '爱心', 'Heart'),
]

LANGUAGE_CHOICES = [
    ('zh', '中文', '中文'),
    ('en', 'English', 'English'),
]

CHOICES = {
    'symbol': SYMBOL_CHOICES,
    'linestyle': LINESTYLE_CHOICES,
    'legend_layout': LEGEND_LAYOUT_CHOICES,
    'legend_pos': LEGEND_POS_CHOICES,
    'peak_mode': PEAK_MODE_CHOICES,
    'count_mode': COUNT_MODE_CHOICES,
    'tick_dir': TICK_DIR_CHOICES,
    'sticker': STICKER_CHOICES,
    'language': LANGUAGE_CHOICES,
}


# ----------------------------------------------------------------------------
# 接口
# ----------------------------------------------------------------------------
def tr(key):
    entry = _STRINGS.get(key)
    if not entry:
        return key
    return entry.get(_LANG, key)


def set_language(lang):
    global _LANG
    _LANG = lang if lang in ('zh', 'en') else 'zh'


def get_language():
    return _LANG


def choice_items(choice_key):
    return [choice_display(choice_key, k) for k, _, _ in CHOICES[choice_key]]


def choice_display(choice_key, value_key):
    for k, zh, en in CHOICES[choice_key]:
        if k == value_key:
            return en if _LANG == 'en' else zh
    return value_key


def choice_key(choice_key, display_text):
    for k, zh, en in CHOICES[choice_key]:
        if display_text in (zh, en):
            return k
    return None


def retranslate_labels(root):
    """按 tr_key 属性批量刷新 QLabel / QPushButton / QCheckBox / QRadioButton 文本。"""
    from PyQt5.QtWidgets import QLabel, QPushButton, QCheckBox, QRadioButton
    for widget_type in (QLabel, QPushButton, QCheckBox, QRadioButton):
        for w in root.findChildren(widget_type):
            key = w.property('tr_key')
            if key:
                w.setText(tr(key))


def retranslate_choices(root):
    """按 choice_key 属性批量刷新可翻译下拉，并保留当前选中的内部键。"""
    from PyQt5.QtWidgets import QComboBox
    for w in root.findChildren(QComboBox):
        ck = w.property('choice_key')
        if not ck:
            continue
        cur = choice_key(ck, w.currentText())
        w.blockSignals(True)
        w.clear()
        w.addItems(choice_items(ck))
        if cur:
            w.setCurrentText(choice_display(ck, cur))
        w.blockSignals(False)
