import sqlite3


class DataBase:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def get_info_about_question_by_user_id(self, user_id, question):
        with self.connection:
            result = self.cursor.execute(f"SELECT {question} FROM quiz WHERE user_id = ?;",
                                         (user_id,)).fetchone()[0]
        return bool(result)

    def set_info_about_question_by_user_id(self, user_id, question):
        with self.connection:
            self.cursor.execute(f"UPDATE quiz SET {question} = ? WHERE user_id = ?;",
                                (1, user_id,))
        self.connection.commit()

    def add_user_to_quiz(self, user_id):
        with self.connection:
            if not (self.get_user_exist_to_quiz(user_id)):
                self.cursor.execute(f"INSERT INTO quiz (user_id) VALUES (?);",
                                    (user_id,))
            else:
                pass
        self.connection.commit()

    def get_user_exist_to_quiz(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT * FROM quiz WHERE user_id = ?;",
                                         (user_id,)).fetchall()
        return bool(len(result))

    def list_of_all_users(self):
        with self.connection:
            list_of_users = self.cursor.execute("SELECT user_id FROM users;").fetchall()
        return list_of_users

    def count_of_users(self):
        with self.connection:
            count = self.cursor.execute("SELECT * FROM users;").fetchall()

        return len(count)

    def user_exists(self, user_id):
        with self.connection:
            searching = self.cursor.execute("SELECT * FROM users WHERE user_id = ?;",
                                            (user_id,)).fetchall()
            return bool(len(searching))

    def logged_verification(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT logged FROM users WHERE user_id = ?;",
                                         (user_id,)).fetchone()
            return result[0]

    def add_user(self, login, role, password, user_id, ID):
        with self.connection:
            self.cursor.execute("INSERT INTO users (login, role, password, user_id, ID) VALUES (?, ?, ?, ?, ?);",
                                (login, role, password, user_id, ID,))
            self.cursor.execute("INSERT INTO personal_data (user_id, ID) VALUES (?, ?);",
                                (user_id, ID,))

        self.connection.commit()

    def register_user(self, login, role, password, user_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET login = ?, role = ?, password = ? WHERE user_id = ?;",
                                (login, role, password, user_id,))

        self.connection.commit()

    def user_verification(self, login, password):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE (login = ? AND password = ?);",
                                         (login, password,)).fetchall()
            return bool(len(result))

    def set_logged(self, user_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET logged = ? WHERE user_id = ?;", ('logged', user_id,))
        self.connection.commit()

    def set_users_name(self, user_id, name):
        with self.connection:
            self.cursor.execute("UPDATE personal_data SET name = ? WHERE user_id = ?;", (name, user_id,))
        self.connection.commit()

    def set_users_surname(self, user_id, surname):
        with self.connection:
            self.cursor.execute("UPDATE personal_data SET surname = ? WHERE user_id = ?;", (surname, user_id,))
        self.connection.commit()

    def set_users_student_id(self, user_id, student_id):
        with self.connection:
            self.cursor.execute("UPDATE personal_data SET student_id = ? WHERE user_id = ?;", (student_id, user_id,))
        self.connection.commit()

    def get_user_name_surname_points(self, user_id):
        with self.connection:
            name = self.cursor.execute("SELECT name FROM personal_data WHERE user_id = ?;",
                                       (user_id,)).fetchone()[0]
            surname = self.cursor.execute("SELECT surname FROM personal_data WHERE user_id = ?;",
                                          (user_id,)).fetchone()[0]
            points = self.cursor.execute("SELECT points FROM users WHERE user_id = ?;",
                                         (user_id,)).fetchone()[0]
            return name, surname, points

    def get_user_role(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT role FROM users WHERE user_id = ?",
                                         (user_id,)).fetchone()
            if result is not None:
                return result[0]
            else:
                return None

    def get_volunteers_list(self):
        with self.connection:
            list_of_users = self.cursor.execute("SELECT user_id FROM users WHERE role = ?;", ('Volunteer',)).fetchall()
        return list_of_users

    def get_user_student_id(self, user_id):
        result = self.cursor.execute("SELECT student_id FROM personal_data WHERE user_id = ?",
                                     (user_id,)).fetchone()
        return result[0]

    def get_user_id_by_login(self, login):
        with self.connection:
            result = self.cursor.execute("SELECT user_id FROM users WHERE login = ?",
                                         (login,)).fetchone()
            return result[0]

    def get_user_login_by_id(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT login FROM users WHERE user_id = ?",
                                         (user_id,)).fetchone()
            return result[0]

    def create_meeting(self, name_of_meeting, date, status, name_rus, hours):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO meetings (name_meeting, date, status, name_rus, hours) VALUES (?, ?, ?, ?, ?);",
                (name_of_meeting, date, status, name_rus, hours,))
            self.cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {name_of_meeting} (user_id TEXT, mark TEXT, latitude INT, longitude INT);")
        self.connection.commit()

    def delete_meeting(self, name_of_meeting):
        with self.connection:
            self.cursor.execute("UPDATE meetings SET status = ? WHERE name_meeting = ?;",
                                ('finished', name_of_meeting,))
            self.cursor.execute(f"DROP TABLE {name_of_meeting};")

        self.connection.commit()

    def set_data_before_creating_qr(self, name_of_meeting, latitude, longitude, access_key, distance, status):
        with self.connection:
            self.cursor.execute("UPDATE meetings SET latitude = ? WHERE name_meeting = ?;",
                                (latitude, name_of_meeting,))
            self.cursor.execute("UPDATE meetings SET longitude = ? WHERE name_meeting = ?;",
                                (longitude, name_of_meeting,))
            self.cursor.execute("UPDATE meetings SET access_key = ? WHERE name_meeting = ?;",
                                (access_key, name_of_meeting,))
            self.cursor.execute("UPDATE meetings SET distance = ? WHERE name_meeting = ?;",
                                (distance, name_of_meeting,))
            self.cursor.execute("UPDATE meetings SET status = ? WHERE name_meeting = ?;",
                                (status, name_of_meeting,))
        self.connection.commit()

    def get_list_of_meetings_by_name(self):
        with self.connection:
            search = self.cursor.execute("SELECT name_meeting FROM meetings;").fetchall()
        return search

    def get_list_of_user_started_meetings(self):
        with self.connection:
            search = self.cursor.execute("SELECT name_meeting FROM meetings WHERE status = ?;",
                                         ('started',)).fetchall()
        return search

    def get_list_of_special_users(self, name_meeting, mark):
        """special means not joined or leaved early users"""
        with self.connection:
            search = self.cursor.execute(f"SELECT user_id FROM {name_meeting} WHERE mark = ?;", (mark,)).fetchall()
        return search

    def get_list_of_all_meeting_participants(self, name_of_meeting):
        with self.connection:
            list_of_members = self.cursor.execute(f"SELECT user_id FROM {name_of_meeting}").fetchall()
        return list_of_members

    def get_list_of_waiting_participants(self, table_name):
        with self.connection:
            search = self.cursor.execute(f"SELECT user_id FROM {table_name} WHERE mark = ?;",
                                         ('waiting',)).fetchall()
            return search

    def get_list_of_volunteers(self):
        with self.connection:
            volunteers_id_list = self.cursor.execute("SELECT * FROM users WHERE role = ?",
                                                     ('Volunteer',)).fetchall()

        return volunteers_id_list

    def check_access_key(self, meeting_name, access_key):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM meetings WHERE (name_meeting = ? AND access_key = ?);',
                                         (meeting_name, access_key,)).fetchall()

        return bool(len(result))

    def join_meeting(self, name_of_meeting, user_id):
        with self.connection:
            self.cursor.execute(f"INSERT INTO {name_of_meeting} (user_id, mark) VALUES (?, ?);", (user_id, 'waiting',))
        self.connection.commit()

    def leave_early(self, name_of_meeting, user_id):
        with self.connection:
            self.cursor.execute(f"UPDATE {name_of_meeting} SET mark = ? WHERE user_id = ?;", ('early', user_id,))
        self.connection.commit()

    def get_points(self, user_id):
        with self.connection:
            search = self.cursor.execute("SELECT points FROM users WHERE user_id = ?;",
                                         (user_id,)).fetchone()
            return search[0]

    def add_points(self, user_id, points):
        with self.connection:
            self.cursor.execute("UPDATE users SET points = ? WHERE user_id = ?;",
                                (points, user_id,)).fetchone()
        self.connection.commit()

    def get_meeting_date(self, name_meeting):
        with self.connection:
            date = self.cursor.execute("SELECT date FROM meetings WHERE name_meeting = ?;",
                                       (name_meeting,)).fetchone()
            return date[0]

    def get_meeting_location(self, meeting_name):
        with self.connection:
            latitude = self.cursor.execute("SELECT latitude FROM meetings WHERE name_meeting = ?;",
                                           (meeting_name,)).fetchone()
            longitude = self.cursor.execute("SELECT longitude FROM meetings WHERE name_meeting = ?;",
                                            (meeting_name,)).fetchone()

            return latitude[0], longitude[0]

    def get_meeting_distance(self, meeting_name):
        with self.connection:
            distance = self.cursor.execute("SELECT distance FROM meetings WHERE name_meeting = ?;",
                                           (meeting_name,)).fetchone()[0]

            return distance

    def get_user_mark(self, table_name, user_id):
        with self.connection:
            search = self.cursor.execute(f"SELECT mark FROM {table_name} WHERE user_id = ?;",
                                         (user_id,)).fetchone()
            return search[0]

    def get_hours_of_meeting(self, name_of_meeting):
        with self.connection:
            hours = self.cursor.execute("SELECT hours FROM meetings WHERE name_meeting = ?;",
                                        (name_of_meeting,)).fetchone()
            return hours[0]

    def mark_as_joined_not_auto(self, name_of_meeting, user_id, points):
        with self.connection:
            self.cursor.execute(f"UPDATE {name_of_meeting} SET mark = ? WHERE user_id = ?;",
                                ('joined', user_id,))
            self.cursor.execute("UPDATE users SET points = ? WHERE user_id = ?;",
                                (points, user_id,))
        self.connection.commit()

    def mark_as_joined(self, name_of_meeting, user_id, points, latitude, longitude):
        with self.connection:
            self.cursor.execute(f"UPDATE {name_of_meeting} SET mark = ? WHERE user_id = ?;",
                                ('joined', user_id,))
            self.cursor.execute(f"UPDATE {name_of_meeting} SET latitude = ? WHERE user_id = ?;",
                                (latitude, user_id,))
            self.cursor.execute(f"UPDATE {name_of_meeting} SET longitude = ? WHERE user_id = ?;",
                                (longitude, user_id,))
            self.cursor.execute("UPDATE users SET points = ? WHERE user_id = ?;",
                                (points, user_id,))
        self.connection.commit()

    def get_rus_meeting_name(self, name_of_meeting):
        with self.connection:
            result = self.cursor.execute(f"SELECT name_rus FROM meetings WHERE name_meeting = ?;",
                                         (name_of_meeting,)).fetchone()
        return result[0]

    def check_meeting_status(self, name_of_meeting):
        with self.connection:
            result = self.cursor.execute(f"SELECT status FROM meetings WHERE name_meeting = ?;",
                                         (name_of_meeting,)).fetchone()
        return result[0]

    def get_user_meeting_exist(self, table_name, user_id):
        with self.connection:
            search = self.cursor.execute(f"SELECT mark FROM {table_name} WHERE user_id = ?;",
                                         (user_id,)).fetchall()
            return bool(len(search))

    def set_role(self, role, user_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET role = ? WHERE user_id = ?;", (role, user_id,))
        self.connection.commit()
