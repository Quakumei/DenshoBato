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
        cmd1 = f"INSERT INTO schools (creator_vk_id, school_name) VALUES ({creator_vk_id},{school_name})"
        self.cursor.execute(cmd1)

        # Fetch new school's id
        cmd2 = f"SELECT school_id FROM schools WHERE school_name LIKE {school_name} AND creator_vk_id LIKE {creator_vk_id}"
        self.cursor.execute(cmd2)
        resp = self.cursor.fetchall()
        print(f"DB response is: '{resp}'")
        school_id = resp[-1]
        print(f"New school id is [{school_id}]")

        # Give the creator the role of creator of the school
        cmd3 = f"INSERT INTO roles_membership (vk_id,role_id,school_id) VALUES ({creator_vk_id},{1},{school_id})"  # TODO: ROLE HERE
        self.cursor.execute(cmd3)

        return school_id

    def fetch_members(self, school_name):
        # Returns list of vk_id of people of the school_name school
        res = []
        return res
