import oracledb

connection = oracledb.connect(
    user="VGUDA",
    password="bf1234",
    dsn="reade.forest.usf.edu:1521/cdb9"
)
print("Successfully connected to Oracle Database")

cursor = connection.cursor()
cursor.execute("SELECT * FROM BULLFLIX.USERS WHERE ROWNUM = 1")
users = cursor.fetchall()
print(users)
cursor.close()
connection.close()