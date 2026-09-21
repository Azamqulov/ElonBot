# 📌 PROJECT DASHBOARD & STATE — ElonBot (Vakansiya E'lon Tayyorlash Boti)

> Bu fayl ElonBot loyihasi holati, arxitektura qarorlari (ADR), faol vazifalar va AI jamoasi protokoli uchun yagona haqiqat manbai (Source of Truth) hisoblanadi.

## 🎯 Overall Objective & Current Phase
- **Loyiha:** ElonBot — Telegram kanallari uchun professional, brendlangan vakansiya e'lonlarini (matn + Pillow yordamida generatsiya qilinadigan rasmli karta) tayyorlovchi va moderatsiya orqali kanalga avtomatik chiqaruvchi Telegram bot.
- **Hozirgi Bosqich:** Phase 1 (MVP) & Core Foundation Development.
- **Status:** In Development.

## 🧠 Architecture Decision Log (ADR)
- **Stack:** Python 3.13+, aiogram 3.x, Pillow (PIL), SQLAlchemy 2.0 (Async), aiosqlite (lokal) / PostgreSQL (Supabase tayyor), Pydantic Settings.
- **Core Protocol:** Global `AGENTS.md` va `skills/` papkasidagi barcha qoidalarga 100% amal qilinadi.
- **Rasm Generatsiya Texnologiyasi:** Pillow bilan 1200×1040 px o'lchamdagi vektorli/geometrik zamonaviy karta, o'zbekcha lotin harflarini to'liq qo'llab-quvvatlovchi TrueType shriftlar va sarlavhalar uchun avtomatik o'lcham moslashuvi (dynamic text wrap & auto-scaling).
- **Data Model:** SQLite / PostgreSQL uchun umumiy asinxron ORM qatlami (`users`, `categories`, `job_requests`, `channels`).
- **Loyihaga xos maxsus qoidalar:**
  1. Matn generatsiyasida bo'sh qolgan maydonlar avtomatik chiqarib tashlanishi va format buzilmasligi shart.
  2. Moderatsiyada admin "Tasdiqlash" bosgan zahoti e'lon belgilangan kanalga avtomatik post qilinishi kerak.
  3. Foydalanuvchi ma'lumotlari xavfsizligi va telefon raqami formati O'zbekiston standartiga (+998) mos kelishi kerak.

## 🤖 AI Developers & Team Protocol
- To'liq pipeline (dev → qa-tester → team-lead → senior-qa → PM) — global `ai-development-team-protocol` skilida.

## 🔄 Active Task (In Progress)
- [x] Arxitektura rejasi (Implementation Plan) tuzildi va tasdiqlandi.
- [x] 1-qadam: Loyiha katalog tuzilmasi, `requirements.txt`, `.env.example` yaratish.
- [x] 2-qadam: Ma'lumotlar bazasi (SQLAlchemy async models, connection, repositories) qatlamini qurish.
- [x] 3-qadam: Rasm generatsiya xizmati (Pillow engine, shriftlar, geometrik shablon) va post formaterini yaratish.
- [x] 4-qadam: aiogram 3 bot arxitekturasi (FSM states, inline/reply klaviaturalar, filtrlash).
- [x] 5-qadam: Foydalanuvchi e'lon topshirish oqimi (user FSM flow, preview, /my_requests).
- [x] 6-qadam: Admin moderatsiya oqimi (tasdiqlash, kanalga avtopost, rad etish, /pending).
- [x] 7-qadam: Superadmin boshqaruv paneli (/add_admin, /add_channel, /stats).
- [x] 8-qadam: Sinovlar va tekshiruv (Image test, Post format test, DB CRUD test, Import test).

