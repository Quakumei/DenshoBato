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
            CODE.REMOVE_USER: self.expel,
            CODE.UPDATE_ROLE: self.update_role,
            CODE.DEBUG: self.debug,
            CODE.HELP: self.help,
            CODE.ECHO: self.echo,
            CODE.CREATE_SCHOOL: self.create_school,
            CODE.INVALID: self.invalid,
            CODE.REGISTER: self.register,
            CODE.INVITE_USER: self.invite_user,
            CODE.CREATE_GROUP: self.create_group,
            CODE.ADD_TO_GROUP: self.add_to_group,
            CODE.INFO_SCHOOL: self.info_school
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
        vk_id = args[1]
        school_id = args[0]
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

    def add_to_group(self, update):
        # Add user specified in msg to the group_id
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        vk_id = args[0]
        group_id = args[1]

        code = self.db_handler.add_to_group(group_id, vk_id, user_id)
        if code == -4:
            err = f"Ошибка: Недостаточно прав или вы не являетесь участником школы этой группы"
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -1:
            err = f"Ошибка: Ошибка базы данных, сообщите разработчику..."
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -5:
            err = f"Ошибка: Пользователь с таким id уже находится в этой группе..."
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -3:
            err = f"Ошибка: Пользователь {vk_id} не зарегистрирован в системе..."
            self.vkapi_handler.send_msg(user_id, err)
        else:
            txt = f"Вы успешно добавили {user_id} в группу {group_id}"
            self.vkapi_handler.send_msg(user_id, txt)

    def info_school(self, update):
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        school_id = args[0]

        # Fetch data
        school_name = self.db_handler.fetch_school_name(school_id)
        school_groups_ids = self.db_handler.fetch_school_groups_ids(school_id)
        school_groups_names = []
        for group_id in school_groups_ids:
            school_groups_names.append(self.db_handler.fetch_group_name(group_id))

        school_groups = []
        for i in range(len(school_groups_ids)):
            school_groups.append((school_groups_ids[i],school_groups_names[i]))

        members_ids = self.db_handler.fetch_school_members_vk_ids(school_id)
        members_names=[]
        members_groups=[]
        members_roles=[]
        for member_id in members_ids:
            members_names.append(self.db_handler.fetch_user_name(member_id))
            # Very bad code you could do better
            members_groups.append([self.db_handler.fetch_group_name(x) for x in self.db_handler.fetch_user_school_groups(school_id, member_id)])
            members_roles.append(self.db_handler.fetch_user_school_role(school_id, member_id))

        members = []
        for i in range(len(members_ids)):
            members.append((members_roles[i],members_names[i],members_groups[i], members_ids[i]))

        # Now we have school_groups (group_id , group_name)
        # Now we have members (role_id, name, group_names, vk_id)

        txt = Utility.school_info((school_id,school_name), school_groups, members, self.db_handler)
        self.vkapi_handler.send_msg(user_id, txt)

    def update_role(self, update):
        # Changes role of the subject
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        school_id = args[0]
        vk_id = args[1]
        new_role_id = args[2]

        code = self.db_handler.update_role(school_id, vk_id, new_role_id, user_id)
        if code == -1:
            err = f"Ошибка: Ошибка базы данных, сообщите разработчику..."
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -4:
            err = f"Ошибка: Недостаточно прав или вы не являетесь участником школы этой группы"
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -2:
            err = f"Ошибка: Ученик {vk_id} не является участником {school_id}..."
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -3:
            err = f"Ошибка: Нет роли {new_role_id}..."
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -5:
            err = f"Ошибка: Нет школы {school_id}..."
            self.vkapi_handler.send_msg(user_id, err)
        if code is True:
            txt = f"Вы успешно сменили роль '{vk_id}' в школе '{school_id}' на '{new_role_id}'"
            self.vkapi_handler.send_msg(user_id, txt)


    def expel(self, update):
        # Removes user from school
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        school_id = args[0]
        vk_id = args[1]

        code = self.db_handler.remove_user(school_id, vk_id, user_id)
        if code == -1:
            err = f"Ошибка: Ошибка базы данных, сообщите разработчику..."
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -4:
            err = f"Ошибка: Недостаточно прав или вы не являетесь участником школы этой группы"
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -2:
            err = f"Ошибка: Ученик {vk_id} не является участником {school_id}..."
            self.vkapi_handler.send_msg(user_id, err)
        elif code == -5:
            err = f"Ошибка: Нет школы {school_id}..."
            self.vkapi_handler.send_msg(user_id, err)
        if code is True:
            txt = f"Вы успешно исключили '{vk_id}' из школы '{school_id}'."
            self.vkapi_handler.send_msg(user_id, txt)

