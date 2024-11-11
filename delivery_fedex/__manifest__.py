# Copyright 2024 Ahmet Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Delivery FedEx",
    "summary": "Delivery Carrier implementation for FedEx API",
    "version": "13.0.1.1.0",
    "category": "Stock",
    "website": "https://github.com/odoo-turkey",
    "author": "Yousef Sheta, Ahmet Yiğit Budak",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["delivery_integration_base"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "views/delivery_fedex_view.xml",
        # 'report/yurtici_carrier_label.xml',
        # 'report/yurtici_sms_template.xml',
        # 'report/reports.xml',
    ],

}
