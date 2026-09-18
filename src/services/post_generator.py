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
        is_pro: bool = False,
    ) -> str:
        """
        Vakansiya matnli postini standart shablonda generatsiya qiladi.
        Bo'sh qoldirilgan ixtiyoriy maydonlar postdan chiqarib tashlanadi.
        Pro tarif uchun ⚡ TEZKOR belgisi qo'shiladi.
        """
        lines = []

        # PRO tarif belgisi
        if is_pro:
            lines += ["⚡ <b>TEZKOR E'LON</b> | PRO tarif", ""]

        lines += [
            "#Vakansiya",
            "",
            f"📌 <b>{position.strip()}</b>",
            "",
            f"🏢 <b>Kompaniya:</b> {company.strip()}",
            "",
        ]

        req = cls.clean_text(requirements)
        if req:
            lines += [f"❗ <b>Talablar:</b>\n{req}", ""]

        sched = cls.clean_text(work_schedule)
        if sched:
            lines += [f"✅ <b>Qulayliklar / Ish tartibi:</b>\n{sched}", ""]

        sal = cls.clean_text(salary) or "Kelishiladi"
        lines += [f"💵 <b>Maosh:</b> {sal}", ""]

        loc = cls.clean_text(location)
        if loc:
            lines += [f"📍 <b>Manzil:</b> {loc}", ""]

        cnt = cls.clean_text(contact)
        if cnt:
            lines.append(f"📞 <b>Aloqa:</b> {cnt}")

        tg = cls.clean_text(telegram_user)
        if tg:
            tg_clean = tg.lstrip("@")
            lines.append(f"✉️ <b>Telegram:</b> @{tg_clean}")

        chan = channel_username.lstrip("@")
        lines += [
            "",
            f"© @{chan} bilan ish va ishchi topish yanada oson.",
        ]

        return "\n".join(lines)
