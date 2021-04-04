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
            CODE.INFO_GROUP: self.info_group,
            CODE.INFO_STUDENT: self.info_student,
            # CODE.INFO_SCHOOL_GROUPS: self.info_school_groups,
            CODE.DELETE_GROUP: self.delete_group,
            CODE.DELETE_SCHOOL: self.delete_school,
            CODE.PM_MSG: self.pm_msg,
            CODE.GROUP_MSG: self.group_msg,
            CODE.REMOVE_USER_FROM_GROUP: self.expel_from_group,
            CODE.REMOVE_USER: self.expel,
            CODE.UPDATE_ROLE: self.update_role,
            CODE.USER_INFO: self.user_info,
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
        self.load_help()

    def handle_act(self, code, update):
        self.act_table[code](update)

    def load_help(self):
        # Loads help string (use from another file)
        self.help = help

    def help(self, update):
        # Print help
        # TODO fix code words in help
        #msg = update['object']['text']
        user_id = update['object']['from_id']
        with open("help.txt") as help_file:
            msg = help_file.read()
        # msg = "".join(msg) # % (HELP_WORD, DEBUG_WORD, CREATE_SCHOOL_WORD, ADD_WORD, WHOIN_WORD, GROUPSEND_WORD)
        self.vkapi_handler.send_msg(user_id, msg)
        return

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
            err = f"Ошибка: Недостаточно прав или вы не являетесь участником {school_id}."
            self.vkapi_handler.send_msg(user_id, err)
        else:
            txt = f"Вы успешно пригласили пользователя {vk_id} в {school_id}."
            self.vkapi_handler.send_msg(user_id, txt)
            notification = f"🔔 Уведомление. 🔔\n"
            notification += f"Вы были приняты в качестве {self.db_handler.fetch_role_name(5)} в школу {self.db_handler.fetch_school_name(school_id)} (school_id: {school_id})" \
                            f"\n(@id{user_id}(инициатор))."
            self.vkapi_handler.send_msg(vk_id, notification)

    def create_group(self, update):
        # Create group with school_name in school_id. Return user its id.
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        school_id = args[0]
        group_name = " ".join(args[1:])

        code = self.db_handler.create_group(group_name, school_id, user_id)
        if code == -4:
            err = f"Ошибка: Недостаточно прав или вы не являетесь участником {school_id}."
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
            err = f"Ошибка: Недостаточно прав или вы не являетесь участником школы этой группы."
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
            txt = f"Вы успешно добавили {vk_id} в группу {group_id}."
            self.vkapi_handler.send_msg(user_id, txt)
            notification = f"""🔔 Уведомление. 🔔\nВы были добавлены в группу {self.db_handler.fetch_group_name(group_id)} (group_id: {group_id}).
(@id{user_id}(инициатор))"""
            self.vkapi_handler.send_msg(vk_id, notification)



    def update_role(self, update):
        # Changes role of the subject
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        school_id = args[0]
        vk_id = args[1]
        new_role_id = args[2]
        last_role_id = self.db_handler.fetch_user_school_role(school_id, vk_id)

        code = self.db_handler.update_role(school_id, vk_id, new_role_id, user_id)
        if code == -1:
            err = f"Ошибка: Ошибка базы данных, сообщите разработчику..."
            self.vkapi_handler.send_msg(user_id, err)

        elif code == -4:
            err = f"Ошибка: Недостаточно прав или вы не являетесь участником школы этой группы."
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
            txt = f"Вы успешно сменили роль '{vk_id}' в школе '{school_id}' на '{new_role_id}'."
            self.vkapi_handler.send_msg(user_id, txt)
            notification = f"🔔 Уведомление. 🔔\n"
            notification += f"Произошла смена вашей роли в {self.db_handler.fetch_school_name(school_id)} (school_id: {school_id}):{self.db_handler.fetch_role_name(last_role_id)} --> {self.db_handler.fetch_role_name(new_role_id)}\n(@id{user_id}(инициатор))."
            self.vkapi_handler.send_msg(vk_id, notification)


    def expel(self, update):
        # Removes user from school
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        school_id = args[0]
        target_id = args[1]

        code = self.db_handler.remove_user(school_id, target_id, user_id)
        if code == -1:
            err = f"Ошибка: Ошибка базы данных, сообщите разработчику..."
            self.vkapi_handler.send_msg(user_id, err)
            return
        elif code == -4:
            err = f"Ошибка: Недостаточно прав или вы не являетесь участником школы этой группы."
            self.vkapi_handler.send_msg(user_id, err)
            return
        elif code == -2:
            err = f"Ошибка: Ученик {target_id} не является участником {self.db_handler.fetch_school_name(school_id)} (school_id: {school_id})..."
            self.vkapi_handler.send_msg(user_id, err)
            return
        elif code == -5:
            err = f"Ошибка: Нет школы c school_id: {school_id}..."
            self.vkapi_handler.send_msg(user_id, err)
            return
        elif code is True:
            txt = f"Вы успешно исключили '{target_id}' из школы '{school_id}'."
            self.vkapi_handler.send_msg(user_id, txt)

        # Sad letter
        notification = f"""🔔 Уведомление. 🔔
Вы были исключены из школы '{self.db_handler.fetch_school_name(school_id)}' (school_id: {school_id}) \n(@id{user_id}(инициатор))."""
        self.vkapi_handler.send_msg(target_id, notification)

    def expel_from_group(self, update):
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        school_id = args[0]
        target_id = args[1]
        group_id = args[2]

        # TODO: Write error codes later
        code = self.db_handler.remove_from_group(school_id, group_id, target_id, user_id)

        if code is True:
            txt = f"Вы успешно исключили '{target_id}' из группы '{group_id}' школы '{school_id}'."
            self.vkapi_handler.send_msg(user_id, txt)
        else:
            err = f"Что-то пошло не так [Код ошибки: {code}]..."
            self.vkapi_handler.send_msg(user_id, err)
            return

        # Sad letter
        notification = f"""🔔 Уведомление. 🔔
Вы были исключены из группы '{self.db_handler.fetch_group_name(group_id)}' (group_id: {group_id}) \n(@id{user_id}(инициатор))"""
        self.vkapi_handler.send_msg(target_id, notification)

    def group_msg(self, update):
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        group_id = args[0]
        bad_n_flag = False
        if not group_id.isnumeric() and group_id[0].isnumeric():
            bad_n_flag = True
            group_id = group_id.split('\n', 1)[0]

        # God blame me for that please
        if not self.db_handler.group_check(group_id):
            err = f"Указанной группы не существует..."
            self.vkapi_handler.send_msg(user_id, err)
            return

        # Permission check
        # Fetch group_ids where can sender send to
        groups_avail = self.db_handler.avail_group_msg_group_ids(user_id)
        if int(group_id) not in groups_avail:
            err = f"Вы не можете писать группе {group_id}... (Доступные:{groups_avail})"
            self.vkapi_handler.send_msg(user_id, err)
            return

        # Fetch ids
        mailing_list_ids = self.db_handler.fetch_group_members(group_id)

        # Send msg

        # Make msg: sender to whom (group_id and word) and school
        msg = msg.split(' ', 1)[1]
        msg = msg[len(group_id):]

        user_id = user_id
        sender_name = self.db_handler.fetch_user_name(user_id)
        group_name = self.db_handler.fetch_group_name(group_id)

        hat = f"✉ Сообщение ✉\n[ОТ: ] {sender_name}(id:{user_id})\n[КОМУ: ] {group_name}(group_id:{group_id})\n\n"
        msg = hat + msg
        attachments = update['object']['attachments']
        attachment_str, urls = Utility.parse_attachments2str(attachments)
        if attachment_str:
            footer = f"\nВложения:\n" + str("\n".join(urls))
            msg = msg + footer
        for id in mailing_list_ids:
            self.vkapi_handler.send_msg(id, msg, attachment_str)

        txt = f"Рассылка успешно выполнена."
        self.vkapi_handler.send_msg(user_id, txt)
        return

    def pm_msg(self, update):
        # Basically group_send but without fetching id and checking whether both of the users are in the same school
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        vk_id = args[0]
        bad_n_flag = False
        if not vk_id.isnumeric() and vk_id[0].isnumeric():
            bad_n_flag = True
            group_id = vk_id.split('\n', 1)[0]

        # God blame me for that please
        if not self.db_handler.user_check(vk_id):
            err = f"Указанного пользователя не существует..."
            self.vkapi_handler.send_msg(user_id, err)
            return

        # Permission check
        # Users must be in the same clan.
        vk_id_pm_avail = [x[0] for x in self.db_handler.fetch_user_schools(vk_id)]
        user_id_pm_avail = [x[0] for x in self.db_handler.fetch_user_schools(user_id)]
        if not list(set(vk_id_pm_avail) & set(user_id_pm_avail)):
            err = f"Вы не можете писать пользователю {vk_id}... (Вы должны состоять в одной школе)"
            self.vkapi_handler.send_msg(user_id, err)
            return

        # Fetch ids
        mailing_list_ids = [vk_id]

        # Send msg

        # Make msg: sender to whom (group_id and word) and school
        msg = msg.split(' ', 1)[1]
        msg = msg[len(vk_id):]

        user_id = user_id
        sender_name = self.db_handler.fetch_user_name(user_id)
        vk_id_name = self.db_handler.fetch_user_name(vk_id)

        hat = f"✉ Сообщение ✉\n[ОТ: ] {sender_name}(id:{user_id})\n[КОМУ: ] {vk_id_name}(vk_id:{vk_id})\n\n"
        msg = hat + msg
        attachments = update['object']['attachments']
        attachment_str, urls = Utility.parse_attachments2str(attachments)
        if attachment_str:
            footer = f"\nВложения:\n" + str("\n".join(urls))
            msg = msg + footer
        for id in mailing_list_ids:
            self.vkapi_handler.send_msg(id, msg, attachment_str)

        txt = f"Сообщение успешно отправлено."
        self.vkapi_handler.send_msg(user_id, txt)
        return

    def delete_school(self, update):
        # Delete school.
        msg = update['object']['text']
        args = Utility.parse_arg(msg)

        # Only '1''s can delete the school.
        user_id = update['object']['from_id']
        school_id = args[0]
        role_id = self.db_handler.fetch_user_school_role(school_id, user_id)
        if not int(role_id) == int('1'):
            err = f"Ошибка: недостаточно прав (вам необходимо быть `Creator`, для этого действия)`."
            self.vkapi_handler.send_msg(user_id, err)
            return

        # Check whether school is valid
        school_name_given = " ".join(args[1:])
        school_name_true = self.db_handler.fetch_school_name(school_id)
        if school_name_given != school_name_true:
            err = f"Ошибка: неверно введено название школы (для вашей безопасности)."
            self.vkapi_handler.send_msg(user_id, err)
            return

        # For sad message
        former_members_ids = self.db_handler.fetch_school_members(school_id)

        self.db_handler.delete_school(school_id)
        txt = f"Успех: школа `{school_name_true}` (id: {school_id}) была удалена."

        # Send poor message to everyone.
        for member_id in former_members_ids:
            notification = f"""🔔 Уведомление. 🔔
Школа '{school_name_true}' (id: {school_id}) была удалена. Как следствие, вы больше не являяетесь её членом.  \n(@id{user_id}(инициатор))"""
            self.vkapi_handler.send_msg(member_id, notification)

        self.vkapi_handler.send_msg(user_id, txt)
        return

    def delete_group(self, update):
        # Delete group.
        msg = update['object']['text']
        args = Utility.parse_arg(msg)

        # Only '3''s and higher can delete the school.
        user_id = update['object']['from_id']
        group_id = args[0]
        school_id = self.db_handler.fetch_group_school(group_id)
        role_id = self.db_handler.fetch_user_school_role(school_id, user_id)
        if not int(role_id) <= int('3'):
            err = f"Ошибка: недостаточно прав (вам необходимо быть `Teacher` или выше для этого действия)`."
            self.vkapi_handler.send_msg(user_id, err)
            return

        # Check whether group_name is valid
        group_name_given = " ".join(args[1:])
        group_name_true = self.db_handler.fetch_group_name(group_id)
        if group_name_given != group_name_true:
            err = f"Ошибка: неверно введено название группы (для вашей безопасности)."
            self.vkapi_handler.send_msg(user_id, err)
            return
        # For sad
        former_members_ids = self.db_handler.fetch_group_members(group_id)

        self.db_handler.delete_group(group_id)
        txt = f"Успех: группа `{group_name_true}` (id: {group_id}) была удалена."

        # Send poor message to everyone.
        for member_id in former_members_ids:
            notification = f"""🔔 Уведомление. 🔔
                Группа '{group_name_true}' (id: {group_id}) была удалена. Как следствие, вы больше не являяетесь её членом. \n(@id{user_id}(инициатор))"""
            self.vkapi_handler.send_msg(member_id, notification)

        self.vkapi_handler.send_msg(user_id, txt)
        return

    def user_info(self, update):
        # Gives user information about his position in system.
        # Имя: nickname (id: user_id)
        # Groups_name (group_id: group_id) (school_name: school_name) -------- '[School_name] Group_name - id: id'
        # Schools_name (school_id: school_id) - corresponding role

        msg = update['object']['text']
        user_id = update['object']['from_id']

        # groups_txt
        groups_txt = []
        user_groups = self.db_handler.fetch_user_groups(user_id)
        if not user_groups:
            groups_txt = ["Вы не состоите ни в одной группе."]
        else:
            for group in user_groups:
                group_id, school_id, group_name = group
                group_school_name = self.db_handler.fetch_school_name(school_id)
                groups_txt.append(f"[\"{group_school_name}\"] \"{group_name}\" - group_id: {group_id}")

        # schools_txt
        user_schools = self.db_handler.fetch_user_schools(user_id)
        schools_txt = []
        for school in user_schools:
            school_id, creator_id, school_name = school
            role_id = self.db_handler.fetch_user_school_role(school_id, user_id)
            role_name = self.db_handler.fetch_role_name(role_id)
            schools_txt.append(f"-- \"{school_name}\" (school_id: {school_id}) - \"{role_name}\"")

        nickname = self.db_handler.fetch_user_name(user_id)
        endl = '\n'  # Otherwise it won't work

        txt = f"""======== ℹ Информация ℹ ========
        
Имя: {nickname} (@id{user_id}(@id{user_id}))
        
-+-+-+-+-+- 📚 Группы 📚 -+-+-+-+-+-
        {endl.join(groups_txt)}
        
-+-+-+-+-+- 🏫 Школы 🏫 -+-+-+-+-+-
        {endl.join(schools_txt)}
        
        """

        self.vkapi_handler.send_msg(user_id, txt)
        return

    def info_school(self, update):
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        school_id = args[0]

        # Fetch data
        school_name = self.db_handler.fetch_school_name(school_id)
        school_groups_ids = self.db_handler.fetch_school_groups(school_id)
        school_groups_names = []
        for group_id in school_groups_ids:
            school_groups_names.append(self.db_handler.fetch_group_name(group_id))

        school_groups = []
        for i in range(len(school_groups_ids)):
            school_groups.append((school_groups_ids[i], school_groups_names[i]))

        members_ids = self.db_handler.fetch_school_members(school_id)
        members_names = []
        members_groups = []
        members_roles = []
        for member_id in members_ids:
            members_names.append(self.db_handler.fetch_user_name(member_id))
            # Very bad code you could do better
            members_groups.append([self.db_handler.fetch_group_name(x) for x in
                                   self.db_handler.fetch_user_school_groups(school_id, member_id)])
            members_roles.append(self.db_handler.fetch_user_school_role(school_id, member_id))

        members = []
        # Now we have school_groups (group_id , group_name)
        # Now we have members (role_id, name, group_names, vk_id)
        # Based on data given (school is a tuple (id,school_name))
        # Return text message for the user
        members = sorted(members, key=lambda x: int(x[0]))

        for i in range(len(members_ids)):
            members.append((members_roles[i], members_names[i], members_groups[i], members_ids[i]))

        res = f"""======== ℹ Информация о школе 🏫 ========
        
Название: '{school_name}' (school_id: {school_id})
        
======== 📚 Школьные группы 📚 ========\n"""
        for group_id, group_name in school_groups:
            res += f"-- \"{group_name}\" (group_id: {group_id})\n"
        res += f"\n-+-+-+- 👨‍🏫 Члены организации 🧓👩‍🦱 -+-+-+-\n"

        members = sorted(members, key=lambda x: int(x[0]))
        prev_role = 0
        cur_role = 0
        for member in members:
            cur_role = member[0]
            if cur_role != prev_role:
                res = res + f"\n{self.db_handler.fetch_role_name(cur_role)}:\n"
                prev_role = cur_role
            # res += f'-- {member[1]} ({", ".join(member[2])}) [id{member[3]}]\n'
            res += f'-- {member[1]} (@id{member[3]}(@id{member[3]}))\n'
        res += '\n' + "-" * 60 + '\n'
        res += f'Итого: {len(members)} участников.\n'

        self.vkapi_handler.send_msg(user_id, res)
        return

        # Now we have school_groups (group_id , group_name)
        # Now we have members (role_id, name, group_names, vk_id)

        # txt = Utility.school_info((school_id, school_name), school_groups, members, self.db_handler)

    def info_group(self, update):
        # sends back message about group_id
        # TODO: check rights
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        group_id = args[0]
        group_name = self.db_handler.fetch_group_name(group_id)

        members_ids = self.db_handler.fetch_group_members(group_id)
        members = []
        school_id = self.db_handler.fetch_group_school(group_id)
        for member_id in members_ids:
            member_name = self.db_handler.fetch_user_name(member_id)
            members.append((self.db_handler.fetch_user_school_role(school_id, member_id), member_name, 0, member_id))
        members = sorted(members, key=lambda x: int(x[0]))
        res = f"======== Группа 📚 {group_name} ========\n"
        # - 👩‍🦱 Члены группы 🧓 -
        cur_role = 0
        prev_role = 0
        for member in members:
            cur_role = member[0]
            if cur_role != prev_role:
                res = res + f"\n{self.db_handler.fetch_role_name(cur_role)}:\n"
                prev_role = cur_role
            # res += f'-- {member[1]} ({", ".join(member[2])}) [id{member[3]}]\n'
            res += f'-- {member[1]} (@id{member[3]}(@id{member[3]}))\n'
        res += '\n' + "-" * 70 + '\n'
        res += f'Итого: {len(members)} участников.\n'

        self.vkapi_handler.send_msg(user_id, res)

    # def info_school_groups(self, update):
    #     # sends back message about all group_ids of school_id
    #     msg = update['object']['text']
    #     user_id = update['object']['from_id']
    #     args = Utility.parse_arg(msg)
    #     school_id = args[0]

    def info_student(self, update):
        # Returns info about a student as if he lived only in school_id.
        # TODO: Permissions
        # TODO: Feature: show similar groups.
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        school_id = args[0]
        school_name = self.db_handler.fetch_school_name(school_id)
        student_id = args[1]
        student_name = self.db_handler.fetch_user_name(student_id)

        res = f"""======== 🧍 Человек в {school_name} 🏫 ========

Имя: {student_name} (@id{student_id}(@id{student_id}))
Роль: {self.db_handler.fetch_role_name(self.db_handler.fetch_user_school_role(school_id, student_id))}
        
-+-+-+-+-+- 📚  Группы -+-+-+-+-+-\n"""

        student_groups_ids = self.db_handler.fetch_user_school_groups(school_id, student_id)
        user_groups_ids = self.db_handler.fetch_user_school_groups(school_id, user_id)
        groups = [(x, self.db_handler.fetch_group_name(x), x in user_groups_ids) for x in student_groups_ids]

        for group in groups:
            group_id = group[0]
            group_name = group[1]
            group_mutual = group[2]
            res += f"-- {group_name} {'🟢 ' if group_mutual else '  '}(group_id: {group_id})\n"
        res += "-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-"
        if True in [x[2] for x in groups]:
            res += "\n🟢 - общие группы"
        self.vkapi_handler.send_msg(user_id, res)
        return
