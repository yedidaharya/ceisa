from odoo import models, fields, api

class CeisaReferensiTutupPu(models.Model):
    _name = 'ceisa.referensi.tutup.pu'
    _description = 'Referensi TutupPu'
    _rec_name = 'kode_uraian_tutup_pu'

    kode_tutup_pu = fields.Char(string='Kode Tutup Pu', required=True)
    uraian_tutup_pu = fields.Char(string='Uraian Tutup Pu', required=True)

    kode_uraian_tutup_pu = fields.Char(
        string='Kode - Uraian TutupPu',
        compute='_compute_kode_uraian_tutup_pu',
        store=True
    )

    @api.depends('kode_tutup_pu', 'uraian_tutup_pu')
    def _compute_kode_uraian_tutup_pu(self):
        for rec in self:
            rec.kode_uraian_tutup_pu = f"{rec.kode_tutup_pu or ''} - {rec.uraian_tutup_pu or ''}"
