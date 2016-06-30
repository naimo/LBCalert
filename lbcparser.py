from flask import url_for, render_template, flash
from flask.ext.mail import Mail, Message
from bs4 import BeautifulSoup
import random
import requests
import re
import sys
import os

from app import app, db, q
from models import Search, LBCentry

def parselbc(id):
    with app.test_request_context():
        search = Search.query.get(id)
        existing_ids = [e.linkid for e in search.lbc_entries]
        proxy = random.choice(app.config['PROXIES'])
    
        url = "/".join([app.config['LBCURL'],search.terms])

        proxies = {"https":app.config['PROXY_URL']}        

        r = requests.get(url, proxies = proxies)
        html = r.text
        soup = BeautifulSoup(html,"html.parser")     

        try:
            section = soup.find("section",{"class":"mainList"})
            links = section.findAll("a",{"class":"list_item"})
        except:
            print(sys.exc_info(), r)
            return id
    
        newitems=[]
        for link in links:
            linkid = int(link['href'].split('/')[-1].split('.')[0])
            #test if id already found in this search
            if linkid in existing_ids:
                break
            else:
                #TODO actually parse category
                category = "category"
                title = link['title'].strip()
                a = LBCentry(linkid=linkid,title=title,category=category)
                pricediv = link.find("h3",{"class":"item_price"})
                if pricediv:
                    m = re.match("(\d+)",pricediv.text.strip())
                    price  = int(m.group(1))
                    a.price=price
                db.session.add(a)
                search.lbc_entries.append(a)
                newitems.append(a)
        db.session.commit()

        # r = requests.get(url_for("show_searches",_external=True))
        if len(newitems)>0:
            mail=Mail(app)
            msg = Message('[LBCbot] New items for "'+search.title+'"', sender='lbcbot@gmail.com', recipients=[search.email,])
            msg.html = render_template('email_entries.html', lbcentries=newitems)
            mail.send(msg)
        return id
        
def task():
    ping_heroku()
    refresh_searches()

def ping_heroku():
    requests.get("http://"+app.config['SERVER_NAME'])

def refresh_searches():
    searches = Search.query.all()
    for search in searches:
        job = q.enqueue_call(
            func=parselbc, args=(search.id,), result_ttl=0
        )