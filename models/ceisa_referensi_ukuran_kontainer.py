from odoo import models, fields, api

class CeisaReferensiUkuranKontainer(models.Model):
    _name = 'ceisa.referensi.ukuran.kontainer'
    _description = 'Referensi Ukuran Kontainer'
    _rec_name = 'kode_uraian_ukuran_kontainer'  # kombinasi dua kolom

    kode_ukuran_kontainer = fields.Char(string='Kode Ukuran Kontainer', required=True)
    uraian_ukuran_kontainer = fields.Char(string='Uraian Ukuran Kontainer', required=True)

    # kolom gabungan yang jadi tampilan dropdown
    kode_uraian_ukuran_kontainer = fields.Char(
        string="Kode - Uraian",
        compute='_compute_kode_uraian',
        store=True
    )

    @api.depends('kode_ukuran_kontainer', 'uraian_ukuran_kontainer')
    def _compute_kode_uraian(self):
        for rec in self:
            rec.kode_uraian_ukuran_kontainer = f"{rec.kode_ukuran_kontainer} - {rec.uraian_ukuran_kontainer or ''}"
