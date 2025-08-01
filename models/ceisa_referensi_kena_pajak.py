from odoo import models, fields, api

class CeisaReferensiKenaPajak(models.Model):
    _name = 'ceisa.referensi.kena.pajak'
    _description = 'Referensi Kena Pajak'
    _rec_name = 'kode_uraian_kena_pajak'

    kode_kena_pajak = fields.Char(string='Kode Kena Pajak', required=True)
    uraian_kena_pajak = fields.Char(string='Uraian Kena Pajak', required=True)
    

    kode_uraian_kena_pajak = fields.Char(
        string='Kode - Uraian Kena Pajak',
        compute='_compute_kode_kena_pajak',
        store=True
    )

    @api.depends('kode_kena_pajak', 'uraian_kena_pajak')
    def _compute_kode_kena_pajak(self):
        for rec in self:
            rec.kode_uraian_kena_pajak = f"{rec.kode_kena_pajak or ''} - {rec.uraian_kena_pajak or ''}"
