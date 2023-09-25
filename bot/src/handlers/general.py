from aiogram.dispatcher.filters import Text
from aiogram import types
from aiogram.dispatcher import FSMContext
# from aiogram.contrib.fsm_storage.memory import MemoryStorage

from ..misc import dp, bot

from ..modules import database
from ..modules import user as us
from ..modules import functions as fn
from ..modules import navigation as nav

from ..modules.messages import general as messages
from ..modules.states.states_bt import *

from pyqrcode import create


db = database.DataBase('database/database.db')
user = us.User()
functions = fn.Functions()
navigation = nav.Navigation()


async def on_startup(_):
    print('[+] Have been started!')


key_words = ['2021', 'Сотрудничество', 'сотрудничество',
             'Мессенджер', 'мессенджер',
             'Специальность', 'специальность', '1961',
             'Роскосмос', 'роскосмос']

words_from_main_handler = ['Моя статистика', 'моя статистика',
                           'Гость',
                           'Как работают баллы?',
                           'Настройки',
                           'Профиль', 'профиль', 'меню', 'Назад',
                           'Меню мероприятий',
                           'Отметить участников',
                           'Список волонтеров',
                           'Рейтинг волонтеров',
                           'Список мероприятий']


async def alert_about_deleting_meeting(rus_name_of_meeting):
    base_of_users = db.list_of_all_users()
    for user_id in base_of_users:
        text = f'Мероприятие \"{rus_name_of_meeting}\" удалено!'
        await bot.send_message(user_id[0], text=text)


async def check_user_log(message):
    user_id = message.from_user.id
    if db.logged_verification(user_id) == 'logged':
        return 0
    else:
        markup = navigation.start_menu()
        await message.answer(text='Тебе нужно войти или зарегистрировться!', reply_markup=markup)
        return 0


async def check_user_role(message):
    user_id = message.from_user.id
    if db.get_user_role(user_id) != 'guest':
        return 0
    else:
        markup = navigation.start_menu()
        await message.answer(text='Тебе нужно войти или зарегистрировться!', reply_markup=markup)
        return 0


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text_greeting = f'Привет {message.from_user.first_name}!'
    user_id = message.from_user.id
    if db.logged_verification(user_id):
        markup = user.get_markup(user_id)
        await message.answer(text=text_greeting)
        await message.answer(text="Ты можешь перейти в наши сообщества, чтобы получить больше полезной информации 😉")
        await message.answer(text=" Telegram - https://t.me/volonterstankin \n VK - https://vk.com/volonterstankin",
                             reply_markup=markup)
        await message.delete()

    else:
        markup = navigation.start_menu()
        ID = db.count_of_users() + 1
        login = 'login' + str(ID)
        db.add_user(login, 'Guest', 1234, user_id, ID)
        await message.answer(text=text_greeting, reply_markup=markup)
        await message.delete()


@dp.message_handler(Text('Регистрация'), state=None)
async def choose_the_role(message: types.Message):
    markup = navigation.two_button_menu('Да', 'Нет', 1)

    await message.answer(text='Ты хочешь стать волонтером?', reply_markup=markup)
    await message.delete()

    await Registration.next()


@dp.message_handler(state=Registration.confirmation)
async def ask_for_login(message: types.Message, state: FSMContext):
    if message.text == 'Да':
        markup = navigation.button_list()
        await message.answer(text='''Введи свой логин: \nВ формате vc(номер студенческого) \nПример: vc123456''',
                             reply_markup=markup)

        await Registration.next()
    elif message.text == 'Нет':
        markup = navigation.guest_menu()
        await message.answer(text='Предлагаю посетить гостевую вкладку, чтобы узнать подробнее про бота!',
                             reply_markup=markup)
        await state.finish()
    elif message.text == 'Назад':
        markup = navigation.start_menu()
        await message.answer(text='Главное меню', reply_markup=markup)
        await state.finish()
    else:
        markup = navigation.start_menu()
        await message.answer(text='Ой.. Что-то пошло не так!', reply_markup=markup)
        await state.finish()


@dp.message_handler(state=Registration.login)
async def get_login_from_user(message: types.Message, state: FSMContext):
    login = message.text

    if message.text == 'Назад':
        markup = navigation.start_menu()
        await message.answer(text='Главное меню', reply_markup=markup)
        await state.finish()
    elif not (db.user_exists(login)):
        login.lower()
        if len(login) == 8 and login[:2] == 'vc':
            if functions.check_login_password(login):
                markup = navigation.button_list()
                await state.update_data(login=login)
                await message.answer(text='''Введи свой пароль: 
                                    \n⁃Используй английские строчные буквы без сиволов: / и @
                                    \n⁃Пароль должен быть длинной не больше 20 символов''', reply_markup=markup)

                await Registration.next()
            else:
                markup = navigation.start_menu()
                await message.answer(text='Ой.. Что-то пошло не так, попробуй еще раз!', reply_markup=markup)
                await state.finish()
        else:
            markup = navigation.start_menu()
            await message.answer(text='Логин введен неправильно!', reply_markup=markup)
            await state.finish()
    else:
        await message.answer(text='Пользователь с таким логином уже существует')
        await Registration.previous()


@dp.message_handler(state=Registration.password)
async def get_password_from_user(message: types.Message, state: FSMContext):
    password = message.text
    if message.text == 'Назад':
        markup = navigation.start_menu()
        await message.answer(text='Главное меню', reply_markup=markup)
        await state.finish()
    elif functions.check_login_password(password):
        markup = navigation.button_list()
        await state.update_data(password=password)
        await message.answer(text='''Укажи свое имя и свою фамилию в формате: \nИван Иванов''', reply_markup=markup)
        await Registration.next()
    else:
        markup = navigation.start_menu()
        await message.answer(text='Ой.. Пароль введен не правильно!', reply_markup=markup)
        await Registration.previous()


