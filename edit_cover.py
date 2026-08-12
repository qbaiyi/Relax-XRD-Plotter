from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# Load source image
src_path = r"C:/Users/Administrator/.workbuddy/clipboard-images/clipboard-2026-08-12T06-42-57-108Z-f1f642ac.jpg"
img = Image.open(src_path).convert("RGBA")
W, H = img.size

# Font paths
FONT_BOLD = r"C:/Windows/Fonts/msyh.ttc"
FONT_REG = r"C:/Windows/Fonts/msyh.ttc"

# Title text (split into two lines)
title_line1 = "WorkBuddy 制作的"
title_line2 = "免费 XRD 画图软件"

# Cover existing title + subtitle region (roughly top 45% of image)
text_region = (0, 0, W, int(H * 0.45))
top = img.crop(text_region).filter(ImageFilter.GaussianBlur(radius=35))
img.paste(top, (0, 0))

# Optional: subtle overlay band for better readability
overlay = Image.new("RGBA", (W, int(H * 0.36)), (255, 255, 255, 0))
# draw = ImageDraw.Draw(overlay)
# draw.rectangle([0, 0, W, int(H*0.36)], fill=(255,255,255,40))
# img = Image.alpha_composite(img, overlay)

draw = ImageDraw.Draw(img)

# Choose font sizes proportional to image width
fs_title = int(W * 0.110)
fs_sub = int(W * 0.040)
title_font = ImageFont.truetype(FONT_BOLD, fs_title)
sub_font = ImageFont.truetype(FONT_REG, fs_sub)

# Draw text with outline helper
def draw_text_centered(draw, y, text, font, fill, outline_width=3, outline_color="white"):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    # outline
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    draw.text((x, y), text, font=font, fill=fill)

# Title line 1
draw_text_centered(draw, int(H * 0.07), title_line1, title_font, fill="#FF4081", outline_width=4)

# Title line 2
bbox1 = draw.textbbox((0, 0), title_line1, font=title_font)
h1 = bbox1[3] - bbox1[1]
draw_text_centered(draw, int(H * 0.07) + h1 + int(H * 0.01), title_line2, title_font, fill="#FF4081", outline_width=4)

# No subtitle (removed "暑假自制" / "简单好用" entirely)

# Save
out_path = r"D:/xrd sof revise/coverpage.png"
img.convert("RGB").save(out_path, quality=95)
print("saved", out_path, "size", img.size)
