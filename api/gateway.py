#!/usr/bin/python3

# FWB server

#import cgitb
#cgitb.enable()

import cgi, sys, json, psycopg2, logging, time, os
from general import createCoupon, sendMsg, subscribe_to_channel
from login import validate, createUser
from app_handlers import getoffers,getchannels,getpoints,subscribe,unsub,register,deregister,mystores,getstorechannels,getsettings
from pos_handlers import addpoints,usecode,specifics, makecode

#logging.basicConfig(filename='fwb.log',level=logging.INFO)


db_name = os.environ("DB_NAME")
db_user = os.environ("DB_USER")
db_password = os.environ("DB_PASSWORD")
db = psycopg2.connect('dbname=' + db_name + ' user=' + db_user + ' password=' + db_password)
cursor = db.cursor()

app_requests = {"getmystores":mystores,"getoffers":getoffers,"getmygroups":getchannels,"getgroups":getstorechannels,"getpoints":getpoints,"subscribe":subscribe,"unsubscribe":unsub,"registerparse":register,"deregisterparse":deregister,"getsettings":getsettings}
pos_requests = {"addpoints":addpoints,"usecode":usecode,"getbrand":specifics,"makecode":makecode}
all_requests = {0:app_requests,1:app_requests,2:pos_requests}

# should be called at the very end of functionality - server quits here
def reply(code,tag,reqtype,data):
    if not(data): data = {}
    data['code'] = code
    if reqtype: data['request'] = reqtype
    if tag: data['tag'] = tag
    print("Content-Type:application/json\n")
    print(json.dumps(data))
    sys.exit(0)

try:
    r = sys.stdin.read()
    request = json.loads(r)
    username = request['username']
    password = request['password']
    clienttype = request['ctype']
    reqtype = request['reqtype']
    tag = request['tag']
except:
    reply(400,None,None,None)


if (reqtype == 'signup'):
    code = createUser(request,cursor)
    if (code == 200): db.commit()
    reply(code,tag,reqtype,{})

isvalid,acc_id,server = validate(request,cursor)

if not(isvalid):
    reply(401,tag,reqtype,None)

if (reqtype == 'validate'):
    if isvalid:
        reply(200,tag,reqtype,server)
    else:
        reply(401,tag,reqtype,None)

try:
    code,result = all_requests[clienttype][reqtype](request,cursor,acc_id)
except:
    db.close()
    reply(500,tag,reqtype,None)

if (str(code)[0] == '2'):
    db.commit()
    db.close()
reply(code,tag,reqtype,result)
