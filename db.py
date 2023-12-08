import oracledb

# Establish a connection to Oracle database
connection = oracledb.connect(
    user="BULLFLIX_WEB",
    password="usf1956!",
    dsn="reade.forest.usf.edu:1521/cdb9"
)
