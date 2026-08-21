#!/usr/bin/env python3
"""One-time prep: turn the real Wix photos into optimized site assets in assets/.
Crops the Tampa-branded van (with its 813 phone number) out of the driveway shot.
Run: py -3.12 prep_images.py
"""
from PIL import Image
import os

SRC = "wix-assets"
DST = "assets"
os.makedirs(DST, exist_ok=True)

def save(img, name, max_w, quality=80):
    if img.width > max_w:
        img = img.resize((max_w, round(img.height * max_w / img.width)), Image.LANCZOS)
    img = img.convert("RGB")
    img.save(os.path.join(DST, name), "JPEG", quality=quality, optimize=True, progressive=True)
    print(name, img.size, os.path.getsize(os.path.join(DST, name)) // 1024, "KB")

# Driveway Land Rover job — crop off the left ~28% (Tampa-branded van w/ 813 number)
im = Image.open(f"{SRC}/377b0f_dc5912bf6fc44d6f952d4dc3d0bbd48b.jpeg")
im = im.crop((int(im.width * 0.28), 0, im.width, im.height))
save(im, "driveway-service.jpg", 1600, 78)
save(im, "og.jpg", 1200, 75)

# Under-hood work
im = Image.open(f"{SRC}/377b0f_ac42f81e79b1401e910d190666eb60a1.jpg")
save(im, "under-hood.jpg", 1400, 78)

# Steering column work (portrait)
im = Image.open(f"{SRC}/377b0f_dda13223c97d4cc79fcc614d34096203.jpeg")
save(im, "interior-work.jpg", 1100, 78)

# Logo (transparent PNG, keep as PNG)
im = Image.open(f"{SRC}/logo_IMG_0472.png")
im.save(os.path.join(DST, "logo.png"), "PNG", optimize=True)
print("logo.png", im.size)
