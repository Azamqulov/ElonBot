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


class AdminRejectFSM(StatesGroup):
    waiting_for_reason = State()


class SuperAdminFSM(StatesGroup):
    waiting_for_admin_tg_id = State()
    waiting_for_channel_id = State()
    waiting_for_category_name = State()
