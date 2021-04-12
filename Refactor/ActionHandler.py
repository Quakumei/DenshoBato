# Handles any action committed by user
from CodeList import *
import Utility
import KeyboardSets


class ActionHandler:
    def __init__(self, vkapi_handler, db_handler, debug_mode=True):
        self.debug_mode = debug_mode
        self.vkapi_handler = vkapi_handler
        self.db_handler = db_handler
        self.help_text = self._load_help()
        self.test = 0

        self.act_table = {
            # Put new actions here (don't forget to add the command in config)
            EVENT.REGISTER: self.register_prompt,

            CODE.RETURN: self._return,
            CODE.CONTINUE: self._continue,
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

    def handle_act(self, code, update):
        try:
            self.act_table[code](update)
        except Exception as e:
            print(
                f"{'=' * 25 + ' ' + 'EXCEPTION OCCURED' + ' ' + '=' * 25}\nIt says: {str(e)}\n{'=' * (50 + len('EXCEPTION OCCURED') + 2)}")
            msg = "🚫 Ошибка: " + str(e)
            user_id = update['object']['from_id']
            self.vkapi_handler.send_msg(user_id, msg)
            self._return(update, "Меню")

    def _load_help(self):
        # Loads help string (to put commands in place)

        # Load CODE_DICT 'in reverse' so we can call ct[CODE] to get string
        ct = {}
        for key, value in CODE_DICT.items():
            ct[value] = key

        txt = f"""
Привет! Я цифровой голубь-почтальон Бато. Моя работа - вовремя доставлять информацию от учителей. 😉

~~~~ Команды ~~~~
· !{ct[CODE.HELP]} - вывести это сообщение.
· - Меню - выйти в главное меню. 
-- 🖊️ Регистрация и вы 

· !{ct[CODE.REGISTER]} (username) - зарегистрироваться в системе с именем username. Если имя не указано, используется ваше имя в социальной сети. Этой же командой можно сменить себе имя.
· !{ct[CODE.USER_INFO]} - вывести список групп и школ, в которых вы числитесь.


-- ℹ Информация ️

· !{ct[CODE.INFO_SCHOOL]} [school_id] -  вывести информацию о школе (все члены).
· !{ct[CODE.INFO_GROUP]} [group_id] - вывести информацию о группе и её составе (все члены).
· !{ct[CODE.INFO_STUDENT]} [school_id] [vk_id] - вывести информацию о пользователе как члене школы (все члены).


-- 📚🏫 Операции с группами и школами 

· !{ct[CODE.CREATE_SCHOOL]} [school_name] - создать школу с именем school_name. 
· !{ct[CODE.CREATE_GROUP]} [school_id] [group_name] - создать группу с именем group_name в школе с school_id (Преподаватель).
· !{ct[CODE.DELETE_SCHOOL]} [school_id] [school_name] - удалить школу (Создатель).
· !{ct[CODE.DELETE_GROUP]} [group_id] [group_name] - удалить группу (Преподаватель).


-- 👨👦👧 Операции над пользователями


· !{ct[CODE.INVITE_USER]} [school_id] [vk_id] - пригласить (добавить) пользователя в школу как вольного слушателя (Ученик).
· !{ct[CODE.ADD_TO_GROUP]} [group_id] [vk_id] - добавить пользователя в группу (Преподаватель).
· !{ct[CODE.UPDATE_ROLE]} [school_id] [vk_id] [new_role_id] - сменить роль пользователю (Администратор).
· !{ct[CODE.REMOVE_USER]} [school_id] [vk_id] - исключить пользователя из школы (Преподаватель).
· !{ct[CODE.REMOVE_USER_FROM_GROUP]} [school_id] [group_id] [vk_id] - исключить пользователя из группы (Преподаватель).


-- ✉ Отправка и рассылка сообщений

· !{ct[CODE.PM_MSG]} [vk_id] (ваше сообщение) - отправить сообщение пользователю. (отправляется ваше сообщение без команды)
· !{ct[CODE.GROUP_MSG]} [group_id] (ваше сообщение) - отправить сообщение группе (Преподаватель). (отправляется ваше сообщение без команды)

~~~~~~~~~~~~~~~~

Бот разработан в рамках школьного проекта ГОУ ЯО "Лицей №86" в 2021 году. 

Если найдёте ошибки/баги, сообщите мне!
Разработчик: @id388032588(Тампио Илья), ученик 11Б класса.
Github: github.com/Quakumei Telegram: @yasumi404
"""
        return txt

    def help(self, update):
        # Print help
        # Permission: everyone

        user_id = update['object']['from_id']

        buttons_res = [[KeyboardSets.text_button('- Меню', "WHITE")]]
        kb = KeyboardSets.create_kb(True, buttons_res)

        self.vkapi_handler.send_msg(user_id, self.help_text, json_kb=kb)
        return

    def echo(self, update):
        # Send message back (Maintenance use only)

        msg = update['object']['text']

        if not msg:
            msg = "fgsfds"
        user_id = update['object']['from_id']
        self.vkapi_handler.send_msg(user_id, msg)

    def create_school(self, update):
        # Creates school (and makes user its owner).
        # Permission: everyone

        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        # Remove trailing backspace and parse school_name
        school_name = " ".join(args)

        school_id = self.db_handler.create_school(school_name, user_id)
        txt = f"✅ Поздравляем, вы создали школу {school_name}! (school_id: {school_id})"
        self.vkapi_handler.send_msg(user_id, txt)
        self._return(update, "Меню")

    def register(self, update):
        # Registers user in the system (Puts an entry to users table).
        # If no argument passed - use his vk name instead.
        # Permission: everyone

        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        nickname = " ".join(args) if args else self.vkapi_handler.get_name(user_id, short=True)

        self.db_handler.user_nickname_update(user_id, nickname)

        txt = f"✅ Вы успешно установили себе имя {nickname}."
        self.vkapi_handler.send_msg(user_id, txt)
        self._return(update, "Меню")

    def invalid(self, update):
        # Wrong command case
        raise Exception("Неверная команда.")

    def invite_user(self, update):
        # Add person to school if you have permission.
        # Permission: 3 or less
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        vk_id = args[1]
        school_id = args[0]

        # Permission check and school existence checks
        initiator_role = self.db_handler.fetch_user_school_role(school_id, user_id)
        if not initiator_role <= 3:
            raise Exception("У вас недостаточно прав.")

        self.db_handler.add_user(vk_id, school_id, user_id)

        txt = f"✅ Вы успешно добавили пользователя {vk_id} в {school_id}."
        self.vkapi_handler.send_msg(user_id, txt)
        self._return(update, "Меню")

        # Send notification to the invited.
        notification = f"🔔 Уведомление. 🔔\n"
        notification += f"Вы были приняты в качестве {self.db_handler.fetch_role_name(5)} в школу {self.db_handler.fetch_school_name(school_id)} (school_id: {school_id})" \
                        f"\n(@id{user_id}(инициатор))."
        self.vkapi_handler.send_msg(vk_id, notification)

    def create_group(self, update):
        # Create group with school_name in school_id. Put creator in it. Return its id.
        # Permission: 3 or less
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        school_id = args[0]
        group_name = " ".join(args[1:])

        # Permission check and school existence checks
        initiator_role = self.db_handler.fetch_user_school_role(school_id, user_id)
        if not initiator_role <= 3:
            raise Exception("У вас недостаточно прав.")

        group_id = self.db_handler.create_group(group_name, school_id, user_id)

        txt = f"✅ Вы успешно создали группу с названием {group_name} в {school_id}. (group_id: {group_id})"
        self.vkapi_handler.send_msg(user_id, txt)
        self._return(update, "Меню")

    def add_to_group(self, update):
        # Add a user to the group.
        # Permission: 3 or less
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        vk_id = args[1]
        group_id = args[0]

        # Permission check and school existence checks
        initiator_role = self.db_handler.fetch_user_school_role(self.db_handler.fetch_group_school(group_id), user_id)
        if not initiator_role <= 3:
            raise Exception("У вас недостаточно прав.")

        self.db_handler.add_to_group(group_id, vk_id, user_id)

        txt = f"✅ Вы успешно добавили {vk_id} в группу {group_id}."
        self.vkapi_handler.send_msg(user_id, txt)
        self._return(update)

        # Send notification.
        notification = f"""🔔 Уведомление. 🔔\nВы были добавлены в группу {self.db_handler.fetch_group_name(group_id)} (group_id: {group_id}).
        (@id{user_id}(инициатор))"""
        self.vkapi_handler.send_msg(vk_id, notification)

    def update_role(self, update):
        # Update role of the user.
        # Permission: 3 or less (can change roles only to roles bigger than user's role_id)
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        school_id = args[0]
        vk_id = args[1]
        new_role_id = args[2]
        last_role_id = self.db_handler.fetch_user_school_role(school_id, vk_id)

        # Check permission
        user_role_id = self.db_handler.fetch_user_school_role(school_id, user_id)
        target_role_id = self.db_handler.fetch_user_school_role(school_id, vk_id)
        if not user_role_id <= 3 or int(new_role_id) <= int(user_role_id) or int(target_role_id) <= int(user_role_id):
            raise Exception("У вас недостаточно прав.")

        self.db_handler.update_role(school_id, vk_id, new_role_id)
        txt = f"✅ Вы успешно сменили роль '{vk_id}' в школе '{school_id}' на '{new_role_id}'."
        self.vkapi_handler.send_msg(user_id, txt)

        # Send notification
        notification = f"🔔 Уведомление. 🔔\n"
        notification += f"Произошла смена вашей роли в {self.db_handler.fetch_school_name(school_id)} (school_id: {school_id}):{self.db_handler.fetch_role_name(last_role_id)} --> {self.db_handler.fetch_role_name(new_role_id)}\n(@id{user_id}(инициатор))."
        self.vkapi_handler.send_msg(vk_id, notification)

    def expel(self, update):
        # Removes user from school
        # Permission: 3 or less
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        school_id = args[0]
        target_id = args[1]

        # Permission check
        initiator_role = self.db_handler.fetch_user_school_role(school_id, user_id)
        target_role = self.db_handler.fetch_user_school_role(school_id, target_id)
        if not initiator_role <= 3 or not initiator_role < target_role:
            raise Exception("У вас недостаточно прав.")

        self.db_handler.remove_user_from_school(school_id, target_id)

        txt = f"✅ Вы успешно исключили '{target_id}' из школы '{school_id}'."
        self.vkapi_handler.send_msg(user_id, txt)
        self._return(update, 'Меню')

        # Send notification
        notification = f"""🔔 Уведомление. 🔔
Вы были исключены из школы '{self.db_handler.fetch_school_name(school_id)}' (school_id: {school_id}) \n(@id{user_id}(инициатор))."""
        self.vkapi_handler.send_msg(target_id, notification)

    def expel_from_group(self, update):
        # Removes user from group
        # Permission: 3 or less

        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        school_id = args[0]
        group_id = args[1]
        target_id = args[2]

        # Permission check
        initiator_role = self.db_handler.fetch_user_school_role(school_id, user_id)
        target_role = self.db_handler.fetch_user_school_role(school_id, target_id)
        if not initiator_role <= 3 and initiator_role >= target_role:
            raise Exception("У вас недостаточно прав.")

        self.db_handler.remove_from_group(group_id, target_id)

        txt = f"✅ Вы успешно исключили '{target_id}' из группы '{group_id}' школы '{school_id}'."
        self.vkapi_handler.send_msg(user_id, txt)
        self._return(update, "Меню")

        # Send notification
        notification = f"""🔔 Уведомление. 🔔
Вы были исключены из группы '{self.db_handler.fetch_group_name(group_id)}' (group_id: {group_id}) \n(@id{user_id}(инициатор))"""
        self.vkapi_handler.send_msg(target_id, notification)

    def group_msg(self, update):
        # Send message to a group
        # Permission: 3 or less

        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        group_id = args[0]

        # Permission check
        initiator_role = self.db_handler.fetch_user_school_role(self.db_handler.fetch_group_school(group_id), user_id)
        if not initiator_role <= 3:
            raise Exception("У вас недостаточно прав.")

        # la crosse
        bad_n_flag = False
        if not group_id.isnumeric() and group_id[0].isnumeric():
            bad_n_flag = True
            group_id = group_id.split('\n', 1)[0]

        # Fetch ids
        mailing_list_ids = [x[0] for x in self.db_handler.fetch_group_members(group_id)]

        # Send msg
        # Make msg: sender to whom (group_id and word) and school
        msg = msg.split(' ', 1)[1]
        msg = msg[len(group_id):]

        user_id = user_id
        sender_name = self.db_handler.fetch_user_name(user_id)
        group_name = self.db_handler.fetch_group_name(group_id)

        hat = f"✉ Сообщение ✉\n[ОТ: ] {sender_name}(id:@id{user_id}(@id{user_id}))\n[КОМУ: ] {group_name}(group_id:{group_id})\n\n"
        msg = hat + msg
        attachments = update['object']['attachments']
        attachment_str, urls = Utility.parse_attachments2str(attachments)
        if attachment_str:
            footer = f"\nВложения:\n" + str("\n".join(urls))
            msg = msg + footer
        for vk_id in mailing_list_ids:
            self.vkapi_handler.send_msg(vk_id, msg, attachment_str)

        txt = f"✅ Рассылка успешно выполнена."
        self.vkapi_handler.send_msg(user_id, txt)
        self._return(update, "Меню")

    def pm_msg(self, update):
        # Send message to a user
        # Permission: should be in the same school.
        # Note: code is lame (copied from group_msg)
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        vk_id = args[0]

        # Permission check (have common school)
        flag = False
        for g1 in self.db_handler.fetch_user_schools(vk_id):
            for g2 in self.db_handler.fetch_schools(user_id):
                if g1 == g2:
                    flag = True
                    break
            if flag is True:
                break
        if not flag:
            raise Exception("У вас недостаточно прав.")

        bad_n_flag = False
        if not vk_id.isnumeric() and vk_id[0].isnumeric():
            bad_n_flag = True
            group_id = vk_id.split('\n', 1)[0]

        # Weird code ahead: copy from group_msg
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

        self.vkapi_handler.send_msg(vk_id, msg, attachment_str)

        txt = f"✅ Сообщение успешно отправлено."
        self.vkapi_handler.send_msg(user_id, txt)
        self._return(update, "Меню")

    def delete_school(self, update):
        # Delete school.
        # Permission: 1 only
        msg = update['object']['text']
        args = Utility.parse_arg(msg)
        user_id = update['object']['from_id']

        school_id = args[0]

        # Permission check
        initiator_role = self.db_handler.fetch_user_school_role(school_id, user_id)
        if not initiator_role <= 1:
            raise Exception("У вас недостаточно прав.")

        # Check whether school_name is valid
        school_name_given = " ".join(args[1:])
        school_name_true = self.db_handler.fetch_school_name(school_id)
        if school_name_given != school_name_true:
            raise Exception("Неверно введено название школы (для вашей безопасности).")

        former_members_ids = self.db_handler.fetch_school_members(school_id)
        self.db_handler.delete_school(school_id)

        # Send notifications
        for member_id in former_members_ids:
            notification = f"""🔔 Уведомление. 🔔
Школа '{school_name_true}' (id: {school_id}) была удалена. Как следствие, вы больше не являяетесь её членом.  \n(@id{user_id}(инициатор))"""
            self.vkapi_handler.send_msg(member_id, notification)

        txt = f"✅ Успех: школа `{school_name_true}` (id: {school_id}) была удалена."
        self.vkapi_handler.send_msg(user_id, txt)
        self._return(update, "Меню")

    def delete_group(self, update):
        # Delete group.
        # Permission: 3 or less
        msg = update['object']['text']
        args = Utility.parse_arg(msg)
        user_id = update['object']['from_id']

        group_id = args[0]

        # Permission check
        initiator_role = self.db_handler.fetch_user_school_role(self.db_handler.fetch_group_school(group_id), user_id)
        if not initiator_role <= 3:
            raise Exception("У вас недостаточно прав.")

        # Check whether group_name is valid
        group_name_given = " ".join(args[1:])
        group_name_true = self.db_handler.fetch_group_name(group_id)
        if group_name_given != group_name_true:
            raise Exception(f"Ошибка: неверно введено название группы (для вашей безопасности).")

        former_members_ids = [x[0] for x in self.db_handler.fetch_group_members(group_id)]
        self.db_handler.delete_group(group_id)

        # Send notifications
        for member_id in former_members_ids:
            notification = f"""🔔 Уведомление. 🔔
                Группа '{group_name_true}' (group_id: {group_id}) была удалена. Как следствие, вы больше не являяетесь её членом. \n(@id{user_id}(инициатор))"""
            self.vkapi_handler.send_msg(member_id, notification)

        txt = f"✅ Успех: группа `{group_name_true}` (id: {group_id}) была удалена."
        self.vkapi_handler.send_msg(user_id, txt)
        self._return(update, "Меню")

    def user_info(self, update):
        # Gives user information about his position in system.
        # Permission: anybody
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
        if user_schools is False:
            user_schools = []
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

        buttons_res = [[KeyboardSets.text_button('- Меню', "WHITE")]]
        kb = KeyboardSets.create_kb(True, buttons_res)

        self.vkapi_handler.send_msg(user_id, txt, json_kb=kb)

    def info_school(self, update):
        # Writes info about the school.
        # Permission: any member of the school

        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)
        school_id = args[0]

        # Permission check
        initiator_role = self.db_handler.fetch_user_school_role(school_id, user_id)
        if not initiator_role:
            raise Exception("У вас недостаточно прав.")

        # Fetch data
        school_name = self.db_handler.fetch_school_name(school_id)
        school_groups_ids = [x[0] for x in self.db_handler.fetch_school_groups(school_id)]
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
            res += f'-- {member[1]} (@id{member[3]}(@id{member[3]}))\n'
        res += '\n' + "-" * 60 + '\n'
        res += f'Итого: {len(members)} участников.\n'

        self.vkapi_handler.send_msg(user_id, res)
        self._return(update, "Меню")

    def info_group(self, update):
        # Prints info about the group.
        # Permission: every school member

        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        group_id = args[0]

        # Permission check
        school_id = self.db_handler.fetch_group_school(group_id)
        if not self.db_handler.user_in_school_check(user_id, school_id):
            raise Exception("У вас недостаточно прав.")

        group_name = self.db_handler.fetch_group_name(group_id)
        members_ids = [x[0] for x in self.db_handler.fetch_group_members(group_id)]
        members = []
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

        buttons_res = [[KeyboardSets.text_button('- Меню', "WHITE")]]
        kb = KeyboardSets.create_kb(True, buttons_res)

        self.vkapi_handler.send_msg(user_id, res, json_kb=kb)

    def info_student(self, update):
        # Returns info on student in scope of the school.
        # Permission: school_id is common school of both students.
        msg = update['object']['text']
        user_id = update['object']['from_id']
        args = Utility.parse_arg(msg)

        school_id = args[0]
        student_id = args[1]

        school_name = self.db_handler.fetch_school_name(school_id)
        student_name = self.db_handler.fetch_user_name(student_id)

        # Permission check
        user_school_list = self.db_handler.fetch_user_schools(user_id)
        target_school_list = self.db_handler.fetch_user_schools(student_id)
        if school_id not in user_school_list or school_id not in target_school_list:
            raise Exception("У вас недостаточно прав.")

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
        self._return(update, "Меню")

    def register_prompt(self, update):
        # Entry point on "Start" button press.
        # Shall never be called by other means.
        user_id = update['object']['from_id']
        msg = "Регистрация"

        user_vk_name = self.vkapi_handler.get_name(user_id, short=True)
        buttons = KeyboardSets.get_register_buttons(user_vk_name)
        print(buttons)
        self.vkapi_handler.send_msg(user_id, msg, json_kb=buttons)

    def __choose_school(self, user_id, level, words, full=False, buttons_rows=2):
        # message maker for _continue
        # buttons, txt = choose_school(user_id, level)
        # Message
        buttons = []
        schools = self.db_handler.fetch_user_schools(user_id, 4)
        schools_txt = Utility.schools2txt(schools)
        txt = schools_txt + "\nПожалуйста, выберите школу."

        # Buttons
        for sch in schools:
            buttons.append(
                KeyboardSets.text_button(
                    f"{COMMAND_SYMBOL if full else (IGNORE_SYMBOL + ' ')}{' '.join(words + [str(sch[0])])}", "GREEN"))
        buttons = Utility.arrange_buttons(buttons, buttons_rows)
        return buttons, txt

    def __choose_group(self, user_id, level, words, full=False, buttons_rows=2):
        # message maker for _continue
        # buttons, txt = choose_group(user_id, level)
        # Message
        buttons = []
        groups = self.db_handler.fetch_user_groups(user_id, level)
        groups_txt = Utility.groups2txt(groups)
        txt = groups_txt + "\nПожалуйста, выберите группу."

        # Buttons
        for g in groups:
            buttons.append(
                KeyboardSets.text_button(
                    f"{COMMAND_SYMBOL if full else (IGNORE_SYMBOL + ' ')}{' '.join(words + [str(g[0])])}", "GREEN"))
        buttons = Utility.arrange_buttons(buttons, buttons_rows)
        return buttons, txt

    def __choose_group_list(self, groups, words, full=False, buttons_rows=2, secondary=True):
        # message maker for _continue
        # buttons, txt = choose_group(user_id, level)
        # Message
        buttons = []
        # groups = self.db_handler.fetch_user_groups(user_id, level)
        groups_txt = Utility.groups2txt(groups)
        txt = groups_txt + "\nПожалуйста, выберите группу."

        # Buttons
        for g in groups:
            buttons.append(
                KeyboardSets.text_button(
                    f"{COMMAND_SYMBOL if full else (IGNORE_SYMBOL + ' ')}{' '.join(words + ['гр' + str(g[0]) if secondary else str(g[0])])}",
                    "GREEN"))
        buttons = Utility.arrange_buttons(buttons, buttons_rows)
        return buttons, txt

    def __choose_member(self, group_id, words, full=True, buttons_rows=2, from_secondary=True):
        # message maker for _continue
        # buttons, txt = choose_group(user_id, level)
        # Message

        # from_secondary -- done
        # members2txt -- DOne

        buttons = []
        members = self.db_handler.fetch_group_members(group_id)
        members_txt = Utility.members2txt(members)
        txt = members_txt + "\nПожалуйста, выберите пользователя."

        # Buttons
        for memb in members:
            buttons.append(
                KeyboardSets.text_button(
                    f"{COMMAND_SYMBOL if full else (IGNORE_SYMBOL + ' ')}{' '.join(([x for x in words if x[:2] != 'гр'] if from_secondary else words) + [str(memb[0])])}",
                    "GREEN"))
        buttons = Utility.arrange_buttons(buttons, buttons_rows)
        return buttons, txt

    def __choose_role(self, level, words, full=True, buttons_rows=2):
        # message maker for _continue
        # buttons, txt = choose_role(user_id, level)
        #    Message
        buttons = []
        roles = self.db_handler.fetch_roles(level=level)
        roles_txt = Utility.roles2txt(roles)
        txt = roles_txt + "\nПожалуйста, выберите новую роль."

        # Buttons
        for r in roles:
            buttons.append(
                KeyboardSets.text_button(
                    f"{COMMAND_SYMBOL if full else (IGNORE_SYMBOL + ' ')}{' '.join(words + [str(r[0])])}", "BLUE"))
        buttons = Utility.arrange_buttons(buttons, buttons_rows)

        return buttons, txt

    def _continue(self, update):
        # Well, that's an atrocity of mine.
        # I can't explain what exactly it does.
        # Handles like 80% of UI and especially buttons.
        # I don't want to even look at that part of code.

        # Action types according to count of arguments
        INSTANT = [USER_INFO_WORD, HELP_WORD, REGISTER_WORD]
        ONE_ARG = [INFO_SCHOOL_WORD, INFO_GROUP_WORD]
        TWO_ARG = [INVITE_USER_WORD, REMOVE_USER_WORD,
                   INFO_STUDENT_WORD, ADD_TO_GROUP_WORD]
        THR_ARG = [UPDATE_ROLE_WORD, REMOVE_USER_FROM_GROUP_WORD]
        MANUAL = [CREATE_SCHOOL_WORD, DELETE_SCHOOL_WORD,
                  CREATE_GROUP_WORD, DELETE_GROUP_WORD,
                  GROUP_MSG_WORD, PM_MSG_WORD]

        msg = update['object']['text'][2:]
        user_id = update['object']['from_id']
        buttons = []
        txt = '<._._.>'

        # Обработка сообщения
        words = msg.split(' ')
        args_count = len(words) - 1

        if words[0] in MANUAL:
            self.vkapi_handler.send_msg(user_id, f"Данная команда прописывается вручную. Подробнее в !помощь")
            self._return(update, "Меню")
            return

        elif words[0] in THR_ARG:
            if args_count == 0:
                if words[0] == UPDATE_ROLE_WORD:
                    buttons, txt = self.__choose_school(user_id, 3, words)
                elif words[0] == REMOVE_USER_FROM_GROUP_WORD:
                    buttons, txt = self.__choose_school(user_id, 3, words)
            elif args_count == 1:
                if words[0] == UPDATE_ROLE_WORD:
                    # Choose group
                    school_id = words[1]
                    groups = self.db_handler.fetch_school_groups(school_id)
                    buttons, txt = self.__choose_group_list(groups, words, full=False, buttons_rows=2)
                elif words[0] == REMOVE_USER_FROM_GROUP_WORD:
                    school_id = words[1]
                    groups = self.db_handler.fetch_school_groups(school_id)
                    buttons, txt = self.__choose_group_list(groups, words, full=False, buttons_rows=2, secondary=False)
            elif args_count == 2:
                if words[0] == UPDATE_ROLE_WORD:
                    if words[2][:2] == 'гр':
                        # Show group ask whom to change
                        group_id = words[2][2:]
                        buttons, txt = self.__choose_member(group_id, words, full=False)
                    else:
                        # Pick role (lower than yours)
                        target_id = words[2]
                        school_id = words[1]
                        buttons, txt = self.__choose_role(self.db_handler.fetch_user_school_role(school_id, user_id),
                                                          words, full=True,
                                                          buttons_rows=1)
                elif words[0] == REMOVE_USER_FROM_GROUP_WORD:
                    if words[2]:
                        # Show group ask whom to expel
                        group_id = words[2]
                        buttons, txt = self.__choose_member(group_id, words, full=True)

        elif words[0] in TWO_ARG:
            if args_count == 0:
                if words[0] == INVITE_USER_WORD:
                    buttons, txt = self.__choose_school(user_id, 4, words)

                elif words[0] == REMOVE_USER_WORD:
                    buttons, txt = self.__choose_school(user_id, 3, words)

                elif words[0] == INFO_STUDENT_WORD:
                    buttons, txt = self.__choose_school(user_id, 5, words)

                elif words[0] == ADD_TO_GROUP_WORD:
                    buttons, txt = self.__choose_group(user_id, 3, words)

            elif args_count == 1:
                if words[0] == INVITE_USER_WORD:
                    txt = f"Пожалуйста, напишите команду самостоятельно.\nКоманда: '{COMMAND_SYMBOL}{' '.join(words)} <vk_id>'"

                elif words[0] == REMOVE_USER_WORD:
                    # List groups
                    school_id = words[1]
                    groups = self.db_handler.fetch_school_groups(school_id)
                    buttons, txt = self.__choose_group_list(groups, words, full=False, buttons_rows=2)
                    pass
                elif words[0] == INFO_STUDENT_WORD:
                    # List groups
                    school_id = words[1]
                    groups = self.db_handler.fetch_school_groups(school_id)
                    buttons, txt = self.__choose_group_list(groups, words, full=False, buttons_rows=2)
                    pass
                elif words[0] == ADD_TO_GROUP_WORD:
                    txt = f"Пожалуйста, напишите команду самостоятельно.\nКоманда: '{COMMAND_SYMBOL}{' '.join(words)} <vk_id>'"

            elif args_count == 2:
                # Only triggers when group are needed to be shown.
                if words[0] == INVITE_USER_WORD:
                    pass
                elif words[0] == REMOVE_USER_WORD:
                    # Show chosen group and choose_member
                    # гр123
                    group_id = words[2][2:]
                    buttons, txt = self.__choose_member(group_id, words, full=True)
                    pass
                elif words[0] == INFO_STUDENT_WORD:
                    # Show chosen group and choose_member
                    # гр123
                    group_id = words[2][2:]
                    buttons, txt = self.__choose_member(group_id, words, full=True)
                    pass
                elif words[0] == ADD_TO_GROUP_WORD:
                    pass
                pass

            elif args_count == 3:
                # Never
                pass

        elif words[0] in ONE_ARG:
            if args_count == 0:
                # Display info and show buttons
                if words[0] == INFO_GROUP_WORD:
                    buttons, txt = self.__choose_group(user_id, 5, words, full=True)

                elif words[0] == INFO_SCHOOL_WORD:
                    buttons, txt = self.__choose_school(user_id, 5, words, full=True)

            elif args_count == 1:
                # That won't happen.
                return

        elif words[0] in ["Потом", "Отмена", "Меню"]:
            # Вывести менюшку.
            txt = "Для получения справки нажмите !помощь"
            buttons = []
            for i in CODE_DICT:
                if i not in []:
                    if i in INSTANT:  # Action ready
                        buttons.append(KeyboardSets.text_button(f"{COMMAND_SYMBOL}{i}", color="BLUE"))
                    else:
                        buttons.append(KeyboardSets.text_button(f"{IGNORE_SYMBOL} {i}", color="WHITE"))
            buttons = Utility.arrange_buttons(buttons, 3)
        
        buttons.append([KeyboardSets.text_button('- Отмена', "WHITE")])
        buttons = KeyboardSets.create_kb(True, buttons)
        self.vkapi_handler.send_msg(user_id, txt, json_kb=buttons)
        return

    def _return(self, update, word="Отмена"):
        # Prints button to go home
        msg = update['object']['text'][2:]
        user_id = update['object']['from_id']
        ans = '<...>'
        buttons_res = [[KeyboardSets.text_button(f'- {word}', "WHITE")]]
        kb = KeyboardSets.create_kb(True, buttons_res, False)
        self.vkapi_handler.send_msg(user_id, ans, json_kb=kb)
