from odoo import models, fields, api

class CeisaReferensiNegara(models.Model):
    _name = 'ceisa.referensi.negara'
    _description = 'Referensi Negara'
    _rec_name = 'kode_uraian_negara'  # gunakan field hasil compute

    kode_negara = fields.Char(string='Kode Negara', required=True)
    uraian_negara = fields.Char(string='Uraian Negara', required=True)
    tarif_freight = fields.Float(string='Tarif Freight')

    kode_uraian_negara = fields.Char(
        string="Kode - Uraian Negara",
        compute='_compute_kode_uraian_negara',
        store=True
    )

    @api.depends('kode_negara', 'uraian_negara')
    def _compute_kode_uraian_negara(self):
        for rec in self:
            rec.kode_uraian_negara = f"{rec.kode_negara or ''} - {rec.uraian_negara or ''}"
