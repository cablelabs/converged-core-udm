#!/usr/bin/env python3
import logging

import connexion
from connexion import NoContent


def getSupiById(supi):
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


def patchRegistrationAmfNon3gppAccess():
    return NoContent, 200


def getRegistrationAmfNon3gppAccess(ueId):
    return NoContent, 200


logging.basicConfig(level=logging.INFO)
app = connexion.App(__name__, specification_dir='openapi/')
app.add_api('TS29503_Nudm_UECM.yaml')
app.add_api('TS29503_Nudm_SDM.yaml')

# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=8080, server='gevent')
