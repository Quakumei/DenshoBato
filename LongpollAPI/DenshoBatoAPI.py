import DenshoBatoDBWorker


# TODO: Добавить всевозможные команды по типу рассылок и тп (с аттачментами)
def db_command(cmd):
    # ifs with cmd and processing args
    pass


def add_school(school_title, admin_id):
    """
    Creates school and makes admin_id the admin
    """
    # TODO: Refusing same school_titles
    db.add_school(school_title, admin_id)
    db.commit_all()


def add_entry(school_title, vk_id, status, class_name):
    """
    New status are given with new entries
    lame, but hope it will work
    """
    db.add_person(school_title, vk_id, status, class_name)
    db.commit_all()


def delete_by_id(school_title, person_id):
    """
    Deletes person from database based on its vk_id
    """
    db.delete_by_id(school_title, person_id)


db = DenshoBatoDBWorker.DBWorker('DenshoBatoDBAlias.sqlite', 'DenshoBatoDBSchools.sqlite', True)
db.add_school("Test_school_alias", 1223123)
db.add_person("Test_school_alias", 228322, "subscriber", "11b")
db.add_person("Test_school_alias", 666999, "subscriber", "11b")

db.commit_all()
