# Handles UI according on msg and user_id (basically msg)
# Словарь с функциями

import CodeList

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

        msg = update['object']['text']
        user_id = update['object']['from_id']

        if msg and msg[0] is self.command_symbol:
            code = msg.split(' ', 1)[0][1:]
            # Handle command
            for (key, value) in self.code_dict.items():
                if key == code:
                    self.action_handler.handle_act(value, update)

                    break
        else:
            # Not a command.
            self.action_handler.handle_act(CodeList.CODE.ECHO, update)
