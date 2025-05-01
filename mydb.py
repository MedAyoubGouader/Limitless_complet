import pymysql

database = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
)
#prepare a cursor object
cursorObject = database.cursor()
# create a database
cursorObject.execute("CREATE DATABASE elderco ")
print("All Done!")