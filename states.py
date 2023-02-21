from aiogram.dispatcher.filters.state import State, StatesGroup

class States(StatesGroup):
    business = State()
    risk = State()
    science = State()
    technic = State()
    communication = State()
    nature = State()
    sign = State()
    art = State()