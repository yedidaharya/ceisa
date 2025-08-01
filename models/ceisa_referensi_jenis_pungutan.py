from odoo import models, fields, api

class CeisaReferensiJenisPungutan(models.Model):
    _name = 'ceisa.referensi.jenis.pungutan'
    _description = 'Referensi Jenis Pungutan'
    _rec_name = 'kode_jenis_pungutan'

    kode_jenis_pungutan = fields.Char(string='Kode Jenis Pungutan', required=True)

    
