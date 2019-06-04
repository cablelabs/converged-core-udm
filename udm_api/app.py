#!/usr/bin/env python3
import json
import logging
import os
import threading
import uuid
from random import randint

import connexion
from connexion import NoContent
from pymongo import MongoClient, errors
import requests
import urllib3


from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

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

urllib3.disable_warnings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('app')


class Monitor(threading.Thread):
    def __init__(self, supi, db, subscriptionId, callback):
        threading.Thread.__init__(self)
        self.supi = supi
        self.db = db
        self.subscriptionId = subscriptionId
        self.running = True
        self.callback = callback
        self.stream = None

    def run(self):
        with self.db.subscription_data_sets.watch([], full_document='default') as self.stream:
            for change in self.stream:
                logger.debug(change)
                changes = []
                for k, v in change['updateDescription']['updatedFields'].items():
                    changeItem = dict(op='MOVE', path=k, newValue=v)
                    changes.append(changeItem)
                notifyItem = dict(resourceId='/' + self.supi, changes=changes)
                notifyItems = [notifyItem]
                document = dict(notifyItems=notifyItems)
                logger.info(document)
                self.post(document)

    def stop(self):
        logger.info('Removing Monitor for %s' % self.subscriptionId)
        self.running = False
        if self.stream is not None:
            self.stream.close()
            logger.info('Stream closed')

    def post(self, body):
        r = requests.post(self.callback, json=body, verify=False)
        if r.status_code == 201 or r.status_code == 200:
            return r.json()
        elif r.status_code == 204:
            return
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
    logger.info(result.modified_count)
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
    logger.info('Deleting Subscription')
    for monitor in monitor_map:
        logger.info('%r' % monitor)
        if subscriptionId == str(monitor['subscriptionId']):
            logger.info('Stopping')
            monitor['monitor'].stop()
    return NoContent, 204

#
# UECM Implementations
#


def putRegistrationAmfNon3gppAccess(ueId, body):
    body['ueId'] = ueId
    result = db.amf_non3gpp_access.replace_one({'ueId': ueId}, body, True)
    if result is None:
        return NoContent, 400
    else:
        document = db.amf_non3gpp_access.find_one({'ueId': ueId})
        if document.get('_id') is not None:
            del document['_id']
        return document, 201, {'Location': '/' + ueId + '/registrations/amf-non-3gpp-access' }

def patchRegistrationAmfNon3gppAccess(ueId, body):
    body['ueId'] = ueId
    if body.get('pei') is not None and body.get('purgeFlag') is not None:
        result = db.amf_non3gpp_access.update_one({'ueId': ueId}, {'$set': {'guami': body['guami']},
                                                                   '$set': {'pei': body['pei']},
                                                                   '$set': {'purgeFlag': body['purgeFlag']}
                                                                   })
    elif body.get('pei') is not None:
        result = db.amf_non3gpp_access.update_one({'ueId': ueId}, {'$set': {'guami': body['guami']},
                                                                   '$set': {'pei': body['pei']}
                                                                   })
    elif body.get('purgeFlag') is not None:
        result = db.amf_non3gpp_access.update_one({'ueId': ueId}, {'$set': {'guami': body['guami']},
                                                                   '$set': {'purgeFlag': body['purgeFlag']}
                                                                   })
    else:
        result = db.amf_non3gpp_access.update_one({'ueId': ueId}, {'$set': {'guami': body['guami']}})
    logger.info(result)
    document = db.amf_non3gpp_access.find_one({'ueId': ueId})
    if document.get('_id') is not None:
        del document['_id']
    return document, 200


def getRegistrationAmfNon3gppAccess(ueId):
    document = db.amf_non3gpp_access.find_one({'ueId': ueId})
    if document is None:
        return NoContent, 404
    else:
        del document['_id']
        return document, 200


with open('/openapi/' + 'TS29571_CommonData.yaml') as cmm_file:
    cmm_data = load(cmm_file, Loader=Loader)

with open('/openapi/' + 'TS29503_Nudm_SDM.yaml') as sdm_file:
    sdm_data = load(sdm_file, Loader=Loader)

with open('/openapi/' + 'TS29503_Nudm_UECM.yaml') as uecm_file:
    uecm_data = load(uecm_file, Loader=Loader)

sdm_data['components']['schemas'].update(cmm_data['components']['schemas'])
sdm_data['components']['responses'] = cmm_data['components']['responses']

uecm_data['components']['schemas'].update(cmm_data['components']['schemas'])
uecm_data['components']['responses'] = cmm_data['components']['responses']


sdm_out_file = open('/openapi/sdm_full.yaml', 'w')
dump(sdm_data, sdm_out_file)
uecm_out_file = open('/openapi/uecm_full.yaml', 'w')
dump(uecm_data, uecm_out_file)

monitor_map = []
spec = '/openapi/'
try:
    app = connexion.App(__name__, specification_dir=spec, debug=True)
    app.add_api('uecm_full.yaml')
    app.add_api('sdm_full.yaml')

    # set the WSGI application callable to allow using uWSGI:
    # uwsgi --http :8080 -w app
    application = app.app
except Exception as e:
    logger.error(e)

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string

replicant = {
    "_id": "rs0",
    "members" : [
        {"_id": 1, "host": "db01:27017"},
        {"_id": 2, "host": "db02:27017"}
    ]
}

client = MongoClient('mongodb://db01:27017/')
try:
    status = client.admin.command("replSetGetStatus")
except errors.OperationFailure:
    client.admin.command("replSetInitiate", replicant)
client.close()

client = MongoClient('mongodb://db01:27017/', replicaset='rs0')
db = client.udm

# Clean out Subscriptions
with open(cwd + 'sdm.json') as json_file:
    json_data = json.load(json_file)
    count = db.supi_sdm_subscriptions.delete_many({'nfInstanceId': json_data['nfInstanceId']}).deleted_count
    logger.debug(count)

# Clean out and insert primary SUPI
with open(cwd + 'supi.json') as json_file:
    json_data = json.load(json_file)
    count = db.subscription_data_sets.delete_many({'supi': json_data['supi']}).deleted_count
    logger.debug(count)
    db.subscription_data_sets.insert_one(json_data)


if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=8080, server='gevent')
