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
DEBUG_WORD = "дебаг" # !дебаг
HELP_WORD = "помощь" # !помощь
CREATE_SCHOOL_WORD = "создать_школу" # !создать_школу school_name
REGISTER_WORD = "рег" # !рег username
INVITE_USER_WORD = "приг" # !приг school_id vk_id
CREATE_GROUP_WORD = "создать_группу" # !создать_группу school_id group_name
ADD_TO_GROUP_WORD = "добавить_в_группу" # !добаить_в_группу vk_id group_id
INFO_SCHOOL_WORD = "инфо_школа" # !инфо_школа school_id
UPDATE_ROLE_WORD = "изм_роль" # !изм_роль school_id vk_id new_role_id
REMOVE_USER_WORD = "искл_шк" #!искл_шк school_id target_id

DB_NAME = 'bato.db'

CODE_DICT = {
    # Add them here too
    REMOVE_USER_WORD: CODE.REMOVE_USER,
    UPDATE_ROLE_WORD: CODE.UPDATE_ROLE,
    INFO_SCHOOL_WORD: CODE.INFO_SCHOOL,
    ADD_TO_GROUP_WORD: CODE.ADD_TO_GROUP,
    CREATE_GROUP_WORD: CODE.CREATE_GROUP,
    INVITE_USER_WORD: CODE.INVITE_USER,
    REGISTER_WORD: CODE.REGISTER,
    HELP_WORD: CODE.HELP,
    DEBUG_WORD: CODE.DEBUG,
    CREATE_SCHOOL_WORD: CODE.CREATE_SCHOOL
}

role_handler = RoleHandler()
db_handler = DatabaseHandler(DB_NAME)

vkapi = VkApiHandler(ACCESS_TOKEN, API_VERSION, GROUP_ID, debug=True)
act_handler = ActionHandler(vkapi, role_handler, db_handler, debug_mode=True)
msg_handler = MsgHandler(CODE_DICT, COMMAND_SYMBOL, act_handler)
vkapi.setMsgHandler(msg_handler)
vkapi.main_loop()
