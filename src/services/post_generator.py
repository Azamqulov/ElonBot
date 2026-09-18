import re
from typing import Optional


class PostGenerator:
    @staticmethod
    def clean_text(text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        cleaned = text.strip()
        return cleaned if cleaned else None

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
        channel_username: str = "freelance_uzb",
    ) -> str:
        """
        Vakansiya matnli postini standart shablonda generatsiya qiladi.
        Bo'sh qoldirilgan ixtiyoriy maydonlar postdan chiqarib tashlanadi.
        """
        lines = [
            "#Vakansiya",
            "",
            f"📌 {position.strip()}",
            "",
            f"🏢 Kompaniya: {company.strip()}",
        ]

        req = cls.clean_text(requirements)
        if req:
            lines.append(f"❗ Talablar: {req}")

        sched = cls.clean_text(work_schedule)
        if sched:
            lines.append(f"✅ Qulayliklar / Ish tartibi: {sched}")

        sal = cls.clean_text(salary) or "Kelishiladi"
        lines.append(f"💵 Maosh: {sal}")

        loc = cls.clean_text(location)
        if loc:
            lines.append(f"📍 Manzil: {loc}")

        cnt = cls.clean_text(contact)
        if cnt:
            lines.append(f"📞 Aloqa: {cnt}")

        tg = cls.clean_text(telegram_user)
        if tg:
            # @ belgisini to'g'rilash
            tg_clean = tg.lstrip("@")
            lines.append(f"✉️ Telegram: @{tg_clean}")

        chan = channel_username.lstrip("@")
        lines.append("")
        lines.append(f"© @{chan} bilan ish va ishchi topish yanada oson.")

        return "\n".join(lines)
