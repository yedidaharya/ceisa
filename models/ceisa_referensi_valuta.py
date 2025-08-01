from odoo import models, fields, api

class CeisaReferensiValuta(models.Model):
    _name = 'ceisa.referensi.valuta'
    _description = 'Referensi Valuta'
    _rec_name = 'kode_uraian_valuta'

    kode_valuta = fields.Char(string='Kode Valuta', required=True)
    uraian_valuta = fields.Char(string='Uraian Valuta', required=True)

    kode_uraian_valuta = fields.Char(
        string='Kode - Uraian Valuta',
        compute='_compute_kode_valuta',
        store=True
    )

    @api.depends('kode_valuta', 'uraian_valuta')
    def _compute_kode_valuta(self):
        for rec in self:
            rec.kode_uraian_valuta = f"{rec.kode_valuta or ''} - {rec.uraian_valuta or ''}"
