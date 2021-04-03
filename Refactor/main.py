# Boots everything up. GUI in future?
# Now simply beginning sequence with config load

from VkApiHandler import *
from MsgHandler import *
from ActionHandler import *
from RoleHandler import *
from DatabaseHandler import *

# Vk API info
ACCESS_TOKEN = '0405278c1d9aa5b5962e158cfc6e036ebb3703d671d5042df8d9d807e1a6cbbb577effb424664c474efe6'
API_VERSION = '5.95'
GROUP_ID = 199935063

# UI Design stuff
# TODO: Move parameters to config file and load them here
# Add new words here
COMMAND_SYMBOL = "!"
USER_INFO_WORD = "инфо" # !инфо
HELP_WORD = "помощь" # !помощь
REGISTER_WORD = "рег" # !рег username
CREATE_SCHOOL_WORD = "создать_школу" # !создать_школу school_name
INVITE_USER_WORD = "приг_шк" # !приг_шк school_id vk_id
UPDATE_ROLE_WORD = "изм_роль" # !изм_роль school_id vk_id new_role_id
REMOVE_USER_WORD = "искл_шк" #!искл_шк school_id target_id
INFO_SCHOOL_WORD = "инфо_школа" # !инфо_школа school_id
ADD_TO_GROUP_WORD = "приг_гр" # !приг_гр vk_id group_id
REMOVE_USER_FROM_GROUP_WORD = "искл_гр" #!искл_гр school_id target_id group_id
GROUP_MSG_WORD = "сообщ_гр" #!сообщ_гр group_id (сообщение)
PM_MSG_WORD = "сообщ_чл" #!сообщ_чл vk_id сообщ
CREATE_GROUP_WORD = "создать_группу" # !создать_группу school_id group_name
DELETE_SCHOOL_WORD = "удалить_школу" #!удалить_школу school_id school_name (to delete securely)
DELETE_GROUP_WORD = "удалить_группу" #!удалить_группу group_id group_name (to delete securely)


DB_NAME = 'bato.db'

CODE_DICT = {
    # Add words here too
    DELETE_GROUP_WORD: CODE.DELETE_GROUP,
    DELETE_SCHOOL_WORD: CODE.DELETE_SCHOOL,
    PM_MSG_WORD: CODE.PM_MSG,
    GROUP_MSG_WORD: CODE.GROUP_MSG,
    REMOVE_USER_FROM_GROUP_WORD: CODE.REMOVE_USER_FROM_GROUP,
    REMOVE_USER_WORD: CODE.REMOVE_USER,
    UPDATE_ROLE_WORD: CODE.UPDATE_ROLE,
    INFO_SCHOOL_WORD: CODE.INFO_SCHOOL,
    ADD_TO_GROUP_WORD: CODE.ADD_TO_GROUP,
    CREATE_GROUP_WORD: CODE.CREATE_GROUP,
    INVITE_USER_WORD: CODE.INVITE_USER,
    REGISTER_WORD: CODE.REGISTER,
    HELP_WORD: CODE.HELP,
    USER_INFO_WORD: CODE.USER_INFO,
    CREATE_SCHOOL_WORD: CODE.CREATE_SCHOOL
}

role_handler = RoleHandler()
db_handler = DatabaseHandler(DB_NAME)

vkapi_handler = VkApiHandler(ACCESS_TOKEN, API_VERSION, GROUP_ID, debug=True)
act_handler = ActionHandler(vkapi_handler, role_handler, db_handler, debug_mode=True)
msg_handler = MsgHandler(CODE_DICT, COMMAND_SYMBOL, act_handler)
vkapi_handler.setMsgHandler(msg_handler)
vkapi_handler.main_loop()
