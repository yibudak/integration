# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import psycopg2
import re
from odoo import api, fields, models, registry, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from .garanti_connector import GarantiConnector
from odoo.addons.payment_garanti.const import (
    TEST_URL,
    PROD_URL,
    PROVISION_URL,
    CURRENCY_CODES,
)

_logger = logging.getLogger(__name__)


class PaymentAcquirerGaranti(models.Model):
    _inherit = "payment.acquirer"

    provider = fields.Selection(selection_add=[("garanti", "Garanti")])
    debug_logging = fields.Boolean(
        "Debug logging", help="Log requests in order to ease debugging"
    )

    garanti_merchant_id = fields.Char(
        string="Merchant ID",
        help="Merchant ID provided by Garanti Sanal Pos",
        required_if_provider="garanti",
        groups="base.group_user",
    )

    garanti_terminal_id = fields.Char(
        string="Terminal ID",
        help="Terminal ID provided by Garanti Sanal Pos",
        required_if_provider="garanti",
        groups="base.group_user",
    )

    garanti_prov_user = fields.Char(
        string="Provision User",
        help="Provision User provided by Garanti Sanal Pos",
        required_if_provider="garanti",
        groups="base.group_user",
    )

    garanti_prov_password = fields.Char(
        string="Provision Password",
        help="Provision Password provided by Garanti Sanal Pos",
        required_if_provider="garanti",
        groups="base.group_user",
    )

    garanti_store_key = fields.Char(
        string="Store Key",
        help="Store Key provided by Garanti Sanal Pos",
        required_if_provider="garanti",
        groups="base.group_user",
    )

    def toggle_debug(self):
        for c in self:
            c.debug_logging = not c.debug_logging

    def log_xml(self, xml_string, func):
        self.ensure_one()

        if self.debug_logging:
            db_name = self._cr.dbname
            # Use a new cursor to avoid rollback that could be caused by an upper method
            try:
                db_registry = registry(db_name)
                with db_registry.cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    IrLogging = env["ir.logging"]
                    created_log = IrLogging.sudo().create(
                        {
                            "name": "payment.acquirer",
                            "type": "server",
                            "dbname": db_name,
                            "level": "DEBUG",
                            "message": str(xml_string),
                            "path": self.provider,
                            "func": func,
                            "line": 1,
                        }
                    )
                    """
                    Save the error message to the database, so we can handle
                    the error message better.
                    """
                    error_obj = env["payment.provider.error"].sudo()
                    error_code = False
                    error_message = False
                    sys_error_message = False
                    # It means that the request has been made by return endpoint
                    if isinstance(xml_string, dict):
                        error_code = xml_string.get("mdstatus", False)
                        error_message = xml_string.get("mderrormessage", False)
                    else:
                        reason_code = re.findall(
                            r"<ReasonCode>(\d+)</ReasonCode>", xml_string
                        )
                        xml_msg = re.findall(r"<ErrorMsg>(.*?)</ErrorMsg>", xml_string)
                        sys_error_msg = re.findall(
                            r"<SysErrMsg>(.*?)</SysErrMsg>", xml_string
                        )
                        if reason_code and xml_msg:
                            error_code = reason_code[0]
                            error_message = xml_msg[0]
                            if sys_error_msg:
                                sys_error_message = sys_error_msg[0]

                    if (
                        error_code
                        and error_message
                        and not error_obj.search_read(
                            [("full_message", "=", f"{error_code}: {error_message}")],
                            limit=1,
                        )
                    ):
                        error_record = error_obj.create(
                            {
                                "error_code": error_code,
                                "sys_error_message": sys_error_message,
                                "error_message": error_message,
                                "log_id": created_log.id,
                            }
                        )
                        error_record._onchange_error_message()
            except psycopg2.Error:
                pass

    @api.model
    def garanti_s2s_form_process(self, data):
        values = {
            "cc_number": data.get("cc_number"),
            "cc_holder_name": data.get("cc_holder_name"),
            "cc_expiry": data.get("cc_expiry"),
            "cc_cvc": data.get("cc_cvc"),
            "cc_brand": data.get("cc_brand"),
            "acquirer_id": int(data.get("acquirer_id")),
            "partner_id": int(data.get("partner_id")),
        }
        payment_method = self.env["payment.token"].sudo().create(values)
        return payment_method

    def _garanti_get_api_url(self):
        """Return the API URL according to the provider state.

        Note: self.ensure_one()

        :return: The API URL
        :rtype: str
        """
        self.ensure_one()
        if self.environment == "prod":
            return PROD_URL
        else:
            return TEST_URL

    def _garanti_get_prov_url(self):
        """
        This method is used to get the provision url
        :return: The provision url
        """
        self.ensure_one()
        return PROVISION_URL

    def _garanti_get_mode(self):
        """
        This method is used to get the mode of the transaction
        :return: The mode of the transaction
        """
        self.ensure_one()
        return self.environment.upper()

    def _garanti_get_company_name(self):
        """
        This method is used to get the company name
        :return: The company name
        """
        self.ensure_one()
        return self.company_id.name

    def _garanti_get_currency_code(self, currency, tx):
        """
        This method is used to get the currency code
        :param currency: The currency id
        :return: The currency code
        """
        currency_id = self.env["res.currency"].browse(currency)
        if currency_id and currency_id.name in CURRENCY_CODES:
            return CURRENCY_CODES[currency_id.name]
        else:
            return "949"

    def _garanti_format_card_number(self, card_number):
        """
        This method is used to format the card number
        :param card_number: The card number
        :return: The formatted card number
        """
        card_number = card_number.replace(" ", "")
        if len(card_number) in [15, 16] and card_number.isdigit():
            return card_number
        else:
            raise ValidationError(_("Card number is not valid."))

    def _garanti_get_return_url(self):
        """
        This method is used to get the return url for the Garanti API
        :return: The return url
        """
        self.ensure_one()
        return (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            + "/payment/garanti/return"
        )

    def _garanti_make_payment_request(self, tx, amount, card_args, client_ip):
        """
        This method is used to make a payment request to the Garanti Endpoint
        :param tx: The transaction
        :param amount: The amount of the transaction
        :param currency: The currency of the transaction
        """
        self.ensure_one()
        connector = GarantiConnector(
            acquirer=self,
            tx=tx,
            amount=amount,
            card_args=card_args,
            client_ip=client_ip,
        )
        if tx.partner_id.country_id and tx.partner_id.country_id.code != "TR":
            notification_data = connector._build_notification_data_for_non_3ds_payment(
                card_args=card_args
            )
            tx._garanti_form_validate(notification_data)
            return {
                "status": "success",
                "method": "non_3ds",
            }
        else:
            method, resp = connector._garanti_make_payment_request()
            return {
                "status": "success",
                "method": method,
                "response": resp,
            }

    def _garanti_validate_card_args(self, card_args):
        """
        Validation method for credit/debit card information
        :param card_args: The card information
        :return: error message if there is any error
        """
        error = ""
        card_number = card_args.get("card_number")
        card_cvv = card_args.get("card_cvv")
        if not card_number or len(card_number) < 15:
            error += _("Card number is not valid.\n")

        if not card_cvv or len(card_cvv) < 3:
            error += _("Card CVV is not valid.\n")

        if not card_args.get("card_name"):
            error += _("Card name is not valid.\n")

        if not card_args.get("card_valid_month") or not card_args.get(
            "card_valid_year"
        ):
            error += _("Card expiration date is not valid.\n")
        return error
