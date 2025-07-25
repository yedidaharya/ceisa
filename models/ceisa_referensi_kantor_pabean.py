from odoo import models, fields, api

class CeisaReferensiKantorPabean(models.Model):
    _name = 'ceisa.referensi.kantor.pabean'
    _description = 'Referensi Kantor Pabean'
    _rec_name = 'kode_uraian_kantor'

    kode_kantor = fields.Char(string='Kode Kantor', required=True)
    uraian_kantor = fields.Char(string='Uraian Kantor', required=True)

    kode_uraian_kantor = fields.Char(
        string="Kode - Uraian Kantor",
        compute='_compute_kode_uraian_kantor',
        store=True
    )

    @api.depends('kode_kantor', 'uraian_kantor')
    def _compute_kode_uraian_kantor(self):
        for rec in self:
            rec.kode_uraian_kantor = f"{rec.kode_kantor or ''} - {rec.uraian_kantor or ''}"
