import os
import sys

# Windows konsolida emojilarni xatosiz chiqarish uchun
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from src.services.image_generator import image_generator
from src.services.post_generator import PostGenerator


def run_tests():
    print("========================================")
    print("1. Testing PostGenerator (Vakansiya)...")
    post_job = PostGenerator.generate_job_post(
        position="Senior Python / aiogram Dasturchi",
        company="TechCorp Uzbekistan",
        requirements="3+ yil tajriba, aiogram 3, PostgreSQL, Docker bilimi",
        salary="15 000 000 - 25 000 000 UZS",
        contact="+998 90 123 45 67",
        location="Toshkent shahri",
        work_schedule="Dushanba-Juma, 09:00 - 18:00",
        telegram_user="techcorp_hr",
        category_name="IT va Dasturlash",
        channel_username="freelance_uzb",
        job_id=14,
    )
    print(post_job)
    assert "#Vakansiya" in post_job
    assert "🆔 E'lon raqami: #14" in post_job
    print("-> Vakansiya Post OK!")

    print("\n========================================")
    print("2. Testing PostGenerator (Rezyume — 3-rasm formati)...")
    post_resume = PostGenerator.generate_resume_post(
        specialty="Grafik Dizayner & AI Specialist",
        name="Said Amir",
        bio="Brendingiz uchun sifatli, zamonaviy va sotuvchi vizual yechimlar yarataman.",
        experience="2 yil",
        services=(
            "SMM: Postlar, Stories va Reels cover\n"
            "Brending: Logotip va firma stili\n"
            "Marketpleys: Uzum uchun sotuvchi infografika\n"
            "Poligrafiya: Flayer, vizitka va bannerlar\n"
            "Mahsulot dizayni: Qadoq va etiketka"
        ),
        tools="Photoshop, Illustrator va AI (Claude, ChatGPT va Gemini)",
        price="Loyiha hajmiga qarab kelishiladi (agentliklar uchun oylik asosida)",
        portfolio="https://t.me/+UT3_fiVqm68yMjcy",
        contact="+99893-302-1755",
        telegram_user="tsb2000",
        category_name="Dizayn",
        channel_username="freelance_uzb",
        job_id=25,
    )
    print(post_resume)
    assert "#Rezyume" in post_resume
    assert "🆔 E'lon raqami: #25" in post_resume
    assert "Grafik Dizayner & AI Specialist" in post_resume
    assert "👤 Said Amir\n⏳ Tajriba: 2 yil" in post_resume
    assert "Photoshop, Illustrator va AI" in post_resume
    print("-> Rezyume Post OK!")

    print("\n========================================")
    print("3. Testing ImageGenerator (Vakansiya Card)...")
    job_card = image_generator.generate_job_card(
        position="Senior Python / aiogram Dasturchi",
        company="TechCorp Uzbekistan",
        salary="15 000 000 - 25 000 000 UZS",
        category_name="IT va Dasturlash",
        badge_text="VAKANSIYA",
        channel_watermark="@freelance_uzb",
        output_filename="test_job_card.png",
    )
    assert os.path.exists(job_card), "Vakansiya rasm fayli yaratilmadi!"
    print(f"-> Vakansiya rasm saqlandi: {job_card}")

    print("\n========================================")
    print("4. Testing ImageGenerator (Rezyume Card)...")
    resume_card = image_generator.generate_job_card(
        position="Grafik Dizayner & AI Specialist",
        company="Said Amir",
        salary="Kelishiladi",
        category_name="Grafik Dizayn",
        badge_text="REZYUME",
        channel_watermark="@freelance_uzb",
        output_filename="test_resume_card.png",
    )
    assert os.path.exists(resume_card), "Rezyume rasm fayli yaratilmadi!"
    print(f"-> Rezyume rasm saqlandi: {resume_card}")

    print("\n========================================")
    print("BARCHA SINOVLAR MUVAFFAQIYATLI O'TDI! ✅")


if __name__ == "__main__":
    run_tests()
