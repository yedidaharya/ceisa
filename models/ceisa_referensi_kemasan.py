from odoo import models, fields, api

class CeisaReferensiKemasan(models.Model):
    _name = 'ceisa.referensi.kemasan'
    _description = 'Referensi Jenis Kemasan'
    _rec_name = 'kode_uraian_kemasan'  # Use the computed field for _rec_name

    kode_kemasan = fields.Char(string='Kode Kemasan', required=True)
    uraian_kemasan = fields.Char(string='Uraian Kemasan', required=True)

    # Computed field with @api.depends to track changes in kode_kemasan and uraian_kemasan
    kode_uraian_kemasan = fields.Char(string="Kode Uraian Kemasan", compute='_compute_kode_uraian_kemasan', store=True)

    @api.depends('kode_kemasan', 'uraian_kemasan')
    def _compute_kode_uraian_kemasan(self):
        for record in self:
            record.kode_uraian_kemasan = f"{record.kode_kemasan} - {record.uraian_kemasan}"
