#!/usr/bin/python

# Food With Benefits website

import web, os, datetime, csv, time, random
from pbkdf2 import crypt
from io import BytesIO

urls = (
    '/','login',
    '/login','login',
    '/offers','offers',
    '/logout','logout',
    '/messaging','messaging',
    '/customers','customers',
    '/app','branding',
    '/settings','settings',

    '/updateMainColor','umc',
    '/updateHighlightColor','uhc',
    '/updatePromoText','upt',
    '/setDollarPoints','sdp',

    '/deleteOffer','dlo',
    '/updateOffer','udo',
    '/createOffer','cro',
    '/updateGroupName','ugn',
    '/deleteGroup','dlg',

    '/getTable','gtt',
    '/addPoints','adp',

    '/setWaitTime','swt',
    '/setStoreName','ssn',
    '/setPin','spn',
    '/setPasswd','spw',

    '/preview','blank',
    '/previewMessage','pvm',
    '/sendMessage','sdm',
    '/deleteMailJob','dmj',

    '/unsub','unsub',
    '/unsubFromGroup','ufg',
    '/subToGroup','stg',
    '/saveRow','svr',
    '/loadGroups','ldg',

    '/gencsv','gcsv'

)

app = web.application(urls, globals(), autoreload=False)
application = app.wsgifunc()

web.config.debug = False

base = os.getcwd()

db_name = os.environ("DB_NAME")
db_user = os.environ("DB_USER")
db_password = os.environ("DB_PASSWORD")
db = web.database(dbn='postgres', db=db_name, user=db_user, pw=db_password)
session = web.session.Session(app, web.session.DBStore(db,'sessions'), initializer={'acc_id': -1})

def isValidCredentials(user,passwd):
    store = db.select('stores', where='pin=$user', vars=locals())
    if (store is None or len(store) == 0):
        return -1
    store = store[0]
    actual = store['password']
    check = crypt(passwd,actual)
    if (check == actual): return store['acc_id']
    else: return -1



class login:
    def GET(self):
        if (session.acc_id != -1): # resume session
            raise web.seeother('/offers')
        t = web.template.frender(base + '/templates/login.html')
        return t(True)

    def POST(self): # check credentials when POSTing to /login
        user, passwd = web.input().user, web.input().passwd
        isValid = isValidCredentials(user,passwd)
        if not(isValid == -1): # successful login, render main page
            session.acc_id = isValid
            raise web.seeother('/offers')
        else:
            t = web.template.frender(base + '/templates/login.html')
            return t(False)
        t = web.template.frender(base + '/templates/login.html')
        return t(False)

class logout: # simple logout page
    def GET(self):
        session.acc_id = -1
        raise web.seeother('/login')

class offers:
    def GET(self):
        if (session.acc_id != -1): # resume session
            t = web.template.frender(base + '/templates/offers.html')
            acc_id = session.acc_id
            groups = db.select('groups', where='owner=$acc_id', vars=locals())
            group_info = {}
            grouplist = []
            subcounts = []
            subtables = []
            for group in groups:
                grouplist.append(group)
                group_info[group['name']] = []
                group_id = group['group_id']
                offers = db.select('offers', where='group_owner=$group_id', vars=locals())
                for offer in offers:
                    group_info[group['name']].append(offer)
                subscribers = db.select('subscriptions',where='$group_id = ANY (groups)', vars=locals())
                subcounts.append(len(subscribers))
                rows = []
                for sub in subscribers:
                    subtable = {}
                    sub_id = sub['acc_id']
                    subscriber = db.select('endusers',where='acc_id=$sub_id',vars=locals())[0]
                    pn = subscriber['phonenumber']
                    if pn is None:
                        pn = "--"
                    else: 
                        pn = str(pn)
                    email = subscriber['email']
                    if email is None:
                        email = "--"
                    subtable['name'] = subscriber['fullname']
                    subtable['pn'] = pn
                    subtable['email'] = email
                    subtable['id'] = sub_id
                    rows.append(subtable)
                subtables.append(rows)
            return t(grouplist,group_info,subcounts,subtables)
        raise web.seeother('/login') # no session, re-route to login

    def POST(self):
        if (session.acc_id == -1): raise web.seeothher('/login')
        acc_id = session.acc_id
        group_name = web.input().groupname
        db.insert('groups',name=group_name,owner=acc_id)
        raise web.seeother('/offers')

