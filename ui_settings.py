from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QDoubleSpinBox, QCheckBox, QComboBox,
                             QPushButton, QGridLayout, QColorDialog)
from PyQt5.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFontDatabase
import matplotlib.font_manager as fm
from theme_manager import (DEFAULT_THEME_NAME, build_color_preview_style,
                           build_combo_box_style, build_line_edit_style,
                           build_secondary_button_style, build_spin_box_style,
                           get_theme)


_CURRENT_THEME_NAME = DEFAULT_THEME_NAME

from i18n import (tr, choice_items, choice_key, choice_display,
                 retranslate_labels, retranslate_choices,
                 SYMBOL_CHOICES, LINESTYLE_CHOICES)


def available_system_fonts():
    families = [family for family in QFontDatabase().families() if family and not family.startswith("@")]
    if not families:
        families = [font.name for font in fm.fontManager.ttflist if getattr(font, "name", None)]
    unique = []
    for family in sorted(families, key=str.casefold):
        if family not in unique:
            unique.append(family)
    preferred = [
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "Arial",
        "Times New Roman",
        "KaiTi",
    ]
    ordered = [family for family in preferred if family in unique]
    ordered.extend([family for family in unique if family not in ordered])
    return ordered


def set_current_theme(theme_name):
    global _CURRENT_THEME_NAME
    _CURRENT_THEME_NAME = theme_name or DEFAULT_THEME_NAME


def spin_box_style(min_width=90):
    return build_spin_box_style(_CURRENT_THEME_NAME, min_width=min_width)


def line_edit_style(min_height=26):
    return build_line_edit_style(_CURRENT_THEME_NAME, min_height=min_height)


def combo_box_style(min_width=120):
    return build_combo_box_style(_CURRENT_THEME_NAME, min_width=min_width)


def color_button_style(color=None):
    color_value = color or get_theme(_CURRENT_THEME_NAME)["panel_alt_bg"]
    return build_color_preview_style(_CURRENT_THEME_NAME, color_value)


def apply_basic_theme(widget):
    for spin_box in widget.findChildren(QDoubleSpinBox):
        min_width = spin_box.property("theme_min_width") or 90
        spin_box.setStyleSheet(spin_box_style(min_width=int(min_width)))
    for line_edit in widget.findChildren(QLineEdit):
        min_height = line_edit.property("theme_min_height") or 26
        line_edit.setStyleSheet(line_edit_style(min_height=int(min_height)))
    for combo_box in widget.findChildren(QComboBox):
        min_width = combo_box.property("theme_min_width") or 120
        combo_box.setStyleSheet(combo_box_style(min_width=int(min_width)))
    for button in widget.findChildren(QPushButton):
        if button.property("theme_role") == "color_button":
            button.setStyleSheet(color_button_style(button.property("selected_color")))
        if button.property("theme_role") == "secondary_button":
            button.setStyleSheet(build_secondary_button_style(_CURRENT_THEME_NAME))


