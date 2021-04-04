# Boots everything up. GUI in future?
# Now simply beginning sequence with config load

from VkApiHandler import *
from MsgHandler import *
from ActionHandler import *
from RoleHandler import *
from DatabaseHandler import *
from CodeList import CODE_DICT, DB_NAME

# Vk API info
ACCESS_TOKEN = '0405278c1d9aa5b5962e158cfc6e036ebb3703d671d5042df8d9d807e1a6cbbb577effb424664c474efe6'
API_VERSION = '5.95'
GROUP_ID = 199935063

role_handler = RoleHandler()
db_handler = DatabaseHandler(DB_NAME)

vkapi_handler = VkApiHandler(ACCESS_TOKEN, API_VERSION, GROUP_ID, debug=True)
act_handler = ActionHandler(vkapi_handler, role_handler, db_handler, debug_mode=True)
msg_handler = MsgHandler(CODE_DICT, COMMAND_SYMBOL, act_handler)
vkapi_handler.setMsgHandler(msg_handler)
vkapi_handler.main_loop()
