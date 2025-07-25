from odoo import models, fields, api

class CeisaReferensiJenisIdentitas(models.Model):
    _name = 'ceisa.referensi.jenis.identitas'
    _description = 'Referensi Jenis Identitas'
    _rec_name = 'kode_uraian_jenis_identitas'

    kode_jenis_identitas = fields.Char(string='Kode Jenis Identitas', required=True)
    uraian_jenis_identitas = fields.Char(string='Uraian Jenis Identitas', required=True)

    kode_uraian_jenis_identitas = fields.Char(
        string='Kode - Uraian Jenis Identitas',
        compute='_compute_kode_uraian',
        store=True
    )

    @api.depends('kode_jenis_identitas', 'uraian_jenis_identitas')
    def _compute_kode_uraian(self):
        for rec in self:
            rec.kode_uraian_jenis_identitas = f"{rec.kode_jenis_identitas or ''} - {rec.uraian_jenis_identitas or ''}"
