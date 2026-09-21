import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_PATH = Path("generated_images") / "test_preview_card.png"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

def generate_test_banner(
    position="SMM menejer",
    salary="suhbat asosida",
    watermark="@Freelance_uzb"
):
    # 2x supersampling for razor-sharp anti-aliased vectors and typography
    SCALE = 2
    W = 1280 * SCALE
    H = 960 * SCALE

    img = Image.new("RGBA", (W, H), (248, 249, 252, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- 1. FON POLIGONLARI (Och kulrang/oq nafis o'tishlar) ---
    bg_polys = [
        ([(W, 0), (int(W * 0.55), 0), (W, int(H * 0.55))], (243, 245, 249, 255)),
        ([(0, H), (0, int(H * 0.45)), (int(W * 0.55), H)], (241, 246, 248, 255)),
        ([(int(W * 0.45), 0), (int(W * 0.75), 0), (int(W * 0.85), int(H * 0.35))], (246, 242, 245, 255)),
        ([(0, int(H * 0.6)), (int(W * 0.3), int(H * 0.8)), (int(W * 0.15), H)], (236, 247, 248, 255)),
        ([(int(W * 0.2), 0), (int(W * 0.5), 0), (int(W * 0.35), int(H * 0.25))], (245, 247, 250, 255)),
    ]
    for poly, col in bg_polys:
        draw.polygon(poly, fill=col)

    # --- 2. O'NG YUQORI QIZIL-BORDO 3D LOW-POLY KRISTALLAR ---
    red_facets = [
        # O'ng devordan burchak
        ([(W, 0), (W - int(240 * SCALE), 0), (W - int(90 * SCALE), int(170 * SCALE))], (152, 16, 46, 255)),
        ([(W, 0), (W - int(90 * SCALE), int(170 * SCALE)), (W, int(150 * SCALE))], (195, 24, 62, 255)),
        ([(W, int(150 * SCALE)), (W - int(90 * SCALE), int(170 * SCALE)), (W, int(310 * SCALE))], (120, 10, 35, 255)),
        ([(W, int(310 * SCALE)), (W - int(90 * SCALE), int(170 * SCALE)), (W - int(170 * SCALE), int(290 * SCALE))], (216, 36, 75, 255)),
        ([(W, int(310 * SCALE)), (W - int(170 * SCALE), int(290 * SCALE)), (W, int(430 * SCALE))], (138, 14, 40, 255)),
        ([(W - int(240 * SCALE), 0), (W - int(430 * SCALE), 0), (W - int(280 * SCALE), int(140 * SCALE))], (215, 30, 68, 255)),
        ([(W - int(240 * SCALE), 0), (W - int(280 * SCALE), int(140 * SCALE)), (W - int(90 * SCALE), int(170 * SCALE))], (234, 48, 86, 255)),
        ([(W - int(280 * SCALE), int(140 * SCALE)), (W - int(90 * SCALE), int(170 * SCALE)), (W - int(170 * SCALE), int(290 * SCALE))], (172, 16, 50, 255)),
        ([(W - int(430 * SCALE), 0), (W - int(600 * SCALE), 0), (W - int(390 * SCALE), int(130 * SCALE))], (238, 72, 102, 255)),
        ([(W - int(430 * SCALE), 0), (W - int(390 * SCALE), int(130 * SCALE)), (W - int(280 * SCALE), int(140 * SCALE))], (226, 54, 90, 255)),
        ([(W - int(390 * SCALE), int(130 * SCALE)), (W - int(280 * SCALE), int(140 * SCALE)), (W - int(330 * SCALE), int(240 * SCALE))], (244, 110, 136, 240)),
        ([(W - int(280 * SCALE), int(140 * SCALE)), (W - int(170 * SCALE), int(290 * SCALE)), (W - int(330 * SCALE), int(240 * SCALE))], (192, 22, 58, 255)),
        ([(W - int(600 * SCALE), 0), (W - int(720 * SCALE), 0), (W - int(520 * SCALE), int(110 * SCALE))], (247, 160, 178, 160)),
        ([(W - int(600 * SCALE), 0), (W - int(520 * SCALE), int(110 * SCALE)), (W - int(390 * SCALE), int(130 * SCALE))], (242, 125, 148, 200)),
        ([(W - int(390 * SCALE), int(130 * SCALE)), (W - int(520 * SCALE), int(110 * SCALE)), (W - int(450 * SCALE), int(220 * SCALE))], (246, 175, 192, 140)),
        ([(W - int(390 * SCALE), int(130 * SCALE)), (W - int(450 * SCALE), int(220 * SCALE)), (W - int(330 * SCALE), int(240 * SCALE))], (240, 135, 155, 180)),
    ]
    for poly, col in red_facets:
        draw.polygon(poly, fill=col)

    # --- 3. CHAP PASTKI FERUZA / TEAL 3D LOW-POLY KRISTALLAR ---
    teal_facets = [
        ([(0, H), (0, H - int(200 * SCALE)), (int(140 * SCALE), H - int(90 * SCALE))], (0, 102, 112, 255)),
        ([(0, H), (int(140 * SCALE), H - int(90 * SCALE)), (int(180 * SCALE), H)], (0, 146, 156, 255)),
        ([(0, H - int(200 * SCALE)), (0, H - int(350 * SCALE)), (int(100 * SCALE), H - int(250 * SCALE))], (0, 80, 90, 255)),
        ([(0, H - int(200 * SCALE)), (int(100 * SCALE), H - int(250 * SCALE)), (int(140 * SCALE), H - int(90 * SCALE))], (0, 125, 135, 255)),
        ([(int(180 * SCALE), H), (int(140 * SCALE), H - int(90 * SCALE)), (int(310 * SCALE), H - int(70 * SCALE))], (0, 170, 180, 255)),
        ([(int(180 * SCALE), H), (int(310 * SCALE), H - int(70 * SCALE)), (int(370 * SCALE), H)], (18, 185, 195, 255)),
        ([(int(140 * SCALE), H - int(90 * SCALE)), (int(100 * SCALE), H - int(250 * SCALE)), (int(240 * SCALE), H - int(200 * SCALE))], (0, 152, 162, 255)),
        ([(int(140 * SCALE), H - int(90 * SCALE)), (int(240 * SCALE), H - int(200 * SCALE)), (int(310 * SCALE), H - int(70 * SCALE))], (8, 166, 176, 255)),
        ([(0, H - int(350 * SCALE)), (0, H - int(480 * SCALE)), (int(80 * SCALE), H - int(360 * SCALE))], (0, 68, 78, 255)),
        ([(0, H - int(350 * SCALE)), (int(80 * SCALE), H - int(360 * SCALE)), (int(100 * SCALE), H - int(250 * SCALE))], (0, 108, 118, 255)),
        ([(int(100 * SCALE), H - int(250 * SCALE)), (int(240 * SCALE), H - int(200 * SCALE)), (int(210 * SCALE), H - int(320 * SCALE))], (60, 196, 204, 255)),
        ([(int(240 * SCALE), H - int(200 * SCALE)), (int(310 * SCALE), H - int(70 * SCALE)), (int(420 * SCALE), H - int(140 * SCALE))], (78, 206, 214, 255)),
        ([(int(310 * SCALE), H - int(70 * SCALE)), (int(370 * SCALE), H), (int(500 * SCALE), H)], (115, 218, 224, 220)),
        ([(int(310 * SCALE), H - int(70 * SCALE)), (int(500 * SCALE), H), (int(420 * SCALE), H - int(140 * SCALE))], (140, 224, 228, 200)),
        ([(int(80 * SCALE), H - int(360 * SCALE)), (int(100 * SCALE), H - int(250 * SCALE)), (int(160 * SCALE), H - int(410 * SCALE))], (100, 212, 218, 160)),
        ([(int(100 * SCALE), H - int(250 * SCALE)), (int(210 * SCALE), H - int(320 * SCALE)), (int(160 * SCALE), H - int(410 * SCALE))], (135, 222, 228, 170)),
        ([(int(240 * SCALE), H - int(200 * SCALE)), (int(420 * SCALE), H - int(140 * SCALE)), (int(360 * SCALE), H - int(280 * SCALE))], (150, 226, 230, 150)),
    ]
    for poly, col in teal_facets:
        draw.polygon(poly, fill=col)

    # Shriftlar
    font_bold = lambda s: ImageFont.truetype("C:\\Windows\\Fonts\\segoeuib.ttf", s * SCALE)
    font_regular = lambda s: ImageFont.truetype("C:\\Windows\\Fonts\\segoeui.ttf", s * SCALE)
    font_semibold = lambda s: ImageFont.truetype("C:\\Windows\\Fonts\\seguisb.ttf", s * SCALE)

    # --- 4. YUQORI CHAP BURCHAK (FL VAKANSIYA BRENDI) ---
    brand_x = int(75 * SCALE)
    brand_y = int(58 * SCALE)
    badge_size = int(72 * SCALE)

    # Gradientli binafsha-bordo kvadrat badge
    badge_img = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(badge_img)
    for i in range(badge_size):
        ratio = i / badge_size
        r = int(60 + (142 - 60) * ratio)
        g = int(14 + (18 - 14) * ratio)
        b = int(72 + (54 - 72) * ratio)
        b_draw.line([(0, i), (badge_size, i)], fill=(r, g, b, 255))

    mask = Image.new("L", (badge_size, badge_size), 0)
    m_draw = ImageDraw.Draw(mask)
    m_draw.rounded_rectangle([0, 0, badge_size, badge_size], radius=int(18 * SCALE), fill=255)
    badge_rounded = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
    badge_rounded.paste(badge_img, (0, 0), mask)

    # Ichida oq rangda "FL"
    fl_draw = ImageDraw.Draw(badge_rounded)
    fl_font = font_bold(32)
    fl_bbox = fl_draw.textbbox((0, 0), "FL", font=fl_font)
    fl_w = fl_bbox[2] - fl_bbox[0]
    fl_h = fl_bbox[3] - fl_bbox[1]
    fl_draw.text(
        ((badge_size - fl_w) // 2, (badge_size - fl_h) // 2 - int(3 * SCALE)),
        "FL",
        fill=(255, 255, 255, 255),
        font=fl_font
    )
    img.paste(badge_rounded, (brand_x, brand_y), badge_rounded)

    # Yonidagi "VAKANSIYA" so'zi
    vak_font = font_bold(33)
    vak_text = "VAKANSIYA"
    # Harflar orasi biroz ochiq qilib chizamiz
    vak_x = brand_x + badge_size + int(20 * SCALE)
    vak_y = brand_y + int(16 * SCALE)
    draw.text((vak_x, vak_y), vak_text, fill=(115, 22, 44, 255), font=vak_font)

    # --- 5. MARKAZIY KARTA (WHITE FLOATING CARD) VA YUMSHOQ SOYA ---
    card_w = int(980 * SCALE)
    card_h = int(630 * SCALE)
    card_x = (W - card_w) // 2
    card_y = int(165 * SCALE)
    card_radius = int(38 * SCALE)

    # Soft ambient drop shadow
    shadow_pad = int(50 * SCALE)
    shadow_img = Image.new("RGBA", (card_w + shadow_pad * 2, card_h + shadow_pad * 2), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_img)
    s_draw.rounded_rectangle(
        [shadow_pad, shadow_pad + int(14 * SCALE), shadow_pad + card_w, shadow_pad + card_h + int(14 * SCALE)],
        radius=card_radius,
        fill=(10, 30, 50, 32)
    )
    shadow_blurred = shadow_img.filter(ImageFilter.GaussianBlur(radius=int(26 * SCALE)))
    img.paste(shadow_blurred, (card_x - shadow_pad, card_y - shadow_pad), shadow_blurred)

    # Oq karta
    card_img = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(card_img)
    c_draw.rounded_rectangle(
        [0, 0, card_w - 1, card_h - 1],
        radius=card_radius,
        fill=(255, 255, 255, 255),
        outline=(238, 242, 247, 255),
        width=int(1.5 * SCALE)
    )
    img.paste(card_img, (card_x, card_y), card_img)

    # --- 6. KARTA ICHIDAGI 3D TAQDIMOT DOSKASI BADGE'I ---
    badge_cx = W // 2
    badge_cy = card_y + int(108 * SCALE)
    b_rad = int(54 * SCALE)

    # Qatlamli kumush/oq doira (soft bevel effect)
    draw.ellipse(
        [badge_cx - b_rad, badge_cy - b_rad, badge_cx + b_rad, badge_cy + b_rad],
        fill=(232, 236, 244, 255)
    )
    draw.ellipse(
        [badge_cx - (b_rad - int(3 * SCALE)), badge_cy - (b_rad - int(3 * SCALE)), badge_cx + (b_rad - int(3 * SCALE)), badge_cy + (b_rad - int(3 * SCALE))],
        fill=(244, 247, 251, 255)
    )
    draw.ellipse(
        [badge_cx - (b_rad - int(6 * SCALE)), badge_cy - (b_rad - int(6 * SCALE)), badge_cx + (b_rad - int(6 * SCALE)), badge_cy + (b_rad - int(6 * SCALE))],
        fill=(255, 255, 255, 255)
    )

    # Doska (Presentation Flipchart / Stand)
    bw, bh = int(48 * SCALE), int(36 * SCALE)
    bx = badge_cx - bw // 2
    by = badge_cy - bh // 2 - int(4 * SCALE)

    # Doska orqa soyasi / ramkasi
    draw.rounded_rectangle(
        [bx, by, bx + bw, by + bh],
        radius=int(4 * SCALE),
        fill=(255, 255, 255, 255),
        outline=(156, 163, 175, 255),
        width=int(2 * SCALE)
    )
    # Tepasidagi qisqich (clip)
    draw.line([(bx + int(14 * SCALE), by), (bx + int(34 * SCALE), by)], fill=(107, 114, 128, 255), width=int(2.5 * SCALE))

    # Diagramma ustunlari
    bar_bottom = by + bh - int(4 * SCALE)
    # Ustun 1: Feruza
    draw.rectangle([bx + int(8 * SCALE), by + int(18 * SCALE), bx + int(14 * SCALE), bar_bottom], fill=(14, 148, 150, 255))
    # Ustun 2: Oltin / to'q sariq
    draw.rectangle([bx + int(17 * SCALE), by + int(12 * SCALE), bx + int(23 * SCALE), bar_bottom], fill=(234, 138, 0, 255))
    # Ustun 3: Moviy
    draw.rectangle([bx + int(26 * SCALE), by + int(8 * SCALE), bx + int(32 * SCALE), bar_bottom], fill=(37, 99, 235, 255))
    # Ustun 4: Yashil
    draw.rectangle([bx + int(35 * SCALE), by + int(14 * SCALE), bx + int(41 * SCALE), bar_bottom], fill=(34, 197, 94, 255))

    # Trend chizig'i (qizil)
    draw.line(
        [(bx + int(11 * SCALE), by + int(16 * SCALE)),
         (bx + int(20 * SCALE), by + int(10 * SCALE)),
         (bx + int(29 * SCALE), by + int(6 * SCALE)),
         (bx + int(38 * SCALE), by + int(12 * SCALE))],
        fill=(225, 29, 72, 255),
        width=int(2 * SCALE)
    )

    # Tripod oyoqchalari (3 ta)
    tripod_top_y = by + bh + int(1 * SCALE)
    tripod_bottom_y = by + bh + int(14 * SCALE)
    draw.line([(bx + int(8 * SCALE), tripod_top_y), (bx - int(3 * SCALE), tripod_bottom_y)], fill=(156, 163, 175, 255), width=int(2.5 * SCALE))
    draw.line([(badge_cx, tripod_top_y), (badge_cx, tripod_bottom_y)], fill=(156, 163, 175, 255), width=int(2.5 * SCALE))
    draw.line([(bx + bw - int(8 * SCALE), tripod_top_y), (bx + bw + int(3 * SCALE), tripod_bottom_y)], fill=(156, 163, 175, 255), width=int(2.5 * SCALE))

    # --- 7. LAVOZIM NOMI (SARLAVHA) ---
    pos_font = font_bold(54)
    p_bbox = draw.textbbox((0, 0), position, font=pos_font)
    pw = p_bbox[2] - p_bbox[0]
    curr_y = card_y + int(208 * SCALE)
    draw.text(((W - pw) // 2, curr_y), position, fill=(136, 18, 46, 255), font=pos_font)

    # --- 8. MAOSH BLOKI (2-rasmdagi kabi 1:1) ---
    maosh_label = "Maosh:"
    label_font = font_regular(27)
    l_bbox = draw.textbbox((0, 0), maosh_label, font=label_font)
    lw = l_bbox[2] - l_bbox[0]
    curr_y += int(86 * SCALE)
    draw.text(((W - lw) // 2, curr_y), maosh_label, fill=(71, 85, 105, 255), font=label_font)

    # Maosh qiymati: KATTA, QALIN, TO'Q FERUZA / TEAL
    sal_font = font_bold(52)
    s_bbox = draw.textbbox((0, 0), salary, font=sal_font)
    sw = s_bbox[2] - s_bbox[0]
    curr_y += int(46 * SCALE)
    draw.text(((W - sw) // 2, curr_y), salary, fill=(0, 126, 138, 255), font=sal_font)

    # Tagidagi nozik vertikal chiziqcha
    sep_y1 = curr_y + int(82 * SCALE)
    sep_y2 = sep_y1 + int(42 * SCALE)
    draw.line([(W // 2, sep_y1), (W // 2, sep_y2)], fill=(195, 205, 215, 255), width=int(2 * SCALE))

    # --- 9. PASTKI O'NG WATERMARK ---
    wm_font = font_bold(25)
    w_bbox = draw.textbbox((0, 0), watermark, font=wm_font)
    ww = w_bbox[2] - w_bbox[0]
    wm_x = W - int(80 * SCALE) - ww
    wm_y = H - int(72 * SCALE)
    draw.text((wm_x, wm_y), watermark, fill=(0, 126, 138, 255), font=wm_font)

    # 2x supersamplingdan so'ng 1280x960 ga yuqori sifatli LANCZOS filter bilan tushiramiz
    final_img = img.resize((1280, 960), Image.LANCZOS)
    final_img.convert("RGB").save(str(OUTPUT_PATH), "PNG", quality=98)
    print(f"Rasm yaratildi: {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_test_banner()