class messaging:
    def GET(self):
        if (session.acc_id != -1): # resume session
            t = web.template.frender(base + '/templates/messaging.html')
            acc_id = session.acc_id
            groups = db.select('groups', where='owner=$acc_id', vars=locals())
            joblist = db.select('mail_jobs', where='mailer_id=$acc_id', vars=locals())
            formatted_jobs = []
            for j in joblist:
                fjob = {}
                fjob['send'] = datetime.datetime.fromtimestamp(j['send']).strftime('%Y-%m-%d %H:%M:%S')
                fjob['message'] = j['message']
                fjob['recur'] = "Send Once"
                if not(j['recur'] == -1):
                    if j['recur'] == 1:
                        fjob['recur'] = "Every Day"
                    else:
                        fjob['recur'] = "Every " + str(j['recur']) + " Days"
                fjob['offer'] = "--"
                if not(j['offer'] == -1):
                    oid = j['offer']
                    fjob['offer'] = db.select('offers',where='offer_id=$oid',vars=locals())[0]['name']
                fjob['id'] = j['job_id']
                fjob['recip'] = "All Customers"
                if (j['ttype'] == 1):
                    gid = j['tinfo']
                    target_group = db.select('groups',where='group_id=$gid',vars=locals())[0]['name']
                    fjob['recip'] = "Members of \"" + target_group + "\" group"
                elif (j['ttype'] == 2):
                    idle_days = j['tinfo']
                    fjob['recip'] = "All customers absent for " + str(idle_days) + " days"
                formatted_jobs.append(fjob)
            grouplist = []
            for group in groups:
                grouplist.append(group['name'])
            return t(grouplist,formatted_jobs)
        raise web.seeother('/login') # no session, re-route to login

class customers:
    def GET(self):
        if (session.acc_id != -1): # resume session
            t = web.template.frender(base + '/templates/customers.html')
            return t(session.acc_id)
        raise web.seeother('/login') # no session, re-route to login

class branding:
    def GET(self):
        if (session.acc_id != -1): # resume session
            t = web.template.frender(base + '/templates/branding.html')
            acc_id = session.acc_id
            store_info = db.select('stores', where='acc_id=$acc_id', vars=locals())
            store = store_info[0]
            logo = store['logo']
            logo = "https://fwbapp.com/api/assets/" + logo
            promotext = store['promo']
            primcolor = store['color']
            wait = store['waittime']
            bgcolor = "rgb(" + str(primcolor[0]) + "," + str(primcolor[1]) + "," + str(primcolor[2]) + ")"
            highlcolor = store['highlight']
            hlcolor = "rgb(" + str(highlcolor[0]) + "," + str(highlcolor[1]) + "," + str(highlcolor[2]) + ")"
            dpp = store['dpp']
            return t(bgcolor,hlcolor,promotext,logo,wait,dpp)
        raise web.seeother('/login') # no session, re-route to login

    # logo upload
    def POST(self):
        if (session.acc_id == -1): raise web.seeother("/")
        filedir = "/var/www/api/assets/"
        x = web.input(logofile={})
        if "logofile" in x:
            if (len(x.logofile.file.read()) > 2097152): return "Filesize over 2mb"
            x.logofile.file.seek(0)
            acc_id = session.acc_id
            store_info = db.select('stores', where='acc_id=$acc_id', vars=locals())
            store = store_info[0]
            oldlogo = store['logo']
            pin = str(store['pin'])
            oldlogo_location = filedir + oldlogo
            filepath = x['logofile'].filename.replace('\\','/')
            filename = pin + '.' + filepath.split('/')[-1].split('.')[-1]
            f = open(filedir +'/'+ filename,'w')
            f.write(x.logofile.file.read())
            f.close()
            db.update('stores',where='acc_id=$acc_id', vars=locals(), logo=filename)
            os.remove(oldlogo_location)
        raise web.seeother("/app")



