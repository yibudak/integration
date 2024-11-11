# Copyright 2024 Yousef Sheta (https://github.com/TrueYouface)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from .fedex_request import FedexRequest
import requests
import json
import phonenumbers
from odoo.exceptions import ValidationError


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("fedex", "Fedex")])

    fedex_grant_type = fields.Selection(
        string="Grant Type",
        selection=[
            ("client_credentials", "client_credentials"),
            ("csp_credentials", "csp_credentials"),
            ("client_pc_credentials", "client_pc_credentials"),
        ],
    )
    fedex_client_id = fields.Char(string="Client ID")
    fedex_client_secret = fields.Char(string="Secret ID")
    fedex_account_number = fields.Char(
        string="FedEx Account Number",
    )
    # fedex_default_package_type_id = fields.Many2one(
    #     string="FedEx Package Type",
    #     comodel_name="stock.package.type",
    # )
    fedex_developer_key = fields.Char(string="Developer Key")
    fedex_developer_password = fields.Char(string="Password")
    fedex_document_stock_type = fields.Selection(
        string="Commercial Invoice Type",
        selection=[
            ("PAPER_4X6", "PAPER_4X6"),
            ("PAPER_4X6.75", "PAPER_4X6.75"),
            ("PAPER_4X8", "PAPER_4X8"),
            ("PAPER_4X9", "PAPER_4X9"),
            ("PAPER_7X4.75", "PAPER_7X4.75"),
            ("PAPER_8.5X11_BOTTOM_HALF_LABEL", "PAPER_8.5X11_BOTTOM_HALF_LABEL"),
            ("PAPER_8.5X11_TOP_HALF_LABEL", "PAPER_8.5X11_TOP_HALF_LABEL"),
            ("PAPER_LETTER", "PAPER_LETTER"),
            ("STOCK_4X6", "STOCK_4X6"),
            ("STOCK_4X6.75", "STOCK_4X6.75"),
            ("STOCK_4X6.75_LEADING_DOC_TAB", "STOCK_4X6.75_LEADING_DOC_TAB"),
            ("STOCK_4X6.75_TRAILING_DOC_TAB", "STOCK_4X6.75_TRAILING_DOC_TAB"),
            ("STOCK_4X8", "STOCK_4X8"),
            ("STOCK_4X9", "STOCK_4X9"),
            ("STOCK_4X9_LEADING_DOC_TAB", "STOCK_4X9_LEADING_DOC_TAB"),
            ("STOCK_4X9_TRAILING_DOC_TAB", "STOCK_4X9_TRAILING_DOC_TAB"),
        ],
    )
    fedex_dropoff_type = fields.Selection(
        string="FedEx Drop-Off Type",
        selection=[
            ("BUSINESS_SERVICE_CENTER", "BUSINESS_SERVICE_CENTER"),
            ("DROP_BOX", "DROP_BOX"),
            ("REGULAR_PICKUP", "REGULAR_PICKUP"),
            ("REQUEST_COURIER", "REQUEST_COURIER"),
            ("STATION", "STATION"),
        ],
    )
    # fedex_duty_payment = fields.Selection(
    #     string="Fedex Duty Payment",
    #     selection=[
    #         ("SENDER", "Sender"),
    #         ("RECIPIENT", "Recipient"),
    #     ]
    # )
    fedex_extra_data_rate_request = fields.Text(
        string="Extra Data for Rate",
        help="""The extra data in FedEx is organized like the inside of a json file.
        This functionality is advanced/technical and should only be used if you know what you are doing.
        
        Example of valid value: ```
        "ShipmentDetails": {"Pieces": {"Piece": {"AdditionalInformation": "extra info"}}}
        ```
        
        With the above example, the AdditionalInformation of each piece will be updated.
        More info on https://www.fedex.com/en-us/developer/web-services/process.html#documentation""",
    )
    fedex_extra_data_Return_request = fields.Text(
        string="Extra Data for Return",
        help="""The extra data in FedEx is organized like the inside of a json file.
        This functionality is advanced/technical and should only be used if you know what you are doing.
        
        Example of valid value: ```
        "ShipmentDetails": {"Pieces": {"Piece": {"AdditionalInformation": "extra info"}}}
        ```
        
        With the above example, the AdditionalInformation of each piece will be updated.
        More info on https://www.fedex.com/en-us/developer/web-services/process.html#documentation""",
    )
    fedex_extra_data_ship_request = fields.Text(
        string="Extra Data for Ship",
        help="""The extra data in FedEx is organized like the inside of a json file.
        This functionality is advanced/technical and should only be used if you know what you are doing.
        
        Example of valid value: ```
        "ShipmentDetails": {"Pieces": {"Piece": {"AdditionalInformation": "extra info"}}}
        ```
        
        With the above example, the AdditionalInformation of each piece will be updated.
        More info on https://www.fedex.com/en-us/developer/web-services/process.html#documentation""",
    )
    fedex_label_file_type = fields.Selection(
        string="FEDEX Label File Type",
        selection=[
            ("PDF", "PDF"),
            ("EPL2", "EPL2"),
            ("PNG", "PNG"),
            ("ZPLII", "ZPLII"),
        ],
    )
    fedex_label_stock_type = fields.Selection(
        string="Label Type",
        selection=[
            ("PAPER_4X6", "PAPER_4X6"),
            ("PAPER_4X6.75", "PAPER_4X6.75"),
            ("PAPER_4X8", "PAPER_4X8"),
            ("PAPER_4X9", "PAPER_4X9"),
            ("PAPER_7X4.75", "PAPER_7X4.75"),
            ("PAPER_8.5X11_BOTTOM_HALF_LABEL", "PAPER_8.5X11_BOTTOM_HALF_LABEL"),
            ("PAPER_8.5X11_TOP_HALF_LABEL", "PAPER_8.5X11_TOP_HALF_LABEL"),
            ("PAPER_LETTER", "PAPER_LETTER"),
            ("STOCK_4X6", "STOCK_4X6"),
            ("STOCK_4X6.75", "STOCK_4X6.75"),
            ("STOCK_4X6.75_LEADING_DOC_TAB", "STOCK_4X6.75_LEADING_DOC_TAB"),
            ("STOCK_4X6.75_TRAILING_DOC_TAB", "STOCK_4X6.75_TRAILING_DOC_TAB"),
            ("STOCK_4X8", "STOCK_4X8"),
            ("STOCK_4X9", "STOCK_4X9"),
            ("STOCK_4X9_LEADING_DOC_TAB", "STOCK_4X9_LEADING_DOC_TAB"),
            ("STOCK_4X9_TRAILING_DOC_TAB", "STOCK_4X9_TRAILING_DOC_TAB"),
        ],
    )
    fedex_locations_radius_value = fields.Integer(
        string="Fedex Locations Radius", help="Maximum locations distance radius."
    )
    fedex_locations_radius_unit = fields.Many2one(
        string="Fedex Locations Radius Unit", comodel_name="uom.uom"
    )
    fedex_locations_radius_unit_name = fields.Char(string="Fedex Radius Unit Name")
    fedex_meter_number = fields.Char(string="Meter Number")
    fedex_saturday_delivery = fields.Boolean(
        string="FedEx Saturday Delivery",
        default=False,
        help="""Special service:Saturday Delivery, can be requested on following days.
        Thursday:
        1.FEDEX_2_DAY.
        Friday:
        1.PRIORITY_OVERNIGHT.
        2.FIRST_OVERNIGHT.
        3.INTERNATIONAL_PRIORITY.
        (To Select Countries)""",
    )
    fedex_service_type = fields.Selection(
        string="Fedex Service Type",
        selection=[
            ("INTERNATIONAL_ECONOMY", "INTERNATIONAL_ECONOMY"),
            ("INTERNATIONAL_PRIORITY", "INTERNATIONAL_PRIORITY"),
            ("FEDEX_INTERNATIONAL_PRIORITY", "FEDEX_INTERNATIONAL_PRIORITY"),
            (
                "FEDEX_INTERNATIONAL_PRIORITY_EXPRESS",
                "FEDEX_INTERNATIONAL_PRIORITY_EXPRESS",
            ),
            ("FEDEX_GROUND", "FEDEX_GROUND"),
            ("FEDEX_2_DAY", "FEDEX_2_DAY"),
            ("FEDEX_2_DAY_AM", "FEDEX_2_DAY_AM"),
            ("FEDEX_3_DAY_FREIGHT", "FEDEX_3_DAY_FREIGHT"),
            ("FIRST_OVERNIGHT", "FIRST_OVERNIGHT"),
            ("PRIORITY_OVERNIGHT", "PRIORITY_OVERNIGHT"),
            ("STANDARD_OVERNIGHT", "STANDARD_OVERNIGHT"),
            ("FEDEX_NEXT_DAY_EARLY_MORNING", "FEDEX_NEXT_DAY_EARLY_MORNING"),
            ("FEDEX_NEXT_DAY_MID_MORNING", "FEDEX_NEXT_DAY_MID_MORNING"),
            ("FEDEX_NEXT_DAY_AFTERNOON", "FEDEX_NEXT_DAY_AFTERNOON"),
            ("FEDEX_NEXT_DAY_END_OF_DAY", "FEDEX_NEXT_DAY_END_OF_DAY"),
            ("FEDEX_EXPRESS_SAVER", "FEDEX_EXPRESS_SAVER"),
            ("FEDEX_REGIONAL_ECONOMY", "FEDEX_REGIONAL_ECONOMY"),
            ("FEDEX_FIRST", "FEDEX_FIRST"),
            ("FEDEX_PRIORITY_EXPRESS", "FEDEX_PRIORITY_EXPRESS"),
            ("FEDEX_PRIORITY", "FEDEX_PRIORITY"),
            ("FEDEX_PRIORITY_EXPRESS_FREIGHT", "FEDEX_PRIORITY_EXPRESS_FREIGHT"),
            ("FEDEX_PRIORITY_FREIGHT", "FEDEX_PRIORITY_FREIGHT"),
            ("FEDEX_ECONOMY_SELECT", "FEDEX_ECONOMY_SELECT"),
            ("FEDEX_INTERNATIONAL_CONNECT_PLUS", "FEDEX_INTERNATIONAL_CONNECT_PLUS"),
        ],
    )
    fedex_use_locations = fields.Boolean(
        string="Use Fedex Locations",
        help="Allows the ecommerce user to choose a pick-up point as delivery address.",
    )
    fedex_weight_unit = fields.Selection(
        string="Fedex Weight Unit", default="LB", selection=[("KG", "KG"), ("LB", "LB")]
    )
    fedex_label_format = fields.Selection(
        string="Label Format",
        selection=[("URL_ONLY", "URL_ONLY"), ("LABEL", "LABEL")],
    )
    fedex_pickup_type = fields.Selection(
        string="Pick-up Type",
        selection=[
            ("CONTACT_FEDEX_TO_SCHEDULE", "CONTACT_FEDEX_TO_SCHEDULE"),
            ("DROPOFF_AT_FEDEX_LOCATION", "DROPOFF_AT_FEDEX_LOCATION"),
            ("USE_SCHEDULED_PICKUP", "USE_SCHEDULED_PICKUP"),
        ],
    )
    fedex_package_type = fields.Selection(
        string="Fedex Package Type",
        selection=[
            ("YOUR_PACKAGING", "YOUR_PACKAGING"),
            ("FEDEX_ENVELOPE", "FEDEX_ENVELOPE"),
            ("FEDEX_BOX", "FEDEX_BOX"),
            ("FEDEX_SMALL_BOX", "FEDEX_SMALL_BOX"),
            ("FEDEX_MEDIUM_BOX", "FEDEX_MEDIUM_BOX"),
            ("FEDEX_LARGE_BOX", "FEDEX_LARGE_BOX"),
            ("FEDEX_EXTRA_LARGE_BOX", "FEDEX_EXTRA_LARGE_BOX"),
            ("FEDEX_10KG_BOX", "FEDEX_10KG_BOX"),
            ("FEDEX_25KG_BOX", "FEDEX_25KG_BOX"),
            ("FEDEX_PAK", "FEDEX_PAK"),
            ("FEDEX_TUBE", "FEDEX_TUBE"),
        ],
    )

    def shorten_address(self, street, max_length=35):
        # TODO: remove this function and just split the address for each 35 characters.
        # Step 1: Define common abbreviations
        abbreviations = {
            "Suite": "Ste",
            "Avenue": "Ave",
            "Boulevard": "Blvd",
            "Street": "St",
            "Drive": "Dr",
            "Road": "Rd",
            "Court": "Ct",
            "Place": "Pl",
        }

        # Step 2: Apply abbreviations
        for long, short in abbreviations.items():
            street = street.replace(long, short)

        # Step 3: Trim to the maximum length
        if len(street) > max_length:
            street = street[:max_length].rstrip()  # Remove trailing spaces

        return street

    def _fedex_payment_type(self):
        if self.payment_type == "sender_pays":
            return "SENDER"
        else:
            return "RECIPIENT"

    def get_shipment_weight(self, picking):
        weight = picking.picking_total_weight
        val = weight * 2.22
        return val

    def _fedex_phone_number(self, partner, field, priority="mobile"):
        priority_field = getattr(partner, priority)
        number = priority_field or (partner.phone or partner.mobile)
        if number:
            try:
                parsed_number = phonenumbers.parse(
                    number, partner.country_id.code or None
                )
                # Extract number and extension
                return getattr(parsed_number, field)
            except ValidationError as e:
                raise ValidationError(_("Error parsing phone number: %s" % str(e)))
        else:
            raise ValidationError(
                _(
                    "%s\nPartner's phone number is missing."
                    " It's a required field for dispatch." % partner.name
                )
            )

    def _prepare_fedex_shipping(self, picking):
        vals = {
            "accountNumber": {"value": self.fedex_account_number},
            "labelResponseOptions": self.fedex_label_format,
            "requestedShipment": {
                "shipper": {
                    "contact": {
                        "companyName": picking.company_id.partner_id.name,
                        "phoneNumber": self._fedex_phone_number(
                            picking.company_id.partner_id, "national_number"
                        ),
                        "emailAddress": picking.company_id.partner_id.email,
                        # "phoneExtension": self._fedex_phone_number(
                        #     picking.company_id.partner_id, "extension"
                        # )
                    },
                    "address": {
                        "countryCode": picking.company_id.country_id.code,
                        "city": picking.company_id.partner_id.city,
                        "streetLines": [
                            self.shorten_address(picking.company_id.partner_id.street)
                        ],
                        "postalCode": picking.company_id.zip,
                    },
                },
                "recipients": [
                    {
                        "contact": {
                            "personName": picking.partner_id.name,
                            "phoneNumber": self._fedex_phone_number(
                                picking.partner_id, "national_number"
                            ),
                            "emailAddress": picking.partner_id.email,
                            # "phoneExtension": self._fedex_phone_number(
                            #     picking.partner_id, "extension"
                            # )
                        },
                        "address": {
                            "countryCode": picking.partner_id.country_id.code,
                            "city": picking.partner_id.city,
                            "stateOrProvinceCode": picking.partner_id.state_id.code,
                            "streetLines": [
                                self.shorten_address(picking.partner_id.street)
                            ],
                            "postalCode": picking.partner_id.zip,
                        },
                    }
                ],
                "pickupType": self.fedex_pickup_type,
                "serviceType": self.fedex_service_type,
                "packagingType": self.fedex_package_type,
                "totalWeight": self.get_shipment_weight(picking),
                "shippingChargesPayment": {"paymentType": self._fedex_payment_type()},
                "labelSpecification": {
                    "imageType": self.fedex_label_file_type,
                    "labelStockType": self.fedex_label_stock_type,
                },
                "customsClearanceDetail": {
                    "dutiesPayment": {"paymentType": self._fedex_payment_type()},
                    "commodities": [
                        {
                            "description": picking.note,
                            "countryOfManufacture": picking.company_id.country_id.code,
                            "quantity": picking.carrier_package_count,
                            "quantityUnits": "PCS",
                            # TODO: Must convert all the prices to the currency of the FedEx's default.
                            "unitPrice": {
                                "amount": 100,  # TODO: change me
                                "currency": picking.shipping_currency_id.name,  # TODO: change me
                            },
                            "customsValue": {
                                "amount": 100,#picking.carrier_price, # TODO: not correct, maybe we should add a new field for this.
                                "currency": picking.shipping_currency_id.name,
                            },
                            "weight": {
                                "units": self.fedex_weight_unit,
                                "value": picking.weight,
                            },
                        }
                    ],
                },
                "requestedPackageLineItems": [
                    {
                        "weight": {
                            "units": self.fedex_weight_unit,
                            "value": picking.weight,
                        }
                    }
                ],
            },
        }
        return vals

    def fedex_send_shipping(self, pickings):
        # url = "https://apis-sandbox.fedex.com/ship/v1/shipments"
        # headers = {
        #     "Content-Type": "application/json",
        #     "X-locale": "en_US",
        #     "Authorization": "Bearer " + self.get_fedex_credentials(),
        # }
        fedex_request = FedexRequest(
            prod_environment=False,
            grant_type=self.fedex_grant_type,
            api_key=self.fedex_client_id,
            secret_key=self.fedex_client_secret,
            account_number=self.fedex_account_number,
        )

        result = []
        for picking in pickings:
            payload = self._prepare_fedex_shipping(picking)
            response = fedex_request.shipment(payload)
            response_data = response.json()
            if response_data["errors"]:
                break
            else:
                # Extract the masterTrackingNumber
                master_tracking_number = response_data["output"]
        return True
