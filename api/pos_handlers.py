#!/usr/bin/python3

import psycopg2, logging, time
from general import createCoupon, sendMsg, subscribe_to_channel
from random import SystemRandom

# Functions to run for pos system requests
# remember to return (code,{json})

def addpoints(request,cursor,acc_id):

    # resovle acc_id
    credential_types = ["app","phonenumber","email"]
    target_credential = request["target"]
    credential_type = int(request["type"])
    target_id = None
    if (credential_types[credential_type] == 'app'):
        target_id = target_credential
    elif (credential_types[credential_type] == 'phonenumber'):
        cursor.execute("SELECT acc_id FROM endusers WHERE phonenumber = %s",(target_credential,))
        target_id = cursor.fetchone()
    elif (credential_types[credential_type] == 'email'):
        cursor.execute("SELECT acc_id FROM endusers WHERE email = %s",(target_credential,))
        target_id = cursor.fetchone()
    if (target_id is None): return (401,{}) # invalid credentials
    target_id = target_id[0]

    # check wait time
    now = int(time.time())
    cursor.execute("SELECT waittime FROM stores WHERE acc_id = %s",(acc_id,))
    wait_hours = cursor.fetchone()[0]
    cursor.execute("SELECT time FROM transactions WHERE acc_id = %s ORDER BY time ASC",(target_id,))
    stamps = cursor.fetchall()
    if (stamps is None or len(stamps) == 0):
        last_visit = 0
    else:
        last_visit = stamps[0][0]
    now = int(time.time())
    wait_until = last_visit + (3600*wait_hours)
    if (now < wait_until):
        return (403,{})

    # determine points to give
    dpp_translated = 1
    cursor.execute("SELECT dpp FROM stores WHERE acc_id = %s",(acc_id,))
    dpp = cursor.fetchone()[0]
    if not(dpp is None):
        dollar_amnt = request['dollars']
        dpp_translated = int(dollar_amnt * dpp)

    # give point
    cursor.execute("SELECT stores, counts FROM points WHERE acc_id = %s",(target_id,))
    point_info = cursor.fetchone()
    target_stores = point_info[0]
    target_counts = point_info[1]
    new = not(acc_id in target_stores)
    notes = ""
    cursor.execute("SELECT primchan FROM stores WHERE acc_id = %s",(acc_id,))
    primchan_id = cursor.fetchone()[0]
    if (new): # never visited this store before
        subscribe_to_channel(cursor,target_id,primchan_id)
        cursor.execute("SELECT counts, stores FROM points WHERE acc_id = %s",(target_id,))
        point_info = cursor.fetchone()
        counts_list = point_info[0]
        stores_list = point_info[1]
        counts_list.append(dpp_translated)
        stores_list.append(acc_id)
        cursor.execute("UPDATE points SET counts = %s WHERE acc_id = %s",(counts_list,target_id))
        cursor.execute("UPDATE points SET stores = %s WHERE acc_id = %s",(stores_list,target_id))
        count = dpp_translated
    else:
        index = target_stores.index(acc_id)
        count = target_counts[index]
        count += dpp_translated
        target_counts[index] = count
        cursor.execute("UPDATE points SET counts = %s WHERE acc_id = %s",(target_counts,target_id))

    # insert this addpoints into a transaction history
    cursor.execute("INSERT INTO transactions VALUES (%s,%s,%s,%s)",(now,target_id,acc_id,notes))
    cursor.execute("SELECT fullname FROM endusers WHERE acc_id = %s",(target_id,))
    fullname = cursor.fetchone()[0]

    # send user a check-in message, if they are subscribed
    cursor.execute("SELECT groups FROM subscriptions WHERE acc_id = %s",(target_id,))
    subbed_groups = cursor.fetchone()[0]
    will_send = False
    for group in subbed_groups:
        cursor.execute("SELECT owner FROM groups WHERE group_id = %s",(group,))
        owner = cursor.fetchone()[0]
        if owner == acc_id:
            will_send = True
            break
    if will_send:
        cursor.execute("SELECT name,template FROM stores WHERE acc_id = %s",(acc_id,))
        msg_info = cursor.fetchone()
        store_name = msg_info[0]
        t = msg_info[1]
        sendMsg(cursor,target_id,acc_id,"Thank you for checking in","Thank you for checking in at " + store_name + ".","You now have " + str(count) + " points at this store.",t)
    
    # return offers you can claim
    cursor.execute("SELECT groups FROM subscriptions WHERE acc_id = %s",(target_id,))
    glist = cursor.fetchone()[0]
    yg = []
    for g in glist:
        cursor.execute("SELECT owner FROM groups WHERE group_id = %s",(g,))
        owner = cursor.fetchone()[0]
        if (owner == acc_id): yg.append(g)
    offers = []
    for sub in yg:
        cursor.execute("SELECT name,description,points,offer_id FROM offers WHERE group_owner = %s",(sub,))
        os = cursor.fetchall()
        for o in os:
            offer = {}
            offer['name'] = o[0]
            offer['desc'] = o[1]
            offer['points'] = o[2]
            offer['id'] = o[3]
            offers.append(offer)
    ret = {}
    ret["name"] = fullname
    ret["offers"] = offers
    ret["points"] = count
    ret["id"] = target_id
    return (200,ret)



