# TZ — Vakansiya E'lon Tayyorlash Boti

## 1. Loyiha maqsadi

Telegram kanallarga (masalan @freelance_uzb kabi) vakansiya e'lonlarini standart, brendlashgan formatda tayyorlaydigan bot. Bot ikki narsa generatsiya qiladi:

1. **Matnli post** — kanal formatidagi tayyor matn (#Vakansiya hashtag, emoji-bullet struktura — mavjud namunalar asosida).
2. **Rasmli karta** — ish turiga mos ikonka bilan, doimiy brend dizaynidagi (logotip, ranglar, layout) PNG rasm.

Ikkalasi birga (photo + caption yoki photo + alohida matn) kanalga chiqadi.

## 2. Rollar va huquqlar

| Rol | Kim | Huquqlar |
|---|---|---|
| **User** | Tashqi mijoz (kanalga vakansiya joylashtirmoqchi bo'lgan har kim) | Bot orqali forma to'ldirib vakansiya so'rovi yuboradi, o'z so'rovlari holatini (kutilmoqda/tasdiqlandi/rad etildi) ko'radi |
| **Admin** | Kanal moderatori | Kelgan so'rovlarni ko'radi, tahrirlaydi, tasdiqlaydi yoki sababi bilan rad etadi. Tasdiqlangani avtomatik kanalga chiqadi |
| **Superadmin** | Bot egasi (siz) | Admin qo'shish/o'chirish, kanallar ro'yxatini boshqarish, kategoriya/ikonka bazasini boshqarish, statistika ko'rish, botning umumiy sozlamalari |

## 3. User oqimi (foydalanuvchi flow)

```
/start
 └─ "🆕 Yangi vakansiya e'loni berish" tugmasi
     ├─ 1) Ish turi/kategoriya tanlash (inline keyboard: Sotuv, IT, Haydovchi, Oshpaz, ...)
     ├─ 2) Lavozim nomi (matn kiritish)
     ├─ 3) Kompaniya nomi
     ├─ 4) Talablar (erkin matn, bir nechta qator bo'lishi mumkin)
     ├─ 5) Maosh ("Kelishiladi" tugmasi YOKI aniq summa kiritish)
     ├─ 6) Manzil/lokatsiya
     ├─ 7) Ish tartibi/qulayliklar (erkin matn)
     ├─ 8) Aloqa (telefon/telegram)
     ├─ 9) PREVIEW — tayyor matn + generatsiya qilingan rasm ko'rsatiladi
     │    ├─ "✅ Yuborish" — adminlarga moderatsiyaga jo'natiladi
     │    ├─ "✏️ Tahrirlash" — istalgan qadamga qaytish
     │    └─ "❌ Bekor qilish"
     └─ Yuborilgach: "So'rovingiz qabul qilindi, admin ko'rib chiqmoqda" + status kuzatish imkoniyati (/my_requests)
```

FSM (Finite State Machine) sifatida aiogram'da amalga oshiriladi — har bir qadam alohida state.

## 4. Admin oqimi

- Yangi so'rov kelganda barcha adminlarga inline tugmali xabar boradi: matn + rasm preview + `✅ Tasdiqlash` / `✏️ Tahrirlab tasdiqlash` / `❌ Rad etish`.
- **Tasdiqlash** → status `approved` → bot avtomatik ravishda belgilangan kanal(lar)ga rasm+matnni post qiladi → status `posted`.
- **Tahrirlab tasdiqlash** → admin matnni to'g'ridan-to'g'ri tahrirlaydi (inline yoki forward qilib qayta yuborish), keyin post qilinadi.
- **Rad etish** → sabab kiritish so'raladi → userga sabab bilan xabar boradi, status `rejected`.
- `/pending` — kutayotgan barcha so'rovlar ro'yxati.

## 5. Superadmin oqimi

- `/add_admin @username` / `/remove_admin` — admin boshqaruvi.
- `/add_channel` — bot post qiladigan kanal(lar)ni qo'shish (bot shu kanalda admin bo'lishi kerak).
- `/add_category` — yangi ish turi kategoriyasi + unga mos ikonka yuklash.
- `/stats` — necha ta so'rov kelgan, necha tasi tasdiqlangan/rad etilgan, eng ko'p so'ralgan kategoriyalar, kunlik/haftalik dinamika.

## 6. Rasmli karta — dizayn spetsifikatsiyasi

Namuna (2-rasm) asosida quyidagi shablon belgilanadi:

- **O'lcham:** 1200×1040 px (Telegram uchun sifatli, 2x zichlik).
- **Fon:** geometrik uchburchak elementlar (yuqori chap — pushti/bordo, pastki chap — teal/ko'k-yashil), qolgan qismi oq.
- **Yuqori chap burchak:** kichik brend belgisi — logotip kvadrati + "VAKANSIYA" matni.
- **Markaziy oq karta (rounded corners, yengil soya):**
  - Tepada — doira ichida ish turiga mos **ikonka** (ko'k rangli badge).
  - Lavozim nomi — katta, qalin, brend rangida (bordo/pushti).
  - "Maosh:" label + qiymat (agar aniq summa kiritilgan bo'lsa ko'rsatiladi, aks holda "batafsil postda").
- **Pastki o'ng burchak:** kanal username (masalan `@freelance_uzb`) — watermark sifatida.

### Ikonka-kategoriya tizimi

Har bir kategoriya uchun oldindan tayyorlangan PNG/SVG ikonka bazada saqlanadi:

| Kategoriya | Ikonka misoli |
|---|---|
| Sotuv/marketing | xarid sumkasi |
| IT/dasturlash | noutbuk |
| Haydovchi/logistika | mashina |
| Oshpaz/umumiy ovqatlanish | oshpaz qalpog'i |
| Ta'lim/repetitor | kitob |
| Go'zallik/salon | qaychi |
| Qurilish | g'isht |
| Ofis/kotib | papka |
| Boshqa | umumiy chamadon |

Superadmin panel orqali yangi kategoriya + ikonka istalgan vaqt qo'shilishi mumkin — statik ro'yxat bilan cheklanib qolmaslik uchun.

### Texnik amalga oshirish

- **Pillow (Python)** bilan: bitta tayyor fon-shablon PNG (dizayner tomonidan bir marta chizilgan) ustiga dinamik qatlamlar (`ImageDraw` + TTF shrift) chiziladi:
  - Ikonka (kategoriya bo'yicha tanlab qo'yiladi).
  - Lavozim matni (uzun matnlar uchun avtomatik font-size kichraytirish yoki qator ko'chirish logikasi kerak).
  - Maosh matni.
- O'zbek lotin harflari (oʻ, gʻ, sh, ch) to'g'ri chiqishi uchun mos shrift tanlanadi (masalan Inter, Montserrat, yoki Manrope — Unicode to'liq qo'llab-quvvatlanadigan).

## 7. Matnli post moduli

1 va 3-rasm namunalari asosida shablon:

```
#Vakansiya

📌 <Lavozim nomi>

👥 Nomzodlar: <talab>
🏢 Kompaniya: <nomi>
❗ Talablar: <matn>
✅ Qulayliklar: <matn>
💵 Maosh: <qiymat yoki "Kelishiladi">
📍 Manzil: <lokatsiya>
📞 Aloqa: <telefon>
✉️ Telegram: <username>

© @<kanal_username> bilan ish va ishchi topish yanada oson.
```

Bo'sh qoldirilgan maydonlar (masalan manzil kiritilmasa) postdan avtomatik olib tashlanadi — bo'sh qatorlar chiqmasligi kerak.

## 8. Texnik stack

| Qism | Tanlov | Izoh |
|---|---|---|
| Bot backend | **Python 3.11+ / aiogram 3.x** | Milliy Sertifikat bot bilan bir xil stack — tajriba mavjud |
| Rasm generatsiya | **Pillow** | Shablon-asosli, tez, brend doim bir xil |
| Ma'lumotlar bazasi | **Supabase (Postgres)** | Standart stack, keyinchalik statistika/dashboard uchun qulay |
| Deployment | Polling (MVP), keyin webhook'ga o'tish mumkin | Kichik-o'rta trafik uchun polling yetarli |

## 9. Ma'lumotlar bazasi sxemasi (asosiy jadvallar)

```
users
  id, tg_id, full_name, phone, role (user/admin/superadmin), created_at

categories
  id, name, icon_path, keywords[]

job_requests
  id, user_id (FK), category_id (FK), position, company,
  requirements, salary, location, work_schedule, contact,
  post_text, image_path,
  status (draft/pending/approved/rejected/posted),
  reviewed_by (FK -> users), rejection_reason,
  created_at, reviewed_at, posted_at

channels
  id, tg_channel_id, name, added_by (FK), is_active
```

## 10. Fazalar rejasi

- **Phase 1 (MVP):** User FSM forma → matn post generatsiya → 1 ta umumiy rasm shablon (ikonkasiz) → admin qo'lda tasdiqlaydi va kanalga qo'lda joylaydi.
- **Phase 2:** Kategoriya-ikonka tizimi → tasdiqlangach **avtomatik** kanalga post → superadmin panel (admin qo'shish/o'chirish).
- **Phase 3:** Ko'p kanal support (bir nechta kanalga bir vaqtda yoki tanlab post qilish) → statistika (`/stats`) → rad etish sababi bilan userga feedback.
- **Phase 4 (ixtiyoriy, kelajakda):** Monetizatsiya (masalan tezkor/tepaga chiqarish pullik), userga o'ziga tahrirlash imkoniyati (admin aralashuvisiz kichik tuzatishlar), AI-generatsiya qilingan fon variant sifatida.

## 11. Ochiq savollar (keyingi qadam uchun)

- Bir nechta kanal bo'lsa, user o'zi kanalni tanlaydimi yoki superadmin belgilaydimi?
- Vakansiya muddati tugagach (masalan 7 kundan keyin) avtomatik "yopiq" deb belgilanadimi?
- Monetizatsiya kerakmi (Payme/Click orqali pullik joylashtirish), yoki hozircha to'liq bepul?
