from odoo import models, fields, api

class CeisaReferensiDokumen(models.Model):
    _name = 'ceisa.referensi.dokumen'
    _description = 'Referensi Jenis Dokumen'
    _rec_name = 'kode_uraian_dokumen'  # dipakai Odoo di UI

    kode_dokumen = fields.Char(string='Kode Dokumen', required=True)
    uraian_dokumen = fields.Char(string='Uraian Dokumen', required=True)

    kode_uraian_dokumen = fields.Char(
        string='Kode - Uraian Dokumen',
        compute='_compute_kode_uraian_dokumen',
        store=True
    )

    @api.depends('kode_dokumen', 'uraian_dokumen')
    def _compute_kode_uraian_dokumen(self):
        for rec in self:
            rec.kode_uraian_dokumen = f"{rec.kode_dokumen or ''} - {rec.uraian_dokumen or ''}"