class settings:
    def GET(self): # storename pin
        if (session.acc_id != -1): # resume session
            t = web.template.frender(base + '/templates/settings.html')
            acc_id = session.acc_id
            store_info = db.select('stores', where='acc_id=$acc_id', vars=locals())
            store = store_info[0]
            pin = store['pin']
            name = store['name']
            return t(pin,name)
        raise web.seeother('/') # no session, re-route to login



#
# The following classes are not pages - they are handlers for ajax requests
#


# Set main color
class umc:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        cHex = web.input().color.replace("#","")
        try:
            r = int(cHex[0:2],16)
            g = int(cHex[2:4],16)
            b = int(cHex[4:6],16)
        except:
            r = 0
            g = 0
            b = 0
        colorRGB = [r,g,b]
        acc_id = session.acc_id
        db.update('stores', where='acc_id = $acc_id', vars=locals(), color=colorRGB)
        return "Success!"

# Set highlight color
class uhc:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        cHex = web.input().color.replace("#","")
        try:
            r = int(cHex[0:2],16)
            g = int(cHex[2:4],16)
            b = int(cHex[4:6],16)
        except:
            r = 0
            g = 0
            b = 0
        colorRGB = [r,g,b]
        acc_id = session.acc_id
        db.update('stores', where='acc_id = $acc_id', vars=locals(), highlight=colorRGB)
        return "Success!"

# Set promo text
class upt:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        new = web.input().text
        acc_id = session.acc_id
        db.update('stores', where='acc_id = $acc_id', vars=locals(), promo=new)
        return "Success!"

# delete offer
class dlo:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        offer_id = web.input().offer_id
        group_owner_info = db.select('offers', where='offer_id=$offer_id', vars=locals())
        owner_id = group_owner_info[0]['group_owner']
        owner_info = db.select('groups', where='group_id=$owner_id', vars=locals())
        owner_id = owner_info[0]['owner']
        if not(owner_id == acc_id): return "Not your group"
        db.delete('offers', where='offer_id=$offer_id', vars=locals())
        return "Success!"

# update offer
class udo:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        offer_id = web.input().offer_id
        group_owner_info = db.select('offers', where='offer_id=$offer_id', vars=locals())
        owner_id = group_owner_info[0]['group_owner']
        owner_info = db.select('groups', where='group_id=$owner_id', vars=locals())
        owner_id = owner_info[0]['owner']
        if not(owner_id == acc_id): return "Not your group"
        newName = web.input().name
        newDesc = web.input().desc
        newPoints = web.input().points
        db.update('offers', where='offer_id=$offer_id', vars=locals(), name=newName, description=newDesc, points=newPoints)
        return "Success!"


# create offer
class cro:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        group_id = web.input().group
        group_info = db.select('groups', where='group_id=$group_id', vars=locals())
        group_owner_id = group_info[0]['owner']
        if not(group_owner_id == acc_id): return "Not your group"
        newName = web.input().name
        newPoints = web.input().points
        newDesc = web.input().desc
        r = db.insert('offers', group_owner=group_id, name=newName, description=newDesc, points=newPoints,expiration=8760)
        new_offer = db.select('offers', where='group_owner=$group_id AND name=$newName AND description=$newDesc AND points=$newPoints', vars=locals())
        offer_id = new_offer[0]['offer_id']
        return offer_id


