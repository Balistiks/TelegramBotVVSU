from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from states import States
import config
import pandas

questions = pandas.read_excel('proftest.xlsx')

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands="start")
async def start(message: types.Message):
    keyboard_start = types.InlineKeyboardMarkup()
    keyboard_start.add(types.InlineKeyboardButton(text="Профтест", callback_data="prof"))
    keyboard_start.add(types.InlineKeyboardButton(text="Канал Абитуриентов ВВГУ", callback_data="kanal"))
    await message.answer("Выбери", reply_markup=keyboard_start)


# Тут я создал переменную в state (счетчик на каком вопросе пользователь), не знаю куда его еще запихнуть
@dp.callback_query_handler(state=None)
async def callBack_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    if call.data == "prof":
        await States.business.set()
        await state.update_data({'number': 0})
        await state.update_data({'business': 0})
        await state.update_data({'risk': 0})
        await state.update_data({'science': 0})
        await state.update_data({'technic': 0})
        await state.update_data({'communication': 0})
        await state.update_data({'nature': 0})
        await state.update_data({'sign': 0})
        await state.update_data({'art': 0})
        await test(call, state)


@dp.callback_query_handler(state=States)
async def test(call: types.CallbackQuery, state: FSMContext):
    print(await state.get_state())
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        None

    data = await state.get_data()
    number = data['number']
    try:
        state_question = questions['type'][number+1]
    except:
        state_question = questions['type'][number-1]
    state_user = await state.get_state()
    state_user = state_user[7::1]

    if state_user != state_question:
        await States.next()
    if call.data == 'yes':
        score_type = data[questions['type'][number-1]]
        if not pandas.isnull(questions.loc[number-1, 'gif_yes']):
            await call.message.answer_video(questions['gif_yes'][number-1])
        await call.message.answer(text=questions['answer_yes'][number-1])
        await state.update_data({questions['type'][number-1]: score_type + 1})
    elif call.data == 'no':
        if not pandas.isnull(questions.loc[number-1, 'gif_yes']):
            await call.message.answer_video(questions['gif_no'][number-1])
        await call.message.answer(text=questions['answer_no'][number-1])

    if number <= 33:
        keyboard_answer = types.InlineKeyboardMarkup()
        keyboard_answer.add(types.InlineKeyboardButton(text=questions['button_yes'][number], callback_data="yes"))
        keyboard_answer.add(types.InlineKeyboardButton(text=questions['button_no'][number], callback_data='no'))
        await call.message.answer(text=questions['qtext'][number], reply_markup=keyboard_answer)
        number = data['number'] + 1
        await state.update_data({'number': number})
    else:
        print(data['number'])
        print(data['business'])
        print(data['risk'])
        print(data['science'])
        print(data['technic'])
        print(data['communication'])
        print(data['nature'])
        print(data['sign'])
        print(data['art'])
    


executor.start_polling(dp, skip_updates=True)