#!/usr/bin/python3

# incoming sms

import psycopg2, cgi, plivo, cgitb, sys
#cgitb.enable()
plivo_username = os.environ("PLIVO_USERNAME")
plivo_key = os.environ("PLIVO_KEY")
plivo_number = os.environ("PLIVO_NUMBER")
p = plivo.RestAPI(plivo_username, plivo_key)
db_name = os.environ("DB_NAME")
db_user = os.environ("DB_USER")
db_password = os.environ("DB_PASSWORD")
db = psycopg2.connect('dbname=' + db_name + ' user=' + db_user + ' password=' + db_password)
cursor = db.cursor()
form = cgi.FieldStorage()
if not("STOP" in form.getvalue("Text")): sys.exit(0)
text = form.getvalue('Text').replace("STOP","")
phone_number = form.getvalue('From')[1:]
phone_number = int(phone_number)
cursor.execute("SELECT acc_id FROM endusers WHERE phonenumber = %s",(phone_number,))
fetch_result = cursor.fetchone()
if not(fetch_result is None):
    acc_id = fetch_result[0]
    cursor.execute("SELECT acc_id,name,ip FROM stores WHERE stopcode = %s",(text,))
    store_info = cursor.fetchone()
    if not(store_info is None):
        store_id = store_info[0]
        store_name = store_info[1]
        store_ip = store_info[2]
        if not(store_ip is None):
            url_target = store_ip + "/api/sms"
            payload = {"Text":form.getValue("Text"),"From":form.getValue("From")}
            requests.post(url_target,params=payload)
            sys.exit(0)
        cursor.execute("SELECT group_id FROM groups WHERE owner = %s",(store_id,))
        store_groups = [x[0] for x in cursor.fetchall()]
        cursor.execute("SELECT groups,unsubs FROM subscriptions WHERE acc_id = %s",(acc_id,))
        group_list = cursor.fetchone()
        sub_list = group_list[1]
        group_list = group_list[0]
        for x in store_groups:
            if x in group_list: 
                index = group_list.index(x)
                group_list.remove(x)
                sub_list.pop(index)
        cursor.execute("UPDATE subscriptions SET groups = %s WHERE acc_id = %s",(group_list,acc_id))
        cursor.execute("UPDATE subscriptions SET unsubs = %s WHERE acc_id = %s",(sub_list,acc_id))
        db.commit()
        params = {'src':plivo_number,'dst':("1" + str(phone_number)),'text':"You will no longer receive offers from " + store_name + ".",'type':'sms'}
        p.send_message(params)
    
cursor.close()
db.close()
