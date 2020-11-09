import DenshoBatoDBWorker


# TODO: Добавить всевозможные команды по типу рассылок и тп (с аттачментами)
def db_command(cmd):
    # ifs with cmd and processing args
    pass


def add_school(school_title, admin_id):
    """

    """
    # TODO: Refusing same school_titles
    db.add_school(school_title, admin_id)
    db.commit_all()


def add_entry(school_title, vk_id, person_name, status, class_name,
              password="______"):  # ______ Is a password prompt (future) probably should not be used here
                                   # Develop no password version in branch...
                                   # Just ignore it now
    """
    New status are given with new entries
    lame, but hope it will work
    """
    db.add_person(school_title, vk_id, person_name, status, class_name, password)
    db.commit_all()


def delete_by_name(school_title, person_name):
    db.delete_by_name(school_title, person_name)


def delete_by_id(school_title, person_id):
    db.delete_by_id(school_title, person_id)




def


db = DenshoBatoDBWorker.DBWorker('DenshoBatoDBAlias.sqlite', 'DenshoBatoDBSchools.sqlite', True)
db.add_school("Test_school_alias", 1223123)
db.add_person("Test_school_alias", 228322, "Josh Peterson", "subscriber", "11B", "123")
db.commit_all()
