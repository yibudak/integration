# Copyright 2024 Yousef Sheta (https://github.com/TrueYouface)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _
from odoo.exceptions import ValidationError
import requests, json

# logger = logging.getLogger(__name__)

FEDEX_API_URL = {
    "test": "https://apis-sandbox.fedex.com",
    "prod": "https://apis.fedex.com",
}


class FedexRequest(object):
    def __init__(
        self,
        prod_environment,
        grant_type,
        api_key,
        secret_key,
        account_number,
    ):
        self.grant_type = grant_type
        self.api_key = api_key
        self.secret_key = secret_key
        self.account_number = account_number
        if prod_environment:
            self.api_url = FEDEX_API_URL["prod"]
        else:
            self.api_url = FEDEX_API_URL["test"]
        self.access_token = self._get_access_token()

    def _process_reply(self, path, vals, content_type, extra_headers={}):
        """This function is created to catch the error info we need to make a
        raw_response request and the extract the error codes from the response."""
        try:
            headers = {"Content-Type": content_type, **extra_headers}
            response = requests.post(
                self.api_url + path,
                data=vals,
                headers=headers,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise ValidationError(
                _(
                    "Error in the request to the Fedex API. This is the "
                    "thrown message:\n\n"
                    "[%s]\n"
                    "%s - %s" % (e, e.__class__.__name__, e)
                )
            )
        return response.json()

    def _get_access_token(self):
        path = "/oauth/token"
        vals = {
            "grant_type": self.grant_type,
            "client_id": self.api_key,
            "client_secret": self.secret_key,
        }
        response = self._process_reply(path, vals, "application/x-www-form-urlencoded")
        return response["access_token"]

    def shipment(self, payload):
        path = "/ship/v1/shipments"
        extra_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-locale": "en_US",
        }
        content_type = "application/json"
        response = self._process_reply(
            path, json.dumps(payload), content_type, extra_headers
        )
        return response