# get table
class gtt:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        table_type = int(web.input().tableType)
        page = int(web.input().page)
        pmin = (page-1)*100
        pmax = (page*100)-1
        if (table_type == 0): # HISTORY
            history = db.select('transactions', where='store=$acc_id', order='time desc', vars=locals())
            mindis = ""
            maxdis = ""
            if (pmin == 0): mindis = "disabled='true'"
            if (min(pmax,len(history)) == len(history)): maxdis = "disabled='true'"
            table = "<p>Showing " + str(pmin+1) + "-" + str(min(pmax+1,len(history))) + " of " + str(len(history)) + " transactions. <button " + mindis + " class='btn btn-warning' onclick='loadTable(document.getElementById(\"ttype\").value,document.getElementById(\"page\").value - 1); document.getElementById(\"page\").value = document.getElementById(\"page\").value - 1;'><span class='glyphicon glyphicon-chevron-left'></span></button> <button " + maxdis + " class='btn btn-warning' onclick='loadTable(document.getElementById(\"ttype\").value,parseInt(document.getElementById(\"page\").value) + 1); document.getElementById(\"page\").value = parseInt(document.getElementById(\"page\").value) + 1;'><span class='glyphicon glyphicon-chevron-right'></span></button></p>"
            table += '<table class="table sorttable" id="disptable"><thead><tr><th>Name</th><th>Phone Number</th><th>Email</th><th>Timestamp</th></tr></thead><tbody>'
            t = []
            for x in range(pmin,min(pmax+1,len(history))):
                t.append(history[x])
            for row in t:
                customer_id = row['acc_id']
                time = row['time']
                timestring = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
                customer = db.select('endusers', where='acc_id=$customer_id', vars=locals())[0]
                name = customer['fullname']
                email = customer['email']
                if (email is None): email = "--"
                phonenumber = customer['phonenumber']
                if (phonenumber is None): phonenumber = "--"
                table += "<tr><td>" + name + "</td><td>" + str(phonenumber) + "</td><td>" + email + "</td><td>" + timestring + "</td></tr>"
            table += "</tbody></table>"
            return table
        elif (table_type == 1): # ALL CUSTOMERS
            table = '<p>Click on a column header to sort by that column. Click on a customer\'s name to add/drop from groups.</p><table class="table sorttable" id="disptable"><thead><tr><th id="namehead">Name</th><th class="sorttable_nosort">Phone Number</th><th class="sorttable_nosort">Email</th><th>Points</th><th>Last Visit</th></thead><tbody>'
            customers = db.select('points', where='$acc_id = ANY (stores)', vars=locals())
            all_customers = []
            all_accids = []
            for row in customers:
                all_customers.append(row)
                all_accids.append(row['acc_id'])
            all_groups = db.select('groups',where='owner=$acc_id',vars=locals())
            for group in all_groups:
                group = group['group_id']
                subs = db.select('subscriptions',where='$group = ANY (groups)',vars=locals())
                for sub in subs:
                    if not(sub['acc_id'] in all_accids):
                        sid = sub['acc_id']
                        all_accids.append(sid)
                        all_customers.append(db.select('points',where='acc_id=$sid',vars=locals())[0])
            for row in all_customers:
                cid = row['acc_id']
                store_list =  row['stores']
                counts_list = row['counts']
                try:
                    count = counts_list[store_list.index(acc_id)]
                except:
                    count = '--'
                customer_id = row['acc_id']
                customer = db.select('endusers', where='acc_id=$customer_id', vars=locals())[0]
                name = customer['fullname']
                email = customer['email']
                if (email is None): email = "--"
                phonenumber = customer['phonenumber']
                if (phonenumber is None): phonenumber = "--"
                lv = db.select('transactions',where='store=$acc_id AND acc_id=$customer_id', order='time desc', vars=locals())
                if (len(lv) == 0):
                    last_visit = '--'
                else:
                    last_visit = datetime.datetime.fromtimestamp(lv[0]['time']).strftime('%Y-%m-%d %H:%M:%S')
                table += "<tr><td><a data-toggle='modal' onclick='loadModal("+str(cid)+");' data-target='#modal'>" + name + "</a></td><td>" + str(phonenumber) + "</td><td>" + email + "</td><td><span><span id='points-" + str(customer_id) + "'>" + (str(count) + ("&nbsp;" * (4-len(str(count))))) + "</span> <button onclick='addPoints(1," + str(customer_id) + ");' id='up-" + str(customer_id) +"' class='pointbutton'><span class='glyphicon glyphicon-plus-sign' aria-hidden='true'></span></button> <button onclick='addPoints(-1," + str(customer_id) + ");' class='pointbutton' id='down-" + str(customer_id) + "'> <span class='glyphicon glyphicon-minus-sign' aria-hidden='true'></span></button></td><td>" + last_visit + "</td></tr>"
            table += "</tbody></table>"
            return table
        elif (table_type == 2): # COUPON REDEMPTIONS
            table = '<table class="table sorttable" id="disptable"><thead><tr><th>Name</th><th>Phone Number</th><th>Email</th><th>Offer Name</th><th>Timestamp</th></thead><tbody>'
            customers = db.select('redemptions',where='store=$acc_id',vars=locals())
            for customer in customers:
                customer_id = customer['acc_id']
                offer_name = customer['name']
                time = str(customer['time']).split('.')[0]
                customer_info = db.select('endusers',where='acc_id=$customer_id',vars=locals())[0]
                pn = customer_info['phonenumber']
                if pn is None: pn = '--'
                pn = str(pn)
                email = customer_info['email']
                if email is None: email = '--'
                customer_name = customer_info['fullname']
                table += "<tr><td>" + customer_name + "</td><td>" + pn + "</td><td>" + email + "</td><td>" + offer_name + "</td><td>" + time + "</td></tr>"
            table += "</tbody></table>"
            return table
                

