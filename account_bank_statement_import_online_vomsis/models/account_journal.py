# Copyright 2022 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    vomsis_account_id = fields.Integer('VOMSIS Account ID')
