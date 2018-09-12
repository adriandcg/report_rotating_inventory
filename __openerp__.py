# -*- coding: utf-8 -*-
{
    'name': "Reporte Inventario Rotativo",

    'summary': """
       Reporte que calcula el inventario rotativo dado un rango de fechas""",

    'description': """
   Inventario Rotativo por rango de fecha
    """,

    'author': "Adrián de la Cruz",
    'website': "http://www.provem.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',

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