# set store name
class ssn:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        new_name = web.input().name
        db.update('stores', where='acc_id=$acc_id', vars=locals(), name=new_name)
        return "Success!"

# set store pin
class spn:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        new_pin = web.input().pin
        if not(len(new_pin) == 4): return "Invalid PIN"
        try:
            new_pin = int(new_pin)
        except:
            return "Invalid PIN"
        check = db.select('stores', where='pin=$new_pin', vars=locals())
        if (len(check) != 0): return str(new_pin) + " Is already in use by another store."
        db.update('stores', where='acc_id=$acc_id', vars=locals(), pin=new_pin)
        return "Success!"

# set store password
class spw:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        newpass = web.input().newpass
        checkpass = web.input().checkpass
        if not(newpass == checkpass): return "The passwords entered do not match."
        elif (len(newpass) < 8): return "Your password must be at leas 8 characters long."
        new_passwd = crypt(newpass)
        db.update('stores', where='acc_id=$acc_id', vars=locals(), password=new_passwd)
        return "Success!"

# blank page (for message preview)
class blank:
    def GET(self):
        return '<html><body id="content"></body></html>'

# preview message
class pvm:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        group = web.input().gr
        subject = web.input().subj
        storename = db.select('stores',where='acc_id=$acc_id',vars=locals())[0]['name']
        header = web.input().head
        message = web.input().msg
        templateFN = db.select('stores', where='acc_id=$acc_id', vars=locals())[0]['template']
        template_file = open('/var/www/api/templates/' + templateFN,'r')
        template_lines = template_file.readlines()
        template_html = ""
        template_file.close()
        for line in template_lines:
            line = line.replace("msgheader",header).replace("msgcontent",message).replace("groupname",group).replace("storename",storename)
            template_html += line
        return template_html