class CollapsibleBox(QWidget):

    def __init__(self, title='', parent=None):
        super().__init__(parent)
        self._collapsed = False
        self._title = title
        self._tr_key = None

        self.toggle_btn = QPushButton(title)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.clicked.connect(self._toggle)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(8)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 6)
        outer.setSpacing(0)
        outer.addWidget(self.toggle_btn)
        outer.addWidget(self.content)

        self.apply_theme()
        self._toggle()

    def _toggle(self):
        self._collapsed = not self.toggle_btn.isChecked()
        self.content.setVisible(not self._collapsed)

    def set_title(self, title):
        self._title = title
        self.toggle_btn.setText(title)

    def addWidget(self, widget):
        self.content_layout.addWidget(widget)

    def addLayout(self, layout):
        self.content_layout.addLayout(layout)

    def apply_theme(self, theme_name=None):
        if theme_name:
            set_current_theme(theme_name)
        theme = get_theme(_CURRENT_THEME_NAME)
        cartoon = theme_name == "卡通乐园"
        radius = "16px" if cartoon else "12px"
        top_radius = "16px 16px 0 0" if cartoon else "12px 12px 0 0"
        bottom_radius = "0 0 16px 16px" if cartoon else "0 0 12px 12px"
        border_w = "3px" if cartoon else "1.5px"
        btn_pad = "14px 18px" if cartoon else "12px 16px"
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: {btn_pad};
                font-weight: bold;
                border: {border_w} solid {theme['border_strong']};
                border-radius: {radius};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme['panel_alt_bg']}, stop:1 {theme['panel_alt_bg_2']});
                color: {theme['text']};
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme['panel_hover']}, stop:1 {theme['panel_alt_bg_2']});
                border-color: {theme['accent']};
            }}
            QPushButton:checked {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme['selection']}, stop:1 {theme['panel_alt_bg_2']});
                border-color: {theme['border_strong']};
                border-radius: {top_radius};
            }}
        """)
        self.content.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 {theme['panel_inner_bg']}, stop:1 {theme['panel_bg']}); "
            f"border: {border_w} solid {theme['border']}; "
            f"border-top: none; border-radius: {bottom_radius};"
        )
        apply_basic_theme(self.content)


def _enable_focus_select_all(spin):
    """聚焦时全选文本：显示“自动”时直接输入数字即可覆盖，无需先删除。"""
    original_handler = spin.focusInEvent

    def handler(event):
        original_handler(event)
        spin.lineEdit().selectAll()

    spin.focusInEvent = handler


class AxisSettingsPanel(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(tr('x_min')); lbl.setProperty('tr_key', 'x_min')
        layout.addWidget(lbl, 0, 0)
        self.x_min_spin = QDoubleSpinBox()
        self.x_min_spin.setRange(-9999, 9999)
        self.x_min_spin.setDecimals(2)
        self.x_min_spin.setSpecialValueText(tr('auto'))
        self.x_min_spin.setValue(-9999)
        self.x_min_spin.setKeyboardTracking(False)
        self.x_min_spin.setProperty("theme_min_width", 90)
        self.x_min_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.x_min_spin, 0, 1)

        lbl = QLabel(tr('x_max')); lbl.setProperty('tr_key', 'x_max')
        layout.addWidget(lbl, 1, 0)
        self.x_max_spin = QDoubleSpinBox()
        self.x_max_spin.setRange(-9999, 9999)
        self.x_max_spin.setDecimals(2)
        self.x_max_spin.setSpecialValueText(tr('auto'))
        self.x_max_spin.setValue(-9999)
        self.x_max_spin.setKeyboardTracking(False)
        self.x_max_spin.setProperty("theme_min_width", 90)
        self.x_max_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.x_max_spin, 1, 1)

        lbl = QLabel(tr('y_min')); lbl.setProperty('tr_key', 'y_min')
        layout.addWidget(lbl, 2, 0)
        self.y_min_spin = QDoubleSpinBox()
        self.y_min_spin.setRange(-9999, 9999)
        self.y_min_spin.setDecimals(2)
        self.y_min_spin.setSpecialValueText(tr('auto'))
        self.y_min_spin.setValue(-9999)
        self.y_min_spin.setKeyboardTracking(False)
        self.y_min_spin.setProperty("theme_min_width", 90)
        self.y_min_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.y_min_spin, 2, 1)

        lbl = QLabel(tr('y_max')); lbl.setProperty('tr_key', 'y_max')
        layout.addWidget(lbl, 3, 0)
        self.y_max_spin = QDoubleSpinBox()
        self.y_max_spin.setRange(-9999, 9999)
        self.y_max_spin.setDecimals(2)
        self.y_max_spin.setSpecialValueText(tr('auto'))
        self.y_max_spin.setValue(-9999)
        self.y_max_spin.setKeyboardTracking(False)
        self.y_max_spin.setProperty("theme_min_width", 90)
        self.y_max_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.y_max_spin, 3, 1)

        lbl = QLabel(tr('x_major')); lbl.setProperty('tr_key', 'x_major')
        layout.addWidget(lbl, 4, 0)
        self.x_major_spin = QDoubleSpinBox()
        self.x_major_spin.setRange(0, 9999)
        self.x_major_spin.setDecimals(1)
        self.x_major_spin.setSpecialValueText(tr('auto'))
        self.x_major_spin.setValue(0)
        self.x_major_spin.setKeyboardTracking(False)
        self.x_major_spin.setProperty("theme_min_width", 90)
        self.x_major_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.x_major_spin, 4, 1)

        lbl = QLabel(tr('y_major')); lbl.setProperty('tr_key', 'y_major')
        layout.addWidget(lbl, 5, 0)
        self.y_major_spin = QDoubleSpinBox()
        self.y_major_spin.setRange(0, 9999)
        self.y_major_spin.setDecimals(1)
        self.y_major_spin.setSpecialValueText(tr('auto'))
        self.y_major_spin.setValue(0)
        self.y_major_spin.setKeyboardTracking(False)
        self.y_major_spin.setProperty("theme_min_width", 90)
        self.y_major_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.y_major_spin, 5, 1)

        lbl = QLabel(tr('tick_dir')); lbl.setProperty('tr_key', 'tick_dir')
        layout.addWidget(lbl, 6, 0)
        self.tick_dir_combo = QComboBox()
        self.tick_dir_combo.addItems(choice_items('tick_dir'))
        self.tick_dir_combo.setProperty("choice_key", "tick_dir")
        self.tick_dir_combo.setProperty("theme_min_width", 120)
        self.tick_dir_combo.setStyleSheet(combo_box_style())
        layout.addWidget(self.tick_dir_combo, 6, 1)

        self.show_x_ticks_check = QCheckBox(tr('show_x_ticks'))
        self.show_x_ticks_check.setProperty('tr_key', 'show_x_ticks')
        self.show_x_ticks_check.setChecked(True)
        layout.addWidget(self.show_x_ticks_check, 7, 0, 1, 2)

        self.show_y_ticks_check = QCheckBox(tr('show_y_ticks'))
        self.show_y_ticks_check.setProperty('tr_key', 'show_y_ticks')
        self.show_y_ticks_check.setChecked(False)
        layout.addWidget(self.show_y_ticks_check, 8, 0, 1, 2)

        self.reset_auto_btn = QPushButton(tr('reset_auto'))
        self.reset_auto_btn.setProperty('tr_key', 'reset_auto')
        self.reset_auto_btn.setProperty("theme_min_width", 120)
        self.reset_auto_btn.setProperty("theme_role", "secondary_button")
        self.reset_auto_btn.setStyleSheet(build_secondary_button_style(_CURRENT_THEME_NAME))
        layout.addWidget(self.reset_auto_btn, 9, 0, 1, 2)

        for spin in [self.x_min_spin, self.x_max_spin, self.y_min_spin,
                     self.y_max_spin, self.x_major_spin, self.y_major_spin]:
            _enable_focus_select_all(spin)
            spin.valueChanged.connect(self.settings_changed)
        self.tick_dir_combo.currentIndexChanged.connect(self.settings_changed)
        self.show_x_ticks_check.stateChanged.connect(self.settings_changed)
        self.show_y_ticks_check.stateChanged.connect(self.settings_changed)
        self.reset_auto_btn.clicked.connect(self.reset_to_auto)

    def retranslate(self):
        retranslate_labels(self)
        retranslate_choices(self)
        for spin in [self.x_min_spin, self.x_max_spin, self.y_min_spin,
                     self.y_max_spin, self.x_major_spin, self.y_major_spin]:
            spin.setSpecialValueText(tr('auto'))

    def reset_to_auto(self):
        sentinel = -9999
        blockers = [
            QSignalBlocker(self.x_min_spin),
            QSignalBlocker(self.x_max_spin),
            QSignalBlocker(self.y_min_spin),
            QSignalBlocker(self.y_max_spin),
            QSignalBlocker(self.x_major_spin),
            QSignalBlocker(self.y_major_spin),
        ]
        self.x_min_spin.setValue(sentinel)
        self.x_max_spin.setValue(sentinel)
        self.y_min_spin.setValue(sentinel)
        self.y_max_spin.setValue(sentinel)
        self.x_major_spin.setValue(0)
        self.y_major_spin.setValue(0)
        del blockers
        self.settings_changed.emit()

    def set_settings(self, cfg):
        sentinel = -9999

        def _v(key):
            value = cfg.get(key)
            return sentinel if value is None else value

        widgets = [self.x_min_spin, self.x_max_spin, self.y_min_spin,
                   self.y_max_spin, self.x_major_spin, self.y_major_spin,
                   self.tick_dir_combo, self.show_x_ticks_check,
                   self.show_y_ticks_check]
        blockers = [QSignalBlocker(w) for w in widgets]
        self.x_min_spin.setValue(_v('x_min'))
        self.x_max_spin.setValue(_v('x_max'))
        self.y_min_spin.setValue(_v('y_min'))
        self.y_max_spin.setValue(_v('y_max'))
        self.x_major_spin.setValue(cfg.get('x_major') or 0)
        self.y_major_spin.setValue(cfg.get('y_major') or 0)
        self.tick_dir_combo.setCurrentText(choice_display('tick_dir', cfg.get('tick_direction', 'in')))
        self.show_x_ticks_check.setChecked(cfg.get('show_x_ticks', True))
        self.show_y_ticks_check.setChecked(cfg.get('show_y_ticks', False))
        del blockers

    def get_settings(self):
        sentinel = -9999
        x_min = self.x_min_spin.value() if self.x_min_spin.value() != sentinel else None
        x_max = self.x_max_spin.value() if self.x_max_spin.value() != sentinel else None
        y_min = self.y_min_spin.value() if self.y_min_spin.value() != sentinel else None
        y_max = self.y_max_spin.value() if self.y_max_spin.value() != sentinel else None
        x_major = self.x_major_spin.value() if self.x_major_spin.value() != 0 else None
        y_major = self.y_major_spin.value() if self.y_major_spin.value() != 0 else None
        tick_direction = choice_key('tick_dir', self.tick_dir_combo.currentText())
        return {
            'x_min': x_min, 'x_max': x_max,
            'y_min': y_min, 'y_max': y_max,
            'x_major': x_major, 'y_major': y_major,
            'tick_direction': tick_direction,
            'show_x_ticks': self.show_x_ticks_check.isChecked(),
            'show_y_ticks': self.show_y_ticks_check.isChecked(),
        }


class LabelSettingsPanel(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        font_items = available_system_fonts()

        lbl = QLabel(tr('title')); lbl.setProperty('tr_key', 'title')
        layout.addWidget(lbl, 0, 0)
        self.title_edit = QLineEdit()
        self.title_edit.setProperty("theme_min_height", 26)
        self.title_edit.setStyleSheet(line_edit_style())
        self.title_edit.setAttribute(Qt.WA_InputMethodEnabled, True)
        layout.addWidget(self.title_edit, 0, 1)

        lbl = QLabel(tr('xlabel')); lbl.setProperty('tr_key', 'xlabel')
        layout.addWidget(lbl, 1, 0)
        self.xlabel_edit = QLineEdit("2θ (°)")
        self.xlabel_edit.setProperty("theme_min_height", 26)
        self.xlabel_edit.setStyleSheet(line_edit_style())
        self.xlabel_edit.setAttribute(Qt.WA_InputMethodEnabled, True)
        layout.addWidget(self.xlabel_edit, 1, 1)

        lbl = QLabel(tr('ylabel')); lbl.setProperty('tr_key', 'ylabel')
        layout.addWidget(lbl, 2, 0)
        self.ylabel_edit = QLineEdit("Intensity (a.u.)")
        self.ylabel_edit.setProperty("theme_min_height", 26)
        self.ylabel_edit.setStyleSheet(line_edit_style())
        self.ylabel_edit.setAttribute(Qt.WA_InputMethodEnabled, True)
        layout.addWidget(self.ylabel_edit, 2, 1)

        lbl = QLabel(tr('title_size')); lbl.setProperty('tr_key', 'title_size')
        layout.addWidget(lbl, 3, 0)
        self.title_size_spin = QDoubleSpinBox()
        self.title_size_spin.setRange(6, 36)
        self.title_size_spin.setValue(14)
        self.title_size_spin.setProperty("theme_min_width", 90)
        self.title_size_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.title_size_spin, 3, 1)

        lbl = QLabel(tr('label_size')); lbl.setProperty('tr_key', 'label_size')
        layout.addWidget(lbl, 4, 0)
        self.label_size_spin = QDoubleSpinBox()
        self.label_size_spin.setRange(6, 36)
        self.label_size_spin.setValue(12)
        self.label_size_spin.setProperty("theme_min_width", 90)
        self.label_size_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.label_size_spin, 4, 1)

        lbl = QLabel(tr('tick_size')); lbl.setProperty('tr_key', 'tick_size')
        layout.addWidget(lbl, 5, 0)
        self.tick_size_spin = QDoubleSpinBox()
        self.tick_size_spin.setRange(6, 36)
        self.tick_size_spin.setValue(10)
        self.tick_size_spin.setProperty("theme_min_width", 90)
        self.tick_size_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.tick_size_spin, 5, 1)

        lbl = QLabel(tr('font')); lbl.setProperty('tr_key', 'font')
        layout.addWidget(lbl, 6, 0)
        self.font_combo = QComboBox()
        self.font_combo.addItems(font_items)
        self.font_combo.setProperty("theme_min_width", 120)
        self.font_combo.setStyleSheet(combo_box_style())
        default_font = "Times New Roman" if "Times New Roman" in font_items else (font_items[0] if font_items else "")
        if default_font:
            self.font_combo.setCurrentText(default_font)
        layout.addWidget(self.font_combo, 6, 1)

        self.title_bold_check = QCheckBox(tr('title_bold'))
        self.title_bold_check.setProperty('tr_key', 'title_bold')
        self.title_bold_check.setChecked(False)
        layout.addWidget(self.title_bold_check, 7, 0, 1, 2)

        self.show_xlabel_check = QCheckBox(tr('show_xlabel'))
        self.show_xlabel_check.setProperty('tr_key', 'show_xlabel')
        self.show_xlabel_check.setChecked(True)
        layout.addWidget(self.show_xlabel_check, 8, 0, 1, 2)

        self.show_ylabel_check = QCheckBox(tr('show_ylabel'))
        self.show_ylabel_check.setProperty('tr_key', 'show_ylabel')
        self.show_ylabel_check.setChecked(True)
        layout.addWidget(self.show_ylabel_check, 9, 0, 1, 2)

        self.title_edit.textChanged.connect(self.settings_changed)
        self.xlabel_edit.textChanged.connect(self.settings_changed)
        self.ylabel_edit.textChanged.connect(self.settings_changed)
        self.title_size_spin.valueChanged.connect(self.settings_changed)
        self.label_size_spin.valueChanged.connect(self.settings_changed)
        self.tick_size_spin.valueChanged.connect(self.settings_changed)
        self.font_combo.currentIndexChanged.connect(self.settings_changed)
        self.title_bold_check.stateChanged.connect(self.settings_changed)
        self.show_xlabel_check.stateChanged.connect(self.settings_changed)
        self.show_ylabel_check.stateChanged.connect(self.settings_changed)

    def retranslate(self):
        retranslate_labels(self)

    def get_settings(self):
        return {
            'title': self.title_edit.text(),
            'xlabel': self.xlabel_edit.text(),
            'ylabel': self.ylabel_edit.text(),
            'title_size': int(self.title_size_spin.value()),
            'label_size': int(self.label_size_spin.value()),
            'tick_size': int(self.tick_size_spin.value()),
            'font_family': self.font_combo.currentText(),
            'title_bold': self.title_bold_check.isChecked(),
            'show_xlabel': self.show_xlabel_check.isChecked(),
            'show_ylabel': self.show_ylabel_check.isChecked(),
        }

    def set_settings(self, cfg):
        widgets = [self.title_edit, self.xlabel_edit, self.ylabel_edit,
                   self.title_size_spin, self.label_size_spin,
                   self.tick_size_spin, self.font_combo,
                   self.title_bold_check, self.show_xlabel_check,
                   self.show_ylabel_check]
        blockers = [QSignalBlocker(w) for w in widgets]
        self.title_edit.setText(cfg.get('title', ''))
        self.xlabel_edit.setText(cfg.get('xlabel', '2θ (°)'))
        self.ylabel_edit.setText(cfg.get('ylabel', 'Intensity (a.u.)'))
        self.title_size_spin.setValue(cfg.get('title_size', 14))
        self.label_size_spin.setValue(cfg.get('label_size', 12))
        self.tick_size_spin.setValue(cfg.get('tick_size', 10))
        font = cfg.get('font_family')
        if font:
            self.font_combo.setCurrentText(font)
        self.title_bold_check.setChecked(cfg.get('title_bold', False))
        self.show_xlabel_check.setChecked(cfg.get('show_xlabel', True))
        self.show_ylabel_check.setChecked(cfg.get('show_ylabel', True))
        del blockers


class LegendSettingsPanel(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        font_items = available_system_fonts()

        self.show_check = QCheckBox(tr('legend_show'))
        self.show_check.setProperty('tr_key', 'legend_show')
        self.show_check.setChecked(True)
        layout.addWidget(self.show_check, 0, 0, 1, 2)

        lbl = QLabel(tr('legend_layout')); lbl.setProperty('tr_key', 'legend_layout')
        layout.addWidget(lbl, 1, 0)
        self.layout_mode_combo = QComboBox()
        self.layout_mode_combo.addItems(choice_items('legend_layout'))
        self.layout_mode_combo.setProperty("choice_key", "legend_layout")
        self.layout_mode_combo.setProperty("theme_min_width", 120)
        self.layout_mode_combo.setStyleSheet(combo_box_style())
        layout.addWidget(self.layout_mode_combo, 1, 1)

        lbl = QLabel(tr('legend_pos')); lbl.setProperty('tr_key', 'legend_pos')
        layout.addWidget(lbl, 2, 0)
        self.position_combo = QComboBox()
        self.position_combo.addItems(choice_items('legend_pos'))
        self.position_combo.setProperty("choice_key", "legend_pos")
        self.position_combo.setProperty("theme_min_width", 120)
        self.position_combo.setStyleSheet(combo_box_style())
        layout.addWidget(self.position_combo, 2, 1)

        lbl = QLabel(tr('legend_font_size')); lbl.setProperty('tr_key', 'legend_font_size')
        layout.addWidget(lbl, 3, 0)
        self.font_size_spin = QDoubleSpinBox()
        self.font_size_spin.setRange(6, 36)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setProperty("theme_min_width", 90)
        self.font_size_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.font_size_spin, 3, 1)

        lbl = QLabel(tr('legend_font')); lbl.setProperty('tr_key', 'legend_font')
        layout.addWidget(lbl, 4, 0)
        self.font_combo = QComboBox()
        self.font_combo.addItems(font_items)
        self.font_combo.setProperty("theme_min_width", 120)
        self.font_combo.setStyleSheet(combo_box_style())
        default_font = "Times New Roman" if "Times New Roman" in font_items else (font_items[0] if font_items else "")
        if default_font:
            self.font_combo.setCurrentText(default_font)
        layout.addWidget(self.font_combo, 4, 1)

        self.show_frame_check = QCheckBox(tr('legend_frame'))
        self.show_frame_check.setProperty('tr_key', 'legend_frame')
        self.show_frame_check.setChecked(False)
        layout.addWidget(self.show_frame_check, 5, 0, 1, 2)

        self.mode_hint_label = QLabel(tr('legend_hint'))
        self.mode_hint_label.setProperty('tr_key', 'legend_hint')
        self.mode_hint_label.setWordWrap(True)
        layout.addWidget(self.mode_hint_label, 6, 0, 1, 2)

        self.show_check.stateChanged.connect(self.settings_changed)
        self.layout_mode_combo.currentIndexChanged.connect(self.settings_changed)
        self.position_combo.currentIndexChanged.connect(self.settings_changed)
        self.font_size_spin.valueChanged.connect(self.settings_changed)
        self.font_combo.currentIndexChanged.connect(self.settings_changed)
        self.show_frame_check.stateChanged.connect(self.settings_changed)

    def retranslate(self):
        retranslate_labels(self)
        retranslate_choices(self)

    def get_settings(self):
        return {
            'show': self.show_check.isChecked(),
            'layout_mode': choice_key('legend_layout', self.layout_mode_combo.currentText()),
            'position': choice_key('legend_pos', self.position_combo.currentText()),
            'font_size': int(self.font_size_spin.value()),
            'font_family': self.font_combo.currentText(),
            'show_frame': self.show_frame_check.isChecked(),
        }

    def set_settings(self, cfg):
        widgets = [self.show_check, self.layout_mode_combo, self.position_combo,
                   self.font_size_spin, self.font_combo, self.show_frame_check]
        blockers = [QSignalBlocker(w) for w in widgets]
        self.show_check.setChecked(cfg.get('show', True))
        self.layout_mode_combo.setCurrentText(
            choice_display('legend_layout', cfg.get('layout_mode', 'grouped')))
        self.position_combo.setCurrentText(
            choice_display('legend_pos', cfg.get('position', 'upper right')))
        self.font_size_spin.setValue(cfg.get('font_size', 10))
        font = cfg.get('font_family')
        if font:
            self.font_combo.setCurrentText(font)
        self.show_frame_check.setChecked(cfg.get('show_frame', False))
        del blockers


class BorderSettingsPanel(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.bold_border_check = QCheckBox(tr('border_bold'))
        self.bold_border_check.setProperty('tr_key', 'border_bold')
        self.bold_border_check.setChecked(False)
        layout.addWidget(self.bold_border_check, 0, 0, 1, 2)

        lbl = QLabel(tr('border_width')); lbl.setProperty('tr_key', 'border_width')
        layout.addWidget(lbl, 1, 0)
        self.border_width_spin = QDoubleSpinBox()
        self.border_width_spin.setRange(0.5, 5.0)
        self.border_width_spin.setSingleStep(0.5)
        self.border_width_spin.setValue(1.0)
        self.border_width_spin.setProperty("theme_min_width", 90)
        self.border_width_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.border_width_spin, 1, 1)

        self.bold_border_check.stateChanged.connect(self._on_bold_toggle)
        self.border_width_spin.valueChanged.connect(self.settings_changed)

    def retranslate(self):
        retranslate_labels(self)

    def _on_bold_toggle(self, state):
        if state == Qt.Checked:
            self.border_width_spin.setValue(2.0)
        else:
            self.border_width_spin.setValue(1.0)
        self.settings_changed.emit()

    def get_settings(self):
        return {
            'bold_border': self.bold_border_check.isChecked(),
            'border_width': self.border_width_spin.value(),
        }

    def set_settings(self, cfg):
        blockers = [QSignalBlocker(self.bold_border_check),
                    QSignalBlocker(self.border_width_spin)]
        self.bold_border_check.setChecked(cfg.get('bold_border', False))
        self.border_width_spin.setValue(cfg.get('border_width', 1.0))
        del blockers


class PeakMarkSettingsPanel(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_data = None
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl = QLabel(tr('peak_mode')); lbl.setProperty('tr_key', 'peak_mode')
        layout.addWidget(lbl, 0, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(choice_items('peak_mode'))
        self.mode_combo.setProperty("choice_key", "peak_mode")
        self.mode_combo.setProperty("theme_min_width", 120)
        self.mode_combo.setStyleSheet(combo_box_style())
        layout.addWidget(self.mode_combo, 0, 1)

        lbl = QLabel(tr('peak_count')); lbl.setProperty('tr_key', 'peak_count')
        layout.addWidget(lbl, 1, 0)
        self.count_mode_combo = QComboBox()
        self.count_mode_combo.addItems(choice_items('count_mode'))
        self.count_mode_combo.setProperty("choice_key", "count_mode")
        self.count_mode_combo.setProperty("theme_min_width", 120)
        self.count_mode_combo.setStyleSheet(combo_box_style())
        layout.addWidget(self.count_mode_combo, 1, 1)

        layout.addWidget(QLabel(tr('peak_manual_count')), 2, 0)
        self.count_spin = QDoubleSpinBox()
        self.count_spin.setRange(1, 10)
        self.count_spin.setDecimals(0)
        self.count_spin.setValue(3)
        self.count_spin.setProperty("theme_min_width", 90)
        self.count_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.count_spin, 2, 1)

        layout.addWidget(QLabel(tr('peak_min_dist')), 3, 0)
        self.min_distance_spin = QDoubleSpinBox()
        self.min_distance_spin.setRange(0.1, 20.0)
        self.min_distance_spin.setDecimals(2)
        self.min_distance_spin.setSingleStep(0.1)
        self.min_distance_spin.setValue(0.5)
        self.min_distance_spin.setProperty("theme_min_width", 90)
        self.min_distance_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.min_distance_spin, 3, 1)

        layout.addWidget(QLabel(tr('peak_decimals')), 4, 0)
        self.decimal_spin = QDoubleSpinBox()
        self.decimal_spin.setRange(0, 4)
        self.decimal_spin.setDecimals(0)
        self.decimal_spin.setValue(2)
        self.decimal_spin.setProperty("theme_min_width", 90)
        self.decimal_spin.setStyleSheet(spin_box_style())
        layout.addWidget(self.decimal_spin, 4, 1)

        self.enable_check = QCheckBox(tr('peak_enable'))
        self.enable_check.setProperty('tr_key', 'peak_enable')
        layout.addWidget(self.enable_check, 5, 0, 1, 2)

        lbl = QLabel(tr('symbol_type')); lbl.setProperty('tr_key', 'symbol_type')
        layout.addWidget(lbl, 6, 0)
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(choice_items('symbol'))
        self.symbol_combo.setProperty("choice_key", "symbol")
        self.symbol_combo.setProperty("theme_min_width", 120)
        self.symbol_combo.setStyleSheet(combo_box_style())
        layout.addWidget(self.symbol_combo, 6, 1)

        lbl = QLabel(tr('symbol_color')); lbl.setProperty('tr_key', 'symbol_color')
        layout.addWidget(lbl, 7, 0)
        self.symbol_color_btn = QPushButton(tr('pick_color'))
        self.symbol_color_btn.setProperty('tr_key', 'pick_color')
        self.symbol_color_btn.setProperty("theme_role", "color_button")
        layout.addWidget(self.symbol_color_btn, 7, 1)

        lbl = QLabel(tr('peak_value_color')); lbl.setProperty('tr_key', 'peak_value_color')
        layout.addWidget(lbl, 8, 0)
        self.text_color_btn = QPushButton(tr('pick_color'))
        self.text_color_btn.setProperty('tr_key', 'pick_color')
        self.text_color_btn.setProperty("theme_role", "color_button")
        layout.addWidget(self.text_color_btn, 8, 1)

        self._set_button_color(self.symbol_color_btn, "#d62728")
        self._set_button_color(self.text_color_btn, "#1f2937")

        self.mode_combo.currentIndexChanged.connect(self.settings_changed)
        self.count_mode_combo.currentIndexChanged.connect(self._on_count_mode_changed)
        self.count_mode_combo.currentIndexChanged.connect(self.settings_changed)
        self.count_spin.valueChanged.connect(self.settings_changed)
        self.min_distance_spin.valueChanged.connect(self.settings_changed)
        self.decimal_spin.valueChanged.connect(self.settings_changed)
        self.enable_check.stateChanged.connect(self._on_data_config_changed)
        self.symbol_combo.currentIndexChanged.connect(self._on_data_config_changed)
        self.symbol_color_btn.clicked.connect(lambda: self._pick_color(self.symbol_color_btn, 'peak_symbol_color'))
        self.text_color_btn.clicked.connect(lambda: self._pick_color(self.text_color_btn, 'peak_text_color'))

        self._on_count_mode_changed()
        self._set_data_controls_enabled(False)

    def _set_button_color(self, button, color):
        button.setProperty("selected_color", color)
        button.setStyleSheet(color_button_style(color))

    def _set_data_controls_enabled(self, enabled):
        for widget in [self.enable_check, self.symbol_combo, self.symbol_color_btn, self.text_color_btn]:
            widget.setEnabled(enabled)

    def _on_count_mode_changed(self, *args):
        self.count_spin.setEnabled(
            self.count_mode_combo.currentText() == choice_display('count_mode', 'manual'))

    def _pick_color(self, button, attr_name):
        current_color = button.property("selected_color") or "#000000"
        color = QColorDialog.getColor(QColor(current_color), self, "选择颜色")
        if color.isValid():
            color_name = color.name()
            self._set_button_color(button, color_name)
            if self._current_data is not None:
                setattr(self._current_data, attr_name, color_name)
            self.settings_changed.emit()

    def _on_data_config_changed(self, *args):
        if self._current_data is None:
            return
        self._current_data.peak_mark_enabled = self.enable_check.isChecked()
        self._current_data.peak_symbol = self._symbol_text_to_key(self.symbol_combo.currentText())
        self._current_data.peak_symbol_color = self.symbol_color_btn.property("selected_color")
        self._current_data.peak_text_color = self.text_color_btn.property("selected_color")
        self.settings_changed.emit()

    def _symbol_text_to_key(self, text):
        return choice_key('symbol', text) or "circle"

    def _symbol_key_to_text(self, key):
        return choice_display('symbol', key)

    def set_current_data(self, data):
        self._current_data = data
        if data is None:
            self._set_data_controls_enabled(False)
            self.enable_check.blockSignals(True)
            self.symbol_combo.blockSignals(True)
            self.enable_check.setChecked(False)
            self.symbol_combo.setCurrentText(choice_display('symbol', 'circle'))
            self._set_button_color(self.symbol_color_btn, "#d62728")
            self._set_button_color(self.text_color_btn, "#1f2937")
            self.enable_check.blockSignals(False)
            self.symbol_combo.blockSignals(False)
            return

        self._set_data_controls_enabled(True)
        self.enable_check.blockSignals(True)
        self.symbol_combo.blockSignals(True)
        self.enable_check.setChecked(data.peak_mark_enabled)
        self.symbol_combo.setCurrentText(self._symbol_key_to_text(data.peak_symbol))
        self._set_button_color(self.symbol_color_btn, data.peak_symbol_color)
        self._set_button_color(self.text_color_btn, data.peak_text_color)
        self.enable_check.blockSignals(False)
        self.symbol_combo.blockSignals(False)

    def get_settings(self):
        return {
            'peak_mark_mode': choice_key('peak_mode', self.mode_combo.currentText()),
            'peak_count_mode': choice_key('count_mode', self.count_mode_combo.currentText()),
            'peak_count': int(self.count_spin.value()),
            'peak_min_distance': self.min_distance_spin.value(),
            'peak_label_decimals': int(self.decimal_spin.value()),
        }

    def set_settings(self, cfg):
        widgets = [self.mode_combo, self.count_mode_combo, self.count_spin,
                   self.min_distance_spin, self.decimal_spin]
        blockers = [QSignalBlocker(w) for w in widgets]
        self.mode_combo.setCurrentText(
            choice_display('peak_mode', cfg.get('peak_mark_mode', 'symbol+value')))
        self.count_mode_combo.setCurrentText(
            choice_display('count_mode', cfg.get('peak_count_mode', 'manual')))
        self.count_spin.setValue(cfg.get('peak_count', 3))
        self.min_distance_spin.setValue(cfg.get('peak_min_distance', 0.5))
        self.decimal_spin.setValue(cfg.get('peak_label_decimals', 2))
        del blockers
        self._on_count_mode_changed()

    def retranslate(self):
        retranslate_labels(self)
        retranslate_choices(self)
