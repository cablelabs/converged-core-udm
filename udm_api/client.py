#!/usr/bin/env python3
import logging
import connexion


def call_me(body):
    logging.info('Recived Notifcation')
    logging.info(body)
    return connexion.NoContent, 204

logging.basicConfig(level=logging.INFO)
spec = '/openapi/'
try:
    app = connexion.App(__name__, specification_dir=spec)
    app.add_api('client.yaml')
    application = app.app
except Exception as e:
    logging.error(e)

if __name__ == '__main__':
    # run our standalone gevent server
    app.run(port=8080, server='gevent')