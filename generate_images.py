"""
generate_images.py
------------------
Generates 750 placeholder photocard images for the ITZY bot and updates
itzy_photocards_fixed.json to reference local file paths.

Usage:
    pip install Pillow
    python generate_images.py

Output:
    - images/<card_id>.png  (300x400px per card, color-coded by rarity)
    - itzy_photocards_fixed.json  (image field updated to local path)

Rarity colour scheme:
    Common    → gray   (#9E9E9E)
    Uncommon  → blue   (#42A5F5)
    Rare      → purple (#AB47BC)
    Epic      → pink   (#EC407A)
    Legendary → gold   (#FFC107)
"""

import json
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit(
        "Pillow is not installed. Run:  pip install Pillow\n"
        "Then re-run this script."
    )

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

JSON_FILE = "itzy_photocards_fixed.json"
OUTPUT_DIR = Path("images")
CARD_WIDTH, CARD_HEIGHT = 300, 400

# Background colours per rarity (dark shade used as card background)
RARITY_BG_COLORS = {
    "Common":    "#424242",   # dark gray
    "Uncommon":  "#1565C0",   # dark blue
    "Rare":      "#6A1B9A",   # dark purple
    "Epic":      "#AD1457",   # dark pink
    "Legendary": "#F57F17",   # dark gold/amber
}

# Accent colours per rarity (lighter, used for the header bar)
RARITY_ACCENT_COLORS = {
    "Common":    "#9E9E9E",
    "Uncommon":  "#42A5F5",
    "Rare":      "#AB47BC",
    "Epic":      "#EC407A",
    "Legendary": "#FFC107",
}

# Rarity badge emoji-style labels
RARITY_LABELS = {
    "Common":    "★ COMMON",
    "Uncommon":  "★★ UNCOMMON",
    "Rare":      "★★★ RARE",
    "Epic":      "★★★★ EPIC",
    "Legendary": "★★★★★ LEGENDARY",
}

# Member accent colours (subtle tint on the bottom bar)
MEMBER_COLORS = {
    "Yeji":       "#FF7043",
    "Lia":        "#66BB6A",
    "Ryujin":     "#EF5350",
    "Chaeryeong": "#26C6DA",
    "Yuna":       "#FFA726",
}

TEXT_COLOR = "#FFFFFF"
SUBTEXT_COLOR = "#DDDDDD"
DARK_OVERLAY = "#00000066"   # semi-transparent (used via alpha blending)


# ---------------------------------------------------------------------------
# Helper: try to load a system font, fall back to PIL default
# ---------------------------------------------------------------------------

def _load_font(size: int, bold: bool = False):
    """Return a PIL font at the requested size, falling back gracefully."""
    candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    candidates_regular = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    candidates = candidates_bold if bold else candidates_regular
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    # PIL built-in bitmap font (no size control, but always available)
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Core image generation
# ---------------------------------------------------------------------------

