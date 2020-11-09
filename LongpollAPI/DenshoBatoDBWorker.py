import sqlite3 as db_engine


class DBWorker:
    # TODO: Добавить методы для сбора id учеников по группам
    def __init__(self, db_name_aliases='DenshoBatoDBAliases.sqlite', db_name_schools='DenshoBatoDBSchools.sqlite',
                 initialize_flag=True):
        # Connection with db / it's creation
        self.conAlias = db_engine.connect(db_name_aliases)
        self.conSchools = db_engine.connect(db_name_schools)
        # Initialize cursor, the most hardworking part of 'em all
        self.curAlias = self.conAlias.cursor()
        self.curSchools = self.conSchools.cursor()

        if initialize_flag:
            self.initialize_db()

    def __del__(self):
        # Always close the connection in the end.
        self.curAlias.close()
        self.conAlias.close()
        self.curSchools.close()
        self.conSchools.close()

    def commit_all(self):
        self.conAlias.commit()
        self.conSchools.commit()

    def initialize_db(self):
        self.curAlias.execute("""CREATE TABLE IF NOT EXISTS main.ALIASES (
                                    SCHOOL_ALIAS TEXT NOT NULL,
                                    ADMIN_ID INTEGER 
                                    );""")
        self.conAlias.commit()

    def add_school(self, school_name, admin_id):
        self.curAlias.execute("""INSERT INTO main.ALIASES VALUES (
                                    ?,
                                    ?
                                    );""", (school_name, admin_id))
        self.curSchools.execute("""CREATE TABLE IF NOT EXISTS main.""" + school_name + """_STATUS (
                                      USER_ID INTEGER NOT NULL,
                                      STATUS TEXT NOT NULL,
                                      CLASS TEXT
                                      );""")
        # self.curSchools.execute("""CREATE TABLE IF NOT EXISTS main.""" + school_name + """_PASSWORDS (
        #                                       USER_ID INTEGER NOT NULL,
        #                                       PASS TEXT NOT NULL
        #                                       );""")
        # self.curSchools.execute("""CREATE TABLE IF NOT EXISTS main.""" + school_name + """_INFO (
        #                                               USER_ID INTEGER NOT NULL,
        #                                               NAME TEXT NOT NULL
        #                                               );""")
        self.add_person(school_name, admin_id, "ADMIN", "No_class")

    def add_person(self, school_name, user_id, status, class_name):
        self.curSchools.execute("""INSERT INTO main.""" + school_name + """_STATUS VALUES (
                                     ?,
                                     ?,
                                     ? );""", (user_id, status, class_name))

    def delete_by_id(self, school_name, user_id):
        self.curSchools.execute("""DELETE FROM main.""" + school_name + """_STATUS
                                   WHERE user_id = """ + str(user_id) + """;""")