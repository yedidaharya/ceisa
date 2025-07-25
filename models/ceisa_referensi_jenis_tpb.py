from odoo import models, fields, api

class CeisaReferensiJenisTpb(models.Model):
    _name = 'ceisa.referensi.jenis.tpb'
    _description = 'Referensi Jenis TPB'
    _rec_name = 'kode_uraian_jenis_tpb'  # akan ditampilkan di dropdown

    kode_jenis_tpb = fields.Char(string='Kode Jenis TPB', required=True)
    uraian_jenis_tpb = fields.Char(string='Uraian Jenis TPB', required=True)

    kode_uraian_jenis_tpb = fields.Char(
        string="Kode - Uraian Jenis TPB",
        compute='_compute_kode_uraian_jenis_tpb',
        store=True
    )

    @api.depends('kode_jenis_tpb', 'uraian_jenis_tpb')
    def _compute_kode_uraian_jenis_tpb(self):
        for rec in self:
            rec.kode_uraian_jenis_tpb = f"{rec.kode_jenis_tpb or ''} - {rec.uraian_jenis_tpb or ''}"
