# Handles any action committed by user
from CodeList import *


class ActionHandler:
    def __init__(self, vkapi_handler, role_handler, db_handler, debug=True):
        self.debug = debug
        self.vkapi_handler = vkapi_handler
        self.role_handler = role_handler
        self.db_handler = db_handler

        self.test = 0

        self.act_table = {
            CODE.DEBUG: self.debug,
            CODE.HELP: self.help,
            CODE.ECHO: self.echo,
        }

    def handle_act(self, code, update):
        self.act_table[code](update)

    def debug(self, update):
        # Debug info
        pass

    def help(self, update):
        # TODO fix code words in help
        user_id = update['object']['from_id']
        with open("help.txt") as help_file:
            msg = help_file.read()
        #msg = "".join(msg) # % (HELP_WORD, DEBUG_WORD, CREATE_SCHOOL_WORD, ADD_WORD, WHOIN_WORD, GROUPSEND_WORD)
        self.vkapi_handler.send_msg(user_id, msg)
        # Help info
        pass

    def echo(self, update):
        msg = update['object']['text']
        # # remove command word
        # msg = msg.split(' ', 1)[1]
        if not msg:
            msg = "fgsfds"
        user_id = update['object']['from_id']
        self.vkapi_handler.send_msg(user_id, msg)
