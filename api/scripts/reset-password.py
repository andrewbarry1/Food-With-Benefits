#!/usr/bin/python3

# this script will reset a store/user password
import psycopg2
from pbkdf2 import crypt

db_name = os.environ("DB_NAME")
db_user = os.environ("DB_USER")
db_password = os.environ("DB_PASSWORD")
db = psycopg2.connect('dbname=' + db_name + ' user=' + db_user + ' password=' + db_password)
cursor = db.cursor()
newpassword = input("Enter new password: ")
hashed = crypt(newpassword)
type = input("Store or User? ")
if (type.lower() == 'store'):
    credential = input("Enter Store name: ")
    cursor.execute("UPDATE stores SET password = %s WHERE name = %s",(hashed,credential))
elif (type.lower() == 'user'):
    credential = input("Enter phone number: ")
    cursor.execute("UPDATE endusers SET password = %s WHERE phonenumber = %s",(hashed,credential))
db.commit()
print("Success")
db.close()
