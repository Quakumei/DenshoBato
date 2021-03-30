# Handles any action committed by user
from CodeList import *
import Utility

class ActionHandler:
    def __init__(self, vkapi_handler, role_handler, db_handler, debug_mode=True):
        self.debug_mode = debug_mode
        self.vkapi_handler = vkapi_handler
        self.role_handler = role_handler
        self.db_handler = db_handler

        self.test = 0

        self.act_table = {
            # Put new actions here (don't forget to add the command in config)
            CODE.DEBUG: self.debug,
            CODE.HELP: self.help,
            CODE.ECHO: self.echo,
            CODE.CREATE_SCHOOL: self.create_school,
            CODE.INVALID: self.invalid
        }

    def handle_act(self, code, update):
        self.act_table[code](update)

    def debug(self, update):
        # Debug info
        pass

    def help(self, update):
        # Print help
        # TODO fix code words in help
        user_id = update['object']['from_id']
        with open("help.txt") as help_file:
            msg = help_file.read()
        #msg = "".join(msg) # % (HELP_WORD, DEBUG_WORD, CREATE_SCHOOL_WORD, ADD_WORD, WHOIN_WORD, GROUPSEND_WORD)
        self.vkapi_handler.send_msg(user_id, msg)
        # Help info
        pass

    def echo(self, update):
        # Send message back
        msg = update['object']['text']
        # # remove command word
        # msg = msg.split(' ', 1)[1]
        if not msg:
            msg = "fgsfds"
        user_id = update['object']['from_id']
        self.vkapi_handler.send_msg(user_id, msg)

    def create_school(self, update):
        # Create school and make vk_id its owner
        msg = update['object']['text']
        user_id = update['object']['from_id']

        # Remove trailing backspace and parse school_name
        school_name = " ".join(Utility.parse_arg(msg))

        self.db_handler.create_school(school_name, user_id)

        # # Maybe use later
        # code = self.db_handler.create_school(school_name, user_id)






    def invalid(self, update):
        # Wrong command
        user_id = update['object']['from_id']
        msg = "Неправильная команда. Напишите !помощь, чтобы узнать больше."
        self.vkapi_handler.send_msg(user_id, msg)
