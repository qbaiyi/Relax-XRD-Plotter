from PyQt5.QtWidgets import (QMainWindow, QWidget, QSplitter, QVBoxLayout,
                             QHBoxLayout, QListWidget, QPushButton, QRadioButton,
                             QButtonGroup, QSlider, QDoubleSpinBox, QComboBox,
                             QLabel, QScrollArea, QFileDialog, QMessageBox,
                             QInputDialog, QSizePolicy, QColorDialog, QLineEdit,
                             QTabWidget)
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtCore import QEvent, Qt, QSettings
from PyQt5.QtGui import QColor, QDragEnterEvent, QDragMoveEvent, QDropEvent
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np

from data_loader import load_xrd_files, XRDData
from theme_manager import (DEFAULT_THEME_NAME, build_bottom_bar_style,
                           build_color_preview_style, build_combo_box_style,
                           build_drag_hint_style, build_hint_label_style,
                           build_inner_card_style,
                           build_line_edit_style, build_main_window_styles,
                           build_message_box_style, build_panel_card_style,
                           build_secondary_button_style, build_spin_box_style,
                           build_splitter_style, build_tab_widget_style,
                           build_theme_selector_label_style,
                           build_title_bar_style, build_title_label_style,
                           build_toolbar_style, get_theme, is_cartoon_theme,
                           list_theme_names, normalize_theme_name)
from xrd_plotter import XRDPlotter, COLOR_SCHEMES
from ui_settings import (CollapsibleBox, AxisSettingsPanel,
                         LabelSettingsPanel, LegendSettingsPanel,
                         BorderSettingsPanel, PeakMarkSettingsPanel,
                         set_current_theme as set_settings_theme)
from i18n import (tr, set_language, get_language, choice_items,
                 choice_key, choice_display, retranslate_labels,
                 retranslate_choices, LINESTYLE_CHOICES)


class LeftPanelScrollArea(QScrollArea):

    def register_wheel_targets(self, root_widget):
        root_widget.installEventFilter(self)
        for child in root_widget.findChildren(QWidget):
            child.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Wheel:
            watched_class = watched.__class__.__name__
            if watched_class in {
                "QDoubleSpinBox",
                "QComboBox",
                "QSlider",
                "QListWidget",
                "QScrollBar",
            }:
                return False
            scroll_bar = self.verticalScrollBar()
            delta = event.angleDelta().y()
            if delta:
                step = max(scroll_bar.singleStep(), 24)
                direction = -1 if delta > 0 else 1
                scroll_bar.setValue(scroll_bar.value() + direction * step)
                return True
        return super().eventFilter(watched, event)


