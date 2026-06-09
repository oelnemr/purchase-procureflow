# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseProcureflow(http.Controller):
#     @http.route('/purchase_procureflow/purchase_procureflow', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_procureflow/purchase_procureflow/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_procureflow.listing', {
#             'root': '/purchase_procureflow/purchase_procureflow',
#             'objects': http.request.env['purchase_procureflow.purchase_procureflow'].search([]),
#         })

#     @http.route('/purchase_procureflow/purchase_procureflow/objects/<model("purchase_procureflow.purchase_procureflow"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_procureflow.object', {
#             'object': obj
#         })

