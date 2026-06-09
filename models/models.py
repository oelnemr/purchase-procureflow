# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class purchase_procureflow(models.Model):
#     _name = 'purchase_procureflow.purchase_procureflow'
#     _description = 'purchase_procureflow.purchase_procureflow'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

