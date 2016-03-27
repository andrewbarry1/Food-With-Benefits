#!/usr/bin/python3
import psycopg2, logging, time
from general import createCoupon, sendMsg, subscribe_to_channel


# getoffers
def getoffers(request,cursor,ac_id):
    channel = request["group"]
    cursor.execute("SELECT group_id FROM groups WHERE name = %s",(channel,))
    gid = cursor.fetchone()
    if (gid is None): return (404,None)
    cursor.execute("SELECT name,description,expiration FROM offers WHERE group_owner = %s",(gid,))
    offer_data = cursor.fetchall()
    ret = {"offers":[]}
    for offer_row in offer_data:
        ret["offers"].append([offer_row[0],offer_row[1],offer_row[2]])
    return (200,ret)
    
# getmygroups
def getchannels(request,cursor,acc_id):
    cursor.execute("SELECT groups FROM subscriptions WHERE acc_id = %s", (acc_id,))
    channels = cursor.fetchone()[0]
    ret = {"groups":[]}
    for channel in channels:
        cursor.execute("SELECT name,owner FROM groups WHERE group_id = %s",(channel,))
        group_info = cursor.fetchone()
        group_name = group_info[0]
        group_owner = group_info[1]
        cursor.execute("SELECT name FROM stores WHERE acc_id = %s",(group_owner,))
        owner_name = cursor.fetchone()[0]
        group_info = (group_name,owner_name)
        ret["groups"].append(group_info)
    return (200,ret)

# getpoints
def getpoints(request,cursor,acc_id):
    store_name = request["store"]
    cursor.execute("SELECT acc_id FROM stores WHERE name = %s",(store_name,))
    store_id = cursor.fetchone()[0]
    cursor.execute("SELECT stores, counts FROM points WHERE acc_id = %s", (acc_id,))
    fetch_data = cursor.fetchone()
    stores = fetch_data[0]
    counts = fetch_data[1]
    ret = {}
    if store_id in stores:
        store_index = stores.index(store_id)
        count = counts[store_index]
        ret['points'] = count
    else:
        ret['points'] = 0
    return (200,ret)

# subscribe
def subscribe(request,cursor,acc_id):
    channel_name = request['name']
    cursor.execute("SELECT group_id FROM groups WHERE name = %s",(channel_name,))
    gid = cursor.fetchone()
    if (gid is None): return (404,{})
    gid = gid[0]
    subscribe_to_channel(cursor, acc_id, gid)
    return (200,{})

# unsubscribe
def unsub(request,cursor,acc_id):
    channel_name = request['name']
    cursor.execute("SELECT group_id FROM groups WHERE name = %s",(channel_name,))
    gid = cursor.fetchone()
    if (gid is None): return (404,{}) # there is no group
    gid = gid[0]
    cursor.execute("SELECT groups, unsubs FROM subscriptions WHERE acc_id = %s", (acc_id,))
    fetch_data = cursor.fetchone()
    groups = fetch_data[0]
    unsubs = fetch_data[1]
    channel_index = groups.index(gid)
    groups.pop(channel_index)
    unsubs.pop(channel_index)
    cursor.execute("UPDATE subscriptions SET groups = %s, unsubs = %s WHERE acc_id = %s", (groups, unsubs, acc_id))
    return (200,{})

# registerparse
def register(request,cursor,acc_id):
    parse_object = request['id']
    cursor.execute("Update endusers SET parseobj = %s WHERE acc_id = %s", (parse_object, acc_id))
    return (200,{})

# deregisterparse
def deregister(request,cursor,acc_id):
    cursor.execute("Update endusers SET parseobj = %s WHERE acc_id = %s", (None, acc_id))
    return (200,{})

# getmystores
def mystores(request,cursor,acc_id):
    cursor.execute("SELECT stores FROM points WHERE acc_id = %s",(acc_id,))
    stores = cursor.fetchone()[0]
    ret = {"stores":[]}
    for store in stores:
        cursor.execute("SELECT name FROM stores WHERE acc_id = %s",(store,))
        store_name = cursor.fetchone()[0]
        ret["stores"].append(store_name)
    return (200,ret)

# getgroups
def getstorechannels(request,cursor,acc_id):
    store_name = request["owner"]
    cursor.execute("SELECT acc_id FROM stores WHERE name = %s",(store_name,))
    store_id = cursor.fetchone()[0]
    cursor.execute("SELECT name FROM groups WHERE owner = %s",(store_id,))
    stores = cursor.fetchall()
    ret = {"groups":[]}
    for store in stores:
        ret["groups"].append(store[0])
    return (200,ret)

# getsettings
def getsettings(request,cursor,acc_id):
    cursor.execute("SELECT phonenumber,email,msgval FROM endusers WHERE acc_id = %s",(acc_id,))
    info = cursor.fetchone()
    ret = {"pn":info[0],"email":info[1],"msgval":info[2]}
    return (200,ret)
