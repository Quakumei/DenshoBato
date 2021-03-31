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
            CODE.INVALID: self.invalid,
            CODE.REGISTER: self.register,
            CODE.INVITE_USER: self.invite_user,
            CODE.CREATE_GROUP: self.create_group
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
        # msg = "".join(msg) # % (HELP_WORD, DEBUG_WORD, CREATE_SCHOOL_WORD, ADD_WORD, WHOIN_WORD, GROUPSEND_WORD)
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

        school_id = self.db_handler.create_school(school_name, user_id)
        if school_id == -1:
            err = f"Вы не зарегистрированы в системе. Напишите !{'рег'} [Имя_пользователя] для регистрации."
            self.vkapi_handler.send_msg(user_id, err)
        else:
            txt = f"Поздравляем, вы создали школу {school_name}!\nЕй присвоен идентификатор - {school_id}."
            self.vkapi_handler.send_msg(user_id, txt)

    def register(self, update):
        # Add vk_id - Name to database (or update it)
        msg = update['object']['text']
        user_id = update['object']['from_id']

        nickname = " ".join(Utility.parse_arg(msg))

        resp = self.db_handler.user_nickname_update(user_id, nickname)
        if resp != -1:
            txt = f"Вы успешно установили себе имя {nickname}."
            self.vkapi_handler.send_msg(user_id, txt)
        else:
            err = f"Что-то пошло не так при регистрации..."
            self.vkapi_handler.send_msg(user_id, err)

    def invalid(self, update):
        # Wrong command
        user_id = update['object']['from_id']
        msg = "Неправильная команда. Напишите !помощь, чтобы узнать больше."
        self.vkapi_handler.send_msg(user_id, msg)

    def invite_user(self, update):
        # Invite vk_id to school_id if you have a permission to.
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        vk_id = args[0]
        school_id = args[1]
        # TODO: Maybe change that later to real invite system
        code = self.db_handler.add_user(vk_id, school_id, user_id)
        if code == -2:
            err = f"Ошибка: Пользователь {vk_id} уже участник школы {school_id}..."
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -1:
            err = f"Ошибка: Ошибка базы данных, сообщите разработчику..."
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -3:
            err = f"Ошибка: Пользователь {vk_id} не зарегистрирован в системе..."
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -4:
            err = f"Ошибка: Недостаточно прав или вы не являетесь участником {school_id}"
            self.vkapi_handler.send_msg(user_id, err)
        else:
            txt = f"Вы успешно пригласили пользователя {vk_id} в {school_id}"
            self.vkapi_handler.send_msg(user_id, txt)

    def create_group(self, update):
        # Create group with school_name in school_id. Return user its id.
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        school_id = args[0]
        group_name = " ".join(args[1:])

        code = self.db_handler.create_group(group_name, school_id, user_id)
        if code == -4:
            err = f"Ошибка: Недостаточно прав или вы не являетесь участником {school_id}"
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -1:
            err = f"Ошибка: Ошибка базы данных, сообщите разработчику..."
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -5:
            err = f"Ошибка: Группа с таким именем в школе {school_id} уже сущестует..."
            self.vkapi_handler.send_msg(user_id, err)
        else:
            txt = f"Вы успешно создали группу с названием {group_name} в {school_id}. Идентификатор новой группы - {code}."
            self.vkapi_handler.send_msg(user_id, txt)

