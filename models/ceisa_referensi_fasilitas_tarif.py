from odoo import models, fields, api

class CeisaReferensiFasilitasTarif(models.Model):
    _name = 'ceisa.referensi.fasilitas.tarif'
    _description = 'Referensi Fasilitas Tarif'
    _rec_name = 'kode_uraian_fasilitas_tarif'

    kode_fasilitas_tarif = fields.Char(string='Kode Fasilitas Tarif', required=True)
    uraian_fasilitas_tarif = fields.Char(string='Uraian Fasilitas Tarif', required=True)

    kode_uraian_fasilitas_tarif = fields.Char(
        string='Kode - Uraian Fasilitas Tarif',
        compute='_compute_kode_uraian',
        store=True
    )

    @api.depends('kode_fasilitas_tarif', 'uraian_fasilitas_tarif')
    def _compute_kode_uraian(self):
        for rec in self:
            rec.kode_uraian_fasilitas_tarif = f"{rec.kode_fasilitas_tarif or ''} - {rec.uraian_fasilitas_tarif or ''}"
