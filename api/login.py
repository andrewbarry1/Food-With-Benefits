#!/usr/bin/python3

import psycopg2
from base64 import b64decode, b64encode
from pbkdf2 import crypt
from random import SystemRandom

# creates and inserts a new account
def createUser(request,cursor):
        fullname = request['fullname']
        username = request['username']
        if (fullname == "" or username == ""): return 401
        ctype = int(request['ctype'])
        type = int(request['type'])
        if (ctype == 0 or ctype == 1):
                passwd = request['password']
        else:
                ra = SystemRandom()
                passwd = str(ra.uniform(0,1000))
        if (type == 1): # pn
                if not(len(username) == 10 or (len(username) == 11 and username[0] == '1')):
                        return 401
                cursor.execute("SELECT phonenumber FROM endusers WHERE phonenumber = %s",(int(username),))
        elif (type == 2): # email
                if not('@' in username):
                        return 401
                cursor.execute("SELECT email FROM endusers WHERE email = %s",(username,))
        else:
                return 401

        res = cursor.fetchone()
        if (res is None):
                pn = None
                email = None
                msgval = 1
                if (type == 1):
                        pn = username
                        msgval *= 2
                elif (type == 2):
                        email = username
                        msgval *= 3
                if (ctype == 0 or ctype == 1):
                        msgval *= 5
                
                hashed = crypt(passwd)
                empty = []
                cursor.execute("INSERT INTO endusers VALUES (nextval('counter_users'),%s,%s,%s,%s,%s,%s) RETURNING acc_id",(pn,None,msgval,email,hashed,fullname))
                acc_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO points VALUES (%s,%s,%s)",(acc_id,empty,empty))
                cursor.execute("INSERT INTO subscriptions VALUES (%s,%s,%s)",(acc_id,empty,empty))
                return 200
        else:
                return 400
        

# login process
def validate(request,cursor):
        uname = request['username']
        password = request['password']
        clientType = request['ctype']
        actual = None
        if (clientType == 2):
                cursor.execute("SELECT password FROM stores WHERE pin = %s",(uname,))
                actual = cursor.fetchone()
        elif (clientType == 1 or clientType == 0):
                cursor.execute("SELECT password FROM endusers WHERE phonenumber = %s OR email = %s",(uname,uname))
                actual = cursor.fetchone()
        else:
                return (False,None,None)
        check = ""
        if not(actual == None):
                actual = actual[0]
                check = crypt(password,actual)
        else:
                return (False,None,None)
        if (check == actual):
                if (clientType == 1 or clientType == 0):
                        ip = None
                        cursor.execute("SELECT acc_id FROM endusers WHERE phonenumber = %s",(uname,))
                        acc_id = cursor.fetchone()[0]
                else:
                        cursor.execute("SELECT acc_id,ip FROM stores WHERE pin = %s",(uname,))
                        ret = cursor.fetchone()
                        acc_id = ret[0]
                        ip = ret[1]
                server = None
                if not(ip is None):
                        server = {}
                        server['IP'] = ip
                return (True,acc_id,server)
        else:
                return (False,None,None)