# send message
class sdm:
    def POST(self):
        from datetime import datetime
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        subject= web.input().subject
        header = web.input().header
        message = web.input().message
        send_date = web.input().send # "06/09/2015 9:13 AM"
        send_datetime = datetime.strptime(send_date,"%m/%d/%Y %I:%M %p")
        send_date_unix = (send_datetime - datetime.fromtimestamp(3600)).total_seconds()
        is_recurring = False
        has_offer = False
        target_type = 0
        recur_days = -1
        target_info = None
        try: # check if message recurs
            recur_days = int(web.input().recur)
            is_recurring = True
        except: pass
        try: # check if message has offer attached
            offer_name = web.input().offname
            try:
                offer_exp = int(web.input().offexp)
            except:
                offer_exp = -1
            has_offer = True
        except:pass
        try: # check if sending to a group
            target_group = web.input().group
            target_type = 1
            g_id = db.select('groups',where='owner=$acc_id AND name=$target_group',vars=locals())[0]['group_id']
            target_info = g_id
        except: pass
        try:
            idle_days = web.input().idledays
            target_type = 2
            target_info = idle_days
        except: pass

        offer_id = -1
        if has_offer: # create offer
            offer_id = db.insert('offers',seqname='offer_ids', group_owner=-1,name=offer_name,description='',expiration=offer_exp,points=0)
        
        # insert email job
        db.insert('mail_jobs',mailer_id=acc_id,subject=subject,header=header,message=message,send=send_date_unix,recur=recur_days,offer=offer_id,ttype=target_type,tinfo=target_info)
        return "Success!"

# unsubscribe from a group (from an email unsub link)
class unsub:
    def GET(self):
        try:
            target = web.input().t
            store_id = web.input().g
            t_id = db.select('endusers',where='email=$target',vars=locals())[0]['acc_id']
            store_name = db.select('stores',where='acc_id=$store_id',vars=locals())[0]['name']
            sublist = db.select('subscriptions',where='acc_id=$t_id',vars=locals())[0]['groups']
            store_groups = [x['name'] for x in db.select('groups',where='owner=$store_id',vars=locals())]
        except:
            return "There was a problem unsubscribing you from this group."
        for group in store_groups:
            if group in sublist: sublist.remove(group)
        db.update('subscriptions',where='acc_id=$t_id',vars=locals(),groups=sublist)
        return "You will no longer receive messages from " + store_name + "."
    
# csv generating & downloading customer data
class gcsv:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        table_type = web.input().ttype
        wf = BytesIO()
        writer = csv.writer(wf,delimiter=',',dialect='excel-tab')
        if (table_type == "0"): # HISTORY
            headers = ['Name','Phone #','Email','Timestamp']
            writer.writerow(headers)
            history = db.select('transactions', where='store=$acc_id', order='time desc', vars=locals())
            for row in history:
                customer_id = row['acc_id']
                time = row['time']
                timestring = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
                customer = db.select('endusers', where='acc_id=$customer_id', vars=locals())[0]
                name = customer['fullname']
                email = customer['email']
                if (email is None): email = "--"
                phonenumber = customer['phonenumber']
                if (phonenumber is None): phonenumber = "--"
                trow = [name,str(phonenumber),email,timestring]
                writer.writerow(trow)
        elif (table_type == "1"): # ALL CUSTOMERS
            headers = ['Name','Phone #','Email','Points','Last Visit']
            writer.writerow(headers)
            customers = db.select('points', where='$acc_id = ANY (stores)', vars=locals())
            for row in customers:
                store_list =  row['stores']
                counts_list = row['counts']
                count = counts_list[store_list.index(acc_id)]
                customer_id = row['acc_id']
                customer = db.select('endusers', where='acc_id=$customer_id', vars=locals())[0]
                name = customer['fullname']
                email = customer['email']
                if (email is None): email = "--"
                phonenumber = customer['phonenumber']
                if (phonenumber is None): phonenumber = "--"
                lv = db.select('transactions',where='store=$acc_id AND acc_id=$customer_id', order='time desc', vars=locals())
                if (len(lv) == 0):
                    last_visit = '--'
                else:
                    last_visit = datetime.datetime.fromtimestamp(lv[0]['time']).strftime('%Y-%m-%d %H:%M:%S')
                trow = [name,str(phonenumber),email,str(count),last_visit]
                writer.writerow(trow)
        elif (table_type == "2"): # COUPON REDEMPTIONS
            headers = ['Name','Phone #','Email','Offer Name','Timestamp']
            writer.writerow(headers)
            customers = db.select('redemptions',where='store=$acc_id',vars=locals())
            for customer in customers:
                customer_id = customer['acc_id']
                offer_name = customer['name']
                time = str(customer['time']).split('.')[0]
                customer_info = db.select('endusers',where='acc_id=$customer_id',vars=locals())[0]
                pn = customer_info['phonenumber']
                if pn is None: pn = '--'
                pn = str(pn)
                email = customer_info['email']
                if email is None: email = '--'
                customer_name = customer_info['fullname']
                row = [customer_name,pn,email,offer_name,time]
                writer.writerow(row)
        csvval = wf.getvalue()
        wf.close()
        web.header('Content-Type','text/csv')
        web.header('Content-disposition','attachment; filename=data.csv')
        return csvval

