import DenshoBatoDBWorker

# Messages
import vk_api
import random

db = DenshoBatoDBWorker.DBWorker('DenshoBatoDBAlias.sqlite', 'DenshoBatoDBSchools.sqlite', True)


def db_command(cmd):
    # ifs with cmd and processing args
    pass


#
# DB MANIPULATION
#
def add_school(school_title, admin_id):
    """
    Creates school and makes admin_id the admin
    """
    # TODO: Refuse same school_titles
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


# Test
# db.add_school("Test_school_alias", 1223123)
# db.add_person("Test_school_alias", 228322, "subscriber", "11b")
# db.add_person("Test_school_alias", 666999, "subscriber", "11b")
#
# db.commit_all()
#

#
#  Sending messages
#
def write_msg(user_id, message, attachment=None):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.getrandbits(64)})


def mass_mailing(school, groups, message):
    # TODO: Add attachments
    # 1.) Fetch ids
    vk_ids = db.fetch_ids_by_groups(school, groups)
    # 2.) Send messages
    # TODO: VKAPI TO ANOTHER FILE
    # For a little time

    print(vk_ids)
    for vk_id in vk_ids:
        write_msg(vk_id, message)


# TEST
TEST_SCHOOL = "TEST_SCH00L"
GROUP_NAME = "TEST_GR0UP"
SUBSCRIBER_TAG = "SUB"
ADMIN_TAG = "ADMIN"
MY_ID = 388032588
MY_TWIN_ID = 422702764
token = '1db3d674ad5402cc10dc136734302e1ea6268510cce9842a0ee9c75124f4c955ea1aeea1d33528cdf9589'
vk = vk_api.VkApi(token=token)
#
# db.add_school(TEST_SCHOOL, MY_ID)
# db.add_person(TEST_SCHOOL, MY_ID, SUBSCRIBER_TAG, GROUP_NAME)
# db.add_person(TEST_SCHOOL, MY_TWIN_ID, SUBSCRIBER_TAG, GROUP_NAME)
# db.commit_all()
# mass_mailing(TEST_SCHOOL, (GROUP_NAME,), "ДАРОВА ЧО КАК НАСТРОЕНИЕ")
#
#

