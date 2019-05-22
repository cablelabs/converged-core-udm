import unittest

import requests


class TestApi(unittest.TestCase):

    def test_get_example(self):

        response = requests.get("http://localhost:8080/nudm-uecm/v1/abc123/registrations/amf-non-3gpp-access")

        self.assertEqual(200, response.status_code)
        self.assertEqual("", response.content.decode())
