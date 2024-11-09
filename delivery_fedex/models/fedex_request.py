# Copyright 2024 Yousef Sheta (https://github.com/TrueYouface)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
import requests, json

# logger = logging.getLogger(__name__)

FEDEX_API_URL = {
    "test": "https://apis-sandbox.fedex.com",
    "prod": "https://eschenker.dbschenker.com",
}


class FedexRequest:

    def __init__(self):

        return



    def _shipping_api_credentials(self):
        credentials = {"applicationArea": {"accessKey": self.access_key}}
        if self.user:
            credentials["applicationArea"]["userId"] = self.user
        if self.group_id:
            credentials["applicationArea"]["groupId"] = self.group_id
        return credentials