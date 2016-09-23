#!/usr/bin/python3
import psycopg2, sendgrid, plivo, random
import sendgrid
import plivo
import random

# General functions used sometimes


# generate a coupon code, insert into db
def createCoupon(cursor,acc_id,store_id,offername,offerpoints,expires):
    rng = random.SystemRandom()
    code = rng.randint(100000,999999)
    cursor.execute("INSERT INTO coupons VALUES (%s,%s,%s,%s,%s,%s)",(acc_id,store_id,code,offername,offerpoints,expires))
    return code

# General-purpose text message sending function
def sendMsg(cursor,acc_id,store_id,subject,header,message,template,msgval = -1):
    cursor.execute("SELECT name FROM stores WHERE acc_id = %s",(store_id,))
    store_name = cursor.fetchone()[0]
    cursor.execute("SELECT stopcode FROM stores WHERE acc_id = %s",(store_id,))
    stopcode = "STOP" + cursor.fetchone()[0]
    if msgval == -1:
        cursor.execute("SELECT msgval FROM endusers WHERE acc_id = %s",(acc_id,))
        msgval = cursor.fetchone()[0]
    # cleaning bool logic
    push = msgval % 2 == 0
    email = msgval % 3 == 0
    text = msgval % 5 == 0

    if (push): # parse code (TODO)
        pass
    if (email): # sendgrid code
        sendgrid_username = os.environ("SENDGRID_USERNAME")
        sendgrid_password = os.environ("SENDGRID_PASSWORD")
        cursor.execute("SELECT email FROM endusers WHERE acc_id = %s",(acc_id,))
        target = cursor.fetchone()[0]
        sg = sendgrid.SendGridClient(sendgrid_username,sendgrid_password)
        mail = sendgrid.Mail()
        mail.set_subject(subject)
        mail.set_from("offers@fwbapp.com")
        mail.add_to(target)
        unsub_link = "http://www.fwbapp.com/unsub?t=" + str(target) + "&g=" + str(store_id)
        html = ""
        template_location = "templates/" + template
        template_file = open(template_location,'r')
        template_lines = template_file.readlines()
        template_file.close()
        message.replace("\n","<br>")
        for line in template_lines:
            html += line.replace("msgheader",header).replace("msgcontent",message).replace("unsuburl",unsub_link).replace("storename",store_name)
        mail.set_html(html)
        sg.send(mail)
    if (text): # plivo code
        cursor.execute("SELECT phonenumber FROM endusers WHERE acc_id = %s",(acc_id,))
        target = cursor.fetchone()[0]
        plivo_username = os.environ("PLIVO_USERNAME")
        plivo_key = os.environ("PLIVO_KEY")
        plivo_number = os.environ("PLIVO_NUMBER")
        p = plivo.RestAPI(plivo_username, plivo_key)
        params = {'src':plivo_number,'dst':("1" + str(target)),'text':(header + " @ " + store_name + ".\n" + message + "\n Reply " + stopcode + " to stop receiving offers."),'type':'sms'}
        p.send_message(params)

def subscribe_to_channel(cursor, acc_id, gid):
    cursor.execute("SELECT nextval('unsub_codes')")
    unsub_code = cursor.fetchone()[0]
    cursor.execute("SELECT groups, unsubs FROM subscriptions WHERE acc_id = %s", (acc_id,))
    fetch_data = cursor.fetchone()
    groups = fetch_data[0]
    unsubs = fetch_data[1]
    cursor.execute("SELECT name FROM groups WHERE group_id = %s", (gid,))
    channel_name = cursor.fetchone()
    if (channel_name is None): return # group does not exist
    channel_name = channel_name[0]
    groups.append(gid)
    unsubs.append(unsub_code)
    cursor.execute("UPDATE subscriptions SET groups = %s WHERE acc_id = %s", (groups, acc_id))
    cursor.execute("UPDATE subscriptions SET unsubs = %s WHERE acc_id = %s", (unsubs, acc_id))
    cursor.execute("SELECT msgval FROM endusers WHERE acc_id = %s",(acc_id,))
    msgval = cursor.fetchone()[0]
#    if (msgval % 2 == 0):
#        sendMsg(cursor,acc_id,channel_name,"","Thanks for subscribing","You will receive text message offers through " + channel_name + ". Reply \'" + str(unsub_code) + "\' at any time to stop receiving these messages.","",2)
