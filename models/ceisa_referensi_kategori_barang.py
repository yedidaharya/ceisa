from odoo import models, fields, api

class CeisaReferensiKategoriBarang(models.Model):
    _name = 'ceisa.referensi.kategori.barang'
    _description = 'Referensi Kategori Barang'
    _rec_name = 'kode_uraian_kategori_barang'

    kode_kategori_barang = fields.Char(string='Kode Kategori Barang', required=True)
    uraian_kategori_barang = fields.Char(string='Uraian Kategori Barang', required=True)
    

    kode_uraian_kategori_barang = fields.Char(
        string='Kode - Uraian Kategori Barang',
        compute='_compute_kode_kategori_barang',
        store=True
    )

    @api.depends('kode_kategori_barang', 'uraian_kategori_barang')
    def _compute_kode_kategori_barang(self):
        for rec in self:
            rec.kode_uraian_kategori_barang = f"{rec.kode_kategori_barang or ''} - {rec.uraian_kategori_barang or ''}"
