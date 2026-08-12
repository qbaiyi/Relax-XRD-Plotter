import math
import sys
from pathlib import Path
from PyQt5.QtCore import QPointF, QSettings, QTimer, Qt
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QLinearGradient,
                         QPainter, QPainterPath, QPen, QPixmap,
                         QRadialGradient)
from PyQt5.QtWidgets import QApplication, QSplashScreen
from theme_manager import DEFAULT_THEME_NAME, normalize_theme_name
from ui_main import XRDMainWindow


SPLASH_IMAGE_NAME = "可爱有趣的XRD画图名字 (1)(1).png"


def resource_path(name):
    """返回资源文件路径，兼容源码运行和 PyInstaller 打包环境。"""
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    else:
        base = Path(__file__).resolve().parent
    return base / name


def create_app_icon():
    image_path = resource_path(SPLASH_IMAGE_NAME)
    pixmap = QPixmap(str(image_path))
    if not pixmap.isNull():
        return QIcon(pixmap)
    return QIcon()


def create_default_splash_pixmap(width=1280, height=720):
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    background = QLinearGradient(0, 0, width, height)
    background.setColorAt(0.0, QColor("#060b16"))
    background.setColorAt(0.35, QColor("#0b1c33"))
    background.setColorAt(0.7, QColor("#111d43"))
    background.setColorAt(1.0, QColor("#1c0f35"))
    painter.fillRect(pixmap.rect(), background)

    for center, radius, color in [
        (QPointF(width * 0.18, height * 0.28), 210, QColor(0, 247, 255, 70)),
        (QPointF(width * 0.76, height * 0.34), 260, QColor(115, 84, 255, 75)),
        (QPointF(width * 0.55, height * 0.72), 220, QColor(255, 82, 168, 60)),
    ]:
        glow = QRadialGradient(center, radius)
        glow.setColorAt(0.0, color)
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)

    painter.setPen(QPen(QColor(130, 190, 255, 24), 1))
    for x in range(0, width, 48):
        painter.drawLine(x, 0, x, height)
    for y in range(0, height, 48):
        painter.drawLine(0, y, width, y)

    painter.setPen(QPen(QColor("#40f2ff"), 2.5))
    for radius in (54, 96, 138):
        painter.drawEllipse(QPointF(width * 0.19, height * 0.34), radius, radius)

    painter.setBrush(QColor("#89f7ff"))
    painter.setPen(Qt.NoPen)
    atom_points = [
        QPointF(width * 0.19, height * 0.34),
        QPointF(width * 0.14, height * 0.27),
        QPointF(width * 0.27, height * 0.31),
        QPointF(width * 0.23, height * 0.42),
        QPointF(width * 0.11, height * 0.38),
    ]
    for point in atom_points:
        painter.drawEllipse(point, 8, 8)
    painter.setPen(QPen(QColor("#8ec5ff"), 1.6))
    bond_pairs = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 3)]
    for start, end in bond_pairs:
        painter.drawLine(atom_points[start], atom_points[end])

    base_y = height * 0.74
    left_x = width * 0.08
    right_x = width * 0.92
    chart_w = right_x - left_x
    pattern = QPainterPath(QPointF(left_x, base_y))
    peaks = [
        (0.08, 0.14, 0.012),
        (0.18, 0.22, 0.016),
        (0.28, 0.34, 0.018),
        (0.44, 0.52, 0.024),
        (0.59, 0.28, 0.018),
        (0.71, 0.42, 0.020),
        (0.84, 0.20, 0.014),
    ]
    for step in range(401):
        t = step / 400.0
        y_val = 0.02
        for center, amplitude, sigma in peaks:
            y_val += amplitude * math.exp(-((t - center) ** 2) / (2 * sigma ** 2))
        wave = 0.012 * math.sin(t * 26.0) + 0.008 * math.cos(t * 17.0)
        x_pos = left_x + chart_w * t
        y_pos = base_y - height * (y_val + wave)
        pattern.lineTo(x_pos, y_pos)
    painter.setPen(QPen(QColor("#7cf9ff"), 4))
    painter.drawPath(pattern)

    second_pattern = QPainterPath(QPointF(left_x, base_y - 36))
    peaks2 = [
        (0.11, 0.10, 0.015),
        (0.23, 0.26, 0.017),
        (0.38, 0.18, 0.019),
        (0.55, 0.30, 0.022),
        (0.67, 0.16, 0.017),
        (0.82, 0.24, 0.016),
    ]
    for step in range(401):
        t = step / 400.0
        y_val = 0.01
        for center, amplitude, sigma in peaks2:
            y_val += amplitude * math.exp(-((t - center) ** 2) / (2 * sigma ** 2))
        wave = 0.01 * math.sin(t * 24.0 + 1.3)
        x_pos = left_x + chart_w * t
        y_pos = base_y - 36 - height * (y_val + wave)
        second_pattern.lineTo(x_pos, y_pos)
    painter.setPen(QPen(QColor("#ff66c4"), 2.5))
    painter.drawPath(second_pattern)

    painter.setPen(QPen(QColor("#64ffda"), 2))
    beam_start = QPointF(width * 0.78, height * 0.18)
    beam_end = QPointF(width * 0.60, height * 0.38)
    painter.drawLine(beam_start, beam_end)
    painter.setPen(QPen(QColor("#ffe066"), 3))
    painter.drawLine(QPointF(width * 0.79, height * 0.19), QPointF(width * 0.63, height * 0.42))

    crystal = QPainterPath()
    crystal.moveTo(width * 0.60, height * 0.42)
    crystal.lineTo(width * 0.66, height * 0.36)
    crystal.lineTo(width * 0.73, height * 0.40)
    crystal.lineTo(width * 0.71, height * 0.49)
    crystal.lineTo(width * 0.63, height * 0.52)
    crystal.closeSubpath()
    painter.setPen(QPen(QColor("#d9a7ff"), 2))
    painter.setBrush(QColor(153, 89, 255, 75))
    painter.drawPath(crystal)

    for angle in range(-55, 65, 20):
        length = 118
        radians = math.radians(angle)
        start = QPointF(width * 0.69, height * 0.45)
        end = QPointF(start.x() + math.cos(radians) * length,
                      start.y() - math.sin(radians) * length)
        painter.setPen(QPen(QColor(113, 255, 210, 120), 2))
        painter.drawLine(start, end)

    title_font = QFont("Arial", 34, QFont.Bold)
    sub_font = QFont("Arial", 16, QFont.Normal)
    mini_font = QFont("Arial", 13, QFont.Bold)

    painter.setPen(QColor("#f5fbff"))
    painter.setFont(title_font)
    painter.drawText(78, 92, "Relax XRD Plotter")

    painter.setPen(QColor("#9fe7ff"))
    painter.setFont(sub_font)
    painter.drawText(82, 132, "AI Concept Splash | X-Ray Diffraction Visualization")

    painter.setPen(QColor("#89f7ff"))
    painter.setFont(mini_font)
    painter.drawText(84, 615, "Diffraction Peaks")
    painter.drawText(958, 104, "Crystal / Beam")

    painter.end()
    return pixmap


