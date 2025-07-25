from odoo import models, fields, api

class CeisaReferensiTujuanPengiriman(models.Model):
    _name = 'ceisa.referensi.tujuan.pengiriman'
    _description = 'Referensi Tujuan Pengiriman'
    _rec_name = 'kode_uraian_tujuan_pengiriman'

    kode_dokumen = fields.Char(string='Kode Dokumen', required=True)
    kode_tujuan_pengiriman = fields.Char(string='Kode Tujuan Pengiriman', required=True)
    uraian_tujuan_pengiriman = fields.Char(string='Uraian Tujuan Pengiriman', required=True)

    kode_uraian_tujuan_pengiriman = fields.Char(
        string="Kode - Uraian Tujuan Pengiriman",
        compute='_compute_kode_uraian',
        store=True
    )

    @api.depends('kode_tujuan_pengiriman', 'uraian_tujuan_pengiriman')
    def _compute_kode_uraian(self):
        for rec in self:
            rec.kode_uraian_tujuan_pengiriman = f"{rec.kode_tujuan_pengiriman or ''} - {rec.uraian_tujuan_pengiriman or ''}"
