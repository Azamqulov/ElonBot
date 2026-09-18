import os
import sys

# Windows konsolida emojilarni xatosiz chiqarish uchun
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from src.services.image_generator import image_generator
from src.services.post_generator import PostGenerator


def run_tests():
    print("1. Testing PostGenerator...")
    post = PostGenerator.generate_job_post(
        position="Senior Python / aiogram Dasturchi",
        company="TechCorp Uzbekistan",
        requirements="3+ yil tajriba, aiogram 3, PostgreSQL, Docker bilimi",
        salary="15 000 000 - 25 000 000 UZS",
        contact="+998 90 123 45 67",
        location="Toshkent shahri, Mirobod tumani (yoki Masofaviy)",
        work_schedule="Dushanba-Juma, 09:00 - 18:00",
        telegram_user="techcorp_hr",
        channel_username="freelance_uzb",
    )
    print("Generated Post Text:\n-------------------")
    print(post)
    print("-------------------")
    assert "#Vakansiya" in post
    assert "Senior Python / aiogram Dasturchi" in post
    assert "@techcorp_hr" in post
    print("PostGenerator OK!")

    print("\n2. Testing ImageGenerator...")
    card_path = image_generator.generate_job_card(
        position="Senior Python / aiogram Dasturchi",
        company="TechCorp Uzbekistan",
        salary="15 000 000 - 25 000 000 UZS",
        category_name="IT va Dasturlash",
        channel_watermark="@freelance_uzb",
        output_filename="test_job_card.png",
    )
    print(f"Generated Card saved at: {card_path}")
    assert os.path.exists(card_path), "Image file was not created!"
    file_size = os.path.getsize(card_path)
    print(f"Image Size: {file_size} bytes ({file_size / 1024:.1f} KB)")
    assert file_size > 10000, "Image file too small or empty!"
    print("ImageGenerator OK!")


if __name__ == "__main__":
    run_tests()
