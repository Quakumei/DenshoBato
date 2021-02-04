import sqlite3

from sqlite3 import Error

CREATE_FLAG = True
DEBUG_FLAG = True
DB_NAME = 'mydatabase.db'


def sql_connection():
    try:
        con = sqlite3.connect(DB_NAME)
        return con

    except Error:
        print(Error)


def sql_tables(con=sql_connection()):
    # cursorObj.execute("CREATE TABLE employees(id integer PRIMARY KEY, name text, salary real, department text, position text, hireDate text)")

    # USERS
    try:
        cursorObj = con.cursor()
        cursorObj.execute(
            "CREATE TABLE users(id integer PRIMARY KEY, user_id text, group_id text, role text)")
        con.commit()
    except Exception as e:
        print(e)

    # SCHOOLS
    try:
        cursorObj = con.cursor()
        cursorObj.execute(
            "CREATE TABLE schools(id integer PRIMARY KEY, group_name text, owner_id text)")
        con.commit()
    except Exception as e:
        print(e)


def fetch_roles(user_id, con=sql_connection()):
    cursorObj = con.cursor()
    cmd = "SELECT * FROM users WHERE user_id=\"" + str(user_id) + "\""
    response = cursorObj.execute(cmd).fetchall()
    if DEBUG_FLAG:
        print(cmd)
        print(response)
    return response


def next_id(table_name, con=sql_connection()):
    cursorObj = con.cursor()
    cmd = """SELECT * FROM """ + str(table_name) + """ WHERE id = (SELECT MAX(id) FROM """ + str(table_name) + """)"""

    response = cursorObj.execute(cmd).fetchall()[0][0] + 1
    if DEBUG_FLAG:
        print(cmd)
        print(response)
    return response


def create_school(school_name, owner_id, con=sql_connection()):
    try:
        cursorObj = con.cursor()
        cmd = 'INSERT into schools VALUES(' + str(next_id('schools')) + ', "' + str(school_name) + '", +"' + str(
            owner_id) + '")'
        if DEBUG_FLAG:
            print(cmd)

        cursorObj.execute(cmd)
        con.commit()
    except Exception as e:
        print(e)
        return -1
    return 0


def user_add_attribute(user_id, group_id, role, con=sql_connection()):
    try:
        cursorObj = con.cursor()
        cmd = 'INSERT into users VALUES(' + str(next_id('users')) + ', "' + str(user_id) + '", "' + str(
            group_id) + '", "' + str(role) + '")'
        if DEBUG_FLAG:
            print(cmd)
        cursorObj.execute(cmd)
        con.commit()

    except Exception as e:
        print(e)
        return -1
    return 0


def fetch_all_schools(con=sql_connection()):
    try:
        cursorObj = con.cursor()
        cmd = "SELECT * FROM schools"
        if DEBUG_FLAG:
            print(cmd)
        response = cursorObj.execute(cmd).fetchall()
        if DEBUG_FLAG:
            print(response)
        return response
    except Exception as e:
        print(e)
        return [["CALL ADMIN", "ERROR"]]


con = sql_connection()
if CREATE_FLAG:
    sql_tables(con)

if DEBUG_FLAG:
    next_id('schools', con)
    next_id('users', con)

    # sql_table(con)
    # print(fetch_roles(con, 388032588))
