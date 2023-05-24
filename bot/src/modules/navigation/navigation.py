from aiogram import types


class Navigation:
    @staticmethod
    def markup_settings(set_using):
        if set_using == 1:
            return types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
        else:
            return types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    @staticmethod
    def button(name_of_button='NoName'):
        return types.KeyboardButton(text=name_of_button)

    def start_menu(self):
        markup = self.markup_settings(0)

        sign_up_button = self.button('Регистрация')
        log_in_button = self.button('Войти')
        guests_button = self.button('Гость')

        markup.add(sign_up_button, log_in_button, guests_button)
        return markup

    def employee_profile_menu(self):
        markup = self.markup_settings(0)

        menu_meetings_meetings = self.button('Меню мероприятий')
        menu_meetings_volunteers = self.button('Отметить участников')
        show_list_of_volunteers = self.button('Список волонтеров')
        add_employee = self.button('Назначить работником')
        ratings_button = self.button('Рейтинг волонтеров')
        settings_button = self.button('Настройки')

        markup.add(menu_meetings_meetings,
                   menu_meetings_volunteers).add(show_list_of_volunteers,
                                                 add_employee).add(ratings_button, settings_button)
        return markup

    def employee_profile_meetings(self):
        markup = self.markup_settings(0)
        add_meeting = self.button('Добавить мероприятие')
        delete_meeting = self.button('Удалить мероприятие')
        show_list_of_meetings = self.button('Список мероприятий')
        back_button = self.button('Назад')
        markup.add(add_meeting, delete_meeting, show_list_of_meetings).add(back_button)

        return markup

    def employee_profile_users(self):
        markup = self.markup_settings(0)
        confirm_button = self.button('Меню отметок')
        qr_button = self.button('Автоматическая отметка')
        back_button = self.button('Назад')
        markup.add(confirm_button, qr_button).add(back_button)

        return markup

    def volunteer_profile_menu(self):
        markup = self.markup_settings(0)

        statistics = self.button('Моя статистика')
        leaving_early = self.button('Уйти раньше')
        join_meeting = self.button('Принять участие')
        confirm_meet = self.button('Подтвердить присутствие')
        show_list_of_meetings = self.button('Список мероприятий')
        settings_button = self.button('Настройки')
        info_button = self.button('Как работают баллы?')

        markup.add(statistics, join_meeting).add(confirm_meet,
                                                 leaving_early, show_list_of_meetings).add(info_button, settings_button)
        return markup

    def settings_menu(self):
        markup = self.markup_settings(0)

        change_name_button = self.button('Установить имя')
        change_surname_button = self.button('Установить фамилию')
        student_id_button = self.button('Установить номер студенческого')
        back_menu = self.button('Назад')

        markup.add(change_name_button, change_surname_button).add(back_menu, student_id_button)
        return markup

    def guest_menu(self):
        markup = self.markup_settings(0)

        sign_up_button = self.button('Регистрация')
        markup.add(sign_up_button)
        return markup

    def greeting_menu(self):
        markup = self.markup_settings(1)

        greeting_button = self.button('Привет')
        markup.add(greeting_button)
        return markup

    def get_location(self):
        markup = self.markup_settings(0)

        go_back_button = self.button('Назад')
        geo_button = types.KeyboardButton('Указать геопозицию', request_location=True)

        markup.add(geo_button).add(go_back_button)
        return markup

    def button_list(self):
        markup = self.markup_settings(0)

        button_back = self.button('Назад')
        markup.add(button_back)

        return markup

    def one_button_menu(self, name_of_button):
        markup = self.markup_settings(0)
        btn = self.button(name_of_button)

        markup.add(btn)
        return markup

    def two_button_menu(self, first_button, second_button, settings):
        markup = self.markup_settings(settings)

        f_btn = self.button(first_button)
        s_btn = self.button(second_button)
        back_button = self.button('Назад')

        markup.add(f_btn, s_btn).add(back_button)
        return markup

    def four_button_menu(self, buttons: list):
        markup = self.markup_settings(1)

        fi_btn = self.button(buttons[0])
        s_btn = self.button(buttons[1])
        t_btn = self.button(buttons[2])
        fo_btn = self.button(buttons[3])
        back_button = self.button('Назад')

        markup.add(fi_btn).add(s_btn).add(t_btn).add(fo_btn).add(back_button)
        return markup

    def choice_menu(self):
        markup = self.markup_settings(1)

        yes_button = self.button('Да')
        no_button = self.button('Нет')
        back_button = self.button('Назад')

        markup.add(yes_button, no_button).add(back_button)

        return markup
