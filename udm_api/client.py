#!/usr/bin/env python3
import logging
import connexion
from time import sleep
import requests
import urllib3
import json
import os


def post(udm, body):
    r = requests.post(udm, json=body, verify=False)
    if r.status_code == 201 or r.status_code == 200 or r.status_code == 204:
        logging.info('Success')
        return r.json()
    else:
        logging.error('Error on Post ' + str(r.status_code))
        temp = r.json()
        if body.get('Name') is not None:
            raise Exception(body['Name'],
                            str(temp['Messages'][0]))
        else:
            raise Exception(body['Addr'],
                            str(temp['Messages'][0]))

def call_me(body):
    logging.info('Recived Notifcation')
    logging.info(body)
    return connexion.NoContent, 204

urllib3.disable_warnings()
cwd = os.getcwd()

logging.basicConfig(level=logging.INFO)
spec = '/openapi/'

try:
    app = connexion.App(__name__, specification_dir=spec)
    app.add_api('client.yaml')
    application = app.app
except Exception as e:
    logging.error(e)

# sleep(20)
# with open(cwd + 'sdm.json') as json_file:
#     json_data = json.load(json_file)
#     monitoredResourceUri = json_data['monitoredResourceUri'][0]
#     udm = 'http://udm:8080' + monitoredResourceUri + '/sdm-subscriptions'
#     post(udm, json_data)

if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=8080, server='gevent')