@dp.message_handler(state=Registration.name_surname_group)
async def get_personal_data(message: types.Message, state: FSMContext):
    answer = message.text.split()
    if answer[0] == 'Назад':
        markup = navigation.start_menu()
        await message.answer(text='Главное меню', reply_markup=markup)
        await state.finish()
    elif len(answer) != 1:
        name_and_surname = answer[:2]
        name = name_and_surname[0]
        await state.update_data(name=name)
        surname = name_and_surname[1]
        await state.update_data(surname=surname)
        text = f"""Ты правильно ввел данные? \n{name} {surname}"""
        markup = navigation.two_button_menu('Да', 'Нет', 1)
        await message.answer(text=text, reply_markup=markup)
        await Registration.next()
    else:
        markup = navigation.start_menu()
        await message.answer(text='Что-то пошло не так!', reply_markup=markup)
        await state.finish()


@dp.message_handler(state=Registration.confirm_personal_data)
async def get_personal_data(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == 'Да':
        data = await state.get_data()
        markup = navigation.one_button_menu('Войти')
        try:
            user_id = message.from_user.id
            login = data.get('login')
            role = 'Volunteer'
            password = data.get('password')
            name = data.get('name')
            surname = data.get('surname')
            student_id = login[2:]

            functions.add_user_to_database(user_id, name, surname, student_id, login, password, role)

            await message.answer(text='Ты можешь войти!', reply_markup=markup)
            await message.delete()
            await state.finish()
        except Exception as error:
            print(error)
            markup = navigation.start_menu()
            await message.answer(text='Ой.. Что-то пошло не так, попробуй еще раз!', reply_markup=markup)
            await state.finish()
    elif answer == 'Нет':
        await message.answer(text='''Укажи свое имя и свою фамилию в формате: \nИван Иванов''')
        await Registration.name_surname_group.set()
    else:
        await Registration.previous()


@dp.message_handler(Text('Войти'), state=None)
async def enter_login(message: types.Message):
    await message.answer(text='Введи свой логин:')
    await LogInProcess.login.set()


@dp.message_handler(state=LogInProcess.login)
async def enter_password(message: types.Message, state: FSMContext):
    login = message.text
    await state.update_data(login=login)

    await message.answer(text='Введи пароль:')
    await LogInProcess.next()


@dp.message_handler(state=LogInProcess.password)
async def checking_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    login = data.get('login')
    password = message.text
    user_id = message.from_user.id

    if db.user_verification(login, password):
        markup = user.get_markup(message.from_user.id)

        db.set_logged(user_id)
        await message.answer(text='Добро пожаловать в профиль!', reply_markup=markup)
    else:
        markup = navigation.start_menu()
        await message.answer(text='Не получилось войти! :(', reply_markup=markup)

    await state.finish()


@dp.message_handler(Text('Установить имя'), state=None)
async def get_new_user_name(message: types.Message):
    markup = navigation.one_button_menu('Назад')
    await message.answer(text='Введи свое имя:', reply_markup=markup)
    await ChangeUserName.new_user_name.set()


@dp.message_handler(state=ChangeUserName.new_user_name)
async def get_new_user_name(message: types.Message, state: FSMContext):
    markup = navigation.settings_menu()
    if message.text == 'Назад':
        await message.answer(text='Меню настроек', reply_markup=markup)
        await state.finish()
    else:
        name = message.text.split()[0]
        id_user = message.from_user.id
        db.set_users_name(id_user, name)
        await message.answer(text='Имя установлено!', reply_markup=markup)
        await state.finish()


@dp.message_handler(Text('Установить фамилию'), state=None)
async def get_new_user_surname(message: types.Message):
    markup = navigation.one_button_menu('Назад')
    await message.answer(text='Введи свою фамилию:', reply_markup=markup)
    await ChangeUserSurname.new_user_surname.set()


@dp.message_handler(state=ChangeUserSurname.new_user_surname)
async def get_new_user_surname(message: types.Message, state: FSMContext):
    markup = navigation.settings_menu()
    if message.text == 'Назад':
        await message.answer(text='Меню настроек', reply_markup=markup)
        await state.finish()
    else:
        surname = message.text.split()[0]
        id_user = message.from_user.id
        db.set_users_surname(id_user, surname)
        await message.answer(text='Фамилия установлена!', reply_markup=markup)
        await state.finish()


@dp.message_handler(Text('Установить номер студенческого'), state=None)
async def get_new_user_surname(message: types.Message):
    markup = navigation.one_button_menu('Назад')
    await message.answer(text='Введи свой номер студенческого:', reply_markup=markup)
    await ChangeUserGroup.new_user_group.set()


@dp.message_handler(state=ChangeUserGroup.new_user_group)
async def get_new_user_surname(message: types.Message, state: FSMContext):
    markup = navigation.settings_menu()
    student_id = message.text
    if message.text == 'Назад':
        await message.answer(text='Меню настроек', reply_markup=markup)
        await state.finish()
    elif len(student_id) == 6:
        student_id = message.text
        id_user = message.from_user.id
        db.set_users_student_id(id_user, student_id)
        await message.answer(text='Номер студенческого установлен!', reply_markup=markup)
        await state.finish()
    else:
        await message.answer(text='Некорректный ввод студенческого номера!', reply_markup=markup)
        await state.finish()


@dp.message_handler(Text('Уйти раньше'), state=None)
async def get_meeting_name(message: types.Message):
    markup = navigation.button_list()
    list_of_meetings = functions.show_volunteers_meetings_lists(message.from_user.id, "started_meetings")

    await message.answer(text=list_of_meetings)
    await message.answer(text="Введи номер мероприятия, с которого хочешь сейчас уйти:",
                         reply_markup=markup)
    await LeaveMeeting.meeting_name.set()


@dp.message_handler(state=LeaveMeeting.meeting_name)
async def try_to_join_meeting(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Твой профиль', reply_markup=markup)
        await state.finish()
    elif message.text.isdigit():
        number_of_meeting = int(message.text)
        user_id = str(message.from_user.id)
        meeting_name = functions.dict_elements.get(user_id).get(number_of_meeting)
        try:
            db.leave_early(meeting_name, message.from_user.id)
            functions.dict_elements.pop(user_id)
            markup = user.get_markup(message.from_user.id)
            await message.answer(text='Не забудь напомнить организатору, что ты ушел раньше!', reply_markup=markup)
            await state.finish()
        except NameError as error:
            print(error)
            functions.dict_elements.pop(user_id)
    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Ой... Что-то пошло не так!', reply_markup=markup)
        await state.finish()


@dp.message_handler(Text('Принять участие'), state=None)
async def get_meeting_name(message: types.Message):
    markup = navigation.button_list()
    list_of_meetings = functions.show_volunteers_meetings_lists(message.from_user.id, "choosing_meeting")
    meetings_to_join = list_of_meetings[0]
    meetings_joined = list_of_meetings[1]

    await message.answer(text=meetings_to_join)
    await message.answer(text=meetings_joined)
    await message.answer(text="Введи номер мероприятия, к которому хочешь присоединиться",
                         reply_markup=markup)
    await JoinMeeting.meeting_name.set()


@dp.message_handler(state=JoinMeeting.meeting_name)
async def try_to_join_meeting(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Твой профиль', reply_markup=markup)
        await state.finish()
    elif message.text.isdigit():
        user_id = str(message.from_user.id)
        number_of_meeting = int(message.text)
        meeting_name = functions.dict_elements.get(user_id).get(number_of_meeting)
        functions.dict_elements.pop(user_id)

        if not (db.get_user_meeting_exist(meeting_name, user_id)):
            try:
                db.join_meeting(meeting_name, message.from_user.id)

                markup = user.get_markup(message.from_user.id)
                await message.answer(text='Ты участвуешь!', reply_markup=markup)
                await state.finish()
            except NameError as error:
                print(error)
        else:
            markup = user.get_markup(message.from_user.id)
            await message.answer(text='Ты уже присоединился к этому мероприятию!', reply_markup=markup)
            await state.finish()
    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Введи число!', reply_markup=markup)
        await state.finish()


@dp.message_handler(Text('Подтвердить присутствие'), state=None)
async def try_join_meeting(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user.get_user_role(user_id) == "Volunteer":
        markup = navigation.button_list()
        text = functions.show_volunteers_meetings_lists(user_id, "confirm_attend")
        await message.answer(text=text, reply_markup=markup)
        await message.answer(text="Введи число:",
                             reply_markup=markup)

        await ConfirmMeeting.name_of_meeting.set()
    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='У тебя нет доступа!', reply_markup=markup)
        await state.finish()


@dp.message_handler(state=ConfirmMeeting.name_of_meeting)
async def check_access_key(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Твой профиль', reply_markup=markup)
        await state.finish()
    elif message.text.isdigit():
        user_id = str(message.from_user.id)
        number_of_meeting = int(message.text)
        if number_of_meeting in functions.dict_elements[user_id].keys():
            name_of_meeting = functions.dict_elements.get(user_id).get(number_of_meeting)
            functions.dict_elements.pop(user_id)
            if db.check_meeting_status(name_of_meeting) == 'started':
                await state.update_data(meeting_name=name_of_meeting)

                markup = navigation.one_button_menu('Назад')
                await message.answer(text='Введи ключ-доступа из qr-кода:', reply_markup=markup)
                await ConfirmMeeting.access_key.set()
            else:
                markup = user.get_markup(message.from_user.id)
                await message.answer(text='Мероприятие еще не началось!', reply_markup=markup)
                await state.finish()
        else:
            markup = user.get_markup(message.from_user.id)
            await message.answer(text='Такого мероприятия нет в списке!', reply_markup=markup)
            await state.finish()
    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Я не знаю такой команды, попробуй еще раз!', reply_markup=markup)
        await state.finish()


@dp.message_handler(state=ConfirmMeeting.access_key)
async def join_meeting(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Твой профиль', reply_markup=markup)
        await state.finish()
    else:
        access_key = message.text
        data = await state.get_data()
        meeting_name = data.get('meeting_name')

        if db.check_access_key(meeting_name, access_key):
            markup = navigation.get_location()
            await message.answer(text='Подтверди свою геопозицию, для подтверждения присутствия',
                                 reply_markup=markup)
            await ConfirmMeeting.location.set()
        else:
            markup = user.get_markup(message.from_user.id)
            await message.answer(text='Подтверждение не пройдено')
            await message.answer(text='Попробуй еще раз!', reply_markup=markup)
            await state.finish()


@dp.message_handler(state=ConfirmMeeting.location, content_types=['location'])
async def confirm_join(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == 'Назад':
        markup = user.get_markup(message.from_user.id)
        await message.answer('Процесс прерван', reply_markup=markup)
        await state.finish()
    else:
        latitude = message.location.latitude
        longitude = message.location.longitude
        data = await state.get_data()
        meeting_name = data.get('meeting_name')
        markup = user.get_markup(message.from_user.id)

        meeting_location = db.get_meeting_location(meeting_name)
        distance = functions.get_distance_between_users(meeting_location, (latitude, longitude))

        maximum_distance = db.get_meeting_distance(meeting_name)

        if distance < maximum_distance:
            points = db.get_points(message.from_user.id)
            hours = db.get_hours_of_meeting(meeting_name)
            points += hours
            db.mark_as_joined(meeting_name, message.from_user.id, points, latitude, longitude)
            await message.answer(text='Поздравляю, приятного время припровождения :)', reply_markup=markup)
            await state.finish()
        else:
            await message.answer(text='Ты находишься слишком далеко ;(', reply_markup=markup)
            await state.finish()


@dp.message_handler(Text('Добавить мероприятие'), state=None)
async def try_create_meeting(message: types.Message):
    user_id = message.from_user.id
    if user.get_user_role(user_id):
        markup = navigation.two_button_menu('Да', 'Нет', 1)
        await message.answer(text='Ты уверен?', reply_markup=markup)
        await CreateMeeting.next()
    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='У тебя нет доступа!', reply_markup=markup)


@dp.message_handler(state=CreateMeeting.confirmation)
async def enter_meeting_name(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        markup = user.get_markup(message.from_user.id)
        await message.answer('Мероприятие не создано', reply_markup=markup)
        await state.finish()
    elif message.text == 'Да':
        markup = navigation.button_list()
        await message.answer(text='Введи название мероприятия:', reply_markup=markup)
        await CreateMeeting.next()

    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Мероприятие не создано', reply_markup=markup)
        await state.finish()


@dp.message_handler(state=CreateMeeting.name_of_meeting)
async def enter_hours_meeting(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        markup = user.get_markup(message.from_user.id)
        await message.answer('Мероприятие не создано', reply_markup=markup)
        await state.finish()
    name_rus = message.text
    name = functions.transform_meeting_name(name_rus)
    await state.update_data(name_of_meeting=name)
    await state.update_data(rus_name_of_meeting=name_rus)

    await message.answer(text='Введи количество часов:')
    await CreateMeeting.next()


@dp.message_handler(state=CreateMeeting.duration_of_meeting)
async def enter_date_meeting(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        markup = user.get_markup(message.from_user.id)
        await message.answer('Мероприятие не создано', reply_markup=markup)
        await state.finish()
    elif message.text.isdigit():
        hours = int(message.text)
        await state.update_data(hours=hours)
        await message.answer(text='''Введи дату: \nВ формате ДЕНЬ.МЕСЯЦ.ГОД \n(XX.XX.XXXX)''')
        await CreateMeeting.next()
    else:
        await message.answer(text='Некоректный ввод часов!')
        await CreateMeeting.previous()


@dp.message_handler(state=CreateMeeting.date_of_meeting)
async def create_meeting(message: types.Message, state: FSMContext):
    date = message.text
    if len(date.split('.')) == 3 and len(date) == 10:
        data = await state.get_data()
        date = message.text
        name_of_meeting = data.get('name_of_meeting')
        rus_name_of_meeting = data.get('rus_name_of_meeting')
        hours = data.get('hours')

        try:
            db.create_meeting(name_of_meeting, date, 'planned', rus_name_of_meeting, hours)
            markup = user.get_markup(message.from_user.id)
            await message.answer(text='Мероприятие создано', reply_markup=markup)
        except Exception:
            markup = user.get_markup(message.from_user.id)
            await message.answer(text='Ой.. Что-то пошло не так, попробуй еще раз!', reply_markup=markup)
        finally:
            await state.finish()

    else:
        await message.answer(text='Некоректный ввод даты!')
        await message.answer(text='''Введи дату: \nВ формате ДЕНЬ.МЕСЯЦ.ГОД \n(XX.XX.XXXX)''')


@dp.message_handler(Text('Автоматическая отметка'), state=None)
async def get_location_of_employee(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if user.get_user_role(user_id):
        markup = navigation.button_list()
        text = functions.show_volunteers_meetings_lists(user_id, "meetings_for_confirmation")

        await message.answer(text=text, reply_markup=markup)
        await message.answer(text="Введи число:",
                             reply_markup=markup)
        await AutoMarks.name_of_meeting.set()
    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='У тебя нет доступа!', reply_markup=markup)
        await state.finish()


@dp.message_handler(state=AutoMarks.name_of_meeting)
async def get_location_of_employee(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Твой профиль', reply_markup=markup)
        await state.finish()
    else:
        if message.text.isdigit():
            number_of_meeting = int(message.text)
            user_id = str(message.from_user.id)
            if number_of_meeting in functions.dict_elements.get(user_id).keys():
                meeting_name = functions.dict_elements.get(user_id).get(number_of_meeting)
                functions.dict_elements.pop(user_id)
                await state.update_data(meeting_name=meeting_name)
                markup = navigation.choice_menu()
                await message.answer(text='Ты сможешь находится на мероприятии?', reply_markup=markup)
                await AutoMarks.next()
            else:
                markup = user.get_markup(message.from_user.id)
                await message.answer(text='Такого мероприятия нет в списке!', reply_markup=markup)
                await state.finish()
        else:
            markup = user.get_markup(message.from_user.id)
            await message.answer(text='Введи число!', reply_markup=markup)
            await state.finish()


@dp.message_handler(state=AutoMarks.set_mode)
async def get_location_of_employee(message: types.Message, state: FSMContext):
    answer = message.text
    mode = 0
    if message.text == 'Назад':
        markup = user.get_markup(message.from_user.id)
        await message.answer('Главное меню', reply_markup=markup)
        await state.finish()
    elif answer == 'Да':
        mode = 1
        markup = navigation.get_location()
        await message.answer(text='Укажи место встречи и напиши "Готово"', reply_markup=markup)
        await AutoMarks.set_location.set()
    elif answer == 'Нет':
        mode = 2
        await message.answer(text='''Введи адресс мероприятия: \n*Возьми точный адрес с карт* \nНапример из 2ГИС''')
        await AutoMarks.set_location2.set()
    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Мероприятие не было установлено!', reply_markup=markup)
        await state.finish()
    await state.update_data(mode=mode)


@dp.message_handler(state=AutoMarks.set_location, content_types=['location', 'text'])
async def creating_qr(message: types.Message, state: FSMContext):
    try:
        longitude = message.location.longitude
        latitude = message.location.latitude
        access_key = functions.generate_access_key()

        await state.update_data(longitude=longitude)
        await state.update_data(latitude=latitude)
        await state.update_data(access_key=access_key)

        await AutoMarks.finish_state.set()
    except Exception as error:
        print(error)
        answer = message.text
        if answer == 'Назад':
            markup = navigation.choice_menu()
            await message.answer(text='Ты сможешь находиться на мероприятии?', reply_markup=markup)
            await AutoMarks.set_mode.set()
        else:
            markup = user.get_markup(message.from_user.id)
            await message.answer(text='Что-то пошло не так!', reply_markup=markup)
            await state.finish()


@dp.message_handler(state=AutoMarks.set_location2)
async def set_location_mode2(message: types.Message, state: FSMContext):
    address = message.text
    data = functions.coordinates_form_address(address)

    longitude = data.get('longitude')
    latitude = data.get('latitude')
    access_key = functions.generate_access_key()

    full_address = data.get('address')

    await state.update_data(longitude=longitude)
    await state.update_data(latitude=latitude)
    await state.update_data(access_key=access_key)

    text = f"""Ты ввел правильный адресс?
            \n{full_address}"""
    markup = navigation.choice_menu()
    await message.answer(text=text, reply_markup=markup)

    await AutoMarks.set_location2_confirm.set()


@dp.message_handler(state=AutoMarks.set_location2_confirm)
async def confirm_location2(message: types.Message):
    answer = message.text
    if answer == 'Да':
        markup = navigation.one_button_menu('Продолжить')
        await message.answer(text='Скоро будет все готово...', reply_markup=markup)
        await AutoMarks.finish_state.set()
    elif answer == 'Нет':
        await message.answer(text='Введи адресс мероприятия:')
        await AutoMarks.previous()
    else:
        markup = navigation.choice_menu()
        await message.answer(text='Ты сможешь находиться на мероприятии?', reply_markup=markup)
        await AutoMarks.set_mode.set()


@dp.message_handler(state=AutoMarks.finish_state)
async def creating_qr(message: types.Message, state: FSMContext):
    data = await state.get_data()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    meeting_name = data.get('meeting_name')

    access_key = data.get('access_key')

    mode = data.get('mode')
    status = 'started'

    if mode == 1:
        await message.answer('Твой текст принят на обработку! \nПожалуйста, подожди')
        qr_code = create(access_key)
        distance = 100
        qr_code.png('qr_code.png', scale=6)

        with open('qr_code.png', 'rb') as code:
            await bot.send_photo(message.chat.id, code)

        db.set_data_before_creating_qr(meeting_name, latitude, longitude, access_key, distance, status)
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Твой QR-код готов', reply_markup=markup)

    if mode == 2:
        distance = 400
        db.set_data_before_creating_qr(meeting_name, latitude, longitude, access_key, distance, status)
        markup = user.get_markup(message.from_user.id)
        await bot.send_location(message.from_user.id, latitude=latitude, longitude=longitude)
        text = f'''Теперь к меропритию можно присоединиться! \nВот ключ доступа: {access_key}'''
        await message.answer(text=text, reply_markup=markup)

    await state.finish()


@dp.message_handler(Text('Назначить/разжаловать работника'), state=None)
async def add_to_list_of_employers(message: types.Message):
    user_id = str(message.from_user.id)
    role = user.get_user_role(user_id)
    if role == "Employee":
        list_of_users = functions.get_list_of_all_users(user_id)
        markup = navigation.button_list()

        await message.answer(text=list_of_users, reply_markup=markup)
        await message.answer(text="Введи действие и номер человека в списке:\nПример:\n\"Разжаловать 1\"\n\"Назначить 2\"",
                             reply_markup=markup)
        await AddEmployee.next()
    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='У тебя нет доступа', reply_markup=markup)


@dp.message_handler(state=AddEmployee.choose_user)
async def choose_user(message: types.Message, state: FSMContext):
    message_data = message.text.split()
    command = message_data[0]
    number_of_user = message_data[1]
    if number_of_user.isdigit():
        number_of_user = int(number_of_user)
        user_id_main = str(message.from_user.id)
        if number_of_user in functions.dict_elements.get(user_id_main).keys():
            user_id = functions.dict_elements.get(user_id_main).get(number_of_user)
            functions.dict_elements.pop(user_id_main)
            await state.update_data(user_id=user_id)
            data = db.get_user_name_surname_points(user_id)
            name, surname = data[0], data[1]
            user_role = db.get_user_role(user_id)
            if command == "Назначить":
                if user_role == "Volunteer":
                    await state.update_data(MODE=1)
                    text = f"Ты хочешь назначить {name} {surname} работником?"
                    markup = navigation.two_button_menu('Да', 'Нет', 1)
                    await message.answer(text=text, reply_markup=markup)
                    await AddEmployee.next()
                else:
                    markup = user.get_markup(message.from_user.id)
                    await message.answer(text="Пользователь уже является работником!", reply_markup=markup)
                    await state.finish()
            elif command == "Разжаловать":
                if user_role == "Employee":
                    await state.update_data(MODE=2)
                    text = f"Ты хочешь разжаловать {name} {surname}?"
                    markup = navigation.two_button_menu('Да', 'Нет', 1)
                    await message.answer(text=text, reply_markup=markup)
                    await AddEmployee.next()
                else:
                    markup = user.get_markup(message.from_user.id)
                    await message.answer(text="Пользователь уже является волонтером!", reply_markup=markup)
                    await state.finish()
        else:
            markup = user.get_markup(message.from_user.id)
            await message.answer(text="Такого пользователя нет в списке!", reply_markup=markup)
            await state.finish()

    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text="Пользователь не добавлен!", reply_markup=markup)
        await state.finish()


@dp.message_handler(state=AddEmployee.confirmation)
async def confirmation(message: types.Message, state: FSMContext):
    answer = message.text
    markup = user.get_markup(message.from_user.id)
    data = await state.get_data()
    user_id = data.get('user_id')
    mode = data.get('MODE')
    if answer == 'Да':
        if mode == 1:
            db.set_role('Employee', user_id)
            await message.answer(text='Пользователь теперь работник!', reply_markup=markup)
            await state.finish()
        elif mode == 2:
            db.set_role('Volunteer', user_id)
            await message.answer(text='Пользователь теперь волонтер!', reply_markup=markup)
            await state.finish()
    else:
        if mode == 1:
            await message.answer(text='Пользователь остался волонтером!', reply_markup=markup)
            await state.finish()
        elif mode == 2:
            await message.answer(text='Пользователь остался работником!', reply_markup=markup)
            await state.finish()


@dp.message_handler(Text('Меню отметок'), state=None)
async def try_to_confirm_join(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user.get_user_role(user_id):
        markup = navigation.two_button_menu('Присутствующие', 'Ушли раньше/Опоздали', 1)
        await message.answer(text="Выбери нужное меню", reply_markup=markup)
        await ConfirmAttend.next()

    else:
        markup = navigation.volunteer_profile_menu()
        await message.answer(text='У тебя нет доступа!', reply_markup=markup)
        await state.finish()


@dp.message_handler(state=ConfirmAttend.choose_type_of_mark)
async def get_username_for_confirm_attend(message: types.Message, state: FSMContext):
    type_of_menu = message.text
    await state.update_data(type_of_menu=type_of_menu)
    user_id = message.from_user.id
    if message.text == 'Назад':
        markup = navigation.employee_profile_menu()
        await message.answer(text='Твой профиль', reply_markup=markup)
        await state.finish()
    elif message.text == 'Присутствующие' or message.text == 'Ушли раньше/Опоздали':
        markup = navigation.button_list()

        text = functions.show_volunteers_meetings_lists(user_id, "meetings_for_confirmation")

        await message.answer(text=text, reply_markup=markup)
        await message.answer(text="Введи число:",
                             reply_markup=markup)
        await ConfirmAttend.next()
    else:
        answer = 'Ой... Что-то пошло не так!'
        markup = user.get_markup(message.from_user.id)
        await message.answer(text=answer, reply_markup=markup)


@dp.message_handler(state=ConfirmAttend.name_of_meeting)
async def get_username_for_confirm_attend(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        markup = navigation.employee_profile_menu()
        await message.answer(text='Твой профиль', reply_markup=markup)
        await state.finish()
    elif message.text.isdigit():
        number_of_meeting = int(message.text)
        user_id = str(message.from_user.id)
        if number_of_meeting in functions.dict_elements.get(user_id).keys():
            name_of_meeting = functions.dict_elements.get(user_id).get(number_of_meeting)
            functions.dict_elements.pop(user_id)
            await state.update_data(name_of_meeting=name_of_meeting)

            markup = navigation.button_list()
            data = await state.get_data()
            type_of_menu = data.get('type_of_menu')
            if type_of_menu == 'Присутствующие':
                list_of_not_joined_users = functions.show_users_list_meeting(name_of_meeting, 'waiting', user_id)
                text = list_of_not_joined_users
                await message.answer(text=text)
                await message.answer(text="Введи число:", reply_markup=markup)
                await ConfirmAttend.next()
            elif type_of_menu == 'Ушли раньше':
                list_of_leaved_early_users = functions.show_users_list_meeting(name_of_meeting, 'early', user_id)
                text = list_of_leaved_early_users
                await message.answer(text=text)
                await message.answer(text="Введи число:", reply_markup=markup)
                await ConfirmAttend.next()
        else:
            markup = navigation.employee_profile_menu()
            await message.answer(text='Такого мероприятия нет в списке!', reply_markup=markup)
            await state.finish()
    else:
        markup = navigation.employee_profile_menu()
        await message.answer(text='Ой... Что-то пошло не так!', reply_markup=markup)
        await state.finish()


@dp.message_handler(state=ConfirmAttend.entering_hours)
async def entering_hours(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        markup = navigation.employee_profile_menu()
        await message.answer(text='Твой профиль', reply_markup=markup)
        await state.finish()
    elif message.text.isdigit():
        user_id_main = str(message.from_user.id)
        if int(message.text) in functions.dict_elements.get(user_id_main).keys():
            number_of_user = int(message.text)
            user_id = str(functions.dict_elements.get(user_id_main).get(number_of_user))
            functions.dict_elements.pop(user_id_main)
            await state.update_data(user_id=user_id)
            data = await state.get_data()
            name_of_meeting = data.get('name_of_meeting')
            mark = db.get_user_mark(name_of_meeting, user_id)
            if mark == 'early':
                await message.answer(text="Введи количество часов:")
                await ConfirmAttend.next()
            elif mark == 'waiting':
                markup = navigation.one_button_menu('Продолжить')
                await message.answer(text="Если готов, нажимай на кнопку продолжить", reply_markup=markup)
                await ConfirmAttend.next()
        else:
            markup = navigation.employee_profile_menu()
            await message.answer(text='Такого пользователя в списке нет!', reply_markup=markup)
            await state.finish()
    else:
        markup = navigation.employee_profile_menu()
        await message.answer(text='Ой... Что-то пошло не так!', reply_markup=markup)
        await state.finish()


@dp.message_handler(state=ConfirmAttend.name_of_user)
async def confirm_attend(message: types.Message, state: FSMContext):
    if message.text == 'Назад':
        markup = navigation.employee_profile_menu()
        await message.answer(text='Профиль', reply_markup=markup)
        await state.finish()

    elif message.text == 'Продолжить' or message.text.isdigit():
        data = await state.get_data()
        name_of_meeting = data.get('name_of_meeting')
        user_id = data.get('user_id')
        mark = db.get_user_mark(name_of_meeting, user_id)
        hours = db.get_hours_of_meeting(name_of_meeting)
        if mark == 'early':
            early_leaved_hours = int(message.text)
            if hours > early_leaved_hours:
                points = int(db.get_points(user_id)) + early_leaved_hours

                db.mark_as_joined_not_auto(name_of_meeting, user_id, points)
                markup = user.get_markup(message.from_user.id)
                await message.answer(text='Участник отмечен!',
                                     reply_markup=markup)
                await state.finish()
            else:
                markup = user.get_markup(message.from_user.id)
                await message.answer(text='Участник не отмечен, мероприятие длилось меньше!',
                                     reply_markup=markup)
                await state.finish()

        elif mark == 'waiting':
            points = int(db.get_points(user_id)) + hours

            db.mark_as_joined_not_auto(name_of_meeting, user_id, points)
            markup = user.get_markup(message.from_user.id)
            await message.answer(text='Участник отмечен как присутствующий!', reply_markup=markup)
            await state.finish()
        else:
            markup = user.get_markup(message.from_user.id)
            await message.answer(text='Участник не отмечен как присутствующий!', reply_markup=markup)
            await state.finish()


@dp.message_handler(Text('Удалить мероприятие'), state=None)
async def confirm_deleting(message: types.Message):
    user_id = message.from_user.id
    role = user.get_user_role(user_id)
    if role == 'Employee':
        markup = navigation.two_button_menu('Да', 'Нет', 1)
        await message.answer(text='Ты уверен, что хочешь удалить мероприятие?', reply_markup=markup)
        await DeletingMeeting.confirm.set()
    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Мероприятие не удалено!', reply_markup=markup)


@dp.message_handler(state=DeletingMeeting.confirm)
async def enter_name_of_meeting(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    if message.text == 'Да':
        markup = navigation.button_list()
        list_of_meetings = functions.show_volunteers_meetings_lists(user_id, "meetings_for_confirmation")
        await message.answer(text=list_of_meetings, reply_markup=markup)
        await message.answer(text="Введи число:",
                             reply_markup=markup)
        await DeletingMeeting.next()
    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Мероприятие не удалено!', reply_markup=markup)
        await state.finish()


@dp.message_handler(state=DeletingMeeting.name_of_meeting)
async def enter_name_of_meeting(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        number_of_meeting = int(message.text)
        user_id = str(message.from_user.id)
        if number_of_meeting in functions.dict_elements.get(user_id).keys():
            name_of_meeting = functions.dict_elements.get(user_id).get(number_of_meeting)
            functions.dict_elements.pop(user_id)
            markup = user.get_markup(message.from_user.id)

            # функция для отправки excel
            excel_file = functions.convert_data_to_excel(name_of_meeting)

            with open(excel_file, 'rb') as file:
                await bot.send_document(message.chat.id, file)

            list_of_members = db.get_list_of_all_meeting_participants(name_of_meeting)
            count_of_members = len(list_of_members)
            hours = db.get_hours_of_meeting(name_of_meeting)

            text1 = f"""Вот excel-файл со всей нужной информацией :) """
            text2 = f"""\nОбщее количество участников: {count_of_members}"""
            text3 = f""" \nКоличество часов: {hours}"""
            text = text1 + text2 + text3
            await message.answer(text=text, reply_markup=markup)

            name_rus = db.get_rus_meeting_name(name_of_meeting)
            await alert_about_deleting_meeting(name_rus)
            db.delete_meeting(name_of_meeting)

            await state.finish()
        else:
            markup = user.get_markup(message.from_user.id)
            await message.answer(text='Такого мероприятия нет в списке!', reply_markup=markup)
            await state.finish()
    else:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Мероприятие не удалено!', reply_markup=markup)
        await state.finish()


@dp.message_handler(Text(words_from_main_handler))
async def main_handler(message: types.Message):
    text_of_message = message.text
    user_id = message.from_user.id

    if db.logged_verification(user_id) == 'logged':
        if db.get_user_role(user_id) == "guest":
            markup = navigation.start_menu()
            await message.answer(text='Тебе нужно войти или зарегистрировться!', reply_markup=markup)
        else:
            if text_of_message in ['Моя статистика', 'моя статистика', 'статистика']:
                markup = user.get_markup(message.from_user.id)
                text = functions.generate_ratings(user_id, 'volunteer')
                await message.answer(text=text, reply_markup=markup)

            elif text_of_message == 'Гость':
                markup = navigation.guest_menu()
                alert = messages.message_for_guest
                await message.answer(text=alert, reply_markup=markup)
                await message.delete()

            elif text_of_message == 'Как работают баллы?':
                user_id = message.from_user.id
                markup = user.get_markup(user_id)
                text = messages.information_about_points
                await message.answer(text=text, parse_mode='HTML', reply_markup=markup)

            elif text_of_message == 'Настройки':
                markup = navigation.settings_menu()
                await message.answer(text='Меню настроек', reply_markup=markup)

            elif text_of_message in ['Профиль', 'профиль', 'меню', 'Назад']:
                user_id = message.from_user.id
                markup = user.get_markup(user_id)
                await message.answer(text='Твой профиль', reply_markup=markup)

            elif text_of_message == 'Меню мероприятий':
                user_id = message.from_user.id
                markup = user.open_additional_menu(user_id, 'meetings')
                await message.answer(text='Меню мероприятий', reply_markup=markup)

            elif text_of_message == 'Отметить участников':
                user_id = message.from_user.id
                if user.get_user_role(user_id) == "Employee":
                    markup = user.open_additional_menu(user_id, 'volunteer')
                    await message.answer(text='Отметить участников', reply_markup=markup)
                else:
                    markup = user.get_markup(user_id)
                    await message.answer(text='У тебя нет доступа!', reply_markup=markup)

            elif text_of_message == 'Список волонтеров':
                user_id = message.from_user.id
                role = user.get_user_role(user_id)
                if role == "Employee":
                    list_of_volunteers = functions.show_volunteers_list()
                    markup = user.get_markup(message.from_user.id)
                    await message.answer(text=list_of_volunteers, reply_markup=markup)
                else:
                    markup = user.get_markup(message.from_user.id)
                    await message.answer(text="У тебя нет доступа!", reply_markup=markup)

            elif text_of_message == 'Рейтинг волонтеров':
                user_id = message.from_user.id
                role = user.get_user_role(user_id)
                if role == "Employee":
                    volunteers_rating = functions.generate_ratings(user_id, role)
                    markup = user.get_markup(message.from_user.id)
                    await message.answer(text=volunteers_rating, reply_markup=markup)
                else:
                    markup = user.get_markup(message.from_user.id)
                    await message.answer(text="У тебя нет доступа!", reply_markup=markup)

            elif text_of_message == 'Список мероприятий':
                user_id = str(message.from_user.id)
                employee = user.get_user_role(user_id)
                if employee:
                    list_of_meetings = functions.show_volunteers_meetings_lists(user_id, "show_notFinished_meetings")
                    answer = list_of_meetings
                    markup = user.get_markup(message.from_user.id)
                    await message.answer(text=answer, reply_markup=markup)
                elif not employee:
                    list_of_meetings = functions.show_volunteers_meetings_lists(user_id, "available_meetings")
                    answer1 = list_of_meetings[0]
                    answer2 = list_of_meetings[1]
                    markup = user.get_markup(message.from_user.id)
                    await message.answer(text=answer1, reply_markup=markup)
                    await message.answer(text=answer2, reply_markup=markup)
                else:
                    answer = 'Ой... Что-то пошло не так!'
                    markup = user.get_markup(message.from_user.id)
                    await message.answer(text=answer, reply_markup=markup)
    else:
        markup = navigation.start_menu()
        await message.answer(text='Тебе нужно войти или зарегистрировться!', reply_markup=markup)


@dp.message_handler()
async def echo(message: types.Message):
    try:
        markup = user.get_markup(message.from_user.id)
        await message.answer(text='Я не знаю такой команды, нажимай на кнопки в профиле! :)',
                             reply_markup=markup)
    except Exception as error:
        print(error)
        markup = navigation.start_menu()
        await message.answer(text='Тебе нужно зарегистрироваться, напиши \'/start\'',
                             reply_markup=markup)


@dp.message_handler(Text(key_words))
async def get_secret_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        role = db.get_user_role(user_id)
        if role == 'guest':
            markup = navigation.start_menu()
            await message.answer(text='Привет! :) Чтобы учавствовать в опросе, нужно пройти регистрацию!',
                                 reply_markup=markup)
        else:
            questions = {'2021': 'Как отмечали день космонавтики в 2021 году?',
                         'Сотрудничество': 'Какая космическая компания сотрудничает со станкином?',
                         'Мессенджер': 'Кто был основоположник теории межпланетных сообщений? Он первым изучил вопрос о ракете, высказал идею создания околоземных станций, рассмотрел вопросы о медико-биологических проблемах, возникающих при длительных космических полетах',
                         'Специальность': 'Какие направления подготовки могут быть напрямую связаны с космосом?',
                         '1961': 'В 1961 вместе с выходом первого человека в космос в Станкине появилась новое направление подготовки. Как оно называлось?',
                         'Роскосмос': '31 мая в 2022 году Генеральный директор роскосмоса вручил сертификат опорного вуза одному из сотрудников нашего университета. Кому был вручен этот сертификат?'}
            buttons = {'2021': ['Cтуденты устроили флешмоб, запустив десятки цветных шаров и выстроившись в число «60»',
                                'Cтуденты смогли запустить модель ракеты в небо на высоту 270 метров',
                                'Cтуденты смотрели трансляцию форума «Знание», на котором выступал Илон Маск',
                                'Cтуденты посетили музей космонавтики на вднх'],
                       'Сотрудничество': ['НПО «Андроидная техника»',
                                          'Роскосмос и АО «ГКНПЦ им. М.В. Хруничева',
                                          'Ростех',
                                          'SpaceX'],
                       'Мессенджер': ['Юрий Алексеевич Гагарин',
                                      'Исаак Ньютон',
                                      'Сергей Павлович Королев',
                                      'Константин Эдуардович Циолковский'],
                       'Специальность': ['Экология/Станкостроение',
                                         'Машиностроение/робототехника/метрология и стандартизация',
                                         'Экономика/Автоматизация технологических процессов и производств',
                                         'Информатика и вычислительная техника'],
                       '1961': ['Автоматизация',
                                'Мехатроника и робототехника',
                                'Техносферная безопасность',
                                'Метрология и стандартизация'],
                       'Роскосмос': ['Проректору по производственному развитию и технологиям',
                                     'Ректору',
                                     'Проректору по научной деятельности',
                                     'Проректору по образовательной деятельности и молодежной политике']}
            encrypt = {'2021': 'twenty',
                       'Сотрудничество': 'sotrudnichestvo',
                       'Мессенджер': 'messendger',
                       'Специальность': 'specialnost',
                       '1961': 'sixty',
                       'Роскосмос': 'roscosmos'}
            key_word = message.text.capitalize()
            question = questions.get(key_word)
            buttons_for_question = buttons.get(key_word)
            encrypt_question = encrypt.get(key_word)
            if question is not None:
                db.add_user_to_quiz(user_id)
                if not (db.get_info_about_question_by_user_id(user_id, encrypt_question)):
                    markup = navigation.four_button_menu(buttons_for_question)

                    await state.update_data(key_word=key_word)
                    await AnswerQuestion.next()
                    await message.answer(text=question, reply_markup=markup)
                else:
                    markup = user.get_markup(user_id)
                    await message.answer(text="Извини, но ты уже отвечал на этот вопрос!",
                                         reply_markup=markup)
                    await state.finish()
    except Exception:
        markup = navigation.start_menu()
        await message.answer(text='Привет! :) Чтобы учавствовать в опросе, нужно пройти регистрацию!',
                             reply_markup=markup)


@dp.message_handler(state=AnswerQuestion)
async def get_answer(message: types.Message, state: FSMContext):
    answers = {'2021': 'Cтуденты устроили флешмоб, запустив десятки цветных шаров и выстроившись в число «60»',
               'Сотрудничество': 'Роскосмос и АО «ГКНПЦ им. М.В. Хруничева',
               'Мессенджер': 'Константин Эдуардович Циолковский',
               'Специальность': 'Машиностроение/робототехника/метрология и стандартизация',
               '1961': 'Автоматизация',
               'Роскосмос': 'Ректору'}
    encrypt = {'2021': 'twenty',
               'Сотрудничество': 'sotrudnichestvo',
               'Мессенджер': 'messendger',
               'Специальность': 'specialnost',
               '1961': 'sixty',
               'Роскосмос': 'roscosmos'}
    data = await state.get_data()
    key_word = data.get('key_word')
    answer = answers.get(key_word)
    user_answer = message.text
    question = encrypt.get(key_word)
    user_id = message.from_user.id

    if user_answer == answer:
        db.set_info_about_question_by_user_id(user_id, question)
        points = db.get_points(user_id) + 1
        db.add_points(user_id, points)
        markup = user.get_markup(user_id)
        await message.answer(text="Поздравляю ты правильно ответил на вопрос, и мы зачислили тебе 1 балл!",
                             reply_markup=markup)
        await state.finish()
    else:
        markup = user.get_markup(user_id)
        db.set_info_about_question_by_user_id(user_id, question)
        await message.answer(text="К сожалению ответ неправильный :(",
                             reply_markup=markup)
        await state.finish()