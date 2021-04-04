# Handles UI according on msg and user_id (basically msg)
# Словарь с функциями

import CodeList
import Utility
import json


class MsgHandler:
    def __init__(self, code_dict, command_symbol, action_handler, debug=True):
        self.debug = debug

        self.action_handler = action_handler
        self.code_dict = code_dict
        self.command_symbol = command_symbol

        if self.debug:
            print(self.code_dict)
            print(self.command_symbol)

    def handle_message(self, update):
        if self.debug:
            print(update)


        if "payload" in update['object'] and update['object']['payload'] == '{"command":"start"}':
            self.action_handler.handle_act(CodeList.EVENT.REGISTER, update)
            return

        msg = update['object']['text']
        user_id = update['object']['from_id']

        if msg and msg[0] is self.command_symbol:
            code = msg.split(' ', 1)[0][1:].lower()
            # Handle command
            for (key, value) in self.code_dict.items():
                if key == code:

                    # Apply restriction ifs
                    name = Utility.parse_arg(msg)
                    if value == CodeList.CODE.CREATE_SCHOOL:
                        if name is False:
                            self.action_handler.handle_act(CodeList.CODE.INVALID, update)
                            return
                    elif value == CodeList.CODE.INVITE_USER or value == CodeList.CODE.ADD_TO_GROUP or value == CodeList.CODE.REMOVE_USER or value == CodeList.CODE.INFO_STUDENT:
                        if not name or len(name) != 2 or not name[0].isnumeric() or not name[1].isnumeric():
                            self.action_handler.handle_act(CodeList.CODE.INVALID, update)
                            return
                    elif value == CodeList.CODE.CREATE_GROUP or value == CodeList.CODE.DELETE_SCHOOL or value == CodeList.CODE.DELETE_GROUP:
                        if not name or len(name) < 2 or not name[0].isnumeric():
                            self.action_handler.handle_act(CodeList.CODE.INVALID, update)
                            return
                    elif value == CodeList.CODE.INFO_SCHOOL or value == CodeList.CODE.INFO_GROUP:
                        if not name or len(name) != 1 or not name[0].isnumeric():
                            self.action_handler.handle_act(CodeList.CODE.INVALID, update)
                            return
                    elif value == CodeList.CODE.UPDATE_ROLE or value == CodeList.CODE.REMOVE_USER_FROM_GROUP:
                        if not name or len(name) != 3 or not name[0].isnumeric() or not name[1].isnumeric() or not name[
                            2].isnumeric():
                            self.action_handler.handle_act(CodeList.CODE.INVALID, update)
                            return
                    elif value == CodeList.CODE.GROUP_MSG or value == CodeList.CODE.PM_MSG:
                        # TOD0: \n problem (look into log below) - Done.
                        group_id = name[0]
                        if not group_id.isnumeric() and group_id[0].isnumeric():
                            group_id = group_id.split('\n', 1)[0]
                        if not name or not group_id.isnumeric():
                            self.action_handler.handle_act(CodeList.CODE.INVALID, update)
                            return

                    self.action_handler.handle_act(value, update)
                    return
        elif msg and msg[0] is CodeList.IGNORE_SYMBOL:
            self.action_handler.handle_act(CodeList.CODE.CONTINUE, update)
            return
        # Not a command.
        else:
            self.action_handler.handle_act(CodeList.CODE.INVALID, update)
            self.action_handler.handle_act(CodeList.CODE.CONTINUE, update)
