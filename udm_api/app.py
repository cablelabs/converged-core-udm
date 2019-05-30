#!/usr/bin/env python3
import json
import logging
import os
import threading
import uuid
from random import randint

import connexion
from connexion import NoContent
from pymongo import MongoClient

cwd = os.getcwd()

# Copyright 2018 Cable Television Laboratories, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import requests
import urllib3

urllib3.disable_warnings()
logger = logging.getLogger('drp-session')


class Monitor(threading.Thread):
    def __init__(self, supi, db, subscriptionId, callback):
        threading.Thread.__init__(self)
        self.supi = supi
        self.db = db
        self.subscriptionId = subscriptionId
        self.running = True
        self.callback = callback

    def run(self):
        while self.running:
            with self.db.subscription_data_sets.watch([], full_document='default') as stream:
                for change in stream:
                    logging.info(change)
                    changes = []
                    for k, v in change['updateDescription']['updatedFields'].items():
                        changeItem = dict(op='MOVE', path=k, newValue=v)
                        changes.append(changeItem)
                    notifyItem = dict(resourceId='/' + self.supi, changes=changes)
                    notifyItems = [notifyItem]
                    document = dict(notifyItems=notifyItems)
                    logging.info(document)
                    self.post(document)

    def stop(self):
        self.running = False

    def post(self, body):
        r = requests.post(self.callback, json=body, verify=False)
        if r.status_code == 201 or r.status_code == 200:
            return r.json()
        else:
            logger.error('Error on Post ' + str(r.status_code))
            temp = r.json()
            if body.get('Name') is not None:
                raise Exception(body['Name'],
                                str(temp['Messages'][0]))
            else:
                raise Exception(body['Addr'],
                                str(temp['Messages'][0]))


def getSupiById(supi):
    document = db.subscription_data_sets.find_one({'supi': supi})
    if document is None:
        return document, 404
    else:
        del document['_id']
        return document, 200


def postTemp(supi):
    result = db.subscription_data_sets.update_one({'supi': supi}, {'$set': {'x': randint(0, 100)}})
    logging.info(result.modified_count)
    return result.modified_count, 201


def getSupiNssai(supi):
    document = db.subscription_data_sets.find_one({'supi': supi})
    if document is None:
        return document, 404
    else:
        nassi = document['amData']['nssai']
        return nassi, 200


def getSupiAmData(supi):
    document = db.subscription_data_sets.find_one({'supi': supi})
    if document is None:
        return document, 404
    else:
        am = document['amData']
        return am, 200


def postSupiSdmSubscriptions(supi, body):
    subscriptionId = uuid.uuid4()
    body['subscriptionId'] = subscriptionId
    id = db.supi_sdm_subscriptions.insert_one(body).inserted_id
    document = db.supi_sdm_subscriptions.find_one({'_id': id})
    del document['_id']
    monitor = Monitor(supi, db, subscriptionId, body['callbackUri'])
    monitor.start()
    monitor_map.append({'subscriptionId': subscriptionId, 'monitor': monitor})
    return document, 201


def deleteSupiSubscriptionById(supi, subscriptionId):
    for monitor in monitor_map:
        if monitor['subscriptionId'] is subscriptionId:
            monitor['monitor'].stop()
    return NoContent, 204

#
# UECM Implementations
#


def putRegistrationAmfNon3gppAccess(ueId, body):
    result = db.amf_non3gpp_access.replace_one({'ueId': ueId}, body, True)
    if result is None:
        return None, 400
    else:
        id = result.upserted_id
        document = db.amf_non3gpp_access.find_one({'_id': id})
        return document, 201, {'Location': '/' + ueId + '/registrations/amf-non-3gpp-access/' + document['amfInstanceId'] }

def patchRegistrationAmfNon3gppAccess(ueId, body):
    return NoContent, 200


def getRegistrationAmfNon3gppAccess(ueId):
    return NoContent, 200


monitor_map = []
logging.basicConfig(level=logging.INFO)
spec = '/openapi/'
try:
    app = connexion.App(__name__, specification_dir=spec)
    app.add_api('TS29503_Nudm_UECM.yaml')
    app.add_api('TS29503_Nudm_SDM.yaml')

    # set the WSGI application callable to allow using uWSGI:
    # uwsgi --http :8080 -w app
    application = app.app
except Exception as e:
    logging.error(e)

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string

replicant = {
    "_id": "rs0",
    "version": 1,
    "members" : [
        {"_id": 1, "host": "db01:27017"},
        {"_id": 2, "host": "db02:27017"}
    ]
}
client = MongoClient('mongodb://db01:27017/', replicaset='rs0')
status = client.admin.command("replSetGetStatus")
if status['set'] is None:
    client.admin.command("replSetInitiate", replicant)

client2 = MongoClient('mongodb://db02:27017/')
status2 = client2.admin.command("replSetGetStatus")
if status2['set'] is None:
    client2.admin.command("replSetInitiate", replicant)
client2.close()

db = client.udm

# Clean out Subscriptions
with open(cwd + 'sdm.json') as json_file:
    json_data = json.load(json_file)
    count = db.supi_sdm_subscriptions.delete_many({'nfInstanceId': json_data['nfInstanceId']}).deleted_count
    logging.debug(count)

# Clean out and insert primary SUPI
with open(cwd + 'supi.json') as json_file:
    json_data = json.load(json_file)
    count = db.subscription_data_sets.delete_many({'supi': json_data['supi']}).deleted_count
    logging.debug(count)
    count = db.supi_sdm_subscriptions.delete_many({'nfInstanceId': json_data['supi']}).deleted_count
    logging.debug(count)
    db.subscription_data_sets.insert_one(json_data)

if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=8080, server='gevent')
