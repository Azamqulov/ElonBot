from aiogram.fsm.state import State, StatesGroup


class JobApplicationFSM(StatesGroup):
    category = State()
    position = State()
    company = State()
    requirements = State()
    salary = State()
    location = State()
    work_schedule = State()
    contact = State()
    preview = State()
    waiting_for_receipt = State()


class ResumeApplicationFSM(StatesGroup):
    category = State()
    specialty = State()
    bio = State()
    full_name = State()
    experience = State()
    services = State()
    tools = State()
    price = State()
    portfolio = State()
    contact = State()
    preview = State()
    waiting_for_receipt = State()


class AdminRejectFSM(StatesGroup):
    waiting_for_reason = State()


class AdminPaymentFSM(StatesGroup):
    waiting_for_price = State()
    waiting_for_card_number = State()
    waiting_for_card_holder = State()


class SuperAdminFSM(StatesGroup):
    waiting_for_admin_tg_id = State()
    waiting_for_channel_id = State()
    waiting_for_category_name = State()
