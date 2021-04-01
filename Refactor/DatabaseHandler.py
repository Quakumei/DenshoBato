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
                f"INSERT INTO roles (permissions, role_name) VALUES ({255},\"{'Creator'}\")",
                f"INSERT INTO roles (permissions, role_name) VALUES ({127},\"{'Admin'}\")",
                f"INSERT INTO roles (permissions, role_name) VALUES ({47},\"{'Teacher'}\")",
                f"INSERT INTO roles (permissions, role_name) VALUES ({3}, \"{'Student'}\")",
                f"INSERT INTO roles (permissions, role_name) VALUES ({1}, \"{'Reader'}\")",
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
        # Creates school, assigns creator and returns its id.
        print(f"Adding school {school_name} for {creator_vk_id}...")

        # Add school to schools table
        cmd1 = f"INSERT INTO schools (creator_vk_id, school_name) VALUES ({creator_vk_id},\"{school_name}\")"
        self.cursor.execute(cmd1)

        # Fetch new school's id
        cmd2 = f"SELECT school_id FROM schools WHERE school_name LIKE \"{school_name}\" AND creator_vk_id LIKE {creator_vk_id}"
        self.cursor.execute(cmd2)
        resp = self.cursor.fetchall()
        print(f"DB response is: '{resp}'")
        school_id = resp[-1][0]
        print(f"New school id is {school_id}")

        # Give the creator the role of creator of the school
        cmd3 = f"INSERT INTO roles_membership (vk_id, role_id, school_id) VALUES ({creator_vk_id}, {1}, {school_id})"
        try:
            self.cursor.execute(cmd3)
        except sqlite3.IntegrityError:
            # May cause problems with hyperthreading stuff
            self.connection.rollback()
            return -1

        # Commit changes to the db
        self.connection.commit()

        return school_id

    def user_nickname_update(self, vk_id, nickname):
        # Updates persons nickname if vk_id is here, creates an entry otherwise
        try:
            cmd1 = f"SELECT vk_id FROM users WHERE vk_id LIKE {vk_id}"
            self.cursor.execute(cmd1)
            results = self.cursor.fetchall()
            print(results)
            if not results:
                cmd2 = f"INSERT INTO users (vk_id, nickname) VALUES ({vk_id},'{nickname}')"
                self.cursor.execute(cmd2)
                self.connection.commit()
            else:
                cmd2 = f"UPDATE users SET nickname='{nickname}' WHERE vk_id={vk_id}"
                self.cursor.execute(cmd2)
                self.connection.commit()
            return True
        except:
            print(f"Проблемы в user_nickname_update(vk_id={vk_id}, nickname={nickname})")
            return -1

    def add_user(self, vk_id, school_id, inviter_id):
        # Add user to school (give him the role of Reader (1))

        try:
            # Check whether the invitee is registered
            cmd1 = f"SELECT * FROM users WHERE vk_id LIKE {vk_id}"
            self.cursor.execute(cmd1)
            res = self.cursor.fetchall()
            if not res:
                return -3

            # Check whether the entry is presented and return -2 in that case
            cmd2 = f"SELECT * FROM roles_membership WHERE vk_id LIKE {vk_id} AND school_id LIKE {school_id}"
            self.cursor.execute(cmd2)
            res = self.cursor.fetchall()
            if res:
                return -2

            # Check whether the inviter is atleast member of school
            # TODO: Upgrade that to role check?
            cmd3 = f"SELECT * FROM roles_membership WHERE vk_id LIKE {inviter_id} AND school_id LIKE {school_id}"
            self.cursor.execute(cmd3)
            res = self.cursor.fetchall()
            if not res:
                return -4

            # Execute, return True on success
            cmd4 = f"INSERT INTO roles_membership (vk_id, role_id, school_id) VALUES ({vk_id}, {5}, {school_id})"
            self.cursor.execute(cmd4)
            self.connection.commit()
            return True
        except:
            return -1

    def create_group(self, group_name, school_id, user_id):
        # Create the group and return its group_id
        # GROUPS WITH SAME SCHOOL_ID AND GROUP_NAME ARE PROHIBITED

        # Check whether the inviter is atleast member of school
        # TODO: Upgrade that to role check?
        cmd1 = f"SELECT * FROM roles_membership WHERE vk_id LIKE {user_id} AND school_id LIKE {school_id}"
        self.cursor.execute(cmd1)
        res = self.cursor.fetchall()
        if not res:
            return -4

        # Check whether there is already group with that name
        cmd2 = f"SELECT * FROM groups WHERE school_id LIKE {school_id} AND group_name LIKE '{group_name}'"
        self.cursor.execute(cmd2)
        res = self.cursor.fetchall()
        if res:
            return -5

        # Create group
        cmd3 = f"INSERT INTO groups (school_id, group_name) VALUES ({school_id}, '{group_name}')"
        self.cursor.execute(cmd3)
        self.connection.commit()

        # Fetch its group_id
        cmd4 = f"SELECT group_id FROM groups WHERE school_id LIKE {school_id} AND group_name LIKE '{group_name}'"
        self.cursor.execute(cmd4)
        res = self.cursor.fetchall()
        group_id = res[0][0]
        return group_id

    def add_to_group(self, group_id, vk_id, user_id):
        # Adds vk_id to group_id if user_id has a permission to.

        # Check whether the inviter is atleast member of school
        # TODO: Upgrade that to role check?
        try:
            # Is person even there?
            cmd1 = f"SELECT * FROM users WHERE vk_id LIKE {vk_id}"
            self.cursor.execute(cmd1)
            res = self.cursor.fetchall()
            if not res:
                return -3

            # Is group even there? + fetch school_id
            cmd1 = f"SELECT * FROM groups WHERE group_id LIKE {group_id}"
            self.cursor.execute(cmd1)
            res = self.cursor.fetchall()
            if not res:
                return -4
            group_school_id = res[0][1]

            # Is group even in the same school as user_id is?
            cmd1 = f"SELECT * FROM roles_membership WHERE vk_id LIKE {user_id} AND school_id LIKE {group_school_id}"
            self.cursor.execute(cmd1)
            res = self.cursor.fetchall()
            if not res:
                return -4

            # Maybe vk_id is already there?
            cmd2 = f"SELECT * FROM groups_membership WHERE vk_id LIKE {vk_id} AND group_id LIKE {group_id}"
            self.cursor.execute(cmd2)
            res = self.cursor.fetchall()
            if res:
                return -5

            # Add if everything above is false.
            cmd3 = f"INSERT INTO groups_membership (vk_id, group_id) VALUES ({vk_id},{group_id})"
            self.cursor.execute(cmd3)
            self.connection.commit()
            return True
        except:
            return -1

    def update_role(self, school_id, vk_id, new_role_id, user_id):
        # Update role of user with vk_id with accordance to user_id permissions
        # Check whether school exists
        check = f"SELECT school_id FROM schools WHERE school_id LIKE {school_id}"
        self.cursor.execute(check)
        res = self.cursor.fetchall()
        if not res:
            return -5

        # Permission check
        user_role_id = self.fetch_user_school_role(school_id, user_id)
        if int(new_role_id) <= int(user_role_id):
            return -4

        # Check whether the role exists or not
        check = f"SELECT role_id FROM roles WHERE role_id LIKE {new_role_id}"
        self.cursor.execute(check)
        res = self.cursor.fetchall()
        if not res:
            return -3

        # Check whether user exists in school or not
        check = f"SELECT role_id FROM roles_membership WHERE school_id LIKE {school_id} AND vk_id LIKE {vk_id}"
        self.cursor.execute(check)
        res = self.cursor.fetchall()
        if not res:
            return -2

        # Execution
        cmd = f"UPDATE roles_membership SET role_id={new_role_id} WHERE vk_id LIKE {vk_id} AND school_id LIKE {school_id}"
        self.cursor.execute(cmd)
        self.connection.commit()
        return True

    # Info parse
    def fetch_school_name(self, school_id):
        # Returns school_id school's name
        cmd = f"SELECT school_name FROM schools WHERE school_id LIKE {school_id}"
        self.cursor.execute(cmd)
        res = self.cursor.fetchall()
        school_name = res[0][0]
        return school_name

    def fetch_school_members_vk_ids(self, school_id):
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
        cmd1 = f"SELECT role_id FROM roles_membership WHERE vk_id LIKE {vk_id} AND school_id LIKE {school_id}"
        self.cursor.execute(cmd1)
        res = self.cursor.fetchall()
        role_id = res[0][0]
        return role_id

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
        group_name = res[0][0]
        return group_name

    def fetch_school_groups_ids(self, school_id):
        # Returns school groups ids of school_id school
        cmd1 = f"SELECT group_id FROM groups WHERE school_id LIKE {school_id}"
        self.cursor.execute(cmd1)
        school_groups_ids = [x[0] for x in self.cursor.fetchall()]
        return school_groups_ids

    def fetch_role_name(self, role_id):
        # Returns role name
        cmd1 = f"SELECT role_name FROM roles WHERE role_id LIKE {role_id}"
        self.cursor.execute(cmd1)
        res = self.cursor.fetchall()
        role_name = res[0][0]
        return role_name
