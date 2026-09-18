from aiogram.fsm.state import State, StatesGroup


class JobApplicationFSM(StatesGroup):
    # 0-qadam: Tarif va to'lov
    tariff = State()           # Start yoki Pro tanlash
    payment_method = State()   # Payme yoki Click tanlash
    waiting_receipt = State()  # Chek (screenshot) kutish

    # 1-8 qadam: Ma'lumot to'ldirish
    category = State()
    position = State()
    company = State()
    requirements = State()
    salary = State()
    location = State()
    work_schedule = State()
    contact = State()
    preview = State()


class AdminRejectFSM(StatesGroup):
    waiting_for_reason = State()


class AdminPaymentFSM(StatesGroup):
    waiting_for_confirm_reason = State()


class SuperAdminFSM(StatesGroup):
    waiting_for_admin_tg_id = State()
    waiting_for_channel_id = State()
    waiting_for_category_name = State()
