import os
import math
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.bot.config import BASE_DIR, settings

OUTPUT_DIR = BASE_DIR / "generated_images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR = BASE_DIR / "src" / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
ICONS_DIR = ASSETS_DIR / "icons"


class CardDesignConfig:
    WIDTH = 1200
    HEIGHT = 1040

    # Brend Ranglar Palitrasi (Zamonaviy va boy)
    BG_COLOR = (248, 249, 252)              # Soft off-white / light slate
    PRIMARY_BURGUNDY = (180, 28, 70)        # Deep burgundy / raspberry
    SECONDARY_TEAL = (14, 148, 150)         # Modern vibrant teal
    DARK_TEXT = (26, 32, 44)                # Deep slate/charcoal
    MUTED_TEXT = (100, 116, 139)            # Slate gray
    WHITE = (255, 255, 255)
    CARD_BG = (255, 255, 255)
    CARD_BORDER = (226, 232, 240)
    BADGE_BG = (237, 242, 247)
    SALARY_GREEN = (22, 163, 74)            # Emerald green


class ImageGenerator:
    def __init__(self):
        self.fonts = self._load_fonts()

    def _get_font(self, font_name: str, size: int) -> ImageFont.FreeTypeFont:
        # 1. Loyiha ichidagi fonts papkasidan tekshirish
        custom_font_path = FONTS_DIR / font_name
        if custom_font_path.exists():
            try:
                return ImageFont.truetype(str(custom_font_path), size)
            except Exception:
                pass

        # 2. Windows tizim shriftlaridan tekshirish
        windows_font_candidates = [
            "C:\\Windows\\Fonts\\segoeuib.ttf" if "bold" in font_name.lower() else "C:\\Windows\\Fonts\\segoeui.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf" if "bold" in font_name.lower() else "C:\\Windows\\Fonts\\arial.ttf",
            "C:\\Windows\\Fonts\\calibrib.ttf" if "bold" in font_name.lower() else "C:\\Windows\\Fonts\\calibri.ttf",
        ]
        for path in windows_font_candidates:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue

        # 3. Default fallback
        return ImageFont.load_default()

    def _load_fonts(self):
        return {
            "title_bold": lambda size: self._get_font("segoeuib.ttf", size),
            "regular": lambda size: self._get_font("segoeui.ttf", size),
        }

    def _draw_geometric_background(self, draw: ImageDraw.ImageDraw, width: int, height: int):
        """TZ 6-bo'limga mos geometrik fon elementlari (bordo va teal aksentlar)."""
        # Yuqori chap / o'ng geometrik burchaklar
        # Yuqori o'ng bordo uchburchak / poligon
        poly1 = [(width - 450, 0), (width, 0), (width, 380)]
        draw.polygon(poly1, fill=(180, 28, 70, 230))

        poly1_sub = [(width - 250, 0), (width, 0), (width, 180)]
        draw.polygon(poly1_sub, fill=(215, 45, 90, 180))

        # Pastki chap teal geometrik burchaklar
        poly2 = [(0, height - 380), (0, height), (420, height)]
        draw.polygon(poly2, fill=(14, 148, 150, 230))

        poly2_sub = [(0, height - 200), (0, height), (220, height)]
        draw.polygon(poly2_sub, fill=(20, 184, 166, 180))

        # Kichik zamonaviy doira aksentlar
        draw.ellipse([width - 120, 420, width - 80, 460], fill=(14, 148, 150, 80))
        draw.ellipse([80, height - 440, 130, height - 390], fill=(180, 28, 70, 80))

    def _draw_category_badge(
        self,
        draw: ImageDraw.ImageDraw,
        center_x: int,
        center_y: int,
        radius: int,
        category_name: str,
    ):
        """Markaziy doira ichidagi chiroyli kategoriya belgisi."""
        # Tashqi doira
        box = [center_x - radius, center_y - radius, center_x + radius, center_y + radius]
        draw.ellipse(box, fill=(238, 242, 255), outline=(199, 210, 254), width=3)

        # Ichki doira
        inner_r = radius - 12
        inner_box = [center_x - inner_r, center_y - inner_r, center_x + inner_r, center_y + inner_r]
        draw.ellipse(inner_box, fill=(79, 70, 229))  # Indigo / Royal blue

        # Kategoriya bosh harflari (masalan IT, SO, HA, OS va h.k.)
        short_code = ""
        words = category_name.split()
        if len(words) >= 2:
            short_code = (words[0][0] + words[1][0]).upper()
        elif len(category_name) >= 2:
            short_code = category_name[:2].upper()
        else:
            short_code = category_name.upper()

        font = self.fonts["title_bold"](int(radius * 0.75))
        bbox = draw.textbbox((0, 0), short_code, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((center_x - tw // 2, center_y - th // 2 - 4), short_code, fill=CardDesignConfig.WHITE, font=font)

    def _wrap_and_fit_text(
        self,
        text: str,
        max_width: int,
        max_height: int,
        base_size: int = 54,
        min_size: int = 34,
    ) -> Tuple[list, ImageFont.FreeTypeFont]:
        """Matnni karta kengligiga moslab qatorlarga bo'ladi va shriftni kerak bo'lsa kichraytiradi."""
        current_size = base_size
        while current_size >= min_size:
            font = self.fonts["title_bold"](current_size)
            words = text.split()
            lines = []
            current_line = []

            for word in words:
                test_line = " ".join(current_line + [word])
                dummy_img = Image.new("RGB", (1, 1))
                d = ImageDraw.Draw(dummy_img)
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

            total_h = len(lines) * (current_size * 1.3)
            if total_h <= max_height and len(lines) <= 3:
                return lines, font

            current_size -= 4

        return lines[:3], self.fonts["title_bold"](min_size)

    def generate_job_card(
        self,
        position: str,
        company: str,
        salary: str,
        category_name: str = "Vakansiya",
        channel_watermark: str = "@freelance_uzb",
        output_filename: Optional[str] = None,
    ) -> str:
        """
        1200x1040 px o'lchamdagi professional vakansiya kartasini chizadi va saqlaydi.
        """
        width = CardDesignConfig.WIDTH
        height = CardDesignConfig.HEIGHT

        # 1. Asosiy canvas
        image = Image.new("RGBA", (width, height), CardDesignConfig.BG_COLOR)
        draw = ImageDraw.Draw(image, "RGBA")

        # 2. Geometrik brend fon
        self._draw_geometric_background(draw, width, height)

        # 3. Markaziy oq karta
        card_w, card_h = 960, 660
        card_x = (width - card_w) // 2
        card_y = (height - card_h) // 2

        # Karta soyasi
        shadow_box = [card_x + 6, card_y + 10, card_x + card_w + 6, card_y + card_h + 10]
        draw.rounded_rectangle(shadow_box, radius=32, fill=(0, 0, 0, 20))

        # Karta foni
        card_box = [card_x, card_y, card_x + card_w, card_y + card_h]
        draw.rounded_rectangle(card_box, radius=32, fill=CardDesignConfig.CARD_BG, outline=CardDesignConfig.CARD_BORDER, width=2)

        # 4. Yuqori chap brend belgisi (Header Badge)
        brand_badge_box = [card_x, 60, card_x + 200, 115]
        draw.rounded_rectangle(brand_badge_box, radius=14, fill=CardDesignConfig.PRIMARY_BURGUNDY)
        badge_font = self.fonts["title_bold"](26)
        draw.text((card_x + 22, 73), "VAKANSIYA", fill=CardDesignConfig.WHITE, font=badge_font)

        # Kategoriya kichik tegi
        cat_font = self.fonts["title_bold"](24)
        draw.text((card_x + 225, 75), f"|  {category_name}", fill=CardDesignConfig.MUTED_TEXT, font=cat_font)

        # 5. Karta ichidagi Kategoriya Ikonkasi (Badge)
        badge_center_x = width // 2
        badge_center_y = card_y + 85
        self._draw_category_badge(draw, badge_center_x, badge_center_y, radius=52, category_name=category_name)

        # 6. Lavozim Nomi (Katta, qalin, markazda)
        lines, pos_font = self._wrap_and_fit_text(
            position,
            max_width=card_w - 120,
            max_height=180,
            base_size=52,
            min_size=34
        )

        curr_y = card_y + 175
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=pos_font)
            lw = bbox[2] - bbox[0]
            draw.text(((width - lw) // 2, curr_y), line, fill=CardDesignConfig.PRIMARY_BURGUNDY, font=pos_font)
            curr_y += int(pos_font.size * 1.25)

        # 7. Kompaniya nomi
        company_clean = f"Kompaniya: {company.strip()}"
        comp_font = self.fonts["title_bold"](32)
        c_bbox = draw.textbbox((0, 0), company_clean, font=comp_font)
        cw = c_bbox[2] - c_bbox[0]
        draw.text(((width - cw) // 2, curr_y + 15), company_clean, fill=CardDesignConfig.DARK_TEXT, font=comp_font)

        # 8. Ajratuvchi chiziq (Divider)
        div_y = curr_y + 75
        draw.line([(card_x + 120, div_y), (card_x + card_w - 120, div_y)], fill=(241, 245, 249), width=2)

        # 9. Maosh Bloki (Zamonaviy yashil kapsula / badge)
        salary_text = salary.strip() if salary.strip() else "Kelishiladi"
        salary_label = f"Maosh: {salary_text}"
        sal_font = self.fonts["title_bold"](34)
        s_bbox = draw.textbbox((0, 0), salary_label, font=sal_font)
        sw = s_bbox[2] - s_bbox[0]
        sh = s_bbox[3] - s_bbox[1]

        capsule_padding_x = 45
        capsule_padding_y = 16
        capsule_w = sw + capsule_padding_x * 2
        capsule_h = sh + capsule_padding_y * 2
        capsule_x = (width - capsule_w) // 2
        capsule_y = div_y + 35

        draw.rounded_rectangle(
            [capsule_x, capsule_y, capsule_x + capsule_w, capsule_y + capsule_h],
            radius=20,
            fill=(240, 253, 244),
            outline=(187, 247, 208),
            width=2
        )
        draw.text(
            (capsule_x + capsule_padding_x, capsule_y + capsule_padding_y - 3),
            salary_label,
            fill=CardDesignConfig.SALARY_GREEN,
            font=sal_font
        )

        # 10. Pastki o'ng burchak Watermark (Kanal username)
        watermark_text = channel_watermark if channel_watermark.startswith("@") else f"@{channel_watermark}"
        wm_font = self.fonts["title_bold"](26)
        wm_bbox = draw.textbbox((0, 0), watermark_text, font=wm_font)
        wm_w = wm_bbox[2] - wm_bbox[0]
        draw.text((card_x + card_w - wm_w, height - 70), watermark_text, fill=CardDesignConfig.MUTED_TEXT, font=wm_font)

        # Pastki chap: "Rasmiy e'lon kanali"
        info_font = self.fonts["title_bold"](22)
        draw.text((card_x + 80, height - 70), "Rasmiy Ish va Vakansiyalar Boti", fill=CardDesignConfig.MUTED_TEXT, font=info_font)

        # Faylni saqlash
        if not output_filename:
            import uuid
            output_filename = f"job_card_{uuid.uuid4().hex[:10]}.png"

        save_path = OUTPUT_DIR / output_filename
        image.convert("RGB").save(str(save_path), format="PNG", quality=95)
        return str(save_path)


# Singleton
image_generator = ImageGenerator()
