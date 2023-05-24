from ..database import database
from ..navigation import navigation as nav


db = database.DataBase('database/database.db')
navigation = nav.Navigation()


class User:
    def __init__(self):
        pass

    @staticmethod
    def __get_menu_from_roles(role):
        roles = {'Employee': navigation.employee_profile_menu(),
                 'Volunteer': navigation.volunteer_profile_menu(),
                 'Guest': navigation.start_menu()}
        return roles[role]

    def get_markup(self, user_id):
        role = db.get_user_role(user_id)
        return self.__get_menu_from_roles(role)

    @staticmethod
    def get_user_role(user_id):
        return db.get_user_role(user_id)

    @staticmethod
    def get_employee_additional_menu(type_of_menu):
        set_type_of_menu = {'volunteer': navigation.employee_profile_users(),
                            'meetings': navigation.employee_profile_meetings()}
        return set_type_of_menu.get(type_of_menu)

    def open_additional_menu(self, user_id, type_of_menu='volunteer'):
        role = db.get_user_role(user_id)
        if role == 'Employee':
            return self.get_employee_additional_menu(type_of_menu)
        else:
            return self.__get_menu_from_roles(role)

    def check(self):
        pass
