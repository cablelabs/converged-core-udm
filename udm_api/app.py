#!/usr/bin/env python3
import json
import logging
from pprint import pprint

import connexion
from connexion import NoContent
from pymongo import MongoClient
import os
cwd = os.getcwd()


def getSupiById(supi):
    document = db.subscription_data_sets.find_one({'supi': supi})
    if document is None:
        return document, 404
    else:
        del document['_id']
        return document, 200


def getSupiNssai(supi):
    document = db.subscription_data_sets.find_one({'supi': supi})
    if document is None:
        return document, 404
    else:
        nassi = document['amData']['nssai']
        return nassi, 200


def getSupiAmData():
    return NoContent, 200


def postSupiSdmSubscriptions():
    return NoContent, 200


def deleteSupiSubscriptionById():
    return NoContent, 200


def putRegistrationAmfNon3gppAccess():
    return NoContent, 200


def patchRegistrationAmfNon3gppAccess(ueId, body):
    return NoContent, 200


def getRegistrationAmfNon3gppAccess(ueId):
    return NoContent, 200


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
    pprint(e)

# connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
client = MongoClient('mongodb://mongodb:27017/')
db = client.udm

with open(cwd + 'supi.json') as json_file:
    json_data = json.load(json_file)
    logging.info(json_data)
    db.subscription_data_sets.insert(json_data)


if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=8080, server='gevent')
