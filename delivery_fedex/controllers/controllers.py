# -*- coding: utf-8 -*-
# from odoo import http


# class ModuleTemplate1(http.Controller):
#     @http.route('/module_template_1/module_template_1', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/module_template_1/module_template_1/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('module_template_1.listing', {
#             'root': '/module_template_1/module_template_1',
#             'objects': http.request.env['module_template_1.module_template_1'].search([]),
#         })

#     @http.route('/module_template_1/module_template_1/objects/<model("module_template_1.module_template_1"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('module_template_1.object', {
#             'object': obj
#         })
