from odoo import models, fields, api

class CeisaReferensiPelabuhan(models.Model):
    _name = 'ceisa.referensi.pelabuhan'
    _description = 'Referensi Pelabuhan'
    _rec_name = 'kode_uraian_pelabuhan'

    kode_pelabuhan = fields.Char(string='Kode Pelabuhan', required=True)
    uraian_pelabuhan = fields.Char(string='Uraian Pelabuhan', required=True)
    kode_kantor = fields.Char(string='Kode Kantor') 

    kode_uraian_pelabuhan = fields.Char(
        string='Kode - Uraian Pelabuhan',
        compute='_compute_kode_uraian',
        store=True
    )

    @api.depends('kode_pelabuhan', 'uraian_pelabuhan')
    def _compute_kode_uraian(self):
        for rec in self:
            rec.kode_uraian_pelabuhan = f"{rec.kode_pelabuhan or ''} - {rec.uraian_pelabuhan or ''}"
