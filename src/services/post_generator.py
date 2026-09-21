import re
from typing import Optional


class PostGenerator:
    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        cleaned = text.strip()
        return cleaned if cleaned else None

    @staticmethod
    def format_title_case(text: Optional[str]) -> Optional[str]:
        """
        Kompaniya nomi yoki Ism-familiyaning har bir so'zi bosh harfini katta (Title Case) qiladi.
        IT, LLC, MCHJ, HR kabi qisqartmalarni saqlab qoladi.
        """
        if not text:
            return text
        words = text.strip().split()
        capitalized_words = []
        for w in words:
            if w.isupper() and len(w) <= 5:
                capitalized_words.append(w)
            else:
                capitalized_words.append(w.capitalize())
        return " ".join(capitalized_words)

    @classmethod
    def format_contact_lines(cls, contact: Optional[str], telegram_user: Optional[str]) -> list[str]:
        """
        Aloqa ma'lumotlarini to'g'ri, takrorlanishlarsiz formatlaydi.
        Agar contact ichida @username bo'lsa, uni ajratib oladi va alohida qatorga qo'yadi.
        Username hech qachon 2 marta takrorlanmaydi.
        """
        cnt = cls.clean_text(contact) or ""
        tg = cls.clean_text(telegram_user) or ""

        # Contact ichidan @username ni aniqlash
        extracted_tg = None
        match = re.search(r"@([A-Za-z0-9_]{3,})", cnt)
        if match:
            extracted_tg = match.group(1)
            # Contact ichidan @username qismini olib tashlash
            cnt = re.sub(r",?\s*@[A-Za-z0-9_]{3,}", "", cnt).strip(" ,|")

        final_tg = extracted_tg or (tg.lstrip("@").strip() if tg else None)

        lines = []
        if cnt:
            lines.append(f"📍 Aloqa: {cnt}")
            if final_tg:
                lines.append(f"@{final_tg}")
        elif final_tg:
            lines.append(f"📍 Aloqa: @{final_tg}")
        else:
            lines.append("📍 Aloqa: Ko'rsatilmagan")

        return lines

    @staticmethod
    def format_salary_amount(raw_text: str, currency: Optional[str] = None) -> str:
        """
        Maosh yoki xizmat narxini UZS/USD valyutalari bilan chiroyli formatlaydi.
        Masalan:
        - "5000000", "UZS" -> "5 000 000 UZS"
        - "800 - 1200", "USD" -> "800 - 1 200 USD"
        - "1000$" -> "1 000 USD"
        - "7000000 so'm" -> "7 000 000 UZS"
        """
        text = raw_text.strip()
        if text.lower() in ("kelishiladi", "kelishamiz", "suhbat asosida"):
            return "Kelishiladi"

        # Agar foydalanuvchi matn ichida $ yoki USD deb yozgan bo'lsa
        if "$" in text or "usd" in text.lower():
            clean = text.replace("$", "").replace("USD", "").replace("usd", "").strip()
            # Raqamlarni probel bilan ajratish
            if "-" in clean:
                p = [x.strip() for x in clean.split("-")]
                return f"{p[0]} - {p[1]} USD"
            digits = clean.replace(" ", "")
            if digits.isdigit():
                return f"{int(digits):,}".replace(",", " ") + " USD"
            return f"{clean} USD"

        # Agar foydalanuvchi so'm yoki sum deb yozgan bo'lsa
        if "so'm" in text.lower() or "som" in text.lower() or "uzs" in text.lower():
            clean = re.sub(r"(so'm|som|uzs)", "", text, flags=re.IGNORECASE).strip()
            if "-" in clean:
                p = [x.strip() for x in clean.split("-")]
                return f"{p[0]} - {p[1]} UZS"
            digits = clean.replace(" ", "")
            if digits.isdigit():
                return f"{int(digits):,}".replace(",", " ") + " UZS"
            return f"{clean} UZS"

        # Agar valyuta tugmasi bosilgan bo'lsa (UZS yoki USD)
        if currency:
            curr_upper = currency.upper()
            if "-" in text:
                parts = [p.strip() for p in text.split("-")]
                formatted_parts = []
                for p in parts:
                    digits_only = p.replace(" ", "")
                    if digits_only.isdigit():
                        formatted_parts.append(f"{int(digits_only):,}".replace(",", " "))
                    else:
                        formatted_parts.append(p)
                return f"{' - '.join(formatted_parts)} {curr_upper}"

            digits_only = text.replace(" ", "")
            if digits_only.isdigit():
                return f"{int(digits_only):,}".replace(",", " ") + f" {curr_upper}"

            return f"{text} {curr_upper}"

        # Agar valyuta belgilanmagan bo'lsa
        digits_only = text.replace(" ", "")
        if digits_only.isdigit():
            num = int(digits_only)
            if num >= 100000:
                return f"{num:,}".replace(",", " ") + " UZS"
            else:
                return f"{num:,}".replace(",", " ") + " USD"

        return text

    @classmethod
    def make_category_hashtags(cls, category_name: Optional[str], base_tag: str = "#Vakansiya") -> str:
        """Kategoriya nomidan chiroyli heshteglar yasaydi."""
        if not category_name:
            return base_tag

        # Maxsus belgilarni tozalash va so'zlarga bo'lish
        words = re.findall(r"[A-Za-zА-Яа-яЎўҚқҒғҲҳ0-9]+", category_name)
        stop_words = {"va", "uchun", "hamda", "yoki", "bilan"}
        cat_tags = []
        for w in words:
            if w.lower() not in stop_words and len(w) > 1:
                cat_tags.append(f"#{w.capitalize()}")

        if cat_tags:
            return f"{base_tag} {' '.join(cat_tags[:2])}"
        return base_tag

    @classmethod
    def generate_job_post(
        cls,
        position: str,
        company: str,
        requirements: str,
        salary: str,
        contact: str,
        location: Optional[str] = None,
        work_schedule: Optional[str] = None,
        telegram_user: Optional[str] = None,
        category_name: Optional[str] = None,
        channel_username: str = "freelance_uzb",
        job_id: Optional[int] = None,
    ) -> str:
        """
        Vakansiya post matnini generatsiya qiladi (3-rasm tartibi asosida).
        """
        lines = []

        # 1. Hashtaglar
        hashtags = cls.make_category_hashtags(category_name, base_tag="#Vakansiya")
        lines.append(hashtags)
        lines.append("")

        # 2. Lavozim va Kompaniya
        pos_clean = position.strip()
        comp_clean = cls.format_title_case(company)
        lines.append(f"👨‍💼 {pos_clean}")
        lines.append(f"🏢 Kompaniya: {comp_clean}")
        lines.append("")

        # 3. Ish tartibi va Manzil (alohida qatorlarda)
        sched = cls.clean_text(work_schedule)
        loc = cls.clean_text(location)

        if sched:
            lines.append(f"⏳ Ish tartibi: {sched}")
        if loc:
            lines.append(f"📍 Manzil: {loc}")

        if sched or loc:
            lines.append("")

        # 4. Talablar va vazifalar
        req = cls.clean_text(requirements)
        if req:
            lines.append("Talablar va vazifalar:")
            req_lines = [l.strip() for l in req.split("\n") if l.strip()]
            for rl in req_lines:
                lines.append(rl)
            lines.append("")

        # 5. Maosh bloki
        sal = cls.clean_text(salary) or "Kelishiladi"
        lines.append(f"💵 Maosh: {sal}")
        lines.append("")

        # 6. Aloqa ma'lumotlari (Dublikatsiz, toza formatda)
        lines.extend(cls.format_contact_lines(contact, telegram_user))
        lines.append("")

        # 7. Yakuniy brend footer va E'lon raqami
        chan = channel_username.lstrip("@")
        lines.append(f"©️ @{chan} bilan frilanserlik endi bir qadam!")
        if job_id:
            lines.append(f"🆔 E'lon raqami: #{job_id}")

        return "\n".join(lines)

    @classmethod
    def generate_resume_post(
        cls,
        specialty: str,
        name: str,
        bio: Optional[str],
        experience: Optional[str],
        services: str,
        tools: Optional[str],
        price: str,
        portfolio: Optional[str],
        contact: str,
        telegram_user: Optional[str] = None,
        category_name: Optional[str] = None,
        channel_username: str = "freelance_uzb",
        job_id: Optional[int] = None,
    ) -> str:
        """
        3-rasm namunasi bilan 100% aynan bir xil tartib va formatda
        rezyume (ish kerak) post matnini generatsiya qiladi.
        """
        lines = []

        # 1. Hashtaglar (#Rezyume #{Kategoriya})
        hashtags = cls.make_category_hashtags(category_name, base_tag="#Rezyume")
        lines.append(hashtags)
        lines.append("")

        # 2. Mutaxassislik (👨‍💼 ...) va Qisqa ta'rif
        lines.append(f"👨‍💼 {specialty.strip()}")
        if bio and bio.strip():
            lines.append(bio.strip())
        lines.append("")

        # 3. Ism va Tajriba (alohida qatorlarda, ism har doim bosh harfda)
        name_clean = cls.format_title_case(name)
        if name_clean:
            lines.append(f"👤 {name_clean}")
        if experience and experience.strip():
            exp_clean = experience.strip()
            if not exp_clean.lower().startswith("tajriba"):
                lines.append(f"⏳ Tajriba: {exp_clean}")
            else:
                lines.append(f"⏳ {exp_clean}")

        if name_clean or (experience and experience.strip()):
            lines.append("")

        # 4. Xizmatlar ro'yxati
        lines.append("Xizmatlar:")
        srv_lines = [l.strip() for l in services.split("\n") if l.strip()]
        for sl in srv_lines:
            lines.append(sl)
        lines.append("")

        # 5. Dasturlar
        if tools and tools.strip():
            lines.append(f"🛠 Dasturlar: {tools.strip()}")
            lines.append("")

        # 6. Narx / Maosh
        pr = cls.clean_text(price) or "Loyiha hajmiga qarab kelishiladi"
        lines.append(f"💵 Narx: {pr}")
        lines.append("")

        # 7. Portfolio havolasi
        if portfolio and portfolio.strip():
            lines.append(f"💼 Portfolio: {portfolio.strip()}")
            lines.append("")

        # 8. Aloqa ma'lumotlari (Dublikatsiz, toza formatda)
        lines.extend(cls.format_contact_lines(contact, telegram_user))
        lines.append("")

        # 9. Yakuniy brend footer va E'lon raqami
        chan = channel_username.lstrip("@")
        lines.append(f"©️ @{chan} bilan frilanserlik endi bir qadam!")
        if job_id:
            lines.append(f"🆔 E'lon raqami: #{job_id}")

        return "\n".join(lines)
