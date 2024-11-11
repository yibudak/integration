# Copyright 2021 Studio73 - Ethan Hildick <ethan@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    fedex_tracking_number = fields.Char(
        string='Tracking Number',
        readonly=True
    )

