# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import phonenumbers
import base64
from dateutil import parser
from odoo import _, fields, models
from odoo.exceptions import ValidationError
from .sendeo_request import SendeoRequest


# SENDEO_STATUS_CODES = {
#     101: ("Kargo Sevk Emri Alındı", "İş Emri Alındı"),
#     102: ("Belge Düzenlendi", "Gönderi Oluşturuldu"),
#     103: ("Şube TM Yükleme", "Çıkış Şubesinden Hareket Etti"),
#     104: ("TM Şube İndirme", "Teslimat Noktasında"),
#     105: ("TM Hat Yükleme", "Hat Aracına Yüklendi"),
#     106: ("TM Hat İndirme", "Hat Aracından İndi"),
#     107: ("TM Şube Yükleme", "Transfer Merkezinden Şubeye Yüklendi"),
#     108: ("Şube TM İndirme", "Transfer Merkezine İndi"),
#     109: ("Şube Dağıtım Yükleme", "Dağıtıma Çıkarıldı"),
#     110: ("Şube Dağıtım İndirme", "Şube Dağıtım İndirme"),
#     111: ("Teslim Edildi", "Teslim Edildi"),
#     112: ("Alıcı Telefonu Yanlış", "Alıcı Telefonu Yanlış"),
#     113: ("İade Talebi", "İade Talebi"),
#     114: ("Alıcı Adresinde Yok", "Alıcı Adresinde Yok"),
#     115: ("Alıcı Adresi Yanlış", "Alıcı Adresi Yanlış"),
#     117: ("Hasarlı Gönderi", "Hasarlı Gönderi"),
#     118: ("Kayıp Kargo", "Kayıp Kargo"),
#     119: ("Devir", "Devir"),
#     120: ("Eksik Teslim Edildi", "Eksik Teslim Edildi"),
#     121: ("Dağıtım Alanı Dışında", "Dağıtım Alanı Dışında"),
#     122: ("Ödeme Tipi Kabul Edilmedi", "Ödeme Tipi Kabul Edilmedi"),
#     123: ("Randevulu Teslimat", "Randevulu Teslimat"),
#     124: ("Mobil Dağıtım Bölgesi", "Mobil Dağıtım Bölgesi"),
#     125: ("Eksik Kargo", "Eksik Kargo"),
#     126: ("Yönlendirme", "Yönlendirme"),
#     127: ("Hat Aracı Gecikmesi", "Hat Aracı Gecikmesi"),
#     128: ("Olumsuz Hava Koşulları", "Olumsuz Hava Koşulları"),
#     129: ("Taşıma Fiyatı Yüksek Bulundu", "Taşıma Fiyatı Yüksek Bulundu"),
#     130: ("Teslim Edilemedi", "Teslim edilemedi"),
#     131: ("İade Gönderi", "İade Edilen Gönderi"),
#     132: ("Ölçüm Tartım", "Ölçüm Tartım yapıldı"),
#     133: ("İptal Gönderi", "İptal Gönderi"),
#     134: ("İade Onay", "İade Talebine Onay Verildi"),
#     135: ("İş Emri İadesi", "İş Emri ile İade Edilen Gönderi"),
#     136: ("İade Red", "Müşteri tarafından red edildi"),
#     137: ("Randevulu Alım", "Müşteri Randevu Verdi"),
#     138: ("Gönderi Alındı", "Gönderi Alındı"),
#     139: ("İptal İş Emri", "İptal İş Emri"),
#     140: ("Kurye Teslimatta", "Kurye Teslimatta"),
#     141: ("Kurye Zimmete Aldı", "Kurye zimmete alma"),
#     142: ("Kurye Zimmetten Çıkardı", "Kurye zimmetten çıkarma"),
#     143: ("Kayıp Kargo", "Kayıp Kargo İş Emri"),
#     151: ("İade Olarak Teslim", "İade Olarak Teslim"),
# }

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("sendeo", "Sendeo")])

    sendeo_username = fields.Char(string="Username", help="Sendeo Username")
    sendeo_password = fields.Char(string="Password", help="Sendeo Password")

    sendeo_incoterm_id = fields.Many2one(
        comodel_name="account.incoterms",
        string="Default Incoterm",
        help="It will be overriden by the sale order one if it's specified.",
    )

    sendeo_default_packaging_id = fields.Many2one(
        comodel_name="product.packaging",
        string="Default Package Type",
        domain=[("package_carrier_type", "=", "sendeo")],
        help="If not delivery package or the package doesn't have defined the packaging"
             "it will default to this type",
    )

    def _get_sendeo_credentials(self):
        """Access key is mandatory for every request while group and user are
        optional"""
        credentials = {
            "prod": self.prod_environment,
            "username": self.sendeo_username,
            "password": self.sendeo_password,
        }
        return credentials

    def _sendeo_address(self, partner):
        """Sender address is the address of the company, required field.
        """
        return partner._display_address()

    def _sendeo_city_id(self, partner):
        """ Sendeo requires city ids without zeros. """
        return partner.state_id.code.lstrip('0')

    def _sendeo_phone_number(self, partner, priority='mobile'):
        """
        Sendeo requires phone number without spaces and country code.
        We use priority selector to handle two different phone numbers.
        :param partner: recordset res.partner
        :param priority: string
        :return: phone number without spaces and country code
        """
        priority_field = getattr(partner, priority)
        if priority_field:
            return phonenumbers.format_number(
                phonenumbers.parse(priority_field, partner.country_id.code or "TR"),
                phonenumbers.PhoneNumberFormat.E164).lstrip('+90')
        elif partner.phone or partner.mobile:
            return phonenumbers.format_number(
                phonenumbers.parse(partner.phone or partner.mobile, partner.country_id.code or "TR"),
                phonenumbers.PhoneNumberFormat.E164).lstrip('+90')
        else:
            raise ValidationError(_("%s\nPartner's phone number is missing."
                                    " It's a required field for dispatch."
                                    % partner.name))

    def _prepare_sendeo_products(self, picking):
        vals = {
            'products': [{
                'count': 3,
                'productCode': '',
                'description': '',
                'price': 1,
            }]
        }
        return vals

    def _prepare_sendeo_shipping(self, picking):
        """Convert picking values for Sendeo Kargo api
        :param picking record with picking to send
        :returns dict values for the connector
        """
        self.ensure_one()
        # We'll compose the request via some diferenced parts, like label settings,
        # address options, incoterms and so. There are lots of thing to take into
        # account to acomplish a properly formed request.
        vals = {}
        vals.update(
            {
                "deliveryType": 1,
                "referenceNo": picking.name,
                "senderAuthority": picking.company_id.name,
                "senderAddress": self._sendeo_address(picking.company_id.partner_id),
                "senderCityId": self._sendeo_city_id(picking.company_id.partner_id),
                "senderDistrictId": picking.company_id.partner_id.district_id.sendeo_code,
                "senderPhone": self._sendeo_phone_number(picking.company_id.partner_id, priority='phone'),
                "senderGSM": self._sendeo_phone_number(picking.company_id.partner_id, priority='mobile'),
                "senderEmail": picking.company_id.partner_id.email,
                "receiver": picking.partner_id.parent_id.name,
                "receiverAuthority": picking.partner_id.name,
                "receiverAddress": self._sendeo_address(picking.partner_id),
                "receiverCityId": self._sendeo_city_id(picking.partner_id),
                "receiverDistrictId": picking.partner_id.district_id.sendeo_code,
                "receiverPhone": self._sendeo_phone_number(picking.partner_id, priority='phone'),
                "receiverGSM": self._sendeo_phone_number(picking.partner_id, priority='mobile'),
                "receiverEmail": picking.partner_id.email,
                "paymentType": 1,
                "collectionType": 0,
                "collectionPrice": 0,
                "serviceType": 1,
                "barcodeLabelType": 2,  # Zebra ZPL
            }
        )
        product_array = self._prepare_sendeo_products(picking)
        vals.update(product_array)
        return vals

    def sendeo_send_shipping(self, pickings):
        """Send booking request to Sendeo
        :param pickings: A recordset of pickings
        :return list: A list of dictionaries although in practice it's
        called one by one and only the first item in the dict is taken. Due
        to this design, we have to inject vals in the context to be able to
        add them to the message.
        """
        sendeo_request = SendeoRequest(**self._get_sendeo_credentials())
        result = []
        for picking in pickings:
            vals = self._prepare_sendeo_shipping(picking)

            try:
                response = sendeo_request._set_delivery(vals)
            except Exception as e:
                raise e

            if not response:
                result.append(vals)
                continue
            vals["tracking_number"] = response.get("TrackingNumber")
            vals["exact_price"] = 0

            body = _("Sendeo Shipping barcode document")
            attachment = []
            barcode = response.get("Barcode")
            if barcode:
                attachment = [
                    (
                        "sendeo_etiket_{}.pdf".format(response.get("TrackingNumber")),
                        base64.b64decode(barcode),
                    )
                ]
            picking.message_post(body=body, attachments=attachment)
            result.append(vals)
        return result

    def sendeo_cancel_shipment(self, pickings):
        """Cancel the expedition
        :param pickings - stock.picking recordset
        :returns bool
        """
        sendeo_request = SendeoRequest(**self._get_sendeo_credentials())
        for picking in pickings.filtered("carrier_tracking_ref"):
            sendeo_request._cancel_shipment(picking.name, picking.carrier_tracking_ref)
            # picking.write({"carrier_tracking_ref": False,
            #                "tracking_state": False,
            #                "tracking_state_history": _('Cancelled')})
        return True

    def sendeo_get_tracking_link(self, picking):
        """Provide tracking link for the customer"""
        return (
                "https://sube.sendeo.com.tr/takip?ccode=%s&musref=%s"
                % (picking.carrier_tracking_ref, picking.name)
        )

    def _sendeo_status_codes(self, status_code):
        """
        Return the status code in Odoo delivery_state selection field format
        For more information, see the API documentation
        """
        if status_code in [101, 102]:
            return "shipping_recorded_in_carrier"
        elif status_code in [103, 105, 106, 107, 109]:
            return "in_transit"
        elif status_code in [133, 139, 136]:
            return "canceled_shipment"
        elif status_code in [112, 113, 114, 115, 117, 118, 119, 120, 121, 122, 125, 127, 128, 129, 130]:
            return "incidence"
        elif status_code in [111]:
            return "customer_delivered"
        else:
            return "warehouse_delivered"

    def sendeo_tracking_state_update(self, picking):
        """Tracking state update"""
        self.ensure_one()
        if not picking.carrier_tracking_ref:
            return
        sendeo_request = SendeoRequest(**self._get_sendeo_credentials())
        response = sendeo_request._get_tracking_states(picking.name, picking.carrier_tracking_ref)
        status_event_list = response.get("StatusHistories")
        picking.write(
            {
                "tracking_state_history": (
                    "\n".join(
                        "{} - [{}] {}".format(
                            parser.parse(t['StatusDate']).strftime("%d/%m/%Y %H:%M:%S"),
                            t['Status'],
                            t['Description'],
                        )
                        for t in status_event_list

                    )
                ),
                "tracking_state": response['StateText'],
                "delivery_state": self._sendeo_status_codes(response['State']),
            }
        )
        return True

    def sendeo_carrier_get_label(self, picking):
        """Generate label for picking
        :returns cargo barcode label
        """
        picking.ensure_one()
        tracking_ref = picking.carrier_tracking_ref
        if picking.delivery_type != "sendeo" or not tracking_ref:
            return

        sendeo_request = SendeoRequest(**self._get_sendeo_credentials())
        response = sendeo_request._shipping_label(tracking_ref)
        barcode = response.get("Barcode")
        if not barcode:
            return False
        label = base64.b64decode(barcode)
        label_name = "aras_etiket_{}.pdf".format(tracking_ref)
        picking.message_post(
            body=(_("Sendeo etiket: %s") % tracking_ref),
            attachments=[(label_name, label)],
        )
        return label

    def sendeo_rate_shipment(self, order):
        """There's no public API so another price method should be used."""
        raise NotImplementedError(
            _(
                "Sendeo API doesn't provide methods to compute delivery "
                "rates, so you should relay on another price method instead or "
                "override this one in your custom code."
            )
        )