# set wait time
class swt:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        nwt = (web.input().wait)
        db.update('stores',where='acc_id=$acc_id',vars=locals(),waittime=nwt)
        return "Success!"

# add points
class adp:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        target_id = int(web.input().user)
        amount = int(web.input().amount)
        target_info = db.select('points',where='acc_id=$target_id',vars=locals())[0]
        stores_list = target_info['stores']
        points_list = target_info['counts']
        points_list[stores_list.index(acc_id)] += amount
        if points_list[stores_list.index(acc_id)] < 0:
            return '-'
        db.update('points',where='acc_id=$target_id',counts=points_list,vars=locals())
        return (str(points_list[stores_list.index(acc_id)]) + ("&nbsp;" * (4 - len(str(points_list[stores_list.index(acc_id)])))))

class ugn:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        newname = web.input().name
        gid = web.input().gid
        db.update('groups',where='group_id=$gid AND owner=$acc_id',vars=locals(),name=newname)
        return "Success!"

class dlg:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        gid = int(web.input().gid)
        subscribers = db.select('subscriptions',where='$gid = ANY (groups)',vars=locals())
        for subscriber in subscribers:
            sub_id = subscriber['acc_id']
            sub_unsubs = subscriber['unsubs']
            sub_stores = subscriber['groups']
            index = sub_stores.index(gid)
            sub_unsubs.pop(index)
            sub_stores.pop(index)
            db.update('subscriptions',where='acc_id=$sub_id', vars=locals(), unsubs=sub_unsubs,groups=sub_stores)
        db.delete('offers',where='group_owner=$gid',vars=locals())
        db.delete('groups',where='owner=$acc_id AND group_id=$gid',vars=locals())
        return "Success!"

class dmj:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        jid = int(web.input().id)
        j_sender = db.select('mail_jobs',where='job_id=$jid',vars=locals())[0]['mailer_id']
        if not(j_sender == acc_id):
            return "You do not own that message"
        else:
            db.delete('mail_jobs',where='job_id=$jid',vars=locals())
            return "Success!"

class ufg:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        gid = web.input().g
        cid = web.input().t
        g_owner = db.select('groups',where='group_id=$gid',vars=locals())[0]['owner']
        if not(g_owner == acc_id):
            return "You do not own that group"
        sub_info = db.select('subscriptions', where='acc_id=$cid',vars=locals())[0]
        sub_groups = sub_info['groups']
        sub_codes = sub_info['unsubs']
        ind = sub_groups.index(int(gid))
        sub_groups.pop(ind)
        sub_codes.pop(ind)
        db.update('subscriptions',where='acc_id=$cid',vars=locals(),groups=sub_groups,unsubs=sub_codes)
        return "Success!"
class stg:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        gid = web.input().g
        cid = web.input().t
        new_unsub = db.select("nextval('unsub_codes')")[0]['nextval']
        target = db.select("subscriptions",where="acc_id=$cid",vars=locals())[0]
        t_groups = target['groups']
        t_unsubs = target['unsubs']
        if not(int(gid) in t_groups):
            t_groups.append(int(gid))
            t_unsubs.append(int(new_unsub))
            db.update('subscriptions',where='acc_id=$cid',vars=locals(),groups=t_groups,unsubs=t_unsubs)
        return "Success!"
        


