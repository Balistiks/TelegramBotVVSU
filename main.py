from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from states import States
import config
import pandas
import numpy as np
from numpy.linalg import norm

spec_xlsx = pandas.read_excel('spec.xlsx')

i = 0
j = 1
spec_list = []
spec_df = pandas.DataFrame(columns=["Направление", 'Список', "url"])

# тут я зачем-то почему-то использую while, а поменять на for че-то уже не хочу
while True:
    if i == 28:
        break
    if j == 7:
        spec_df.loc[len(spec_df.index)] = [spec_xlsx.loc[i][0], spec_list, spec_xlsx.loc[i][7]]
        spec_list = []
        j = 1
        i += 1
        continue
    spec_list.append(spec_xlsx.loc[i][j])
    j += 1

print(spec_df)


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
        await call.message.answer("Привет! Меня зовут Proforio")
        await call.message.answer("Сегодня я помогу тебе узнать сильные стороны твоей личности и выбрать наиболее подходящую профессию")
        await call.message.answer("Для этого надо ответить на 34 вопроса, каждый из которых предполагает только один вариант ответа")
        await call.message.answer("Выбирай наиболее привлекательный для тебя и помни: правильных и неправильных ответов здесь нет, так что не думай над вопросами слишком долго")
        await call.message.answer("Первый ответ, приходящий на ум, обычно самый точны")
        await call.message.answer("Но для начала нам стоит познакомиться, хорошо?")
        await call.message.answer("Как тебя зовут?")
        await States.get_name.set()


@dp.message_handler(state=States.get_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data({'name': message.text}) # сохранение имени
    await message.answer(text=f"Очень приятно, {message.text}")
    await message.answer(text='Чтобы продолжить, нам обязательно нужен твой номер телефона, обещаю не звонить по ночам🙂')
    await States.next()


@dp.message_handler(state=States.get_phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data({'phone': message.text}) # сохранение телефона
    await message.answer(text='Ну и e-mail, если он у тебя есть')
    await States.next()


@dp.message_handler(state=States.get_email)
async def get_email(message: types.Message, state: FSMContext):
    await state.update_data({'email': message.text}) # сохранение email
    await States.next()
    await start_question(message.chat.id, state)


# я так сделал потому что там появилась проблема с вызовом функции question, и я решил ее так решить 
async def start_question(user, state):
    await state.update_data({'number': 0})
    await state.update_data({'business': 0})
    await state.update_data({'risk': 0})
    await state.update_data({'science': 0})
    await state.update_data({'technic': 0})
    await state.update_data({'communication': 0})
    await state.update_data({'nature': 0})
    await state.update_data({'sign': 0})
    await state.update_data({'art': 0})
    start_question_keyboard = types.InlineKeyboardMarkup()
    start_question_keyboard.add(types.InlineKeyboardButton(text="Да", callback_data="Да"))
    start_question_keyboard.add(types.InlineKeyboardButton(text="Нет", callback_data="Нет"))
    await bot.send_message(chat_id=user, text="Начнем?", reply_markup=start_question_keyboard)


@dp.callback_query_handler(state=States.prof)
async def question(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'Нет':
        await state.finish()
        await call.message.answer(text="Сюда мб текст надо добавить")
    else:
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
            await end_prof(call.message.chat.id, state)


async def end_prof(user, state):
    data = await state.get_data()
    user_score = []
    for i in ['sign','communication','art','technic','nature','business']:
        user_score.append(data[i]/cnt_types[i])
    user_score = np.array(user_score)
    user_df = pandas.DataFrame(columns=['Направление', 'Расстояние между векторами', 'url'])

    for i in range(0, 28):
        spec_score = np.array(spec_df.loc[i][1])
        user_df.loc[len(user_df.index)] = [spec_df.loc[i][0], norm(user_score-spec_score, ord=1), spec_df.loc[i][2]]
    user_df.sort_values(by='Расстояние между векторами')
    print(user_df)
    for i in range(0, 5):
        await bot.send_message(chat_id=user, text=f'{i+1} направление:\n'
                                             f'{user_df.loc[i][0]}\n'
                                             f'{user_df.loc[i][2]}')


    


executor.start_polling(dp, skip_updates=True)