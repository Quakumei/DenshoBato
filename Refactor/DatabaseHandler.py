# Everything related to SQL, etc goes here.
# Nothing related to SQL ever goes out.

import sqlite3


class DatabaseHandler:

    def __init__(self, dbfile=None):
        if dbfile is None:
            dbfile = "bato.db"

        # Basic connection
        self.connection = sqlite3.connect(dbfile)
        self.cursor = self.connection.cursor()

        # Initializing database script
        init_tables_cmds = ["pragma foreign_keys = ON",
                            "CREATE TABLE IF NOT EXISTS users(vk_id INTEGER PRIMARY KEY, nickname TEXT)",
                            "CREATE TABLE IF NOT EXISTS schools(school_id INTEGER PRIMARY KEY AUTOINCREMENT, creator_vk_id INTEGER, school_name TEXT)",
                            "CREATE TABLE IF NOT EXISTS roles(role_id INTEGER PRIMARY KEY AUTOINCREMENT, permissions INTEGER, role_name TEXT)",
                            "CREATE TABLE IF NOT EXISTS groups(group_id INTEGER PRIMARY KEY AUTOINCREMENT, school_id INTEGER, group_name TEXT, FOREIGN KEY(school_id) REFERENCES schools(school_id))",
                            "CREATE TABLE IF NOT EXISTS roles_membership(vk_id INTEGER, role_id INTEGER, school_id INTEGER, FOREIGN KEY(school_id) REFERENCES schools(school_id), FOREIGN KEY(vk_id) REFERENCES users(vk_id), FOREIGN KEY(role_id) REFERENCES roles(role_id))",
                            "CREATE TABLE IF NOT EXISTS groups_membership(vk_id INTEGER, group_id INTEGER, FOREIGN KEY(group_id) REFERENCES groups(group_id), FOREIGN KEY(vk_id) REFERENCES users(vk_id))",
                            "SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%'ORDER BY 1"]
        for cmd in init_tables_cmds:
            self.cursor.execute(cmd)
        results = self.cursor.fetchall()
        # Print created tables for check
        print(results)

        # Insert roles in roles table if not already here
        self.cursor.execute("SELECT role_id FROM roles")
        results = self.cursor.fetchall()
        print(results)
        if not results:
            init_roles_cmds = [
                f"INSERT INTO roles (permissions, role_name) VALUES ({255},\"{'Создатель'}\")",
                f"INSERT INTO roles (permissions, role_name) VALUES ({127},\"{'Администратор'}\")",
                f"INSERT INTO roles (permissions, role_name) VALUES ({47},\"{'Преподаватель'}\")",
                f"INSERT INTO roles (permissions, role_name) VALUES ({3}, \"{'Ученик'}\")",
                f"INSERT INTO roles (permissions, role_name) VALUES ({1}, \"{'Вольный слушатель'}\")",
                f"SELECT * FROM roles"
            ]
            print(init_roles_cmds)
            for cmd in init_roles_cmds:
                self.cursor.execute(cmd)
            # Print created roles for check
            results = self.cursor.fetchall()
            self.connection.commit()
            print(results)

    def create_school(self, school_name, creator_vk_id):
        # Creates school, assigns creator and returns new school's id.
        print(f"Adding school {school_name} for {creator_vk_id}...")

        # Add school to schools table
        cmd1 = f"INSERT INTO schools (creator_vk_id, school_name) VALUES ({creator_vk_id},\"{school_name}\")"
        try:
            self.cursor.execute(cmd1)
        except sqlite3.IntegrityError:
            self.connection.rollback()
            raise Exception("Вы не зарегистрированы в системе. Напишите !помощь, чтобы узнать больше.")

        # Fetch new school's id
        cmd2 = f"SELECT school_id FROM schools WHERE school_name LIKE \"{school_name}\" AND creator_vk_id LIKE {creator_vk_id}"
        self.cursor.execute(cmd2)
        resp = self.cursor.fetchall()
        print(f"DB response is: '{resp}'")
        school_id = resp[-1][0]
        print(f"New school id is {school_id}")

        # Give the creator the role of creator of the school
        cmd3 = f"INSERT INTO roles_membership (vk_id, role_id, school_id) VALUES ({creator_vk_id}, {1}, {school_id})"

        # Commit changes to the db
        self.connection.commit()

        return school_id

    def user_nickname_update(self, vk_id, nickname):
        # Updates users nickname if vk_id is here, creates an entry otherwise.

        # Check if entry is presented
        cmd1 = f"SELECT vk_id FROM users WHERE vk_id LIKE {vk_id}"
        self.cursor.execute(cmd1)
        results = self.cursor.fetchall()

        # print(results)
        if not results:
            cmd2 = f"INSERT INTO users (vk_id, nickname) VALUES ({vk_id},'{nickname}')"
        else:
            cmd2 = f"UPDATE users SET nickname='{nickname}' WHERE vk_id={vk_id}"
        self.cursor.execute(cmd2)
        self.connection.commit()

    def add_user(self, vk_id, school_id, inviter_id):
        # Add user to school (give him the role of Reader (1))

        # Check whether the entry is presented and return -2 in that case
        if self.user_in_school_check(vk_id, school_id):
            raise Exception(
                f"Пользователь '{self.fetch_user_name(vk_id)}' уже в составе '{self.fetch_school_name(school_id)}'.")

        # Check whether the invitee is registered
        if not self.user_check(vk_id):
            raise Exception(f"Пользователь @id{vk_id} не зарегистрирован в системе.")

        # Execute
        cmd4 = f"INSERT INTO roles_membership (vk_id, role_id, school_id) VALUES ({vk_id}, {5}, {school_id})"
        self.cursor.execute(cmd4)
        self.connection.commit()

    def create_group(self, group_name, school_id, user_id):
        # Create the group and return its group_id

        # Check whether there is already group with that name
        cmd2 = f"SELECT * FROM groups WHERE school_id LIKE {school_id} AND group_name LIKE '{group_name}'"
        self.cursor.execute(cmd2)
        res = self.cursor.fetchall()
        if res:
            raise Exception(f"Группа с таким именем в этой школе уже существует.")

        # Create group
        cmd3 = f"INSERT INTO groups (school_id, group_name) VALUES ({school_id}, '{group_name}')"
        self.cursor.execute(cmd3)
        self.connection.commit()

        # Fetch its group_id
        cmd4 = f"SELECT group_id FROM groups WHERE school_id LIKE {school_id} AND group_name LIKE '{group_name}'"
        self.cursor.execute(cmd4)
        res = self.cursor.fetchall()

        group_id = res[0][0]

        # Add creator to group
        self.add_to_group(group_id, user_id, user_id)

        return group_id

    def add_to_group(self, group_id, vk_id, user_id):
        # Add vk_id to group if user_id has a permission to.

        # Check correctness of vk_id.
        if not self.user_check(vk_id):
            raise Exception(f"Пользователь @id{vk_id} не зарегистрирован в системе.")

        # Check if user already is in the group.
        cmd2 = f"SELECT * FROM groups_membership WHERE vk_id LIKE {vk_id} AND group_id LIKE {group_id}"
        self.cursor.execute(cmd2)
        res = self.cursor.fetchall()
        if res:
            raise Exception(f"Пользователь уже в составе группы.")

        # Check permission.
        if not self.fetch_user_school_role(self.fetch_group_school(group_id), user_id) <= 3:
            raise Exception(f"У вас недостаточно прав.")

        # Check group existence and fetch school_id.
        school_id = self.fetch_group_school(group_id)
        if not school_id:
            raise Exception(f"Группы с group_id {group_id} в данной школе нет.")

        # Check if both user_id and vk_id are in the same school as the group in.
        # todo: that one's sketchy
        if not self.user_in_school_check(vk_id, school_id) or not self.user_in_school_check(user_id, school_id):
            raise Exception(f"Чтобы пригласить этого человека в группу, вы должны быть в составе одной школы.")

        # Act.
        cmd3 = f"INSERT INTO groups_membership (vk_id, group_id) VALUES ({vk_id},{group_id})"
        self.cursor.execute(cmd3)
        self.connection.commit()

    def school_check(self, school_id):
        # Check whether a school exists
        check = f"SELECT school_id FROM schools WHERE school_id LIKE {school_id}"
        self.cursor.execute(check)
        res = self.cursor.fetchall()
        if not res:
            return False
        return True

    def role_check(self, role_id):
        # Check whether the role exists or not
        check = f"SELECT role_id FROM roles WHERE role_id LIKE {role_id}"
        self.cursor.execute(check)
        res = self.cursor.fetchall()
        if not res:
            return False
        return True

    def user_check(self, vk_id):
        # Return True if user is in the system. Otherwise - False.
        cmd1 = f"SELECT * FROM users WHERE vk_id LIKE {vk_id}"
        self.cursor.execute(cmd1)
        res = self.cursor.fetchall()
        if not res:
            return False
        return True

    def user_in_school_check(self, vk_id, school_id):
        # Return True if user is in the school school-id
        if self.user_check(vk_id):
            cmd2 = f"SELECT * FROM roles_membership WHERE vk_id LIKE {vk_id} AND school_id LIKE {school_id}"
            self.cursor.execute(cmd2)
            res = self.cursor.fetchall()
            if res:
                return True
        else:
            return False

    def update_role(self, school_id, vk_id, new_role_id):
        # Update role of user with vk_id with accordance to user_id permissions

        # Check whether the role exists or not
        if not self.role_check(new_role_id):
            raise Exception(f"Неверная роль (role_id:{new_role_id})")

        # Execution
        cmd = f"UPDATE roles_membership SET role_id={new_role_id} WHERE vk_id LIKE {vk_id} AND school_id LIKE {school_id}"
        self.cursor.execute(cmd)
        self.connection.commit()

    def remove_user(self, school_id, target_id, user_id):
        # TODO: REFACTOR THIS PIECE OF SHUTTLECOCK
        # Remove user from school

        # Check whether school exists
        if not self.school_check(school_id):
            return -5
        # Check whether user exists in school or not
        if not self.user_in_school_check(target_id, school_id):
            return -2
        # Check whether user exists in school or not
        if not self.user_in_school_check(user_id, school_id):
            return -2
        # Permission check
        user_role_id = self.fetch_user_school_role(school_id, user_id)
        target_role_id = self.fetch_user_school_role(school_id, target_id)
        if int(target_role_id) <= int(user_role_id):
            return -4

        cmd = f"DELETE FROM roles_membership WHERE vk_id LIKE {target_id} and school_id LIKE {school_id}"
        self.cursor.execute(cmd)
        self.connection.commit()
        return True

    def remove_from_group(self, group_id, target_id):
        # Remove user from group

        # Check whether a target is a part of a group
        cmd = f"SELECT * FROM groups_membership WHERE vk_id LIKE {target_id} AND group_id LIKE {group_id}"
        self.cursor.execute(cmd)
        res = self.cursor.fetchall()
        if not res:
            raise Exception("Пользователь не состоит в группе.")

        cmd = f"DELETE FROM groups_membership WHERE vk_id LIKE {target_id} AND group_id LIKE {group_id}"
        self.cursor.execute(cmd)
        self.connection.commit()
        return True

    # Info parse
    def fetch_school_name(self, school_id):
        # Returns school_id school's name
        cmd = f"SELECT school_name FROM schools WHERE school_id LIKE {school_id}"
        self.cursor.execute(cmd)
        res = self.cursor.fetchall()
        school_name = res[0][0] if res else ''
        return school_name

    def fetch_school_members(self, school_id):
        # Returns list of vk_ids of people of the school_id school
        cmd = f"SELECT vk_id FROM roles_membership WHERE school_id LIKE {school_id}"
        self.cursor.execute(cmd)
        res = self.cursor.fetchall()
        return [x[0] for x in res]

    def fetch_user_school_groups(self, school_id, vk_id):
        # Returns list of group_ids of groups of school_id vk_id is in.
        # 1.) fetch schools group_ids
        cmd1 = f"SELECT group_id FROM groups WHERE school_id LIKE {school_id}"
        self.cursor.execute(cmd1)
        school_groups_ids = [x[0] for x in self.cursor.fetchall()]

        # 2.) fetch groups the person are in
        cmd2 = f"SELECT group_id FROM groups_membership WHERE vk_id LIKE {vk_id}"
        self.cursor.execute(cmd2)
        vk_id_groups_ids = [x[0] for x in self.cursor.fetchall()]

        # 3.) Compare and add
        res = []
        for group in vk_id_groups_ids:
            if group in school_groups_ids:
                res.append(group)

        return res

    def fetch_user_school_role(self, school_id, vk_id):
        # Return users role_id in the school

        # Check if school exists.
        if not self.fetch_school_name(school_id):
            raise Exception(f"Школы с school_id {school_id} не существует.")

        cmd1 = f"SELECT role_id FROM roles_membership WHERE vk_id LIKE {vk_id} AND school_id LIKE {school_id}"
        self.cursor.execute(cmd1)
        res = self.cursor.fetchall()
        if res:
            role_id = res[0][0]
            return role_id
        else:
            return False

    def fetch_user_name(self, vk_id):
        # Return username of vk_id
        cmd1 = f"SELECT nickname FROM users WHERE vk_id LIKE {vk_id}"
        self.cursor.execute(cmd1)
        res = self.cursor.fetchall()
        nickname = res[0][0]
        return nickname

    def fetch_group_name(self, group_id):
        # Return group_name of the group_id
        cmd1 = f"SELECT group_name FROM groups WHERE group_id LIKE {group_id}"
        self.cursor.execute(cmd1)
        res = self.cursor.fetchall()
        if res:
            return res[0][0]
        else:
            return False

    def fetch_school_groups(self, school_id):
        # Returns school groups ids of school_id school
        cmd1 = f"SELECT * FROM groups WHERE school_id LIKE {school_id}"
        self.cursor.execute(cmd1)
        res = self.cursor.fetchall()
        school_groups = res
        return school_groups

    def fetch_role_name(self, role_id):
        # Returns role name
        cmd1 = f"SELECT role_name FROM roles WHERE role_id LIKE {role_id}"
        self.cursor.execute(cmd1)
        res = self.cursor.fetchall()
        if res:
            return res[0][0]
        else:
            return False

    def group_check(self, group_id):
        # Check groups for existence
        cmd = f"SELECT group_id FROM groups WHERE group_id LIKE {group_id}"
        self.cursor.execute(cmd)
        res = self.cursor.fetchall()
        if res:
            return True
        else:
            return False

    def fetch_user_schools(self, user_id, level=5):
        # Good method.
        # Returns array of schools user is in.
        if not self.user_check(user_id):
            raise Exception(f"Пользователь @id{user_id} не зарегистрирован в системе.")
        cmd = f"SELECT * FROM roles_membership WHERE vk_id LIKE {user_id}"
        self.cursor.execute(cmd)
        school_ids = [x[2] for x in self.cursor.fetchall()]
        schools = []
        for school_id in school_ids:
            cmd = f"SELECT * FROM schools WHERE school_id LIKE {school_id}"
            self.cursor.execute(cmd)
            res = self.cursor.fetchall()
            schools.append(res[0])
        # RETURN: [(SCHOOL_ID, CREATOR_ID, SCHOOL_NAME,)]

        schools_filtered = []
        for school in schools:
            role_id = self.fetch_user_school_role(school[0], user_id)
            if role_id <= level:
                schools_filtered.append(school)

        if schools_filtered:
            return schools_filtered
        else:
            return False

    def fetch_user_groups(self, user_id, level=5):
        # Returns list of tuples *with 3 columns* of groups info.
        cmd = f"SELECT group_id FROM groups_membership WHERE vk_id LIKE {user_id}"
        self.cursor.execute(cmd)
        group_ids = [x[0] for x in self.cursor.fetchall()]

        groups = []
        for group_id in group_ids:
            cmd = f"SELECT * FROM groups WHERE group_id LIKE {group_id}"
            self.cursor.execute(cmd)
            groups.append(self.cursor.fetchall()[0])

        # Filter by role
        groups_filtered = []
        for group in groups:
            if int(self.fetch_user_school_role(group[1], user_id)) <= level:
                groups_filtered.append(group)

        if groups_filtered:
            return groups_filtered
        else:
            return False

    def fetch_group_members(self, group_id):
        # Returns list of group members
        cmd = f"SELECT vk_id FROM groups_membership WHERE group_id LIKE {group_id}"
        self.cursor.execute(cmd)
        members = [x[0] for x in self.cursor.fetchall()]
        members = [(x, self.fetch_user_name(x)) for x in members]
        return members  # [vk_id][nickname]

    def avail_group_msg_group_ids(self, user_id):
        # Title says it all (available)
        # 1.) Get schools ids where user < 3 (teacher or more)
        # 2.) Get groups ids of school groups
        cmd = f"SELECT school_id, role_id FROM roles_membership WHERE vk_id LIKE {user_id}"
        self.cursor.execute(cmd)
        school_ids = self.cursor.fetchall()
        filtered_ids = []
        for id, role in school_ids:
            if role <= 3:
                filtered_ids.append(id)

        # Fetch group_ids by school_ids
        result_ids = []
        for school_id in filtered_ids:
            result_ids = result_ids + [x[0] for x in self.fetch_school_groups(school_id)]

        return result_ids

    # TODO: обернуть в декоратор методы и добавить try: except e: return e для любых случайных ошибок.

    def remove_user_from_group(self, group_id, target_id):
        # Remove user from group in groups_membership.
        cmd = f"DELETE FROM groups_membership WHERE group_id LIKE {group_id} AND vk_id LIKE {target_id}"
        self.cursor.execute(cmd)
        self.connection.commit()
        return True

    def remove_user_from_school(self, school_id, target_id):
        # Remove user from school in roles_membership.

        # 1.) Fetch school groups
        school_groups_ids = [x[0] for x in self.fetch_school_groups(school_id)]
        # 2.) Remove from school groups
        for group_id in school_groups_ids:
            self.remove_user_from_group(group_id, target_id)
        # 3.) Remove  from school
        cmd = f"DELETE FROM roles_membership WHERE school_id LIKE {school_id} AND vk_id LIKE {target_id}"
        self.cursor.execute(cmd)
        self.connection.commit()

    def delete_group(self, group_id):
        # Delete group.
        # 1.) Remove all its participants from groups_membership.
        # 2.) Remove the group itself in groups.
        group_members_ids = self.fetch_group_members(group_id)
        for member_id in group_members_ids:
            self.remove_user_from_group(group_id, member_id)
        cmd = f"DELETE FROM groups WHERE group_id LIKE {group_id}"
        self.cursor.execute(cmd)
        self.connection.commit()
        return True

    def delete_school(self, school_id):
        # Delete school.
        # 1.) Remove all its participants from roles_membership.
        # 2.) Remove all school groups from groups.
        # 3.) Remove the school itself in schools.
        school_members_ids = self.fetch_school_members(school_id)
        for member_id in school_members_ids:
            self.remove_user_from_school(school_id, member_id)
        school_groups_ids = [x[0] for x in self.fetch_school_groups(school_id)]
        for group_id in school_groups_ids:
            self.delete_group(group_id)
        cmd = f"DELETE FROM schools WHERE school_id LIKE {school_id}"
        self.cursor.execute(cmd)
        self.connection.commit()
        return True

    def fetch_group_school(self, group_id):
        # Returns id of a school to which group_id group belongs
        cmd = f"SELECT school_id FROM groups where group_id LIKE {group_id}"
        self.cursor.execute(cmd)
        res = self.cursor.fetchall()
        if res:
            return res[0][0]
        else:
            raise Exception(f"Группы с group_id ({group_id}) не существует.")

    def fetch_roles(self, level=5):
        # Returns list with roles entries
        cmd = f"SELECT * FROM roles"
        self.cursor.execute(cmd)
        roles = self.cursor.fetchall()

        # Filter
        roles_filtered = []
        for role in roles:
            # role_id permissions role_name
            role_id, permissions, role_name = role
            if int(role_id) > int(level):
                roles_filtered.append(role)
        if roles_filtered:
            return roles_filtered
        else:
            return []
