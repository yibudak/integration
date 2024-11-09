# -*- coding: utf-8 -*-
{
    'name': "FedEx Integration",

    'summary': """
        A module to integrate FedEx Delivery, Tracking, and Rates into Odoo """,

    # 'description': """
    #     Long description of module's purpose
    # """,

    'sequence': -10,

    'application': True,

    'author': "Yousef Sheta",
    'website': "https://github.com/TrueYouface",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Delivery',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'delivery_integration_base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/delivery_fedex_view.xml',
        # 'views/stock_picking_views.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
