import mysql.connector


mydb = mysql.connector.connect(
  host = "localhost",
  user = "root",
  password = "tarun@123"
)

print(dir(mydb))
print(mydb.server_info)
