import sqlite3 as db_engine

# Connection with db
conn = db_engine.connect('Chinook_Sqlite.sqlite')

# object for making requests and getting their results
cursor = conn.cursor()

# To fill

# # Request in SQL
# cursor.execute("SELECT Name FROM Artist ORDER BY Name LIMIT 3")
#
# # Get results
# results = cursor.fetchall()
#
# results2 = cursor.fetchall()
#
# print(results)
# print(results2)

# # Execution of several requests at once
# cursor.executescript("""
#  insert into Artist values (Null, 'A Aagrh!');
#  insert into Artist values (Null, 'A Aagrh-2!');
# """)
#
# # USING VARIABLES !!! IMPORTANT
# # C подставновкой по порядку на места знаков вопросов:
# cursor.execute("SELECT Name FROM Artist ORDER BY Name LIMIT ?", ('2'))
#
# # И с использованием именнованных замен:
# cursor.execute("SELECT Name from Artist ORDER BY Name LIMIT :limit", {"limit": 3})
# For more info see https://www.python.org/dev/peps/pep-0249/#paramstyle


# Insert in SQL
cursor.execute("insert into Artist values (Null, 'A Aagrh!') ")

# If we not only read, but change the db, we should commit the changes
conn.commit()

# Check the result by reading
cursor.execute("""
            SELECT Name 
            FROM Artist 
            ORDER BY Name 
            LIMIT 3
        """)  # For readability
# results = cursor.fetchone()
# results = cursor.fetchmany(2)
results = cursor.fetchall()
print(results)

# Using cursor as iterator
# # Использование курсора как итератора
# for row in cursor.execute('SELECT Name from Artist ORDER BY Name LIMIT 3'):
#         print(row)
# # ('A Cor Do Som',)
# # ('Aaron Copland & London Symphony Orchestra',)
# # ('Aaron Goldberg',)

#

# Don't forget to close the connection
conn.close()
