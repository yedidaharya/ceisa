from odoo import models, fields, api

class CeisaReferensiTps(models.Model):
    _name = 'ceisa.referensi.tps'
    _description = 'Referensi TPS'
    _rec_name = 'kode_uraian_tps'

    kode_tps = fields.Char(string='Kode TPS', required=True)
    uraian_tps = fields.Char(string='Uraian TPS', required=True)
    kode_kantor = fields.Char(string='Kode Kantor') 

    kode_uraian_tps = fields.Char(
        string='Kode - Uraian Tps',
        compute='_compute_kode_tps',
        store=True
    )

    @api.depends('kode_tps', 'uraian_tps')
    def _compute_kode_tps(self):
        for rec in self:
            rec.kode_uraian_tps = f"{rec.kode_tps or ''} - {rec.uraian_tps or ''}"
