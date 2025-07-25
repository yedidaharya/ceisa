from odoo import models, fields, api

class CeisaReferensiSatuan(models.Model):
    _name = 'ceisa.referensi.satuan'
    _description = 'Referensi Satuan'
    _rec_name = 'kode_uraian_satuan'

    kode_satuan = fields.Char(string='Kode Satuan', required=True)
    uraian_satuan = fields.Char(string='Uraian Satuan', required=True)

    kode_uraian_satuan = fields.Char(
        string='Kode - Uraian Satuan',
        compute='_compute_kode_uraian_satuan',
        store=True
    )

    @api.depends('kode_satuan', 'uraian_satuan')
    def _compute_kode_uraian_satuan(self):
        for rec in self:
            rec.kode_uraian_satuan = f"{rec.kode_satuan or ''} - {rec.uraian_satuan or ''}"