def create_splash_pixmap():
    image_path = resource_path(SPLASH_IMAGE_NAME)
    pixmap = QPixmap(str(image_path))
    if not pixmap.isNull():
        splash = pixmap.scaled(840, 840, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter = QPainter(splash)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        shadow_font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(shadow_font)
        text_rect = splash.rect().adjusted(0, 0, -28, -24)
        painter.setPen(QColor(255, 255, 255, 210))
        painter.drawText(text_rect.adjusted(1, 1, 1, 1), Qt.AlignRight | Qt.AlignBottom,
                         "qxh (WIT)\nqbaiyi@qq.com")
        painter.setPen(QColor(22, 82, 196))
        painter.drawText(text_rect, Qt.AlignRight | Qt.AlignBottom,
                         "qxh (WIT)\nqbaiyi@qq.com")
        painter.end()
        return splash
    return create_default_splash_pixmap()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(create_app_icon())
    settings = QSettings("RelaxXRDPlotter", "Relax XRD Plotter")
    theme_name = normalize_theme_name(settings.value("ui/theme", DEFAULT_THEME_NAME, type=str))
    splash = QSplashScreen(create_splash_pixmap(), Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.show()
    app.processEvents()
    window = XRDMainWindow(theme_name=theme_name)
    window.setWindowIcon(create_app_icon())

    def show_main_window():
        window.show()
        splash.finish(window)

    QTimer.singleShot(1500, show_main_window)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
