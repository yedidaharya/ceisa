from odoo import models, fields, api

class CeisaReferensiTipeKontainer(models.Model):
    _name = 'ceisa.referensi.tipe.kontainer'
    _description = 'Referensi Tipe Kontainer'
    _rec_name = 'kode_uraian_tipe_kontainer'

    kode_tipe_kontainer = fields.Char(string='Kode Tipe Kontainer', required=True)
    uraian_tipe_kontainer = fields.Char(string='Uraian Tipe Kontainer', required=True)

    kode_uraian_tipe_kontainer = fields.Char(
        string='Kode - Uraian',
        compute='_compute_kode_uraian_tipe_kontainer',
        store=True
    )

    @api.depends('kode_tipe_kontainer', 'uraian_tipe_kontainer')
    def _compute_kode_uraian_tipe_kontainer(self):
        for rec in self:
            rec.kode_uraian_tipe_kontainer = f"{rec.kode_tipe_kontainer} - {rec.uraian_tipe_kontainer or ''}"
