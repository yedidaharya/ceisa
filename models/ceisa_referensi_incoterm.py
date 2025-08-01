from odoo import models, fields, api

class CeisaReferensiIncoterm(models.Model):
    _name = 'ceisa.referensi.incoterm'
    _description = 'Referensi Incoterm'
    _rec_name = 'kode_uraian_incoterm'

    kode_incoterm = fields.Char(string='Kode TPS', required=True)
    uraian_incoterm = fields.Char(string='Uraian TPS', required=True)
    

    kode_uraian_incoterm = fields.Char(
        string='Kode - Uraian Incoterm',
        compute='_compute_kode_incoterm',
        store=True
    )

    @api.depends('kode_incoterm', 'uraian_incoterm')
    def _compute_kode_incoterm(self):
        for rec in self:
            rec.kode_uraian_incoterm = f"{rec.kode_incoterm or ''} - {rec.uraian_incoterm or ''}"
