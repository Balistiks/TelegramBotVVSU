from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from states import States
import config
import pandas
import numpy as np
from numpy.linalg import norm

questions = pandas.read_excel('proftest.xlsx')
cnt_types=questions['type'].value_counts()

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

business_inf = np.array([0.4,0.2,0,0,0,0.4])
prik_math = np.array([1,0,0,0,0,0])

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
        # добавить приветствия из оригинального теста + ввод имени и номера + сохранения номера и username из tg
        await States.prof.set()
        await state.update_data({'number': 0})
        await state.update_data({'business': 0})
        await state.update_data({'risk': 0})
        await state.update_data({'science': 0})
        await state.update_data({'technic': 0})
        await state.update_data({'communication': 0})
        await state.update_data({'nature': 0})
        await state.update_data({'sign': 0})
        await state.update_data({'art': 0})
        await question(call, state)


@dp.callback_query_handler(state=States.prof)
async def question(call: types.CallbackQuery, state: FSMContext):
    print(await state.get_state())
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except:
        None

    data = await state.get_data()
    number = data['number']

    if call.data == 'yes':
        print("yes")
        print(questions['type'][number-1])
        score_type = data[questions['type'][number-1]]
        if not pandas.isnull(questions.loc[number-1, 'gif_yes']):
            await call.message.answer_video(questions['gif_yes'][number-1])
        await call.message.answer(text=questions['answer_yes'][number-1])
        await state.update_data({questions['type'][number-1]: score_type + 1})
    elif call.data == 'no':
        if not pandas.isnull(questions.loc[number-1, 'gif_no']):
            await call.message.answer_video(questions['gif_no'][number-1])
        await call.message.answer(text=questions['answer_no'][number-1])

    if number <= 33:
        print(number)
        keyboard_answer = types.InlineKeyboardMarkup()
        keyboard_answer.add(types.InlineKeyboardButton(text=questions['button_yes'][number], callback_data="yes"))
        keyboard_answer.add(types.InlineKeyboardButton(text=questions['button_no'][number], callback_data='no'))
        await call.message.answer(text=questions['qtext'][number], reply_markup=keyboard_answer)
        number = data['number'] + 1
        await state.update_data({'number': number})
    else:
        await end_prof(call, state)


async def end_prof(call, state):
    data = await state.get_data()
    user_score = []
    for i in ['sign','communication','art','technic','nature','business']:
        user_score.append(data[i]/cnt_types[i])
    user_score = np.array(user_score)
    for spec in [business_inf,prik_math]:
        print('Расстояние между векторами a и b: {norm}'.format(norm = norm(user_score-spec, ord=1)))
    # создать структуру для хранения расстояний для каждого направления подготовки(например, датафрейм)
    # выдать пользователю топ5 направлений с наименьшим расстоянием


    


executor.start_polling(dp, skip_updates=True)