## ✅ Completed Checklist (History)
- [2026-09-14] Loyiha texnik topshirig'i o'rganildi, implementatsiya rejasi tasdiqlandi.
- [2026-09-14] Barcha asosiy modullar (Pillow 1200x1040 karta generatori, Post generatori, SQLAlchemy Async DB, aiogram 3 FSM, Admin moderatsiya va kanalga avtopost) 100% ishlab chiqildi va sinovdan o'tkazildi.
- [2026-09-20] 8-qadamda (aloqa ma'lumotlari) foydalanuvchining o'z raqami va Telegram username'i chiqib turadigan, bitta bosishda kontakt ulashadigan Reply keyboard tugmasi joriy qilindi.
- [2026-09-21] Rasm dizayni 2-rasm etaloni bilan 1:1 formatda ideal qilindi (1280x960 px, 2x supersampling antialiasing, low-poly 3D kristal fasetlar, yumshoq ambient floating soya, 3D taqdimot doskasi piktogrammasi, qalin to'q bordo sarlavha, to'q feruza katta maosh bloki, vertikal separator, toza "FL VAKANSIYA" va "@Freelance_uzb" watermark).
- [2026-09-21] Post matni (PostGenerator) 3-rasm tartibi va formatiga 100% moslashtirildi (#Vakansiya #Kategoriya, 👨‍💼 Lavozim, 🏢 Kompaniya, ⏳ Ish tartibi | 📍 Manzil, Talablar va vazifalar, 💵 Maosh, 📍 Aloqa + @username, ©️ @freelance_uzb brend xabari).
- [2026-09-21] Ikki yo'nalishli e'lon berish (Vakansiya / Ishchi kerak va Rezyume / Ish kerak) tizimi to'liq ishlab chiqildi.
- [2026-09-21] Admin va Superadmin paneli to'liq interaktiv tugmalar (buttons) va FSM ga o'tkazildi (slash-command'lar yo'qotildi).
- [2026-09-21] Telegram postlarining eng oxirgi qatoriga unikal "🆔 E'lon raqami: #ID" avtomatik biriktirilishi yo'lga qo'yildi.
- [2026-09-21] To'lov tizimi va chek tasdiqlash oqimi to'liq ishlab chiqildi:
  1. `bot_settings` jadvali va `SettingsRepository` orqali admin panelda e'lon narxi, karta raqami, karta egasi va to'lov holatini boshqarish.
  2. Vakansiya va Rezyume berishda narx, karta egasi va nusxalanuvchi karta raqami bilan invoys chiqarish.
  3. Foydalanuvchidan to'lov chekini (foto/skrinshot) qabul qilish va xavfsiz saqlash.
  4. Moderatsiyada adminlarga e'lon banneri bilan birga mijozning to'lov cheki rasmini ko'rsatish va bitta bosishda kanalga tasdiqlash yoki rad etish.
- [2026-09-21] Aloqa qismidagi username dublikati (ikki marta chiqishi) to'liq bartaraf etildi (telefon va username aniq ajratilib faqat bir marta pastki qatorda chiqadi).
- [2026-09-21] Kompaniya nomi va Ism-familiya foydalanuvchi qanday kiritishidan qat'i nazar avtomatik Title Case (har bir so'zi katta harf, qisqartmalar o'z holicha) formatiga keltirildi.
- [2026-09-21] 'ℹ️ Bot haqida' bo'limiga to'g'ridan-to'g'ri @Musurmon_dev profiliga havola qiluvchi '💬 Support' inline tugmasi qo'shildi.
- [2026-09-21] Maosh (Vakansiya) va Narx (Rezyume) kiritish bosqichida `[🇺🇿 UZS (So'm)]` hamda `[🇺🇸 USD (Dollar)]` valyuta tanlash tugmalari joriy qilindi. Tanlangan valyutaga ko'ra summani probellar bilan chiroyli formatlash (masalan, `10 000 000 UZS` yoki `800 - 1 200 USD`), shuningdek valyutani almashtirish va `[🤝 Kelishiladi]` opsiyalari to'liq ishga tushirildi.

## 📋 Roadmap & Upcoming Tasks (Backlog)
- [ ] Avtomatlashtirilgan Click / Payme Merchant API webhook to'lovlari (chek yubormasdan to'g'ridan-to'g'ri P2P/Merchant tasdiqlash).
- [ ] Ko'p kanalli moslashuvchan rejim (foydalanuvchi bir nechta kanaldan birini tanlashi yoki admin rejalashtirishi).
- [ ] AI yordamida lavozim va talablar matnini sayqallash (imlo va grammatik tuzatish).

## 🐛 Known Bugs & UX Defects (Issue Tracker)
- Hozircha aniqlangan muammo yo'q.
