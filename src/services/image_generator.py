import os
import math
from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.bot.config import BASE_DIR, settings

OUTPUT_DIR = BASE_DIR / "generated_images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR = BASE_DIR / "src" / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"


class ImageGenerator:
    """
    2-rasm namunasi bilan 1:1 nisbatda, ultra-zamonaviy,
    kristal low-poly fasetli va floating card uslubidagi banner generatori.
    2x Supersampling (antialiasing) bilan ishlaydi.
    """
    WIDTH = 1280
    HEIGHT = 960

    def __init__(self):
        self._font_cache = {}

    def _get_font(self, font_type: str, size: int) -> ImageFont.FreeTypeFont:
        key = (font_type, size)
        if key in self._font_cache:
            return self._font_cache[key]

        font_map = {
            "bold": [
                str(FONTS_DIR / "bold.ttf"),
                "C:\\Windows\\Fonts\\segoeuib.ttf",
                "C:\\Windows\\Fonts\\arialbd.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            ],
            "regular": [
                str(FONTS_DIR / "regular.ttf"),
                "C:\\Windows\\Fonts\\segoeui.ttf",
                "C:\\Windows\\Fonts\\arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            ],
            "semibold": [
                str(FONTS_DIR / "semibold.ttf"),
                "C:\\Windows\\Fonts\\seguisb.ttf",
                "C:\\Windows\\Fonts\\segoeuib.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            ],
        }

        candidates = font_map.get(font_type, font_map["regular"])
        for path in candidates:
            if os.path.exists(path):
                try:
                    f = ImageFont.truetype(path, size)
                    self._font_cache[key] = f
                    return f
                except Exception:
                    continue

        try:
            fallback = ImageFont.truetype("DejaVuSans.ttf", size)
        except Exception:
            fallback = ImageFont.load_default()
        self._font_cache[key] = fallback
        return fallback

    def _wrap_and_fit_text(
        self,
        text: str,
        max_width: int,
        max_height: int,
        scale: int = 2,
        base_size: int = 54,
        min_size: int = 34,
    ) -> Tuple[List[str], ImageFont.FreeTypeFont]:
        """Matnni karta kengligiga moslab chiroyli qatorlarga bo'ladi."""
        current_size = base_size
        while current_size >= min_size:
            font = self._get_font("bold", current_size * scale)
            words = text.split()
            lines = []
            current_line = []

            for word in words:
                test_line = " ".join(current_line + [word])
                dummy = Image.new("RGB", (1, 1))
                d = ImageDraw.Draw(dummy)
                bbox = d.textbbox((0, 0), test_line, font=font)
                w = bbox[2] - bbox[0]

                if w <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                        current_line = []
            if current_line:
                lines.append(" ".join(current_line))

            total_h = len(lines) * (current_size * scale * 1.25)
            if total_h <= max_height and len(lines) <= 2:
                return lines, font

            current_size -= 4

        return lines[:2], self._get_font("bold", min_size * scale)

    def generate_job_card(
        self,
        position: str,
        company: str,
        salary: str,
        category_name: str = "Vakansiya",
        badge_text: str = "VAKANSIYA",
        price_label: str = "Maosh:",
        channel_watermark: str = "@freelance_uzb",
        output_filename: Optional[str] = None,
    ) -> str:
        """
        2-rasm namunasi bilan 1:1 o'xshash, 1280x960 px o'lchamdagi
        professional vakansiya kartasini chizadi va saqlaydi.
        """
        SCALE = 2
        W = self.WIDTH * SCALE
        H = self.HEIGHT * SCALE

        # 1. Asosiy fon
        img = Image.new("RGBA", (W, H), (248, 249, 252, 255))
        draw = ImageDraw.Draw(img, "RGBA")

        # Orqa fondagi juda nafis geometrik uchburchaklar
        bg_polys = [
            ([(W, 0), (int(W * 0.55), 0), (W, int(H * 0.55))], (243, 245, 249, 255)),
            ([(0, H), (0, int(H * 0.45)), (int(W * 0.55), H)], (241, 246, 248, 255)),
            ([(int(W * 0.45), 0), (int(W * 0.75), 0), (int(W * 0.85), int(H * 0.35))], (246, 242, 245, 255)),
            ([(0, int(H * 0.6)), (int(W * 0.3), int(H * 0.8)), (int(W * 0.15), H)], (236, 247, 248, 255)),
            ([(int(W * 0.2), 0), (int(W * 0.5), 0), (int(W * 0.35), int(H * 0.25))], (245, 247, 250, 255)),
        ]
        for poly, col in bg_polys:
            draw.polygon(poly, fill=col)

        # 2. O'ng yuqori qizil-bordo 3D low-poly kristal fasetlari
        red_facets = [
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

        # 3. Chap pastki feruza / teal 3D low-poly kristal fasetlari
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

        # 4. Yuqori chap burchak (FL VAKANSIYA brendi)
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

        # "FL" yozuvi
        fl_font = self._get_font("bold", int(32 * SCALE))
        fl_bbox = b_draw.textbbox((0, 0), "FL", font=fl_font)
        fl_w = fl_bbox[2] - fl_bbox[0]
        fl_h = fl_bbox[3] - fl_bbox[1]
        fl_d = ImageDraw.Draw(badge_rounded)
        fl_d.text(
            ((badge_size - fl_w) // 2, (badge_size - fl_h) // 2 - int(3 * SCALE)),
            "FL",
            fill=(255, 255, 255, 255),
            font=fl_font
        )
        img.paste(badge_rounded, (brand_x, brand_y), badge_rounded)

        # Badge matni (VAKANSIYA yoki REZYUME)
        vak_font = self._get_font("bold", int(33 * SCALE))
        vak_x = brand_x + badge_size + int(20 * SCALE)
        vak_y = brand_y + int(16 * SCALE)
        draw.text((vak_x, vak_y), badge_text.upper(), fill=(115, 22, 44, 255), font=vak_font)

        # 5. Markaziy karta (White Floating Card)
        card_w = int(980 * SCALE)
        card_h = int(630 * SCALE)
        card_x = (W - card_w) // 2
        card_y = int(165 * SCALE)
        card_radius = int(38 * SCALE)

        # Yumshoq tarqaluvchan ambient drop-shadow
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

        # 6. Karta ichidagi 3D taqdimot doskasi (Presentation Flipchart Stand)
        badge_cx = W // 2
        badge_cy = card_y + int(108 * SCALE)
        b_rad = int(54 * SCALE)

        draw.ellipse([badge_cx - b_rad, badge_cy - b_rad, badge_cx + b_rad, badge_cy + b_rad], fill=(232, 236, 244, 255))
        draw.ellipse([badge_cx - (b_rad - int(3 * SCALE)), badge_cy - (b_rad - int(3 * SCALE)), badge_cx + (b_rad - int(3 * SCALE)), badge_cy + (b_rad - int(3 * SCALE))], fill=(244, 247, 251, 255))
        draw.ellipse([badge_cx - (b_rad - int(6 * SCALE)), badge_cy - (b_rad - int(6 * SCALE)), badge_cx + (b_rad - int(6 * SCALE)), badge_cy + (b_rad - int(6 * SCALE))], fill=(255, 255, 255, 255))

        bw, bh = int(48 * SCALE), int(36 * SCALE)
        bx = badge_cx - bw // 2
        by = badge_cy - bh // 2 - int(4 * SCALE)

        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=int(4 * SCALE), fill=(255, 255, 255, 255), outline=(156, 163, 175, 255), width=int(2 * SCALE))
        draw.line([(bx + int(14 * SCALE), by), (bx + int(34 * SCALE), by)], fill=(107, 114, 128, 255), width=int(2.5 * SCALE))

        bar_bottom = by + bh - int(4 * SCALE)
        draw.rectangle([bx + int(8 * SCALE), by + int(18 * SCALE), bx + int(14 * SCALE), bar_bottom], fill=(14, 148, 150, 255))
        draw.rectangle([bx + int(17 * SCALE), by + int(12 * SCALE), bx + int(23 * SCALE), bar_bottom], fill=(234, 138, 0, 255))
        draw.rectangle([bx + int(26 * SCALE), by + int(8 * SCALE), bx + int(32 * SCALE), bar_bottom], fill=(37, 99, 235, 255))
        draw.rectangle([bx + int(35 * SCALE), by + int(14 * SCALE), bx + int(41 * SCALE), bar_bottom], fill=(34, 197, 94, 255))

        draw.line(
            [(bx + int(11 * SCALE), by + int(16 * SCALE)),
             (bx + int(20 * SCALE), by + int(10 * SCALE)),
             (bx + int(29 * SCALE), by + int(6 * SCALE)),
             (bx + int(38 * SCALE), by + int(12 * SCALE))],
            fill=(225, 29, 72, 255),
            width=int(2 * SCALE)
        )

        tripod_top_y = by + bh + int(1 * SCALE)
        tripod_bottom_y = by + bh + int(14 * SCALE)
        draw.line([(bx + int(8 * SCALE), tripod_top_y), (bx - int(3 * SCALE), tripod_bottom_y)], fill=(156, 163, 175, 255), width=int(2.5 * SCALE))
        draw.line([(badge_cx, tripod_top_y), (badge_cx, tripod_bottom_y)], fill=(156, 163, 175, 255), width=int(2.5 * SCALE))
        draw.line([(bx + bw - int(8 * SCALE), tripod_top_y), (bx + bw + int(3 * SCALE), tripod_bottom_y)], fill=(156, 163, 175, 255), width=int(2.5 * SCALE))

        # 7. Lavozim Nomi (Sarlavha)
        lines, pos_font = self._wrap_and_fit_text(
            position.strip(),
            max_width=card_w - int(120 * SCALE),
            max_height=int(140 * SCALE),
            scale=SCALE,
            base_size=54,
            min_size=36
        )
        curr_y = card_y + int(208 * SCALE)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=pos_font)
            lw = bbox[2] - bbox[0]
            draw.text(((W - lw) // 2, curr_y), line, fill=(136, 18, 46, 255), font=pos_font)
            curr_y += int(pos_font.size * 1.18)

        # 8. Maosh / Narx Bloki (2-rasm bilan 1:1)
        maosh_label = price_label
        label_font = self._get_font("regular", int(27 * SCALE))
        l_bbox = draw.textbbox((0, 0), maosh_label, font=label_font)
        lw = l_bbox[2] - l_bbox[0]
        curr_y += int(20 * SCALE)
        draw.text(((W - lw) // 2, curr_y), maosh_label, fill=(71, 85, 105, 255), font=label_font)

        # Maosh qiymati: KATTA, QALIN, TO'Q FERUZA
        salary_clean = salary.strip() if salary.strip() else "Kelishiladi"
        # Agar "kelishiladi" bo'lsa "suhbat asosida" yoki "kelishiladi"
        sal_font = self._get_font("bold", int(50 * SCALE))
        s_bbox = draw.textbbox((0, 0), salary_clean, font=sal_font)
        sw = s_bbox[2] - s_bbox[0]

        # Agar maosh matni juda uzun bo'lsa shriftni moslash
        if sw > card_w - int(120 * SCALE):
            sal_font = self._get_font("bold", int(38 * SCALE))
            s_bbox = draw.textbbox((0, 0), salary_clean, font=sal_font)
            sw = s_bbox[2] - s_bbox[0]

        curr_y += int(46 * SCALE)
        draw.text(((W - sw) // 2, curr_y), salary_clean, fill=(0, 126, 138, 255), font=sal_font)

        # Nozik vertikal ajratuvchi chiziqcha
        sep_y1 = curr_y + int(76 * SCALE)
        sep_y2 = sep_y1 + int(42 * SCALE)
        draw.line([(W // 2, sep_y1), (W // 2, sep_y2)], fill=(195, 205, 215, 255), width=int(2 * SCALE))

        # 9. Pastki o'ngdagi Watermark
        wm_clean = channel_watermark if channel_watermark.startswith("@") else f"@{channel_watermark}"
        wm_font = self._get_font("bold", int(25 * SCALE))
        w_bbox = draw.textbbox((0, 0), wm_clean, font=wm_font)
        ww = w_bbox[2] - w_bbox[0]
        wm_x = W - int(80 * SCALE) - ww
        wm_y = H - int(72 * SCALE)
        draw.text((wm_x, wm_y), wm_clean, fill=(0, 126, 138, 255), font=wm_font)

        # 10. 2x supersamplingdan 1280x960 ga yuqori aniqlikda tushirish
        final_img = img.resize((self.WIDTH, self.HEIGHT), Image.LANCZOS)

        if not output_filename:
            import uuid
            output_filename = f"job_card_{uuid.uuid4().hex[:10]}.png"

        save_path = OUTPUT_DIR / output_filename
        final_img.convert("RGB").save(str(save_path), format="PNG", quality=98)
        return str(save_path)


# Singleton
image_generator = ImageGenerator()
