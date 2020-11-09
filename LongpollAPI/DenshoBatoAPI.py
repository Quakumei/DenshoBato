import DenshoBatoDBWorker

# TODO: Добавить всевозможные команды по типу рассылок и тп (с аттачментами)
def db_command(cmd):
    # ifs with cmd and processing args
    pass


db = DenshoBatoDBWorker.DBWorker('DenshoBatoDBAlias.sqlite', 'DenshoBatoDBSchools.sqlite', True)
db.add_school("Test_school_alias", 1223123)
db.add_person("Test_school_alias", 228322, "Josh Peterson", "Receiver", "11B", "123")
db.commit_all()
