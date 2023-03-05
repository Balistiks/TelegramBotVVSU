from aiogram.dispatcher.filters.state import State, StatesGroup
class States(StatesGroup):
    get_name = State()
    get_phone = State()
    get_email = State()
    prof = State()