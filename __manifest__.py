# -*- coding: utf-8 -*-
{
    "name": "Purchase ProcureFlow",
    "summary": "Streamline procurement requests, approvals, and purchasing workflows",
    "description": "",
    "author": "omarelnemr",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Purchases",
    "version": "17.0.1.0.0",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "purchase",
        "hr",
    ],
    # always loaded
    "data": [
        # 'security/ir.model.access.csv',
        "views/views.xml",
        "views/templates.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
