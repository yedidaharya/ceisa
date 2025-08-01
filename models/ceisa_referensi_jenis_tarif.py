from odoo import models, fields, api

class CeisaReferensiJenisTarif(models.Model):
    _name = 'ceisa.referensi.jenis.tarif'
    _description = 'Referensi Jenis Tarif'
    _rec_name = 'kode_uraian_jenis_tarif'

    kode_jenis_tarif = fields.Char(string='Kode Jenis Tarif', required=True)
    uraian_jenis_tarif = fields.Char(string='Uraian Jenis Tarif', required=True)
    

    kode_uraian_jenis_tarif = fields.Char(
        string='Kode - Uraian Jenis Tarif',
        compute='_compute_kode_jenis_tarif',
        store=True
    )

    @api.depends('kode_jenis_tarif', 'uraian_jenis_tarif')
    def _compute_kode_jenis_tarif(self):
        for rec in self:
            rec.kode_uraian_jenis_tarif = f"{rec.kode_jenis_tarif or ''} - {rec.uraian_jenis_tarif or ''}"