def hex_to_rgb(hex_color: str):
    """Convert '#RRGGBB' to (R, G, B)."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def blend(base_rgb, overlay_rgb, alpha: float):
    """Alpha-blend overlay onto base. alpha in [0, 1]."""
    return tuple(int(b * (1 - alpha) + o * alpha) for b, o in zip(base_rgb, overlay_rgb))


def wrap_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw):
    """Wrap text to fit within max_width pixels. Returns list of lines."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def generate_card_image(card: dict, output_path: Path):
    """Generate a single 300×400 placeholder image for the given card."""
    rarity   = card.get("rarity", "Common")
    member   = card.get("member", "")
    card_id  = card.get("id", "")
    name     = card.get("name", "")
    album    = card.get("album", "")
    card_type = card.get("type", "")

    bg_color     = hex_to_rgb(RARITY_BG_COLORS.get(rarity, "#424242"))
    accent_color = hex_to_rgb(RARITY_ACCENT_COLORS.get(rarity, "#9E9E9E"))
    member_color = hex_to_rgb(MEMBER_COLORS.get(member, "#FFFFFF"))

    img  = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), bg_color)
    draw = ImageDraw.Draw(img)

    # --- Header bar (top 56px) ---
    header_color = blend(bg_color, accent_color, 0.55)
    draw.rectangle([(0, 0), (CARD_WIDTH, 56)], fill=header_color)

    # --- Diagonal accent stripe ---
    stripe_color = blend(bg_color, accent_color, 0.18)
    draw.polygon(
        [(0, CARD_HEIGHT), (CARD_WIDTH * 0.6, CARD_HEIGHT),
         (CARD_WIDTH, CARD_HEIGHT * 0.55), (CARD_WIDTH, CARD_HEIGHT)],
        fill=stripe_color,
    )

    # --- Bottom member bar (last 48px) ---
    footer_color = blend(bg_color, member_color, 0.35)
    draw.rectangle([(0, CARD_HEIGHT - 48), (CARD_WIDTH, CARD_HEIGHT)], fill=footer_color)

    # --- Fonts ---
    font_id      = _load_font(11)
    font_rarity  = _load_font(13, bold=True)
    font_member  = _load_font(22, bold=True)
    font_name    = _load_font(12)
    font_album   = _load_font(11)
    font_type    = _load_font(11)

    # --- Card ID (top-left of header) ---
    draw.text((10, 8), card_id, font=font_id, fill=TEXT_COLOR)

    # --- Rarity label (top-right of header) ---
    rarity_label = RARITY_LABELS.get(rarity, rarity)
    rb = draw.textbbox((0, 0), rarity_label, font=font_rarity)
    rarity_w = rb[2] - rb[0]
    draw.text((CARD_WIDTH - rarity_w - 10, 8), rarity_label, font=font_rarity, fill=TEXT_COLOR)

    # --- Member name (large, centred in middle zone) ---
    mb = draw.textbbox((0, 0), member, font=font_member)
    member_w = mb[2] - mb[0]
    member_x = (CARD_WIDTH - member_w) // 2
    draw.text((member_x, 80), member, font=font_member, fill=TEXT_COLOR)

    # --- Decorative horizontal rule below member name ---
    rule_y = 115
    draw.line([(20, rule_y), (CARD_WIDTH - 20, rule_y)], fill=accent_color, width=2)

    # --- Card name (wrapped, centred) ---
    name_lines = wrap_text(name, font_name, CARD_WIDTH - 24, draw)
    y_cursor = 128
    for line in name_lines:
        lb = draw.textbbox((0, 0), line, font=font_name)
        line_w = lb[2] - lb[0]
        draw.text(((CARD_WIDTH - line_w) // 2, y_cursor), line, font=font_name, fill=TEXT_COLOR)
        y_cursor += 18

    # --- Album label ---
    y_cursor += 6
    ab = draw.textbbox((0, 0), album, font=font_album)
    album_w = ab[2] - ab[0]
    draw.text(((CARD_WIDTH - album_w) // 2, y_cursor), album, font=font_album, fill=SUBTEXT_COLOR)
    y_cursor += 18

    # --- Card type label ---
    tb = draw.textbbox((0, 0), card_type, font=font_type)
    type_w = tb[2] - tb[0]
    draw.text(((CARD_WIDTH - type_w) // 2, y_cursor), card_type, font=font_type, fill=SUBTEXT_COLOR)

    # --- Decorative horizontal rule above footer ---
    draw.line(
        [(20, CARD_HEIGHT - 52), (CARD_WIDTH - 20, CARD_HEIGHT - 52)],
        fill=accent_color, width=1,
    )

    # --- Member name repeated in footer (small) ---
    footer_label = f"ITZY · {member}"
    flb = draw.textbbox((0, 0), footer_label, font=font_id)
    footer_w = flb[2] - flb[0]
    draw.text(
        ((CARD_WIDTH - footer_w) // 2, CARD_HEIGHT - 36),
        footer_label, font=font_id, fill=TEXT_COLOR,
    )

    img.save(output_path, "PNG", optimize=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Load JSON
    if not os.path.exists(JSON_FILE):
        sys.exit(f"Error: '{JSON_FILE}' not found. Run this script from the repo root.")

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    cards = data.get("cards", [])
    if not cards:
        sys.exit("Error: No cards found in JSON.")

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    total = len(cards)
    print(f"Generating {total} card images into '{OUTPUT_DIR}/' ...")

    updated = 0
    skipped = 0

    for i, card in enumerate(cards, start=1):
        card_id = card.get("id", f"card_{i}")
        filename = f"{card_id}.png"
        output_path = OUTPUT_DIR / filename
        local_path = f"images/{filename}"

        # Generate image
        try:
            generate_card_image(card, output_path)
        except Exception as exc:
            print(f"  [WARN] Failed to generate {card_id}: {exc}")
            skipped += 1
            continue

        # Update JSON entry to local path
        card["image"] = local_path
        updated += 1

        # Progress indicator every 50 cards
        if i % 50 == 0 or i == total:
            print(f"  [{i}/{total}] {card_id} → {local_path}")

    # Write updated JSON back
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(
        f"\nDone! {updated} images generated, {skipped} skipped.\n"
        f"JSON updated: '{JSON_FILE}'\n"
        f"Images saved to: '{OUTPUT_DIR}/'\n"
        "\nNext steps:\n"
        "  1. Commit the images/ directory and updated JSON to your repo, OR\n"
        "  2. Upload images to a hosting service (e.g. Imgur, Cloudinary) and\n"
        "     re-run with the hosted URLs by replacing the local paths in the JSON."
    )


if __name__ == "__main__":
    main()
