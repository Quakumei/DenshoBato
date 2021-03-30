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
DEBUG_WORD = "дебаг"
HELP_WORD = "помощь"
CREATE_SCHOOL_WORD = "создать_школу"

DB_NAME = 'bato.db'

CODE_DICT = {
    # Add them here too
    HELP_WORD:CODE.HELP,
    DEBUG_WORD:CODE.DEBUG,
    CREATE_SCHOOL_WORD:CODE.CREATE_SCHOOL
}


role_handler = RoleHandler()
db_handler = DatabaseHandler(DB_NAME)

vkapi = VkApiHandler(ACCESS_TOKEN, API_VERSION, GROUP_ID, debug=True)
act_handler = ActionHandler(vkapi, role_handler, db_handler , debug=True)
msg_handler = MsgHandler(CODE_DICT, COMMAND_SYMBOL, act_handler)
vkapi.setMsgHandler(msg_handler)
vkapi.main_loop()
