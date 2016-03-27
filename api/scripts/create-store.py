#!/usr/bin/python3

# this script will create a new store
import psycopg2
from pbkdf2 import crypt

db_name = os.environ("DB_NAME")
db_user = os.environ("DB_USER")
db_password = os.environ("DB_PASSWORD")
db = psycopg2.connect('dbname=' + db_name + ' user=' + db_user + ' password=' + db_password)
cursor = db.cursor()

name = input("Name of store: ")
passwd = input("Store passwd: ")
pin = input("Store PIN: ")
stopcode = input("Stopcode: ")
print("Setting up store... fields not asked for will be set to defaults")

hashed = crypt(passwd)
hl = [0,0,0]
bg = [255,255,255]
cursor.execute("INSERT INTO stores(acc_id,name,password,waittime,pin,logo,promo,color,highlight,primchan,template,stopcode) VALUES (nextval('counter_stores'),%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(name,hashed,4,int(pin),"d.png","Default promo text",hl,bg,-1,'quiznos',stopcode)) # TODO - default template, d.png
cursor.execute("SELECT acc_id FROM stores WHERE pin = %s",(pin,))
acc_id = cursor.fetchone()[0]
cursor.execute("INSERT INTO groups(name,owner) VALUES (%s,%s)",(name,acc_id))
cursor.execute("SELECT group_id FROM groups WHERE owner = %s",(acc_id,))
primchan_id = cursor.fetchone()[0]
cursor.execute("UPDATE stores SET primchan = %s WHERE acc_id = %s",(primchan_id,acc_id))
db.commit()

print("Success")
db.close()
