from odoo import models, fields, api

class CeisaReferensiAsuransi(models.Model):
    _name = 'ceisa.referensi.asuransi'
    _description = 'Referensi Asuransi'
    _rec_name = 'kode_uraian_asuransi'

    kode_asuransi = fields.Char(string='Kode Asuransi', required=True)
    uraian_asuransi = fields.Char(string='Uraian Asuransi', required=True)
    

    kode_uraian_asuransi = fields.Char(
        string='Kode - Uraian Asuransi',
        compute='_compute_kode_asuransi',
        store=True
    )

    @api.depends('kode_asuransi', 'uraian_asuransi')
    def _compute_kode_asuransi(self):
        for rec in self:
            rec.kode_uraian_asuransi = f"{rec.kode_asuransi or ''} - {rec.uraian_asuransi or ''}"