class XRDMainWindow(QMainWindow):

    def __init__(self, theme_name=None):
        super().__init__()
        self.settings = QSettings("RelaxXRDPlotter", "Relax XRD Plotter")
        saved_theme_name = self.settings.value("ui/theme", DEFAULT_THEME_NAME, type=str)
        self.current_theme_name = normalize_theme_name(theme_name or saved_theme_name)
        self.current_language = self.settings.value("ui/language", "zh", type=str)
        set_language(self.current_language)
        self.data_list = []
        self.manual_markers = []
        self.selected_manual_marker_index = None
        self._manual_marker_counter = 1
        self._dragging_marker_index = None
        self._dragging_marker_active = False
        self._dragging_label = None
        self._legend_layout_mode = 'grouped'
        self._stickers = []
        self._selected_sticker_index = None
        self._sticker_counter = 1
        self._theme_names = list_theme_names()
        set_settings_theme(self.current_theme_name)
        self._init_ui()
        self._connect_auto_refresh()
        self.apply_theme(self.current_theme_name, save=False, refresh=False)

    def _init_ui(self):
        self.setWindowTitle("Relax XRD Plotter")
        self.resize(1360, 840)
        self.setMinimumSize(1024, 640)
        self.setStyleSheet(build_main_window_styles(self.current_theme_name))

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)

        self.title_bar = QWidget()
        self.title_bar.setMaximumHeight(56)
        self.title_bar.setStyleSheet(build_title_bar_style(self.current_theme_name))
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(10, 4, 10, 4)
        title_bar_layout.setSpacing(8)

        self.title_label = QLabel(tr('app_title'))
        self.title_label.setStyleSheet(build_title_label_style(self.current_theme_name))
        title_bar_layout.addWidget(self.title_label)

        title_bar_layout.addStretch()

        self.hint_label = QLabel(tr('drag_hint'))
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setProperty('tr_key', 'drag_hint')
        self.hint_label.setStyleSheet(build_drag_hint_style(self.current_theme_name))

        self.ui_theme_label = QLabel("UI")
        self.ui_theme_label.setStyleSheet(build_theme_selector_label_style(self.current_theme_name))
        title_bar_layout.addWidget(self.ui_theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.setProperty("theme_min_width", 150)
        self.theme_combo.addItems(self._theme_names)
        self.theme_combo.setStyleSheet(build_combo_box_style(self.current_theme_name, 150))
        self.theme_combo.setCurrentText(self.current_theme_name)
        title_bar_layout.addWidget(self.theme_combo)

        self.btn_author = QPushButton(tr('btn_author'))
        self.btn_author.setProperty('tr_key', 'btn_author')
        self.btn_author.setStyleSheet(build_secondary_button_style(self.current_theme_name))
        self.btn_author.clicked.connect(self.show_author_info)
        title_bar_layout.addWidget(self.btn_author)

        self.lang_label = QLabel(tr('language'))
        self.lang_label.setProperty('tr_key', 'language')
        self.lang_label.setStyleSheet(build_theme_selector_label_style(self.current_theme_name))
        title_bar_layout.addWidget(self.lang_label)

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(choice_items('language'))
        self.lang_combo.setProperty("theme_min_width", 100)
        self.lang_combo.setStyleSheet(build_combo_box_style(self.current_theme_name, 100))
        self.lang_combo.setCurrentText(choice_display('language', self.current_language))
        title_bar_layout.addWidget(self.lang_combo)

        self._cartoon_widgets = [self.title_label, self.hint_label, self.ui_theme_label]

        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        self.lang_combo.currentTextChanged.connect(self._on_language_changed)
        main_layout.addWidget(self.title_bar)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet(build_splitter_style(self.current_theme_name))
        main_layout.addWidget(self.splitter)

        left_panel = self._build_left_panel()
        right_panel = self._build_right_panel()
        annotation_panel = self._build_annotation_panel()

        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)
        self.splitter.addWidget(annotation_panel)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 0)
        self.splitter.setSizes([360, 940, 320])

    def apply_theme(self, theme_name, save=True, refresh=True):
        theme_name = normalize_theme_name(theme_name)
        self.current_theme_name = theme_name
        set_settings_theme(theme_name)

        self.setStyleSheet(build_main_window_styles(theme_name))
        self.title_bar.setStyleSheet(build_title_bar_style(theme_name))
        self.title_label.setStyleSheet(build_title_label_style(theme_name))
        self.hint_label.setStyleSheet(build_drag_hint_style(theme_name))
        self.ui_theme_label.setStyleSheet(build_theme_selector_label_style(theme_name))
        self.btn_author.setStyleSheet(build_secondary_button_style(theme_name))
        self.theme_combo.blockSignals(True)
        self.theme_combo.setStyleSheet(build_combo_box_style(theme_name, 150))
        self.theme_combo.setCurrentText(theme_name)
        self.theme_combo.blockSignals(False)
        self.lang_label.setStyleSheet(build_theme_selector_label_style(theme_name))
        self.lang_combo.blockSignals(True)
        self.lang_combo.setStyleSheet(build_combo_box_style(theme_name, 100))
        self.lang_combo.blockSignals(False)
        self.splitter.setStyleSheet(build_splitter_style(theme_name))

        self.left_tabs.setStyleSheet(build_tab_widget_style(theme_name))
        self.left_panel_wrapper.setStyleSheet(build_panel_card_style(theme_name))
        self.annotation_panel_wrapper.setStyleSheet(build_panel_card_style(theme_name))
        self.annotation_header.setStyleSheet(build_title_label_style(theme_name))
        self.right_panel_container.setStyleSheet(build_panel_card_style(theme_name))
        self.bottom_button_bar.setStyleSheet(build_bottom_bar_style(theme_name))
        self.toolbar.setStyleSheet(build_toolbar_style(theme_name))
        self.color_widget.setStyleSheet(build_inner_card_style(theme_name))

        self.name_edit.setStyleSheet(build_line_edit_style(theme_name, 26))
        self.current_linewidth_spin.setStyleSheet(build_spin_box_style(theme_name, 80))
        self.current_linestyle_combo.setStyleSheet(build_combo_box_style(theme_name, 110))
        self.offset_spin.setStyleSheet(build_spin_box_style(theme_name, 80))
        self.scheme_combo.setStyleSheet(build_combo_box_style(theme_name, 180))
        self.manual_symbol_combo.setStyleSheet(build_combo_box_style(theme_name, 120))
        self.manual_size_spin.setStyleSheet(build_spin_box_style(theme_name, 70))
        self.manual_default_text_edit.setStyleSheet(build_line_edit_style(theme_name, 26))
        self.manual_current_text_edit.setStyleSheet(build_line_edit_style(theme_name, 26))
        self.figure_width_spin.setStyleSheet(build_spin_box_style(theme_name, 70))
        self.figure_height_spin.setStyleSheet(build_spin_box_style(theme_name, 70))
        self.manual_hint_label.setStyleSheet(build_hint_label_style(theme_name))
        self.figure_tip_label.setStyleSheet(build_hint_label_style(theme_name))
        self.sticker_hint_label.setStyleSheet(build_hint_label_style(theme_name))
        self.sticker_type_combo.setStyleSheet(build_combo_box_style(theme_name, 120))
        self.sticker_size_spin.setStyleSheet(build_spin_box_style(theme_name, 70))

        for box in self.findChildren(CollapsibleBox):
            box.apply_theme(theme_name)

        self._set_manual_color_button(self.manual_color_btn.property("selected_color") or "#d62728")
        self._set_sticker_color_button(self.sticker_color_btn.property("selected_color") or "#FF6B6B")
        self.update_color_buttons()

        is_cartoon = is_cartoon_theme(theme_name)
        self.plotter.set_cartoon_mode(is_cartoon)
        for widget in getattr(self, '_cartoon_widgets', []):
            if widget:
                widget.setStyleSheet(widget.styleSheet())

        if save:
            self.settings.setValue("ui/theme", theme_name)
        if refresh:
            if self.data_list:
                self.refresh_plot(silent_if_empty=True)
            else:
                self.canvas.draw_idle()

    def _on_language_changed(self, text):
        lang = choice_key('language', text) or self.current_language
        if lang == self.current_language:
            return
        self.current_language = lang
        set_language(lang)
        self.settings.setValue("ui/language", lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        # 1) 静态文本：QLabel / QPushButton / QCheckBox / QRadioButton（按 tr_key）
        retranslate_labels(self)
        # 2) 可翻译下拉（按 choice_key，保留当前选中的内部键）
        retranslate_choices(self)
        # 3) 左侧标签页标题
        for index, key in enumerate(self._left_tab_keys):
            self.left_tabs.setTabText(index, tr(key))
        # 4) 折叠面板标题
        for box in self.findChildren(CollapsibleBox):
            trk = getattr(box, '_tr_key', None)
            if trk:
                box.set_title(tr(trk))
        # 5) 各设置面板的内部文本 / 特殊值文字
        self.axis_panel.retranslate()
        self.label_panel.retranslate()
        self.legend_panel.retranslate()
        self.border_panel.retranslate()
        self.peak_panel.retranslate()
        # 6) 语言下拉本身（选项为语言名，保持与当前语言一致）
        self.lang_combo.blockSignals(True)
        if self.lang_combo.currentText() != choice_display('language', self.current_language):
            self.lang_combo.setCurrentText(choice_display('language', self.current_language))
        self.lang_combo.blockSignals(False)
        # 7) 刷新画面（图例标签等随 UI 文字更新）
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)
        else:
            self.canvas.draw_idle()

    def show_author_info(self):
        theme = get_theme(self.current_theme_name)
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Information)
        box.setWindowTitle(tr('author_title'))
        box.setTextFormat(Qt.RichText)
        box.setText(
            f"<div style='color:{theme['text']}; font-size:13px;'>"
            + tr('author_body').format(accent=theme['accent_hover'])
            + "</div>"
        )
        box.setStyleSheet(build_message_box_style(self.current_theme_name))
        box.exec_()

    def _show_message(self, icon, title, text):
        box = QMessageBox(self)
        box.setIcon(icon)
        box.setWindowTitle(title)
        box.setText(text)
        box.setStyleSheet(build_message_box_style(self.current_theme_name))
        box.exec_()

    def _show_info_message(self, title, text):
        self._show_message(QMessageBox.Information, title, text)

    def _show_warning_message(self, title, text):
        self._show_message(QMessageBox.Warning, title, text)

    def _connect_auto_refresh(self):
        self.radio_overlay.toggled.connect(self._refresh_plot_if_ready)
        self.radio_stacked.toggled.connect(self._refresh_plot_if_ready)
        self.offset_spin.valueChanged.connect(self._refresh_plot_if_ready)
        self.axis_panel.settings_changed.connect(self._refresh_plot_if_ready)
        self.label_panel.settings_changed.connect(self._refresh_plot_if_ready)
        self.legend_panel.settings_changed.connect(self._refresh_plot_if_ready)
        self.border_panel.settings_changed.connect(self._refresh_plot_if_ready)
        self.peak_panel.settings_changed.connect(self._refresh_plot_if_ready)

    def _refresh_plot_if_ready(self, *args):
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def _clear_plot_view(self):
        self.plotter.clear()
        self.canvas.draw()

    def _append_loaded_file(self, filepath):
        if str(filepath).lower().endswith('.xrdproj'):
            self._load_project(filepath)
            return
        datasets = load_xrd_files(filepath)
        self.data_list.extend(datasets)

    def _build_right_panel(self):
        self.right_panel_container = QWidget()
        self.right_panel_container.setStyleSheet(build_panel_card_style(self.current_theme_name))
        layout = QVBoxLayout(self.right_panel_container)
        layout.setContentsMargins(8, 8, 8, 8)

        self.figure = Figure(figsize=(8, 6), dpi=100, facecolor='white')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent;")

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet(build_toolbar_style(self.current_theme_name))

        self.plotter = XRDPlotter(self.figure)
        self.canvas.mpl_connect('button_press_event', self._on_canvas_click)
        self.canvas.mpl_connect('motion_notify_event', self._on_canvas_motion)
        self.canvas.mpl_connect('button_release_event', self._on_canvas_release)
        self.canvas.mpl_connect('pick_event', self._on_canvas_pick)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self._build_bottom_buttons())
        return self.right_panel_container

    def _make_tab_page(self, sections):
        scroll = LeftPanelScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 8, 4, 6)
        layout.setSpacing(4)
        for section in sections:
            layout.addWidget(section)
        layout.addStretch()
        scroll.setWidget(container)
        scroll.register_wheel_targets(container)
        return scroll

    def _build_left_panel(self):
        self.left_tabs = QTabWidget()
        self.left_tabs.setDocumentMode(True)
        self.left_tabs.tabBar().setExpanding(True)
        self.left_tabs.setMinimumWidth(320)
        self.left_tabs.setMaximumWidth(440)
        self.left_tabs.setStyleSheet(build_tab_widget_style(self.current_theme_name))

        # 数据页：文件管理 + 绘图模式 + 配色
        data_section = self._build_data_section()
        data_section.setAcceptDrops(True)
        data_section.dragEnterEvent = self._on_drag_enter
        data_section.dragMoveEvent = self._on_drag_move
        data_section.dropEvent = self._on_drop
        self.left_tabs.addTab(
            self._make_tab_page([
                data_section,
                self._build_mode_section(),
                self._build_color_section(),
            ]),
            tr('tab_data'))

        # 绘图页：画布、坐标、文字、图例、边框
        self.left_tabs.addTab(
            self._make_tab_page([
                self._build_figure_size_section(),
                self._build_axis_section(),
                self._build_label_section(),
                self._build_legend_section(),
                self._build_border_section(),
            ]),
            tr('tab_plot'))

        self._left_tab_keys = ['tab_data', 'tab_plot']

        # 儿童贴图功能已从界面移除（保留内部构建以兼容引用）
        self._sticker_box = self._build_sticker_section()

        self.left_panel_wrapper = QWidget()
        self.left_panel_wrapper.setStyleSheet(build_panel_card_style(self.current_theme_name))
        wrapper_layout = QVBoxLayout(self.left_panel_wrapper)
        wrapper_layout.setContentsMargins(6, 6, 6, 6)
        wrapper_layout.setSpacing(0)
        wrapper_layout.addWidget(self.left_tabs)

        return self.left_panel_wrapper

    def _build_annotation_panel(self):
        self.annotation_panel_wrapper = QWidget()
        self.annotation_panel_wrapper.setStyleSheet(build_panel_card_style(self.current_theme_name))
        self.annotation_panel_wrapper.setMinimumWidth(300)
        self.annotation_panel_wrapper.setMaximumWidth(420)
        wrapper_layout = QVBoxLayout(self.annotation_panel_wrapper)
        wrapper_layout.setContentsMargins(6, 6, 6, 6)
        wrapper_layout.setSpacing(4)

        self.annotation_header = QLabel(tr('annotation_header'))
        self.annotation_header.setProperty('tr_key', 'annotation_header')
        self.annotation_header.setAlignment(Qt.AlignCenter)
        self.annotation_header.setStyleSheet(build_title_label_style(self.current_theme_name))
        wrapper_layout.addWidget(self.annotation_header)

        wrapper_layout.addWidget(self._make_tab_page([
            self._build_peak_section(),
            self._build_manual_marker_section(),
        ]))

        return self.annotation_panel_wrapper

    def _build_data_section(self):
        box = CollapsibleBox(tr('data_files'))
        box._tr_key = 'data_files'
        box.toggle_btn.setChecked(True)
        box._toggle()

        self.file_list = QListWidget()
        box.addWidget(self.file_list)

        box.addWidget(self.hint_label)

        self.btn_open = QPushButton(tr('btn_open'))
        self.btn_open.setProperty('tr_key', 'btn_open')
        self.btn_open.setMinimumHeight(40)
        box.addWidget(self.btn_open)

        rename_layout = QHBoxLayout()
        lbl = QLabel(tr('legend_name')); lbl.setProperty('tr_key', 'legend_name')
        rename_layout.addWidget(lbl)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(tr('legend_name_ph'))
        self.name_edit.setProperty("theme_min_height", 26)
        self.name_edit.setStyleSheet(build_line_edit_style(self.current_theme_name, 26))
        self.name_edit.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.btn_apply_name = QPushButton(tr('btn_apply_name'))
        self.btn_apply_name.setProperty('tr_key', 'btn_apply_name')
        self.btn_apply_name.setFixedWidth(60)
        rename_layout.addWidget(self.name_edit)
        rename_layout.addWidget(self.btn_apply_name)
        box.addLayout(rename_layout)

        linewidth_layout = QHBoxLayout()
        lbl = QLabel(tr('line_width')); lbl.setProperty('tr_key', 'line_width')
        linewidth_layout.addWidget(lbl)
        self.current_linewidth_spin = QDoubleSpinBox()
        self.current_linewidth_spin.setRange(0.5, 8.0)
        self.current_linewidth_spin.setSingleStep(0.2)
        self.current_linewidth_spin.setDecimals(1)
        self.current_linewidth_spin.setValue(1.0)
        self.current_linewidth_spin.setEnabled(False)
        self.current_linewidth_spin.setProperty("theme_min_width", 80)
        self.current_linewidth_spin.setStyleSheet(build_spin_box_style(self.current_theme_name, 80))
        linewidth_layout.addWidget(self.current_linewidth_spin)
        box.addLayout(linewidth_layout)

        linestyle_layout = QHBoxLayout()
        lbl = QLabel(tr('line_style')); lbl.setProperty('tr_key', 'line_style')
        linestyle_layout.addWidget(lbl)
        self.current_linestyle_combo = QComboBox()
        self.current_linestyle_combo.addItems(choice_items('linestyle'))
        self.current_linestyle_combo.setProperty("choice_key", "linestyle")
        self.current_linestyle_combo.setEnabled(False)
        self.current_linestyle_combo.setProperty("theme_min_width", 110)
        self.current_linestyle_combo.setStyleSheet(build_combo_box_style(self.current_theme_name, 110))
        linestyle_layout.addWidget(self.current_linestyle_combo)
        box.addLayout(linestyle_layout)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton(tr('btn_add'))
        self.btn_add.setProperty('tr_key', 'btn_add')
        self.btn_remove = QPushButton(tr('btn_remove'))
        self.btn_remove.setProperty('tr_key', 'btn_remove')
        self.btn_up = QPushButton(tr('btn_up'))
        self.btn_up.setProperty('tr_key', 'btn_up')
        self.btn_down = QPushButton(tr('btn_down'))
        self.btn_down.setProperty('tr_key', 'btn_down')
        self.btn_up.setFixedWidth(36)
        self.btn_down.setFixedWidth(36)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_remove)
        btn_layout.addWidget(self.btn_up)
        btn_layout.addWidget(self.btn_down)
        box.addLayout(btn_layout)

        self.btn_add.clicked.connect(self.add_files)
        self.btn_open.clicked.connect(self.add_files)
        self.btn_remove.clicked.connect(self.remove_selected)
        self.btn_up.clicked.connect(self.move_up)
        self.btn_down.clicked.connect(self.move_down)
        self.btn_apply_name.clicked.connect(self.apply_selected_display_name)
        self.name_edit.editingFinished.connect(self.apply_selected_display_name)
        self.current_linewidth_spin.valueChanged.connect(self.apply_selected_line_width)
        self.current_linestyle_combo.currentIndexChanged.connect(self.apply_selected_line_style)
        self.file_list.currentRowChanged.connect(self._on_file_selection_changed)
        self.name_edit.setEnabled(False)
        self.btn_apply_name.setEnabled(False)

        return box

    def _build_mode_section(self):
        box = CollapsibleBox(tr('plot_mode'))
        box._tr_key = 'plot_mode'
        box.toggle_btn.setChecked(True)
        box._toggle()

        mode_layout = QHBoxLayout()
        self.radio_overlay = QRadioButton(tr('overlay'))
        self.radio_overlay.setProperty('tr_key', 'overlay')
        self.radio_stacked = QRadioButton(tr('stacked'))
        self.radio_stacked.setProperty('tr_key', 'stacked')
        self.radio_stacked.setChecked(True)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.radio_overlay)
        self.mode_group.addButton(self.radio_stacked)
        mode_layout.addWidget(self.radio_overlay)
        mode_layout.addWidget(self.radio_stacked)
        box.addLayout(mode_layout)

        offset_layout = QHBoxLayout()
        lbl = QLabel(tr('offset')); lbl.setProperty('tr_key', 'offset')
        offset_layout.addWidget(lbl)
        self.offset_slider = QSlider(Qt.Horizontal)
        self.offset_slider.setRange(1, 20)
        self.offset_slider.setValue(8)
        self.offset_slider.setTickInterval(1)
        self.offset_spin = QDoubleSpinBox()
        self.offset_spin.setRange(0.1, 2.0)
        self.offset_spin.setSingleStep(0.1)
        self.offset_spin.setValue(0.8)
        self.offset_spin.setDecimals(1)
        self.offset_spin.setProperty("theme_min_width", 80)
        self.offset_spin.setStyleSheet(build_spin_box_style(self.current_theme_name, 80))
        offset_layout.addWidget(self.offset_slider)
        offset_layout.addWidget(self.offset_spin)
        box.addLayout(offset_layout)

        self.offset_slider.valueChanged.connect(
            lambda v: self.offset_spin.setValue(v / 10.0))
        self.offset_spin.valueChanged.connect(
            lambda v: self.offset_slider.setValue(int(v * 10)))

        return box

    def _build_color_section(self):
        box = CollapsibleBox(tr('colors'))
        box._tr_key = 'colors'
        box.toggle_btn.setChecked(True)
        box._toggle()

        scheme_layout = QHBoxLayout()
        lbl = QLabel(tr('color_scheme')); lbl.setProperty('tr_key', 'color_scheme')
        scheme_layout.addWidget(lbl)
        self.scheme_combo = QComboBox()
        self.scheme_combo.addItems(sorted(COLOR_SCHEMES.keys()))
        self.scheme_combo.setProperty("theme_min_width", 180)
        self.scheme_combo.setStyleSheet(build_combo_box_style(self.current_theme_name, 180))
        scheme_layout.addWidget(self.scheme_combo)
        box.addLayout(scheme_layout)

        self.color_widget = QWidget()
        self.color_widget.setStyleSheet(build_inner_card_style(self.current_theme_name))
        self.color_layout = QVBoxLayout(self.color_widget)
        self.color_layout.setContentsMargins(4, 4, 4, 4)
        self.color_layout.setSpacing(3)
        box.addWidget(self.color_widget)

        self.scheme_combo.currentTextChanged.connect(self._on_scheme_changed)

        return box

    def _build_axis_section(self):
        box = CollapsibleBox(tr('axes'))
        box._tr_key = 'axes'
        self.axis_panel = AxisSettingsPanel()
        box.addWidget(self.axis_panel)
        return box

    def _build_peak_section(self):
        box = CollapsibleBox(tr('peak_marking'))
        box._tr_key = 'peak_marking'
        box.toggle_btn.setChecked(True)
        box._toggle()
        self.peak_panel = PeakMarkSettingsPanel()
        box.addWidget(self.peak_panel)
        return box

    def _build_sticker_section(self):
        box = CollapsibleBox(tr('stickers'))
        box._tr_key = 'stickers'

        self.sticker_mode_enabled_check = QCheckBox(tr('sticker_enable'))
        self.sticker_mode_enabled_check.setProperty('tr_key', 'sticker_enable')
        self.sticker_mode_enabled_check.setChecked(False)
        box.addWidget(self.sticker_mode_enabled_check)

        type_layout = QHBoxLayout()
        lbl = QLabel(tr('sticker_type')); lbl.setProperty('tr_key', 'sticker_type')
        type_layout.addWidget(lbl)
        self.sticker_type_combo = QComboBox()
        self.sticker_type_combo.addItems(choice_items('sticker'))
        self.sticker_type_combo.setProperty("choice_key", "sticker")
        self.sticker_type_combo.setProperty("theme_min_width", 120)
        self.sticker_type_combo.setStyleSheet(build_combo_box_style(self.current_theme_name, 120))
        type_layout.addWidget(self.sticker_type_combo)
        box.addLayout(type_layout)

        style_layout = QHBoxLayout()
        lbl = QLabel(tr('sticker_color')); lbl.setProperty('tr_key', 'sticker_color')
        style_layout.addWidget(lbl)
        self.sticker_color_btn = QPushButton(tr('pick_color'))
        self.sticker_color_btn.setProperty('tr_key', 'pick_color')
        self.sticker_color_btn.setFixedWidth(90)
        style_layout.addWidget(self.sticker_color_btn)
        style_layout.addWidget(QLabel(tr('size')))
        self.sticker_size_spin = QDoubleSpinBox()
        self.sticker_size_spin.setRange(8, 80)
        self.sticker_size_spin.setDecimals(0)
        self.sticker_size_spin.setSingleStep(2)
        self.sticker_size_spin.setValue(20)
        self.sticker_size_spin.setProperty("theme_min_width", 70)
        self.sticker_size_spin.setStyleSheet(build_spin_box_style(self.current_theme_name, 70))
        style_layout.addWidget(self.sticker_size_spin)
        box.addLayout(style_layout)

        self.sticker_hint_label = QLabel(tr('sticker_hint'))
        self.sticker_hint_label.setProperty('tr_key', 'sticker_hint')
        self.sticker_hint_label.setWordWrap(True)
        self.sticker_hint_label.setStyleSheet(build_hint_label_style(self.current_theme_name))
        box.addWidget(self.sticker_hint_label)

        self.sticker_list = QListWidget()
        self.sticker_list.setMaximumHeight(140)
        box.addWidget(self.sticker_list)

        move_row = QHBoxLayout()
        self.btn_sticker_up = QPushButton(tr('btn_up_move'))
        self.btn_sticker_up.setProperty('tr_key', 'btn_up_move')
        self.btn_sticker_down = QPushButton(tr('btn_down_move'))
        self.btn_sticker_down.setProperty('tr_key', 'btn_down_move')
        move_row.addWidget(self.btn_sticker_up)
        move_row.addWidget(self.btn_sticker_down)
        box.addLayout(move_row)

        btn_row = QHBoxLayout()
        self.btn_delete_sticker = QPushButton(tr('btn_delete_selected'))
        self.btn_delete_sticker.setProperty('tr_key', 'btn_delete_selected')
        self.btn_clear_stickers = QPushButton(tr('btn_clear_all'))
        self.btn_clear_stickers.setProperty('tr_key', 'btn_clear_all')
        btn_row.addWidget(self.btn_delete_sticker)
        btn_row.addWidget(self.btn_clear_stickers)
        box.addLayout(btn_row)

        self._set_sticker_color_button("#FF6B6B")
        self.sticker_mode_enabled_check.stateChanged.connect(self._on_sticker_mode_enabled_changed)
        self.sticker_color_btn.clicked.connect(self._choose_sticker_color)
        self.sticker_list.currentRowChanged.connect(self._on_sticker_selected)
        self.btn_delete_sticker.clicked.connect(self.delete_selected_sticker)
        self.btn_clear_stickers.clicked.connect(self.clear_stickers)
        self.btn_sticker_up.clicked.connect(lambda: self.move_selected_sticker(0.0, 0.01))
        self.btn_sticker_down.clicked.connect(lambda: self.move_selected_sticker(0.0, -0.01))
        self._set_sticker_section_enabled(False)

        return box

    def _build_manual_marker_section(self):
        box = CollapsibleBox(tr('manual_markers'))
        box._tr_key = 'manual_markers'

        self.manual_marker_enabled_check = QCheckBox(tr('manual_enable'))
        self.manual_marker_enabled_check.setProperty('tr_key', 'manual_enable')
        self.manual_marker_enabled_check.setChecked(False)
        box.addWidget(self.manual_marker_enabled_check)

        symbol_layout = QHBoxLayout()
        lbl = QLabel(tr('symbol_type')); lbl.setProperty('tr_key', 'symbol_type')
        symbol_layout.addWidget(lbl)
        self.manual_symbol_combo = QComboBox()
        self.manual_symbol_combo.addItems(choice_items('symbol'))
        self.manual_symbol_combo.setProperty("choice_key", "symbol")
        self.manual_symbol_combo.setProperty("theme_min_width", 120)
        self.manual_symbol_combo.setStyleSheet(build_combo_box_style(self.current_theme_name, 120))
        symbol_layout.addWidget(self.manual_symbol_combo)
        box.addLayout(symbol_layout)

        style_layout = QHBoxLayout()
        lbl = QLabel(tr('manual_symbol_color')); lbl.setProperty('tr_key', 'manual_symbol_color')
        style_layout.addWidget(lbl)
        self.manual_color_btn = QPushButton(tr('pick_color'))
        self.manual_color_btn.setProperty('tr_key', 'pick_color')
        self.manual_color_btn.setFixedWidth(90)
        style_layout.addWidget(self.manual_color_btn)
        style_layout.addWidget(QLabel(tr('size')))
        self.manual_size_spin = QDoubleSpinBox()
        self.manual_size_spin.setRange(20, 300)
        self.manual_size_spin.setDecimals(0)
        self.manual_size_spin.setSingleStep(10)
        self.manual_size_spin.setValue(70)
        self.manual_size_spin.setProperty("theme_min_width", 70)
        self.manual_size_spin.setStyleSheet(build_spin_box_style(self.current_theme_name, 70))
        style_layout.addWidget(self.manual_size_spin)
        box.addLayout(style_layout)

        self.manual_hint_label = QLabel(tr('manual_hint'))
        self.manual_hint_label.setProperty('tr_key', 'manual_hint')
        self.manual_hint_label.setWordWrap(True)
        self.manual_hint_label.setStyleSheet(build_hint_label_style(self.current_theme_name))
        box.addWidget(self.manual_hint_label)

        default_text_layout = QHBoxLayout()
        lbl = QLabel(tr('default_text')); lbl.setProperty('tr_key', 'default_text')
        default_text_layout.addWidget(lbl)
        self.manual_default_text_edit = QLineEdit()
        self.manual_default_text_edit.setPlaceholderText(tr('default_text_ph'))
        self.manual_default_text_edit.setProperty("theme_min_height", 26)
        self.manual_default_text_edit.setStyleSheet(build_line_edit_style(self.current_theme_name, 26))
        self.manual_default_text_edit.setAttribute(Qt.WA_InputMethodEnabled, True)
        default_text_layout.addWidget(self.manual_default_text_edit)
        box.addLayout(default_text_layout)

        current_text_layout = QHBoxLayout()
        lbl = QLabel(tr('current_text')); lbl.setProperty('tr_key', 'current_text')
        current_text_layout.addWidget(lbl)
        self.manual_current_text_edit = QLineEdit()
        self.manual_current_text_edit.setPlaceholderText(tr('current_text_ph'))
        self.manual_current_text_edit.setProperty("theme_min_height", 26)
        self.manual_current_text_edit.setStyleSheet(build_line_edit_style(self.current_theme_name, 26))
        self.manual_current_text_edit.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.btn_apply_marker_text = QPushButton(tr('btn_apply_text'))
        self.btn_apply_marker_text.setProperty('tr_key', 'btn_apply_text')
        self.btn_apply_marker_text.setFixedWidth(90)
        current_text_layout.addWidget(self.manual_current_text_edit)
        current_text_layout.addWidget(self.btn_apply_marker_text)
        box.addLayout(current_text_layout)

        self.manual_marker_list = QListWidget()
        self.manual_marker_list.setMaximumHeight(140)
        box.addWidget(self.manual_marker_list)

        move_row1 = QHBoxLayout()
        self.btn_marker_up = QPushButton(tr('btn_up_move'))
        self.btn_marker_up.setProperty('tr_key', 'btn_up_move')
        self.btn_marker_down = QPushButton(tr('btn_down_move'))
        self.btn_marker_down.setProperty('tr_key', 'btn_down_move')
        move_row1.addWidget(self.btn_marker_up)
        move_row1.addWidget(self.btn_marker_down)
        box.addLayout(move_row1)

        move_row2 = QHBoxLayout()
        self.btn_marker_left = QPushButton(tr('btn_left'))
        self.btn_marker_left.setProperty('tr_key', 'btn_left')
        self.btn_marker_right = QPushButton(tr('btn_right'))
        self.btn_marker_right.setProperty('tr_key', 'btn_right')
        move_row2.addWidget(self.btn_marker_left)
        move_row2.addWidget(self.btn_marker_right)
        box.addLayout(move_row2)

        btn_row1 = QHBoxLayout()
        self.btn_delete_marker = QPushButton(tr('btn_delete_selected'))
        self.btn_delete_marker.setProperty('tr_key', 'btn_delete_selected')
        self.btn_undo_marker = QPushButton(tr('btn_undo_last'))
        self.btn_undo_marker.setProperty('tr_key', 'btn_undo_last')
        btn_row1.addWidget(self.btn_delete_marker)
        btn_row1.addWidget(self.btn_undo_marker)
        box.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        self.btn_clear_markers = QPushButton(tr('btn_clear_all'))
        self.btn_clear_markers.setProperty('tr_key', 'btn_clear_all')
        btn_row2.addWidget(self.btn_clear_markers)
        box.addLayout(btn_row2)

        self._set_manual_color_button("#d62728")
        self.manual_marker_enabled_check.stateChanged.connect(self._on_manual_marker_enabled_changed)
        self.manual_color_btn.clicked.connect(self._choose_manual_marker_color)
        self.manual_marker_list.currentRowChanged.connect(self._on_manual_marker_selected)
        self.btn_apply_marker_text.clicked.connect(self.apply_selected_manual_marker_text)
        self.manual_current_text_edit.editingFinished.connect(self.apply_selected_manual_marker_text)
        self.btn_delete_marker.clicked.connect(self.delete_selected_manual_marker)
        self.btn_undo_marker.clicked.connect(self.undo_last_manual_marker)
        self.btn_clear_markers.clicked.connect(self.clear_manual_markers)
        self.btn_marker_up.clicked.connect(lambda: self.move_selected_manual_marker(0.0, 0.01))
        self.btn_marker_down.clicked.connect(lambda: self.move_selected_manual_marker(0.0, -0.01))
        self.btn_marker_left.clicked.connect(lambda: self.move_selected_manual_marker(-0.01, 0.0))
        self.btn_marker_right.clicked.connect(lambda: self.move_selected_manual_marker(0.01, 0.0))
        self._set_manual_marker_section_enabled(False)
        self._update_manual_marker_controls()

        return box

    def _build_figure_size_section(self):
        box = CollapsibleBox(tr('figure_size'))
        box._tr_key = 'figure_size'
        box.toggle_btn.setChecked(True)
        box._toggle()
        size_layout = QHBoxLayout()
        lbl = QLabel(tr('width_in')); lbl.setProperty('tr_key', 'width_in')
        size_layout.addWidget(lbl)
        self.figure_width_spin = QDoubleSpinBox()
        self.figure_width_spin.setRange(2.0, 20.0)
        self.figure_width_spin.setDecimals(1)
        self.figure_width_spin.setSingleStep(0.5)
        self.figure_width_spin.setValue(8.0)
        self.figure_width_spin.setProperty("theme_min_width", 70)
        self.figure_width_spin.setStyleSheet(build_spin_box_style(self.current_theme_name, 70))
        size_layout.addWidget(self.figure_width_spin)
        lbl = QLabel(tr('height_in')); lbl.setProperty('tr_key', 'height_in')
        size_layout.addWidget(lbl)
        self.figure_height_spin = QDoubleSpinBox()
        self.figure_height_spin.setRange(2.0, 20.0)
        self.figure_height_spin.setDecimals(1)
        self.figure_height_spin.setSingleStep(0.5)
        self.figure_height_spin.setValue(6.0)
        self.figure_height_spin.setProperty("theme_min_width", 70)
        self.figure_height_spin.setStyleSheet(build_spin_box_style(self.current_theme_name, 70))
        size_layout.addWidget(self.figure_height_spin)
        box.addLayout(size_layout)

        self.figure_tip_label = QLabel(tr('figure_tip'))
        self.figure_tip_label.setProperty('tr_key', 'figure_tip')
        self.figure_tip_label.setWordWrap(True)
        self.figure_tip_label.setStyleSheet(build_hint_label_style(self.current_theme_name))
        box.addWidget(self.figure_tip_label)

        self.figure_width_spin.valueChanged.connect(self._on_figure_size_changed)
        self.figure_height_spin.valueChanged.connect(self._on_figure_size_changed)
        return box

    def _build_label_section(self):
        box = CollapsibleBox(tr('title_labels'))
        box._tr_key = 'title_labels'
        self.label_panel = LabelSettingsPanel()
        box.addWidget(self.label_panel)
        return box

    def _build_legend_section(self):
        box = CollapsibleBox(tr('legend'))
        box._tr_key = 'legend'
        self.legend_panel = LegendSettingsPanel()
        box.addWidget(self.legend_panel)
        return box

    def _build_border_section(self):
        box = CollapsibleBox(tr('border'))
        box._tr_key = 'border'
        self.border_panel = BorderSettingsPanel()
        box.addWidget(self.border_panel)
        return box

    def _build_bottom_buttons(self):
        self.bottom_button_bar = QWidget()
        self.bottom_button_bar.setStyleSheet(build_bottom_bar_style(self.current_theme_name))
        layout = QHBoxLayout(self.bottom_button_bar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        self.btn_refresh = QPushButton(tr('btn_refresh'))
        self.btn_refresh.setProperty('tr_key', 'btn_refresh')
        self.btn_export = QPushButton(tr('btn_export'))
        self.btn_export.setProperty('tr_key', 'btn_export')
        self.btn_save_data = QPushButton(tr('btn_save'))
        self.btn_save_data.setProperty('tr_key', 'btn_save')
        layout.addWidget(self.btn_refresh)
        layout.addWidget(self.btn_export)
        layout.addWidget(self.btn_save_data)

        self.btn_refresh.clicked.connect(self.refresh_plot)
        self.btn_export.clicked.connect(self.export_figure)
        self.btn_save_data.clicked.connect(self.save_processed_data)

        return self.bottom_button_bar

    def save_processed_data(self):
        """保存当前工作成果。

        - .xrdproj 工程文件：数据 + 全部编辑信息（配色/线宽/坐标/图例/标峰/手动标记/
          图例标签位置等），下次打开或拖入即可在原基础上继续编辑；
        - .csv / .txt：仅导出当前图上数据（含堆叠偏移）。
        """
        if not self.data_list:
            self._show_info_message(tr('msg_hint'), tr('please_add_data'))
            return
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, tr('save_dialog'), "processed_xrd.xrdproj",
            "XRD工程文件 (*.xrdproj);;CSV (*.csv);;TXT (*.txt)")
        if not filepath:
            return
        lower = filepath.lower()
        if lower.endswith('.xrdproj') or '工程文件' in selected_filter:
            if not lower.endswith('.xrdproj'):
                filepath += '.xrdproj'
            try:
                self._save_project(filepath)
                self._show_info_message(
                    tr('save_ok'),
                    tr('save_ok_msg').format(path=filepath))
            except Exception as e:
                self._show_warning_message(tr('save_failed'), tr('save_failed_msg').format(err=e))
            return
        if not (lower.endswith('.csv') or lower.endswith('.txt')):
            filepath += '.txt' if 'TXT' in selected_filter else '.csv'
        try:
            import pandas as pd
            offsets = [0.0] * len(self.data_list)
            if self.radio_stacked.isChecked():
                factor = self.offset_spin.value()
                maxima = [float(np.max(d.intensity) - np.min(d.intensity))
                          for d in self.data_list]
                for i in range(1, len(self.data_list)):
                    offsets[i] = offsets[i - 1] + maxima[i - 1] * factor
            columns = {}
            name_counts = {}
            for data, off in zip(self.data_list, offsets):
                name = data.display_name
                if name in name_counts:
                    name_counts[name] += 1
                    name = f"{name}_{name_counts[name]}"
                else:
                    name_counts[name] = 1
                columns[f"{name}_2theta"] = pd.Series(np.asarray(data.two_theta))
                columns[f"{name}_Intensity"] = pd.Series(np.asarray(data.intensity) + off)
            df = pd.DataFrame(columns)
            sep = ',' if filepath.lower().endswith('.csv') else '\t'
            df.to_csv(filepath, index=False, sep=sep, encoding='utf-8-sig')
            self._show_info_message(tr('save_ok'), tr('save_ok_data_msg').format(path=filepath))
        except Exception as e:
            self._show_warning_message(tr('save_failed'), tr('save_failed_data_msg').format(err=e))

    def _save_project(self, filepath):
        import json
        datasets = []
        for data in self.data_list:
            pos = self.plotter._label_positions.get(id(data))
            datasets.append({
                'filename': data.filename,
                'display_name': data.display_name,
                'color': data.color,
                'line_width': getattr(data, 'line_width', 1.0),
                'line_style': getattr(data, 'line_style', 'solid'),
                'peak_mark_enabled': data.peak_mark_enabled,
                'peak_symbol': data.peak_symbol,
                'peak_symbol_color': data.peak_symbol_color,
                'peak_text_color': data.peak_text_color,
                'label_position': list(pos) if pos else None,
                'two_theta': np.asarray(data.two_theta).tolist(),
                'intensity': np.asarray(data.intensity).tolist(),
            })
        proj = {
            'app': 'Relax XRD Plotter',
            'version': 1,
            'plot_mode': 'stacked' if self.radio_stacked.isChecked() else 'overlay',
            'offset': self.offset_spin.value(),
            'figure_width': self.figure_width_spin.value(),
            'figure_height': self.figure_height_spin.value(),
            'axis': self.axis_panel.get_settings(),
            'label': self.label_panel.get_settings(),
            'legend': self.legend_panel.get_settings(),
            'border': self.border_panel.get_settings(),
            'peak': self.peak_panel.get_settings(),
            'datasets': datasets,
            'manual_markers': self.manual_markers,
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(proj, f, ensure_ascii=False, indent=1)

    def _load_project(self, filepath):
        import json
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                proj = json.load(f)
        except Exception as e:
            self._show_warning_message(tr('open_failed'), tr('open_failed_msg').format(path=filepath, err=e))
            return

        self.data_list = []
        self.manual_markers = proj.get('manual_markers', [])
        self.selected_manual_marker_index = None
        for item in proj.get('datasets', []):
            data = XRDData(
                two_theta=np.asarray(item['two_theta'], dtype=float),
                intensity=np.asarray(item['intensity'], dtype=float),
                filename=item.get('filename', ''),
                display_name=item.get('display_name', ''),
                color=item.get('color', '#1f77b4'),
                line_width=item.get('line_width', 1.0),
                line_style=item.get('line_style', 'solid'),
                peak_mark_enabled=item.get('peak_mark_enabled', False),
                peak_symbol=item.get('peak_symbol', 'circle'),
                peak_symbol_color=item.get('peak_symbol_color', '#d62728'),
                peak_text_color=item.get('peak_text_color', '#1f2937'),
            )
            self.data_list.append(data)
            pos = item.get('label_position')
            if pos:
                self.plotter.save_label_position(data, pos)

        # 恢复全局编辑状态（阻断信号，最后统一刷新）
        self.radio_stacked.blockSignals(True)
        self.radio_overlay.blockSignals(True)
        if proj.get('plot_mode', 'stacked') == 'stacked':
            self.radio_stacked.setChecked(True)
        else:
            self.radio_overlay.setChecked(True)
        self.radio_stacked.blockSignals(False)
        self.radio_overlay.blockSignals(False)
        self.offset_spin.blockSignals(True)
        self.offset_spin.setValue(proj.get('offset', 0.8))
        self.offset_spin.blockSignals(False)
        self.figure_width_spin.blockSignals(True)
        self.figure_width_spin.setValue(proj.get('figure_width', 8.0))
        self.figure_width_spin.blockSignals(False)
        self.figure_height_spin.blockSignals(True)
        self.figure_height_spin.setValue(proj.get('figure_height', 6.0))
        self.figure_height_spin.blockSignals(False)
        self.axis_panel.set_settings(proj.get('axis', {}))
        self.label_panel.set_settings(proj.get('label', {}))
        self.legend_panel.set_settings(proj.get('legend', {}))
        self.border_panel.set_settings(proj.get('border', {}))
        self.peak_panel.set_settings(proj.get('peak', {}))

        self.update_file_list()
        self.update_color_buttons()
        self._sync_manual_marker_list()
        self.refresh_plot(silent_if_empty=True)

    def _on_drag_enter(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _on_drag_move(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _on_drop(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if not files:
            return
        for filepath in files:
            if filepath.lower().endswith(('.xy', '.dat', '.csv', '.txt', '.xlsx', '.xrdproj')):
                try:
                    self._append_loaded_file(filepath)
                except Exception as e:
                    self._show_warning_message(tr('load_failed'), tr('load_failed_msg').format(path=filepath, err=e))
        self.update_file_list()
        self.update_color_buttons()
        self._refresh_plot_if_ready()

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, tr('open_dialog'), "",
            "XRD数据文件 (*.xy *.dat *.csv *.txt *.xlsx);;XRD工程文件 (*.xrdproj);;所有文件 (*)")
        if not files:
            return
        for filepath in files:
            try:
                self._append_loaded_file(filepath)
            except Exception as e:
                self._show_warning_message(tr('load_failed'), tr('load_failed_msg').format(path=filepath, err=e))
        self.update_file_list()
        self.update_color_buttons()
        self._refresh_plot_if_ready()

    def remove_selected(self):
        row = self.file_list.currentRow()
        if row < 0:
            return
        self.data_list.pop(row)
        self.update_file_list()
        self.update_color_buttons()
        self._on_file_selection_changed(self.file_list.currentRow())
        if self.data_list:
            self._refresh_plot_if_ready()
        else:
            self._clear_plot_view()

    def move_up(self):
        row = self.file_list.currentRow()
        if row <= 0:
            return
        self.data_list[row - 1], self.data_list[row] = (
            self.data_list[row], self.data_list[row - 1])
        self.update_file_list()
        self.file_list.setCurrentRow(row - 1)
        self.refresh_plot()

    def move_down(self):
        row = self.file_list.currentRow()
        if row < 0 or row >= len(self.data_list) - 1:
            return
        self.data_list[row], self.data_list[row + 1] = (
            self.data_list[row + 1], self.data_list[row])
        self.update_file_list()
        self.file_list.setCurrentRow(row + 1)
        self.refresh_plot()

    def update_file_list(self):
        current_row = self.file_list.currentRow()
        self.file_list.clear()
        for data in self.data_list:
            n_points = len(data.two_theta)
            self.file_list.addItem(f"{data.display_name} ({n_points}{tr('points_suffix')})")
        if self.data_list:
            if 0 <= current_row < len(self.data_list):
                self.file_list.setCurrentRow(current_row)
            elif current_row < 0:
                self.file_list.setCurrentRow(0)

    def _on_file_selection_changed(self, row):
        has_selection = 0 <= row < len(self.data_list)
        self.name_edit.setEnabled(has_selection)
        self.btn_apply_name.setEnabled(has_selection)
        self.current_linewidth_spin.setEnabled(has_selection)
        self.current_linestyle_combo.setEnabled(has_selection)
        if has_selection:
            self.name_edit.setText(self.data_list[row].display_name)
            self.current_linewidth_spin.blockSignals(True)
            self.current_linewidth_spin.setValue(self.data_list[row].line_width)
            self.current_linewidth_spin.blockSignals(False)
            self.current_linestyle_combo.blockSignals(True)
            self.current_linestyle_combo.setCurrentText(self._line_style_label(self.data_list[row].line_style))
            self.current_linestyle_combo.blockSignals(False)
            self.peak_panel.set_current_data(self.data_list[row])
        else:
            self.name_edit.clear()
            self.current_linewidth_spin.blockSignals(True)
            self.current_linewidth_spin.setValue(1.0)
            self.current_linewidth_spin.blockSignals(False)
            self.current_linestyle_combo.blockSignals(True)
            self.current_linestyle_combo.setCurrentText(choice_display('linestyle', 'solid'))
            self.current_linestyle_combo.blockSignals(False)
            self.peak_panel.set_current_data(None)

    def apply_selected_display_name(self):
        row = self.file_list.currentRow()
        if row < 0 or row >= len(self.data_list):
            return
        new_name = self.name_edit.text().strip()
        if not new_name:
            self._show_warning_message(tr('name_invalid'), tr('name_empty'))
            self.name_edit.setText(self.data_list[row].display_name)
            return
        self.data_list[row].display_name = new_name
        self.update_file_list()
        self.file_list.setCurrentRow(row)
        self.update_color_buttons()
        self.refresh_plot()

    def apply_selected_line_width(self):
        row = self.file_list.currentRow()
        if row < 0 or row >= len(self.data_list):
            return
        self.data_list[row].line_width = self.current_linewidth_spin.value()
        self._refresh_plot_if_ready()

    def _line_style_key(self, label):
        return choice_key('linestyle', label) or "solid"

    def _line_style_label(self, key):
        return choice_display('linestyle', key)

    def apply_selected_line_style(self):
        row = self.file_list.currentRow()
        if row < 0 or row >= len(self.data_list):
            return
        self.data_list[row].line_style = self._line_style_key(self.current_linestyle_combo.currentText())
        self._refresh_plot_if_ready()

    def update_color_buttons(self):
        while self.color_layout.count():
            item = self.color_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, data in enumerate(self.data_list):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(4, 2, 4, 2)
            row_layout.setSpacing(6)

            name_label = QLabel(data.display_name)
            name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            name_label.setStyleSheet("font-size: 12px;")

            color_btn = QPushButton()
            color_btn.setFixedSize(28, 20)
            color_btn.setStyleSheet(build_color_preview_style(self.current_theme_name, data.color))

            idx = i
            color_btn.clicked.connect(lambda checked, index=idx: self._pick_color(index))

            row_layout.addWidget(name_label)
            row_layout.addWidget(color_btn)
            self.color_layout.addWidget(row)

    def _pick_color(self, index):
        if index < 0 or index >= len(self.data_list):
            return
        current_color = QColor(self.data_list[index].color)
        color = QColorDialog.getColor(current_color, self, "选择颜色")
        if color.isValid():
            self.data_list[index].color = color.name()
            self.update_color_buttons()
            self._refresh_plot_if_ready()

    def _on_scheme_changed(self, scheme_name):
        if not self.data_list:
            return
        self.plotter.apply_color_scheme(self.data_list, scheme_name)
        self.update_color_buttons()
        self._refresh_plot_if_ready()

    def _set_manual_color_button(self, color):
        self.manual_color_btn.setProperty("selected_color", color)
        self.manual_color_btn.setStyleSheet(build_color_preview_style(self.current_theme_name, color))

    def _choose_manual_marker_color(self):
        current_color = QColor(self.manual_color_btn.property("selected_color") or "#d62728")
        color = QColorDialog.getColor(current_color, self, "选择手动符号颜色")
        if color.isValid():
            self._set_manual_color_button(color.name())

    def _manual_symbol_key(self):
        return choice_key('symbol', self.manual_symbol_combo.currentText()) or "circle"

    def _manual_symbol_label(self, symbol):
        return choice_display('symbol', symbol)

    def _format_manual_marker_text(self, marker, index):
        text = str(marker.get('text', '') or '').strip()
        text_suffix = f" | 文字:{text}" if text else ""
        return (
            f"{index + 1}. {self._manual_symbol_label(marker['symbol'])} | "
            f"x={marker['x']:.2f}, y={marker['y']:.2f}{text_suffix}"
        )

    def _is_sticker_mode_enabled(self):
        return self.sticker_mode_enabled_check.isChecked()

    def _on_sticker_mode_enabled_changed(self, state):
        enabled = state == Qt.Checked
        if enabled and self.manual_marker_enabled_check.isChecked():
            self.manual_marker_enabled_check.blockSignals(True)
            self.manual_marker_enabled_check.setChecked(False)
            self.manual_marker_enabled_check.blockSignals(False)
            self._set_manual_marker_section_enabled(False)
            self._update_manual_marker_controls()
        self._set_sticker_section_enabled(enabled)
        self._update_sticker_controls()

    def _set_sticker_section_enabled(self, enabled):
        widgets = [
            self.sticker_type_combo,
            self.sticker_color_btn,
            self.sticker_size_spin,
            self.sticker_list,
            self.btn_sticker_up,
            self.btn_sticker_down,
            self.btn_delete_sticker,
            self.btn_clear_stickers,
        ]
        for widget in widgets:
            widget.setEnabled(enabled)

    def _set_sticker_color_button(self, color):
        self.sticker_color_btn.setProperty("selected_color", color)
        self.sticker_color_btn.setStyleSheet(build_color_preview_style(self.current_theme_name, color))

    def _choose_sticker_color(self):
        current_color = QColor(self.sticker_color_btn.property("selected_color") or "#FF6B6B")
        color = QColorDialog.getColor(current_color, self, "选择贴图颜色")
        if color.isValid():
            self._set_sticker_color_button(color.name())

    def _add_sticker_at(self, x, y):
        sticker = {
            'id': self._sticker_counter,
            'x': float(x),
            'y': float(y),
            'type': self.sticker_type_combo.currentText(),
            'color': self.sticker_color_btn.property("selected_color") or "#FF6B6B",
            'size': float(self.sticker_size_spin.value()),
        }
        self._sticker_counter += 1
        self._stickers.append(sticker)
        self._selected_sticker_index = len(self._stickers) - 1
        self._sync_sticker_list()
        self.refresh_plot(silent_if_empty=True)

    def _sync_sticker_list(self):
        self.sticker_list.blockSignals(True)
        self.sticker_list.clear()
        for index, sticker in enumerate(self._stickers):
            self.sticker_list.addItem(
                f"{index + 1}. {sticker['type']} | x={sticker['x']:.2f}, y={sticker['y']:.2f}"
            )
        if self._selected_sticker_index is not None and 0 <= self._selected_sticker_index < len(self._stickers):
            self.sticker_list.setCurrentRow(self._selected_sticker_index)
        self.sticker_list.blockSignals(False)
        self._update_sticker_controls()

    def _update_sticker_controls(self):
        has_selection = (
            self._is_sticker_mode_enabled()
            and self._selected_sticker_index is not None
            and 0 <= self._selected_sticker_index < len(self._stickers)
        )
        self.btn_delete_sticker.setEnabled(has_selection)
        self.btn_sticker_up.setEnabled(has_selection)
        self.btn_sticker_down.setEnabled(has_selection)
        self.btn_clear_stickers.setEnabled(self._is_sticker_mode_enabled() and bool(self._stickers))

    def _on_sticker_selected(self, row):
        if row < 0 or row >= len(self._stickers):
            self._selected_sticker_index = None
        else:
            self._selected_sticker_index = row
        self._update_sticker_controls()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def delete_selected_sticker(self):
        index = self._selected_sticker_index
        if index is None or not (0 <= index < len(self._stickers)):
            return
        self._stickers.pop(index)
        if not self._stickers:
            self._selected_sticker_index = None
        else:
            self._selected_sticker_index = min(index, len(self._stickers) - 1)
        self._sync_sticker_list()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def clear_stickers(self):
        if not self._stickers:
            return
        self._stickers.clear()
        self._selected_sticker_index = None
        self._sync_sticker_list()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def move_selected_sticker(self, dx_ratio, dy_ratio):
        index = self._selected_sticker_index
        if index is None or not (0 <= index < len(self._stickers)):
            return
        x_min, x_max = self.plotter.axes.get_xlim()
        y_min, y_max = self.plotter.axes.get_ylim()
        x_step = (x_max - x_min) * dx_ratio
        y_step = (y_max - y_min) * dy_ratio
        self._stickers[index]['x'] += x_step
        self._stickers[index]['y'] += y_step
        self._sync_sticker_list()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def _is_manual_marker_enabled(self):
        return self.manual_marker_enabled_check.isChecked()

    def _set_manual_marker_section_enabled(self, enabled):
        widgets = [
            self.manual_symbol_combo,
            self.manual_color_btn,
            self.manual_size_spin,
            self.manual_default_text_edit,
            self.manual_current_text_edit,
            self.btn_apply_marker_text,
            self.manual_marker_list,
            self.btn_marker_up,
            self.btn_marker_down,
            self.btn_marker_left,
            self.btn_marker_right,
            self.btn_delete_marker,
            self.btn_undo_marker,
            self.btn_clear_markers,
        ]
        for widget in widgets:
            widget.setEnabled(enabled)

    def _on_manual_marker_enabled_changed(self, state):
        enabled = state == Qt.Checked
        if enabled and hasattr(self, 'sticker_mode_enabled_check') and self.sticker_mode_enabled_check.isChecked():
            self.sticker_mode_enabled_check.blockSignals(True)
            self.sticker_mode_enabled_check.setChecked(False)
            self.sticker_mode_enabled_check.blockSignals(False)
            self._set_sticker_section_enabled(False)
            self._update_sticker_controls()
        self._dragging_marker_active = False
        self._dragging_marker_index = None
        self._set_manual_marker_section_enabled(enabled)
        self._update_manual_marker_controls()

    def _update_manual_marker_controls(self):
        has_selection = (
            self._is_manual_marker_enabled()
            and
            self.selected_manual_marker_index is not None
            and 0 <= self.selected_manual_marker_index < len(self.manual_markers)
        )
        section_enabled = self._is_manual_marker_enabled()
        self.manual_symbol_combo.setEnabled(section_enabled)
        self.manual_color_btn.setEnabled(section_enabled)
        self.manual_size_spin.setEnabled(section_enabled)
        self.manual_default_text_edit.setEnabled(section_enabled)
        self.manual_marker_list.setEnabled(section_enabled)
        self.btn_undo_marker.setEnabled(section_enabled and bool(self.manual_markers))
        self.btn_clear_markers.setEnabled(section_enabled and bool(self.manual_markers))
        self.manual_current_text_edit.setEnabled(has_selection)
        self.btn_apply_marker_text.setEnabled(has_selection)
        self.btn_delete_marker.setEnabled(has_selection)
        self.btn_marker_up.setEnabled(has_selection)
        self.btn_marker_down.setEnabled(has_selection)
        self.btn_marker_left.setEnabled(has_selection)
        self.btn_marker_right.setEnabled(has_selection)
        self.manual_current_text_edit.blockSignals(True)
        if has_selection:
            self.manual_current_text_edit.setText(
                self.manual_markers[self.selected_manual_marker_index].get('text', '')
            )
        else:
            self.manual_current_text_edit.clear()
        self.manual_current_text_edit.blockSignals(False)

    def _sync_manual_marker_list(self):
        self.manual_marker_list.blockSignals(True)
        self.manual_marker_list.clear()
        for index, marker in enumerate(self.manual_markers):
            self.manual_marker_list.addItem(self._format_manual_marker_text(marker, index))
        if self.selected_manual_marker_index is not None and 0 <= self.selected_manual_marker_index < len(self.manual_markers):
            self.manual_marker_list.setCurrentRow(self.selected_manual_marker_index)
        self.manual_marker_list.blockSignals(False)
        self._update_manual_marker_controls()

    def _set_selected_manual_marker(self, index):
        if index is None or not (0 <= index < len(self.manual_markers)):
            self.selected_manual_marker_index = None
            self.manual_marker_list.blockSignals(True)
            self.manual_marker_list.clearSelection()
            self.manual_marker_list.setCurrentRow(-1)
            self.manual_marker_list.blockSignals(False)
        else:
            self.selected_manual_marker_index = index
            self.manual_marker_list.blockSignals(True)
            self.manual_marker_list.setCurrentRow(index)
            self.manual_marker_list.blockSignals(False)
            self.manual_current_text_edit.blockSignals(True)
            self.manual_current_text_edit.setText(self.manual_markers[index].get('text', ''))
            self.manual_current_text_edit.blockSignals(False)
        self._update_manual_marker_controls()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def _on_manual_marker_selected(self, row):
        if row < 0 or row >= len(self.manual_markers):
            self.selected_manual_marker_index = None
        else:
            self.selected_manual_marker_index = row
            self.manual_current_text_edit.blockSignals(True)
            self.manual_current_text_edit.setText(self.manual_markers[row].get('text', ''))
            self.manual_current_text_edit.blockSignals(False)
        self._update_manual_marker_controls()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def apply_selected_manual_marker_text(self):
        index = self.selected_manual_marker_index
        if index is None or not (0 <= index < len(self.manual_markers)):
            return
        self.manual_markers[index]['text'] = self.manual_current_text_edit.text().strip()
        self._sync_manual_marker_list()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def _find_manual_marker_at(self, x, y):
        if not self.manual_markers:
            return None
        x_min, x_max = self.plotter.axes.get_xlim()
        y_min, y_max = self.plotter.axes.get_ylim()
        x_span = max(abs(x_max - x_min), 1e-9)
        y_span = max(abs(y_max - y_min), 1e-9)

        closest_index = None
        closest_distance = None
        for index, marker in enumerate(self.manual_markers):
            norm_dx = (marker['x'] - x) / x_span
            norm_dy = (marker['y'] - y) / y_span
            distance = norm_dx * norm_dx + norm_dy * norm_dy
            if distance <= 0.0016 and (closest_distance is None or distance < closest_distance):
                closest_index = index
                closest_distance = distance
        return closest_index

    def _on_canvas_pick(self, event):
        if event.mouseevent.button != 1:
            return
        for text, data in getattr(self.plotter, '_curve_labels', []):
            if event.artist is text:
                self._dragging_label = (text, data)
                break

    def _on_canvas_click(self, event):
        if event.button != 1 or event.inaxes != self.plotter.axes:
            return
        if event.xdata is None or event.ydata is None:
            return
        # 图例手动拖动模式下，点到标签时不添加手动标记
        if self._legend_layout_mode == 'drag':
            for text, _data in getattr(self.plotter, '_curve_labels', []):
                try:
                    contains, _info = text.contains(event)
                except Exception:
                    contains = False
                if contains:
                    return
        if self._is_sticker_mode_enabled():
            self._add_sticker_at(event.xdata, event.ydata)
            return
        if not self._is_manual_marker_enabled():
            return

        hit_index = self._find_manual_marker_at(event.xdata, event.ydata)
        if hit_index is not None:
            self._set_selected_manual_marker(hit_index)
            self._dragging_marker_index = hit_index
            self._dragging_marker_active = True
            return

        if not self.data_list:
            return

        marker = {
            'id': self._manual_marker_counter,
            'x': float(event.xdata),
            'y': float(event.ydata),
            'symbol': self._manual_symbol_key(),
            'color': self.manual_color_btn.property("selected_color") or "#d62728",
            'size': float(self.manual_size_spin.value()),
            'text': self.manual_default_text_edit.text().strip(),
        }
        self._manual_marker_counter += 1
        self.manual_markers.append(marker)
        self.selected_manual_marker_index = len(self.manual_markers) - 1
        self._sync_manual_marker_list()
        self.refresh_plot(silent_if_empty=True)

    def _on_canvas_motion(self, event):
        if self._dragging_label is not None:
            if event.inaxes == self.plotter.axes and event.xdata is not None and event.ydata is not None:
                text, _data = self._dragging_label
                text.set_position((float(event.xdata), float(event.ydata)))
                self.canvas.draw_idle()
            return
        if not self._dragging_marker_active or not self._is_manual_marker_enabled():
            return
        index = self._dragging_marker_index
        if index is None or not (0 <= index < len(self.manual_markers)):
            return
        if event.inaxes != self.plotter.axes or event.xdata is None or event.ydata is None:
            return
        self.manual_markers[index]['x'] = float(event.xdata)
        self.manual_markers[index]['y'] = float(event.ydata)
        self.selected_manual_marker_index = index
        self._sync_manual_marker_list()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def _on_canvas_release(self, event):
        if event.button != 1:
            return
        if self._dragging_label is not None:
            text, data = self._dragging_label
            self.plotter.save_label_position(data, text.get_position())
            self._dragging_label = None
        self._dragging_marker_active = False
        self._dragging_marker_index = None

    def delete_selected_manual_marker(self):
        index = self.selected_manual_marker_index
        if index is None or not (0 <= index < len(self.manual_markers)):
            return
        self.manual_markers.pop(index)
        if not self.manual_markers:
            self.selected_manual_marker_index = None
        else:
            self.selected_manual_marker_index = min(index, len(self.manual_markers) - 1)
        self._sync_manual_marker_list()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def undo_last_manual_marker(self):
        if not self.manual_markers:
            return
        self.manual_markers.pop()
        if not self.manual_markers:
            self.selected_manual_marker_index = None
        else:
            self.selected_manual_marker_index = len(self.manual_markers) - 1
        self._sync_manual_marker_list()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def clear_manual_markers(self):
        if not self.manual_markers:
            return
        self.manual_markers.clear()
        self.selected_manual_marker_index = None
        self._sync_manual_marker_list()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def move_selected_manual_marker(self, dx_ratio, dy_ratio):
        index = self.selected_manual_marker_index
        if index is None or not (0 <= index < len(self.manual_markers)):
            return
        x_min, x_max = self.plotter.axes.get_xlim()
        y_min, y_max = self.plotter.axes.get_ylim()
        x_step = (x_max - x_min) * dx_ratio
        y_step = (y_max - y_min) * dy_ratio
        self.manual_markers[index]['x'] += x_step
        self.manual_markers[index]['y'] += y_step
        self._sync_manual_marker_list()
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)

    def _on_figure_size_changed(self):
        width = self.figure_width_spin.value()
        height = self.figure_height_spin.value()
        self.figure.set_size_inches(width, height, forward=True)
        if self.data_list:
            self.refresh_plot(silent_if_empty=True)
        else:
            self.canvas.draw_idle()

    def refresh_plot(self, silent_if_empty=False):
        if not self.data_list:
            if not silent_if_empty:
                self._show_info_message(tr('msg_hint'), tr('please_add_data'))
            return

        border_cfg = self.border_panel.get_settings()
        self.plotter.set_border_width(border_cfg['border_width'])

        label_cfg = self.label_panel.get_settings()
        self.plotter.set_font_family(label_cfg['font_family'])
        legend_cfg = self.legend_panel.get_settings()
        self.plotter.set_legend_font_family(legend_cfg['font_family'])

        if self.radio_stacked.isChecked():
            offset_factor = self.offset_spin.value()
            self.plotter.plot_stacked(self.data_list,
                                      offset_factor=offset_factor)
        else:
            self.plotter.plot_overlay(self.data_list)

        axis_cfg = self.axis_panel.get_settings()
        self.plotter.set_axis_range(
            x_min=axis_cfg['x_min'], x_max=axis_cfg['x_max'],
            y_min=axis_cfg['y_min'], y_max=axis_cfg['y_max'])
        self.plotter.set_axis_ticks(
            x_major=axis_cfg['x_major'], y_major=axis_cfg['y_major'],
            tick_direction=axis_cfg['tick_direction'],
            show_x_ticks=axis_cfg['show_x_ticks'],
            show_y_ticks=axis_cfg['show_y_ticks'])

        self.plotter.set_labels(
            title=label_cfg['title'],
            xlabel=label_cfg['xlabel'],
            ylabel=label_cfg['ylabel'],
            title_size=label_cfg['title_size'],
            label_size=label_cfg['label_size'],
            tick_size=label_cfg['tick_size'],
            title_bold=label_cfg['title_bold'],
            show_xlabel=label_cfg['show_xlabel'],
            show_ylabel=label_cfg['show_ylabel'])

        legend_layout_mode = legend_cfg.get('layout_mode', 'grouped')
        self._legend_layout_mode = legend_layout_mode
        if legend_layout_mode == 'grouped':
            self.plotter.set_legend(
                show=legend_cfg['show'],
                position=legend_cfg['position'],
                show_frame=legend_cfg['show_frame'],
                font_size=legend_cfg['font_size'],
                font_family=legend_cfg['font_family'])
        else:
            self.plotter.set_legend(show=False)
            if legend_cfg['show']:
                self.plotter.draw_curve_labels(
                    draggable=(legend_layout_mode == 'drag'),
                    font_size=legend_cfg['font_size'],
                    font_family=legend_cfg['font_family'])

        peak_cfg = self.peak_panel.get_settings()
        self.plotter.annotate_peaks(self.data_list, peak_cfg)
        self.plotter.draw_manual_markers(self.manual_markers, self.selected_manual_marker_index)
        self.plotter.draw_stickers(self._stickers)

        self.canvas.draw()

    def export_figure(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, tr('export_dialog'), "",
            "PNG (*.png);;TIFF (*.tiff);;SVG (*.svg);;PDF (*.pdf)")
        if not filepath:
            return
        dpi, ok = QInputDialog.getInt(
            self, tr('export_dpi'), tr('export_dpi_msg'), 300, 72, 1200)
        if not ok:
            return
        try:
            self.plotter.export_figure(
                filepath,
                dpi=dpi,
                width=self.figure_width_spin.value(),
                height=self.figure_height_spin.value(),
            )
            self._show_info_message(tr('export_ok'), tr('export_ok_msg').format(path=filepath))
        except Exception as e:
            self._show_warning_message(tr('export_failed'), tr('export_failed_msg').format(err=e))