# usecode
def usecode(request,cursor,acc_id):
    pin = int(request["id"])
    cursor.execute("SELECT pin FROM stores WHERE acc_id = %s",(acc_id,))
    check = cursor.fetchone()[0]
    if not(pin == check):
        return (401,{}) # incorrect pin

    code = int(request['code'])
    cursor.execute("SELECT acc_id,store_id,offer_id,exp FROM coupons WHERE code = %s AND store_id = %s",(code,acc_id))
    results = cursor.fetchone()
    if (results is None):
        return (404,{}) # code doesn't exist
    code_owner = results[0]
    code_store = results[1]
    offer_id = results[2]
    exp = results[3]
    if not(code_store == acc_id):
        return (403,{}) # not the right store
    if (int(time.time()) > exp):
        cursor.execute("DELETE FROM coupons WHERE code = %s",(code,))
        return (410,{}) # code is expired
    cursor.execute("SELECT name FROM offers WHERE offer_id = %s",(offer_id,))
    code_name = cursor.fetchone()[0]
    ret = {}
    ret['offer'] = code_name
    cursor.execute("DELETE FROM coupons WHERE code = %s",(code,))
    cursor.execute("INSERT INTO redemptions(acc_id,store,name) VALUES (%s,%s,%s)",(code_owner,code_store,code_name))
    return (200,ret)
    

# getbrand
def specifics(request,cursor,acc_id):
    cursor.execute("SELECT logo, promo, color, highlight, dpp FROM stores WHERE acc_id = %s",(acc_id,))
    info = cursor.fetchone()
    cursor.execute("SELECT name FROM stores WHERE acc_id = %s",(acc_id,))
    storename = cursor.fetchone()[0]
    ret = {"logo":info[0],"promo":info[1],"color":info[2],"highlight":info[3],"name":storename,"dollars":not(info[4] is None)}
    return (200,ret)

# makecode
def makecode(request,cursor,acc_id):
    coupon_id = request['id']
    target_id = request['target']

    cursor.execute("SELECT points,name FROM offers WHERE offer_id = %s",(coupon_id,))
    coupon_points = cursor.fetchone()
    if (coupon_points is None): return (404,{})
    offer_name = coupon_points[1]
    coupon_points = coupon_points[0]

    rng = SystemRandom()
    code = rng.randrange(100000,999999)
    cursor.execute("INSERT INTO coupons VALUES (%s,%s,%s,%s)",(target_id,code,acc_id,coupon_id))

    cursor.execute("SELECT stores,counts FROM points WHERE acc_id = %s",(target_id,))
    store_info = cursor.fetchone()
    target_stores = store_info[0]
    target_counts = store_info[1]
    cursor.execute("SELECT fullname, msgval FROM endusers WHERE acc_id = %s",(target_id,))
    target_info = cursor.fetchone()
    target_name = target_info[0]
    msgval = target_info[1]

    target_counts[target_stores.index(acc_id)] = target_counts[target_stores.index(acc_id)] - coupon_points
    cursor.execute("UPDATE points SET counts = %s WHERE acc_id = %s",(target_counts,target_id))
    ret = {}
    ret['points'] = target_counts[target_stores.index(acc_id)]
    ret['name'] = target_name

    cursor.execute("SELECT template FROM stores WHERE acc_id = %s",(acc_id,))
    msg_info = cursor.fetchone()
    template = msg_info[1]
    subject = "Here is your coupon."
    a_or_an = "a"
    if (offer_name[0] in 'aeiou'): a_or_an = "an"
    header = "Here's your coupon code for " + a_or_an + " " + offer_name + "."
    message = "Your code is " + str(code) + ". Use it next time you visit!"
    sendMsg(cursor,target_id,acc_id,subject,header,message,template)

    return (200,ret)
