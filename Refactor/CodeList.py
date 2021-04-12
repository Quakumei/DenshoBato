class CODE:
    HELP = 0
    USER_INFO = 1
    ECHO = 2
    CREATE_SCHOOL = 3
    INVALID = 4
    REGISTER = 5
    INVITE_USER = 6
    CREATE_GROUP = 7
    ADD_TO_GROUP = 8
    INFO_SCHOOL = 9
    UPDATE_ROLE = 10
    REMOVE_USER = 11
    REMOVE_USER_FROM_GROUP = 12
    GROUP_MSG = 13
    PM_MSG = 14
    DELETE_SCHOOL = 15
    DELETE_GROUP = 16
    INFO_GROUP = 17
    # INFO_SCHOOL_GROUPS = 18
    INFO_STUDENT = 19
    CONTINUE = 20
    RETURN = 21


# UI Design stuff
# TODO: Move parameters to config file and load them here
# Add new words here
COMMAND_SYMBOL = "!"
USER_INFO_WORD = "инфо"  # !инфо
HELP_WORD = "помощь"  # !помощь
REGISTER_WORD = "рег"  # !рег (username)
CREATE_SCHOOL_WORD = "создать_шк"  # !создать_школу school_name
INVITE_USER_WORD = "приг_шк"  # !приг_шк school_id vk_id
UPDATE_ROLE_WORD = "изм_роль"  # !изм_роль school_id vk_id new_role_id
REMOVE_USER_WORD = "искл_шк"  # !искл_шк school_id target_id
INFO_SCHOOL_WORD = "инфо_шк"  # !инфо_школа school_id
ADD_TO_GROUP_WORD = "приг_гр"  # !приг_гр vk_id group_id
REMOVE_USER_FROM_GROUP_WORD = "искл_гр"  # !искл_гр school_id target_id group_id
GROUP_MSG_WORD = "сообщ_гр"  # !сообщ_гр group_id (сообщение)
PM_MSG_WORD = "сообщ_чл"  # !сообщ_чл vk_id сообщ
CREATE_GROUP_WORD = "создать_гр"  # !создать_группу school_id group_name
DELETE_SCHOOL_WORD = "удалить_школу"  # !удалить_школу school_id school_name (to delete securely)
DELETE_GROUP_WORD = "удалить_группу"  # !удалить_группу group_id group_name (to delete securely)
INFO_GROUP_WORD = "инфо_гр"  # !инфо_группа group_id (check rights)
# INFO_SCHOOL_GROUPS_WORD = "инфо_шк_гр" #!инфо_шк_гр school_id
INFO_STUDENT_WORD = "инфо_уч"  # !инфо_уч school_id student_id
CONTINUE_WORD = "п"
IGNORE_SYMBOL = "-"

DB_NAME = 'bato.db'

CODE_DICT = {
    # Add words here too (order affects menu)
    HELP_WORD: CODE.HELP,
    REGISTER_WORD: CODE.REGISTER,
    USER_INFO_WORD: CODE.USER_INFO,

    INFO_SCHOOL_WORD: CODE.INFO_SCHOOL,
    INFO_STUDENT_WORD: CODE.INFO_STUDENT,
    INFO_GROUP_WORD: CODE.INFO_GROUP,

    CREATE_GROUP_WORD: CODE.CREATE_GROUP,
    CREATE_SCHOOL_WORD: CODE.CREATE_SCHOOL,
    ADD_TO_GROUP_WORD: CODE.ADD_TO_GROUP,

    DELETE_GROUP_WORD: CODE.DELETE_GROUP,
    DELETE_SCHOOL_WORD: CODE.DELETE_SCHOOL,
    INVITE_USER_WORD: CODE.INVITE_USER,

    REMOVE_USER_FROM_GROUP_WORD: CODE.REMOVE_USER_FROM_GROUP,
    REMOVE_USER_WORD: CODE.REMOVE_USER,
    UPDATE_ROLE_WORD: CODE.UPDATE_ROLE,

    PM_MSG_WORD: CODE.PM_MSG,
    GROUP_MSG_WORD: CODE.GROUP_MSG,  #

}

class EVENT:
    REGISTER = 101
