# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = 'shopinvader.backend'

    @api.model
    def _get_default_model(self):
        domain = self.env['se.index']._get_model_domain()
        models = self.env['ir.model'].search(domain)
        return models

    se_backend_id = fields.Many2one(
        'se.backend',
        'Search Engine Backend')
    index_ids = fields.One2many(
        'se.index',
        related='se_backend_id.index_ids',
    )

    @api.multi
    def force_recompute_all_binding_index(self):
        self.mapped('se_backend_id.index_ids').force_recompute_all_binding()
        return True

    @api.multi
    def force_batch_export_index(self):
        for index in self.mapped('se_backend_id.index_ids'):
            index.force_batch_export()
        return True

    @api.multi
    def clear_index(self):
        for index in self.mapped('se_backend_id.index_ids'):
            index.clear_index()
        return True

    @api.multi
    def add_misssing_index(self):
        self.ensure_one()
        models = self._get_default_model()
        index_obj = self.env['se.index']
        ir_export_obj = self.env['ir.exports']
        for model in models:
            for lang in self.lang_ids:
                if not self.index_ids.filtered(
                        lambda i: i.lang_id == lang and i.model_id == model):
                    ir_export = ir_export_obj.search([('resource', '=', model.model)])
                    index_obj.create({
                        'backend_id' : self.se_backend_id.id,
                        'model_id': model.id,
                        'lang_id': lang.id,
                        'exporter_id': ir_export.id,
                    })
        return True