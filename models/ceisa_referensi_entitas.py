from odoo import models, fields, api

class CeisaReferensiEntitas(models.Model):
    _name = 'ceisa.referensi.entitas'
    _description = 'Referensi Entitas'
    _rec_name = 'kode_uraian_entitas'

    kode_entitas = fields.Char(string='Kode Entitas', required=True)
    uraian_entitas = fields.Char(string='Uraian Entitas', required=True)

    kode_uraian_entitas = fields.Char(
        string='Kode - Uraian Entitas',
        compute='_compute_kode_uraian_entitas',
        store=True
    )

    @api.depends('kode_entitas', 'uraian_entitas')
    def _compute_kode_uraian_entitas(self):
        for rec in self:
            rec.kode_uraian_entitas = f"{rec.kode_entitas or ''} - {rec.uraian_entitas or ''}"
