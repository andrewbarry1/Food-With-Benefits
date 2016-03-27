#!/usr/bin/python

# Mail dispatch cronjob

import sendgrid, plivo, psycopg2, time, multiprocessing, time, datetime
from datetime import datetime
from general import sendMsg
from random import SystemRandom

db_name = os.environ("DB_NAME")
db_user = os.environ("DB_USER")
db_password = os.environ("DB_PASSWORD")
db = psycopg2.connect('dbname=' + db_name + ' user=' + db_user + ' password=' + db_password)

# sendMsg(cursor,target_id,store_id,subject,header,message,template,msgval = -1)
# note that template is the filename of the template which resides in api/templates
# replace channel with store_id

def do_job(job): # Send the targets some mail
    j_id = job[0]
    j_sender = job[1]
    j_subject = job[2]
    j_header = job[3]
    j_message = job[4]
    j_send_time = job[5]
    j_recur = job[6]
    j_offer_id = job[7]
    j_target_type = job[8]
    j_target_info = job[9]
    j_recur_count = job[10]
    cursor = db.cursor()

    targets = []
    if (j_target_type == 0): # all customers who have checked into the store
        cursor.execute("select acc_id FROM transactions WHERE store = %s",(j_sender,))
        targets = set([x[0] for x in cursor.fetchall()])
    elif (j_target_type == 1): # all customers who are subscribed to a group
        target_group = j_target_info
        cursor.execute("SELECT acc_id FROM subscriptions WHERE %s = ANY (groups)",(target_group,))
        targets = set([x[0] for x in cursor.fetchall()])
    elif (j_target_type == 2): # all customers who have not checked in within x days
        idle_days = int(j_target_info)
        cursor.execute("SELECT acc_id,time FROM transactions WHERE store = %s ORDER BY time DESC",(j_sender,))
        all_checkins = cursor.fetchall()
        index = 0
        maxs = {}
        for checkin in all_checkins:
            if checkin[0] not in maxs:
                #print(str(checkin[0]) + " Is being checked.")
                maxs[checkin[0]] = checkin[1]
                first_eligible_second = checkin[1] + (86400*idle_days)
                if checkin[1] < int(time.time())-(86400*idle_days): # most recent checkin was over idle_days ago from now, do antispam procedure
                    #print(str(checkin[0]) + " Is eligible.")
                    if j_recur_count == 0 or int(time.time()) < first_eligible_second + (86400*1.01*j_recur): # this is the first time, or we're less than 1 full recur away from the first time the target was eligible
                        print(str(checkin[0]) + " Is a proper target - not being spammed!")
                        targets.append(checkin[0])

    # attach a coupon if necessary
    target_codes = {}
    expstr = ""
    offer_name = ""
    if not(j_offer_id == -1):
        cursor.execute("SELECT name, expiration FROM offers WHERE offer_id = %s",(j_offer_id,))
        offer_info = cursor.fetchone()
        offer_name = offer_info[0]
        offer_expiration = offer_info[1]
        exptime = int(time.time()) + (offer_expiration*3600)
        rng = SystemRandom()
        for t in targets:
            #print("Creating coupon for acc_Id " + str(t))
            code = rng.randrange(100000,999999)
            exptime = int(time.time())+(3600*offer_expiration)
            cursor.execute("INSERT INTO coupons VALUES (%s,%s,%s,%s,%s)",(t,code,j_sender,j_offer_id,exptime))
            target_codes[t] = code
        if not(offer_expiration == -1):
            expstr = "\nOffer expires " + datetime.fromtimestamp(exptime).strftime("%m/%d/%y %I:%M")

        
    cursor.execute("SELECT template FROM stores WHERE acc_id = %s",(j_sender,))
    template = cursor.fetchone()[0]

    sent = []
    for target in targets:
        if not(target in sent):
            msg = j_message
            if not(j_offer_id == -1):
                msg += "\nUse the code '" + str(target_codes[target]) + "' for a " + offer_name + "!" + expstr
            #print("Sending message to " + str(target) + "(mailer.py)")
            sendMsg(cursor,target,j_sender,j_subject,j_header,msg,template)
            sent.append(target)
    #print("j-recur " + str(j_recur))
    if not(j_recur == -1): # reschedule job
        newsend = j_send_time + (j_recur*86400)
        #print("Newsend " + str(newsend))
        cursor.execute("UPDATE mail_jobs SET send = %s,recur_count = %s WHERE job_id = %s",(newsend,j_recur_count+1,j_id))
    else: # thank god it's over
        cursor.execute("DELETE FROM mail_jobs WHERE job_id = %s",(j_id,))
    db.commit()


cursor = db.cursor()
cursor.execute("SELECT * FROM mail_jobs WHERE send <= %s",(int(time.time()),))
jobs = cursor.fetchall()
#print(jobs)
process_list = []
for job in jobs:
    #print(job)
    p = multiprocessing.Process(target=do_job, args=(job,))
    p.start()
    process_list.append(p)
while True:
    for process in process_list:
        if process.is_alive(): break
    else: break
db.close()
