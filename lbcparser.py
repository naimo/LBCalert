from flask import url_for, render_template, flash
from flask_mail import Mail, Message

import random
import requests
import re
import sys
import os
import json
import dateparser
import html
import json
import logging

from flask_login import login_user
from app import app, db, q, conn
from rq import Connection, get_failed_queue
from models import User, Search, LBCentry


# ps, pe, mrs, rs, ms, ccs, sqs, ros, cs, bros
# f a(all) p(private) c(company)
# c = category number
# zipcode = zipcode
# q = query
# o = page
# w ?
# ca ?
# ps - pe price range(categories)
# rs - re year range
# ms - me km range
# ccs - cce cylindre

def get_listing_url(linkid):
    url = app.config['BASE_URL'] + "view.json?" + "ad_id=" + str(linkid)
    return url + "&app_id=" + app.config['APP_ID'] + "&key=" + app.config['API_KEY']

def list_items(search, proxy=None):
    logger = logging.getLogger('rq.worker')

    url = search.get_url()
    logger.info("[list_items]" + str(url))

    if proxy is not None and proxy != "":
        print("[list_items] using proxy " + proxy)
        r = requests.get(url, proxies = {"https":proxy})
    else:
        r = requests.get(url)

    ads = r.json()['ads']

    listings = []

    existing_ids = [e.linkid for e in search.lbc_entries]

    for ad in ads:
        listid = int(ad['list_id'])
        price = ad['price']
        
        if (price == ''):
            price = None
        else:
            price = int(price.replace(" ",""))

        if search.minprice is not None and \
                price is not None and price < search.minprice:
            continue
        if search.maxprice is not None and \
                price is not None and price > search.maxprice:
            continue

        # TODO check updated price and update row in DB
        if listid in existing_ids:
            continue
            # existing_entry = LBCentry.query.get(listid)
            # if price >= existing_entry.price:
            #     continue

        listing_url = get_listing_url(listid)
        
        if proxy is not None:
            r = requests.get(listing_url, proxies = {"https":proxy})
        else:
            r = requests.get(listing_url)
        try :
            text = r.content.decode(r.encoding)
            listing_json = json.loads(text, strict=False)
        except Exception as e:
            logger.error("[list_items] " + str(listing_url))
            logger.error("[list items] " + str(listid) + " skipped cause : " + str(e))
            continue
        if 'body' in listing_json:
            description = listing_json['body']
        else:
            description = ""

        title = ad['subject']
        category = int(ad['category_id'])

        location = ad['region_name'] + ' - ' + \
                   ad['city'] + ' (' + ad['zipcode'] + ')'
#                   ad['dpt_name'] + ' - ' + \
        time = dateparser.parse(ad['date'])
        if "thumb_hd" in ad:
            imgurl = ad['thumb_hd']
        else:
            imgurl = None
        if "list_time" in ad:
            time = ad['list_time']

        imgnumber = None

        params={
            "linkid":listid,
            "title":title,
            "category":category,
            "price":price,
            "time":time,
            "location":location,
            "imgurl":imgurl,
            "imgnumber":imgnumber,
            "description": description
        }

        #print(params)

        a = LBCentry(**params)
        logger.info("[list_items]" + str(a))
        listings.append(a)
    return listings

def parselbc(id, page):
    with app.test_request_context():
        search = Search.query.get(id)

        new_items = list_items(search, app.config['PROXY_URL'])

        if len(new_items)>0:
            for listing in new_items:
                db.session.add(listing)
                search.lbc_entries.append(listing)
            db.session.commit()

            mail=Mail(app)
            msg = Message('[LBCbot - '+app.config["VERSION"]+'] New items for "'+search.title+'"', sender='lbcbot@gmail.com', recipients=[user.email for user in search.users])
            msg.html = render_template('email_entries.html', lbcentries=new_items)
            mail.send(msg)
        return id

def task():
    refresh_searches()

def refresh_searches():
    # Clear failed jobs
    with Connection(conn):
        fq = get_failed_queue()
    for job in fq.jobs:
            print("delete job " + job.id)
            job.delete()
    searches = Search.query.all()
    for search in searches:
        job = q.enqueue_call(
            func=parselbc, args=(search.id,1), result_ttl=0
        )
        print(search.title)

if __name__=="__main__":
    search = Search(title = "test", terms = "test", user=None)
    url = search.get_url()
    list_items(url)
