from aiogram.dispatcher.filters.state import State, StatesGroup


class Registration(StatesGroup):
    confirmation = State()
    login = State()
    password = State()
    name_surname_group = State()
    confirm_personal_data = State()


class LogInProcess(StatesGroup):
    login = State()
    password = State()


class DeletingProfile(StatesGroup):
    confirmation = State()


class LeaveMeeting(StatesGroup):
    meeting_name = State()


class JoinMeeting(StatesGroup):
    meeting_name = State()


class ConfirmMeeting(StatesGroup):
    name_of_meeting = State()
    access_key = State()
    location = State()


class CreateMeeting(StatesGroup):
    confirmation = State()
    name_of_meeting = State()
    duration_of_meeting = State()
    date_of_meeting = State()


class AutoMarks(StatesGroup):
    name_of_meeting = State()
    set_mode = State()
    set_location = State()
    set_location2 = State()
    set_location2_confirm = State()
    finish_state = State()


class DeletingMeeting(StatesGroup):
    confirm = State()
    name_of_meeting = State()


class ChangeUserName(StatesGroup):
    new_user_name = State()


class ChangeUserSurname(StatesGroup):
    new_user_surname = State()


class ChangeUserGroup(StatesGroup):
    new_user_group = State()


class ConfirmAttend(StatesGroup):
    choose_type_of_mark = State()
    name_of_meeting = State()
    entering_hours = State()
    name_of_user = State()


class AddEmployee(StatesGroup):
    choose_user = State()
    confirmation = State()


class Greeting(StatesGroup):
    greeting = State()


class AnswerQuestion(StatesGroup):
    answer = State()
