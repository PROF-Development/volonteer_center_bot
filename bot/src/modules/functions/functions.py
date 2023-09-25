import pandas
from transliterate import translit
from geopy import distance
from geopy.geocoders import Nominatim
from random import randint
from ..database.database import DataBase

db = DataBase('database/database.db')


class Functions:
    def __init__(self):
        self.dict_elements = {}
        self.ratings = {}
        self.len_of_key = 10
        self.digits = '0123456789'
        self.letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.spec_symbols = '-_!#$&?'
        self.dict_of_digits = {1: 'First', 2: 'Second', 3: 'Third',
                               4: 'Fourth', 5: 'Fifth', 6: 'Sixth',
                               7: 'Seventh', 8: 'Eighth', 9: 'Ninth'}
        self.symbols_for_access_key = self.digits + self.letters

    def check_login_password(self, to_check):
        if len(to_check) <= 20:
            for index in range(len(to_check)):
                symbol = to_check[index]
                if symbol != '/' and symbol != '@' and (
                        symbol in self.letters or symbol in self.spec_symbols or symbol in self.digits):
                    continue
                else:
                    return False
            return True
        else:
            return False

    @staticmethod
    def transform_meeting_name(name):
        meeting_name = translit(name, language_code='ru', reversed=True)
        arr = meeting_name.split(' ')

        for index in range(len(arr)):
            word = arr[index]
            word = word.replace('\'', '')
            arr[index] = word.capitalize()

        meeting_name = ''.join(arr)

        return meeting_name

    def generate_ratings(self, user_id_main: str, user_role):
        list_of_volunteers = db.get_list_of_volunteers()
        self.ratings[user_id_main] = {}
        for user in list_of_volunteers:
            user_id = user[1]
            users_points = user[6]
            self.ratings[user_id_main][user_id] = users_points

        self.ratings[user_id_main] = dict(sorted(self.ratings[user_id_main].items(),
                                                 key=lambda item: item[1], reverse=True))

        if user_role == 'volunteer':
            return self.write_ratings(user_id_main)
        else:
            return self.write_ratings_for_employee(user_id_main)

    def write_ratings_for_employee(self, user_id_main):
        text = """Топ волонтеров:"""

        user_number = 1
        for user_id in self.ratings[user_id_main].keys():
            data = db.get_user_name_surname_points(user_id)
            name = data[0]
            surname = data[1]
            points = self.ratings[user_id_main][user_id]
            text += f"\n{user_number}. {surname} {name} {points} баллов"
            user_number += 1

        return text

    def write_ratings(self, user_id_main: str):
        points = self.ratings[user_id_main][user_id_main]
        text = f"""На данный момент у тебя {points} баллов \nТоп волонтеров:"""

        number_of_user_in_top = 1
        for user_id in self.ratings[user_id_main].keys():
            points = self.ratings[user_id_main][user_id]
            if points != 0:
                data = db.get_user_name_surname_points(user_id)
                name = data[0]
                surname = data[1]
                text += f"\n{number_of_user_in_top}. {surname} {name} {points} баллов"
                number_of_user_in_top += 1
            if number_of_user_in_top == 6:
                break

        if number_of_user_in_top == 1:
            text += f"\nВ топе пока что никого нет, стань первым!"

        return text

    @staticmethod
    def add_user_to_database(user_id, name, surname, student_id, login, password, role):
        db.register_user(login, role, password, user_id)
        db.set_users_name(user_id, name)
        db.set_users_surname(user_id, surname)
        db.set_users_student_id(user_id, student_id)

    def get_list_of_all_users(self, user_id_main):
        roles_dict = {
            "Employee": "Работник",
            "Volunteer": "Волонтер"
        }
        data = db.list_of_all_users()
        number = 1
        data = sorted(data)
        user_id_main = str(user_id_main)
        self.dict_elements[user_id_main] = {}
        result = "Выберите участника:\n"
        for participant in data:
            user_id = participant[2]
            user_role = roles_dict.get(db.get_user_role(user_id))
            name = participant[1]
            surname = participant[0]
            self.dict_elements[user_id_main][number] = int(user_id)
            result += f"{number}. {surname} {name} - {user_role}\n"
            number += 1
        return result

    def show_volunteers_meetings_lists(self, user_id, type_of_list: str):
        """Бывшая show_meetings_list_volunteer

        Эта функция заменила:
        - show_started_meetings_list_volunteer
        - show_meetings_list_volunteer_confirm
        - show_meetings_list_for_attend
        - show_meetings"""
        user_id = str(user_id)
        if type_of_list == "started_meetings":
            list_of_meetings = db.get_list_of_user_started_meetings()
        else:
            list_of_meetings = db.get_list_of_meetings_by_name()

        lists = {"available_meetings": 'Доступные мероприятия:',
                 "choosing_meeting": 'Выбери мероприятие:',
                 "started_meetings": 'Мероприятия, которые сейчас идут:',
                 "confirm_attend": 'Выбери мероприятие:',
                 "meetings_for_confirmation": 'Выбери мероприятие:',
                 "show_notFinished_meetings": 'Список мероприятий:'}

        text = lists[type_of_list]
        text2 = 'Мероприятия, в которых ты учавствуешь:'
        count_of_elem = 1
        count_of_elem2 = 1

        dict_of_meetings = {}
        self.dict_elements[user_id] = {}
        meetings = []
        for name_of_meeting in list_of_meetings:
            meeting_name_rus = db.get_rus_meeting_name(name_of_meeting[0])
            dict_of_meetings[meeting_name_rus] = name_of_meeting
            meetings.append(meeting_name_rus)

        meetings.sort()

        if type_of_list == "confirm_attend" or type_of_list == 'started_meetings':

            for meeting_name_rus in meetings:
                name_of_meeting = dict_of_meetings[meeting_name_rus][0]
                if db.check_meeting_status(name_of_meeting) != 'finished':
                    if db.get_user_meeting_exist(name_of_meeting, user_id):
                        if db.get_user_mark(name_of_meeting, user_id) == 'waiting':
                            text += f'\n {count_of_elem}. «{meeting_name_rus}»'
                            self.dict_elements[user_id][int(count_of_elem)] = name_of_meeting
                            count_of_elem += 1
                        if db.get_user_mark(name_of_meeting, user_id) == 'joined' \
                                and type_of_list == 'started_meetings':
                            text += f'\n {count_of_elem}. «{meeting_name_rus}»'
                            self.dict_elements[user_id][int(count_of_elem)] = name_of_meeting
                            count_of_elem += 1
        else:
            for meeting_name_rus in meetings:
                meeting = dict_of_meetings.get(meeting_name_rus)[0]
                if db.check_meeting_status(meeting) != 'finished':
                    if not (db.get_user_meeting_exist(meeting, user_id)):
                        date = db.get_meeting_date(meeting)
                        text += f'\n {count_of_elem}. «{meeting_name_rus}» {date}'
                        self.dict_elements[user_id][int(count_of_elem)] = meeting
                        count_of_elem += 1
                    else:
                        meeting_name_rus = db.get_rus_meeting_name(meeting)
                        text2 += f'\n {count_of_elem2}. «{meeting_name_rus}»'
                        count_of_elem2 += 1

        if type_of_list == "available_meetings" or type_of_list == "choosing_meeting":
            return text, text2
        else:
            return text

    def show_users_list_meeting(self, meeting_name, mark, user_id_main):
        list_of_users = db.get_list_of_special_users(meeting_name, mark)
        text = 'Выбери человека:'

        number_of_user = 1
        self.dict_elements[user_id_main] = {}
        for user_id in list_of_users:
            user_name_surname = db.get_user_name_surname_points(user_id[0])
            name = user_name_surname[0]
            surname = user_name_surname[1]
            text += f'\n {number_of_user}. {name} {surname}'
            self.dict_elements[user_id_main][int(number_of_user)] = user_id[0]
            number_of_user += 1

        return text

    def show_users_list(self, user_id_main):
        volunteers_id_list = db.get_volunteers_list()
        self.dict_elements[user_id_main] = {}
        if volunteers_id_list is not None:
            list_of_users = "Выбери участника:"
            number_of_user = 1

            dictionary_of_users = {}
            surnames = []
            for user_id in volunteers_id_list:
                user_id = user_id[0]
                data = db.get_user_name_surname_points(user_id)
                user_name, user_surname = data[0], data[1]
                dictionary_of_users[user_surname] = [user_name, user_id]
                surnames.append(user_surname)

            surnames.sort()

            for surname in surnames:
                user_id = dictionary_of_users.get(surname)[1]
                name = dictionary_of_users.get(surname)[0]
                list_of_users += f'\n {number_of_user}. {surname} {name}'
                self.dict_elements[user_id_main][int(number_of_user)] = user_id
                number_of_user += 1
            return list_of_users
        else:
            return None

    @staticmethod
    def show_volunteers_list():
        volunteers_id_list = db.get_list_of_volunteers()
        volunteers_list = 'Список волонтеров:'
        dictionary_of_users = {}
        surnames = []
        for user_id in volunteers_id_list:
            user_id = user_id[1]
            data = db.get_user_name_surname_points(user_id)
            user_name, user_surname, user_points = map(str, data)
            dictionary_of_users[user_surname] = [user_name, user_points]
            surnames.append(user_surname)

        surnames.sort()

        number_of_volunteer = 1
        for surname in surnames:
            data = dictionary_of_users.get(surname)
            name = data[0]
            points = data[1]
            volunteers_list += f'\n {number_of_volunteer}. {surname} {name}: {points}'
            number_of_volunteer += 1

        return volunteers_list

    def generate_access_key(self):
        access_key = ''
        for i in range(self.len_of_key):
            symbol = self.symbols_for_access_key[randint(0, len(self.symbols_for_access_key) - 1)]
            access_key += symbol

        return access_key

    @staticmethod
    def get_distance_between_users(coordinates_of_employees=(0, 0), coordinates_of_volunteer=(0, 0)):
        coordinates_of_volunteer = coordinates_of_volunteer
        coordinates_of_employee = coordinates_of_employees

        result = distance.distance(coordinates_of_employee, coordinates_of_volunteer).meters

        return result

    @staticmethod
    def convert_data_to_excel(name_of_meeting):
        rus_name_of_meeting = db.get_rus_meeting_name(name_of_meeting)
        list_of_members = db.get_list_of_all_meeting_participants(name_of_meeting)
        file_name = f'{rus_name_of_meeting}.xlsx'

        data_frame = {'Имя': [],
                      'Фамилия': [],
                      'Номер студенческого': [], '': ''}

        for user in list_of_members:
            user_id = user[0]
            user_personal_data = db.get_user_name_surname_points(user_id)
            name = user_personal_data[0]
            surname = user_personal_data[1]
            student_id = db.get_user_student_id(user_id)

            data_frame['Имя'].append(name)
            data_frame['Фамилия'].append(surname)
            data_frame['Номер студенческого'].append(student_id)

        data_frame = pandas.DataFrame(data_frame)
        data_frame.to_excel(file_name)
        return file_name

    @staticmethod
    def coordinates_form_address(address):
        geolocator = Nominatim(user_agent='Location_checker')
        location = geolocator.geocode(address)
        result = {'address': location,
                  'longitude': location.longitude,
                  'latitude': location.latitude}

        return result
