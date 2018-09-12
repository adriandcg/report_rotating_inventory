# -*- coding: utf-8 -*-
{
    'name': "Report Rotating Inventory",

    'summary': """
       This report calculate the rotating inventory""",

    'description': """
   Rotating inventory by date range
    """,

    'author': "Adrián de la Cruz",
    'website': "http://www.provem.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Warehouse',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','product','stock_account'],
    # always loaded
    'data': [
        'wizard/wizard_report_rotating_inventory.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
