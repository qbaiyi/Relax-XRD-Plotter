import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch

W, H, DPI = 1080, 1440, 150
fw, fh = W / DPI, H / DPI

FONT = r"C:/Windows/Fonts/msyh.ttc"
fp_title = fm.FontProperties(fname=FONT, size=60, weight="bold")
fp_sub = fm.FontProperties(fname=FONT, size=34)
fp_small = fm.FontProperties(fname=FONT, size=22)
fp_en = fm.FontProperties(fname=FONT, size=24)

# ---- background gradient (soft light blue -> white) ----
yy, xx = np.mgrid[0:1:fh*DPI, 0:1:fw*DPI]
grad = np.ones((int(fh*DPI), int(fw*DPI), 3))
top = np.array([0.91, 0.95, 1.00])
bot = np.array([1.00, 1.00, 1.00])
grad = (top[None, None, :] * yy[..., None] + bot[None, None, :] * (1 - yy[..., None]))

fig = plt.figure(figsize=(fw, fh), dpi=DPI)
fig.figimage(grad, xo=0, yo=0, zorder=0)

# ---- XRD diffraction pattern ----
t = np.linspace(10, 80, 1200)
def peak(t, c, a, w):
    return a * np.exp(-((t - c) ** 2) / (2 * w ** 2))
y = 6 + 0.04 * t
peaks = [(18, 28, 1.1), (28, 60, 0.9), (36, 42, 1.0), (43, 90, 1.3),
         (47, 35, 0.8), (54, 70, 1.1), (61, 50, 1.0), (68, 38, 0.85), (73, 30, 0.8)]
for c, a, w in peaks:
    y += peak(t, c, a, w)
y += np.random.RandomState(3).normal(0, 0.6, t.size)
y = np.clip(y, 0, None)

ax = fig.add_axes([0.10, 0.30, 0.80, 0.42])
ax.plot(t, y, color="#1565c0", lw=2.6)
ax.fill_between(t, 0, y, color="#1565c0", alpha=0.10)
ax.set_xlim(10, 80)
ax.set_ylim(0, max(y) * 1.12)
ax.set_xticks([20, 30, 40, 50, 60, 70])
ax.set_yticks([])
ax.set_xlabel("2θ (°)", fontproperties=fp_small, color="#374151")
ax.tick_params(colors="#6b7280", labelsize=18)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#9ca3af")
ax.set_title("XRD 衍射图谱", fontproperties=fp_small, color="#374151", pad=10)

# ---- title block ----
fig.text(0.5, 0.915, "免费 XRD 作图软件", ha="center", va="center",
         fontproperties=fp_title, color="#0f172a")
fig.text(0.5, 0.84, "WorkBuddy 制作", ha="center", va="center",
         fontproperties=fp_sub, color="#1d4ed8")

# ---- bottom badge ----
fig.text(0.5, 0.215, "Relax XRD Plotter", ha="center", va="center",
         fontproperties=fp_en, color="#475569")
fig.text(0.5, 0.165, "中文 / English 双界面  ·  拖拽导入  ·  一键导出",
         ha="center", va="center", fontproperties=fp_small, color="#6b7280")

# rounded badge for "WorkBuddy"
axb = fig.add_axes([0.5, 0.255, 0.001, 0.001])
axb.axis("off")

plt.savefig("coverpage.png", dpi=DPI)
print("saved coverpage.png")
