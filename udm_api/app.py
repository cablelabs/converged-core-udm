#!/usr/bin/env python3
import logging
import os
from pprint import pprint

import connexion
from connexion import NoContent
from pymongo import MongoClient

cwd = os.getcwd()


def getSupiById(supi, dataset_names=None):
    pprint(supi)
    pprint(dataset_names)
    return NoContent, 200


def getSupiNssai():
    return NoContent, 200


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
# pprint(cwd)
# spec = 'file:///' + cwd + '/openapi/'
# pprint(spec)
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

if __name__ == '__main__':
    # run our standalone gevent server
    try:
        app.run(port=8080, server='gevent')
    except Exception as e:
        pprint(e)
        pprint(e.with_traceback())