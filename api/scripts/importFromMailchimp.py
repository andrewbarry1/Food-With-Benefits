#!/usr/bin/python3

# Use this to import customer information from existing Mailchimp users (and Splango with slight modification)
# Some things are inserted in strangely because we have to shoehorn what they've got into what we need

import psycopg2, csv, sys, requests, json, random
from pbkdf2 import crypt

db_name = os.environ("DB_NAME")
db_user = os.environ("DB_USER")
db_password = os.environ("DB_PASSWORD")
db = psycopg2.connect('dbname=' + db_name + ' user=' + db_user + ' password=' + db_password)
cursor = db.cursor()


filename = sys.argv[1]
file = open(filename,'r')
reader = csv.reader(file)
first = True
cursor.execute("SELECT primchan FROM stores WHERE acc_id = %s",(6,))
gid = cursor.fetchone()[0]
for row in reader:
    if first:
        first = False
        continue
    email = row[0]
    fullname = row[1] + row[2]
    cursor.execute("SELECT * FROM endusers WHERE email = %s",(email,))
    if not(cursor.fetchone() is None): continue
    cursor.execute("INSERT INTO endusers VALUES (nextval('counter_users'),%s,%s,%s,%s,%s,%s) RETURNING acc_id",(None,None,3,email,crypt("ThisIsATotallySecurePasswordNotReally"+str(random.random())),fullname))
    acc_id = cursor.fetchone()[0]
    a = [6]
    g = [gid]
    r = [0]
    cursor.execute("INSERT INTO points VALUES (%s,%s,%s)",(acc_id,a,r))
    cursor.execute("INSERT INTO subscriptions VALUES (%s,%s,%s)",(acc_id,r,g))




print("Done")
db.commit()
