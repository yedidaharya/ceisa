from odoo import models, fields, api

class CeisaReferensiCaraAngkut(models.Model):
    _name = 'ceisa.referensi.cara.angkut'
    _description = 'Referensi Cara Angkut'
    _rec_name = 'kode_uraian_cara_angkut'

    kode_cara_angkut = fields.Char(string='Kode Cara Angkut', required=True)
    uraian_cara_angkut = fields.Char(string='Uraian Cara Angkut', required=True)

    kode_uraian_cara_angkut = fields.Char(
        string='Kode - Uraian',
        compute='_compute_kode_uraian_cara_angkut',
        store=True
    )

    @api.depends('kode_cara_angkut', 'uraian_cara_angkut')
    def _compute_kode_uraian_cara_angkut(self):
        for rec in self:
            rec.kode_uraian_cara_angkut = f"{rec.kode_cara_angkut or ''} - {rec.uraian_cara_angkut or ''}"
