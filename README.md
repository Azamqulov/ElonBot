# 🚀 ElonBot — Vakansiya E'lon Tayyorlash Boti

Telegram kanallari (masalan `@freelance_uzb`) uchun professional, brendlangan vakansiya e'lonlarini (matnli post va Pillow yordamida generatsiya qilinadigan rasmli karta) tayyorlovchi, moderatsiya tizimi orqali kanalga avtomatik chiqaruvchi Telegram bot.

---

## 🌟 Asosiy Imkoniyatlar

1. **Foydalanuvchi Oqimi (User FSM):**
   - 9 bosqichli qulay FSM forma (Kategoriya tanlash, Lavozim, Kompaniya, Talablar, Maosh / Kelishiladi, Manzil, Ish tartibi, Aloqa).
   - Real-vaqtda post matni va **1200×1040 px** o'lchamdagi brend karta preview'sini ko'rsatish.
   - Moderatsiyaga yuborish va o'z so'rovlari holatini (`/my_requests`) kuzatish.

2. **Dizayn & Karta Generatori (Pillow Engine):**
   - Zamonaviy geometrik fon (bordo va feruza aksentlar, markaziy oq karta, soya effekti).
   - O'zbekcha lotin harflari (oʻ, gʻ, sh, ch) bilan to'liq moslik.
   - Uzun sarlavhalar uchun avtomatik shrift o'lchamini kichraytirish va matnni qatorlarga chiroyli bo'lish (auto-wrap & scaling).
   - Yashil kapsula ichidagi ajratilgan maosh bloki va kanal suv belgisi (watermark).

3. **Admin Moderatsiyasi:**
   - Yangi e'lon kelganda adminlarga darhol rasm + matn preview'si bilan bildirishnoma boradi.
   - **✅ Tasdiqlash:** Bir marta bosish bilan e'lon avtomatik ravishda belgilangan kanalga post qilinadi va foydalanuvchiga xushxabar boradi.
   - **❌ Rad etish:** Admin rad etish sababini yozadi va foydalanuvchiga tuzatish uchun sababi bilan yuboriladi.
   - `/pending` buyrug'i orqali kutayotgan barcha arizalar navbatini ko'rish.

4. **Superadmin Paneli:**
   - `/add_admin <tg_id>` — yangi admin tayinlash.
   - `/remove_admin <tg_id>` — adminlikdan olish.
   - `/add_channel <@kanal>` — bot post chiqaradigan yangi kanallarni ulash.
   - `/stats` — umumiy tizim statistikasi.

---

## 🛠️ O'rnatish va Ishga Tushirish

### 1. Muhitni tayyorlash
Loyiha papkasiga o'ting va virtual muhitni yarating:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Sozlamalarni kiritish (`.env`)
`.env.example` faylidan `.env` nusxa oling va o'zingizning sozlamalaringizni kiriting:
```ini
BOT_TOKEN=1234567890:AA...YOUR_TELEGRAM_BOT_TOKEN
SUPERADMIN_IDS=Sening_Telegram_ID_raqaming
DEFAULT_CHANNEL_ID=@freelance_uzb
DATABASE_URL=sqlite+aiosqlite:///./data/elonbot.db
WATERMARK_TEXT=@freelance_uzb
```
*(Eslatma: Bot post chiqarishi uchun siz ko'rsatgan kanalda administrator huquqiga ega bo'lishi shart).*

### 3. Botni ishga tushirish
```bash
.\venv\Scripts\python main.py
```

---

## 📁 Loyiha Strukturasi

```
ElonBot/
├── .env.example
├── .gitignore
├── requirements.txt
├── GOLDEN RULES.md
├── README.md
├── test_generators.py          # Rasm va matn generatorlari testi
├── test_database.py            # Baza CRUD operatsiyalari testi
├── generated_images/           # Bot yaratgan tayyor kartalar
├── src/
│   ├── bot/
│   │   ├── config.py           # Pydantic Settings
│   │   ├── middlewares/        # Database va foydalanuvchi middleware
│   │   ├── states/             # FSM holatlari
│   │   ├── keyboards/          # Inline va Reply menyular
│   │   └── handlers/
│   │       ├── common.py       # /start, /cancel, /my_requests
│   │       ├── user_job.py     # Vakansiya kiritish 1-9 qadamlar
│   │       ├── admin.py        # Moderatsiya va kanalga avtopost
│   │       └── superadmin.py   # Admin/Kanal boshqaruvi va statistika
│   ├── database/
│   │   ├── models.py           # SQLAlchemy modellar
│   │   ├── connection.py       # DB engine, session va seed
│   │   └── repositories.py     # CRUD repozitoriyalari
│   └── services/
│       ├── post_generator.py   # Telegram post matni formati
│       └── image_generator.py  # Pillow 1200x1040 karta chizuvchi
└── main.py                     # Bot ishga tushirish kirish nuqtasi
```