class svr:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        em = web.input().em
        pn = web.input().pn
        fn = web.input().fn
        gid = web.input().group
        if not(pn == ''):
            pn_check = db.select('endusers',where='phonenumber=$pn',vars=locals())
        else:
            pn_check = []
        new_id = -1
        new_em = "--"
        new_pn = "--"
        new_fn = "--"
        if len(pn_check) > 0:
            new_info = pn_check[0]
            new_id = new_info['acc_id']
            new_em = new_info['email']
            new_fn = new_info['fullname']
            new_pn = new_info['phonenumber']
        else:
            if not(em == ''):
                em_check = db.select('endusers',where='email=$em',vars=locals())
            else:
                em_check = []
            if len(em_check) > 0:
                new_info = em_check[0]
                new_id = new_info['acc_id']
                new_em = new_info['email']
                new_fn = new_info['fullname']
                new_pn = new_info['phonenumber']
        if not(new_id == -1):
            tpoints = db.select('points',where='acc_id=$new_id',vars=locals())[0]
            tcounts = tpoints['counts']
            tstores = tpoints['stores']
            if not(acc_id in tstores):
                tstores.append(acc_id)
                tcounts.append(0)
                db.update('points',where='acc_id=$new_id',vars=locals(),counts=tcounts,stores=tstores)
            new_unsub = db.select("nextval('unsub_codes')")[0]['nextval']
            target = db.select("subscriptions",where="acc_id=$new_id",vars=locals())[0]
            t_groups = target['groups']
            t_unsubs = target['unsubs']
            if not(int(gid) in t_groups):
                t_groups.append(int(gid))
                t_unsubs.append(int(new_unsub))
                db.update('subscriptions',where='acc_id=$new_id',vars=locals(),groups=t_groups,unsubs=t_unsubs)
            else:
                return "Same"
        else: # account not found - make a new one
            if (fn == '' or (em == '' and pn == '')): return "Please fill out all required fields."
            calcval = 1
            if not(em == "" or em is None):
                calcval *= 3
            else: em = None
            if not(pn == "" or pn is None):
                calcval *= 2
            else: pn = None
            new_id = db.select("nextval('counter_users')")[0]['nextval']
            new_fn = fn
            new_pn = pn
            new_em = em
            db.insert("endusers",acc_id=new_id,phonenumber=pn,parseobj=None,msgval=calcval,email=em,fullname=fn,password=crypt("ThisIsAPasswordToBeResetLater"))
            tstores = [acc_id]
            tcounts = [0]
            db.insert('points',acc_id=new_id,counts=tcounts,stores=tstores)
            empty = []
            db.insert("points",acc_id=new_id,stores=empty,counts=empty)
            glist = [int(gid)]
            ulist = [int(db.select("nextval('unsub_codes')")[0]['nextval'])]
            db.insert("subscriptions",acc_id=new_id,groups=glist,unsubs=ulist)
        if new_fn is None: new_fn = "--"
        if new_pn is None: new_pn = "--"
        if new_em is None: new_em = "--"
        return "Success!\n" + str(new_id) + "\n" + new_fn + "\n" + str(new_pn) + "\n" + new_em

class ldg:
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        cid = web.input().id
        ret = ""
        cgroups = db.select('subscriptions',where='acc_id=$cid',vars=locals())[0]['groups']
        ogroups = db.select('groups',where='owner=$acc_id',vars=locals())
        if len(ogroups) == 0: return ""
        for g in ogroups:
            ret += g['name'] + "\n" + str(g['group_id']) + "\n"
            if g['group_id'] in cgroups:
                ret += 'y'
            else:
                ret += 'n'
            ret += "\n"
        return ret[:-1]

class sdp:        
    def POST(self):
        if (session.acc_id == -1): return "No login"
        acc_id = session.acc_id
        amnt = web.input().amount
        if (amnt == '-1'): amnt = None
        db.update('stores',where='acc_id=$acc_id',vars=locals(),dpp=amnt)
        return "Success!"
