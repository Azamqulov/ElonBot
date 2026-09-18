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

## 📋 Roadmap & Upcoming Tasks (Backlog)
- [ ] Payme / Click integratsiyasi (pullik VIP yoki shoshilinch e'lonlar uchun).
- [ ] Ko'p kanalli moslashuvchan rejim (foydalanuvchi bir nechta kanaldan birini tanlashi yoki admin rejalashtirishi).
- [ ] AI yordamida lavozim va talablar matnini sayqallash (imlo va grammatik tuzatish).

## 🐛 Known Bugs & UX Defects (Issue Tracker)
- Hozircha aniqlangan muammo yo'q.
