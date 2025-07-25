from odoo import models, fields, api

class CeisaReferensiJenisKontainer(models.Model):
    _name = 'ceisa.referensi.jenis.kontainer'
    _description = 'Referensi Jenis Kontainer'
    _rec_name = 'kode_uraian_jenis_kontainer'

    kode_jenis_kontainer = fields.Char(string='Kode Jenis Kontainer', required=True)
    uraian_jenis_kontainer = fields.Char(string='Uraian Jenis Kontainer', required=True)

    kode_uraian_jenis_kontainer = fields.Char(
        string='Kode - Uraian',
        compute='_compute_kode_uraian_jenis_kontainer',
        store=True
    )

    @api.depends('kode_jenis_kontainer', 'uraian_jenis_kontainer')
    def _compute_kode_uraian_jenis_kontainer(self):
        for rec in self:
            rec.kode_uraian_jenis_kontainer = f"{rec.kode_jenis_kontainer} - {rec.uraian_jenis_kontainer or ''}"
