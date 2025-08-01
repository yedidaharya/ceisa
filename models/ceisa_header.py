import pyodbc, requests, logging
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)


class CeisaHeader(models.Model):
    _name = 'ceisa.header'
    _description = 'CEISA Header'

    _sql_constraints = [
        ('unique_nomor_aju', 'UNIQUE(nomor_aju)', 'Nomor Aju harus unik.'),
    ]

    asuransi = fields.Float(digits=(18, 2), default=0.00)
    bruto = fields.Float(string='Berat Kotor (KGM)', digits=(18, 4), default=0.0000)
    cif = fields.Float(digits=(18, 2), default=0.00)
    kode_jenis_tpb = fields.Char(string='Kode Jenis TPB', default='')

    jenis_tpb_lookup = fields.Many2one(
        'ceisa.referensi.jenis.tpb',
        string='Jenis TPB (Dropdown)',
        compute='_compute_jenis_tpb_lookup',
        inverse='_inverse_jenis_tpb_lookup',
        store=False
    )

    @api.depends('kode_jenis_tpb')
    def _compute_jenis_tpb_lookup(self):
        for rec in self:
            rec.jenis_tpb_lookup = self.env['ceisa.referensi.jenis.tpb'].search(
                [('kode_jenis_tpb', '=', rec.kode_jenis_tpb)],
                limit=1
            )

    def _inverse_jenis_tpb_lookup(self):
        for rec in self:
            if rec.jenis_tpb_lookup:
                rec.kode_jenis_tpb = rec.jenis_tpb_lookup.kode_jenis_tpb


    kode_tujuan_tpb = fields.Char(string='Kode Tujuan TPB', default='')

    tujuan_tpb_lookup = fields.Many2one(
        'ceisa.referensi.jenis.tpb',
        string='Tujuan TPB',
        compute='_compute_tujuan_tpb_lookup',
        inverse='_inverse_tujuan_tpb_lookup',
        store=False
    )

    @api.depends('kode_tujuan_tpb')
    def _compute_tujuan_tpb_lookup(self):
        for rec in self:
            rec.tujuan_tpb_lookup = self.env['ceisa.referensi.jenis.tpb'].search(
                [('kode_jenis_tpb', '=', rec.kode_tujuan_tpb)],
                limit=1
            )

    def _inverse_tujuan_tpb_lookup(self):
        for rec in self:
            if rec.tujuan_tpb_lookup:
                rec.kode_tujuan_tpb = rec.tujuan_tpb_lookup.kode_jenis_tpb

    freight = fields.Float(digits=(18, 2), default=0.00)
    harga_penyerahan = fields.Float(string="Harga Penyerahan", digits=(18, 4), default=0.0000)
    id_pengguna = fields.Char(default='')
    jabatan_ttd = fields.Char(string='Jabatan', default='')
    jumlah_kontainer = fields.Integer(default=0)
    kode_dokumen = fields.Char(default='')

    kode_kantor = fields.Char(string='Kode Kantor', default='')
    
    kode_kantor_bongkar = fields.Char(string='Kode Kantor Bongkar', default='')

    kantor_pabean_lookup = fields.Many2one(
        'ceisa.referensi.kantor.pabean',
        string='Kantor Pabean',
        compute='_compute_kantor_lookup',
        inverse='_inverse_kantor_lookup',
        store=False
    )


    @api.depends('kode_kantor')
    def _compute_kantor_lookup(self):
        for rec in self:
            rec.kantor_pabean_lookup = self.env['ceisa.referensi.kantor.pabean'].search([
                ('kode_kantor', '=', rec.kode_kantor)
            ], limit=1)

    def _inverse_kantor_lookup(self):
        for rec in self:
            if rec.kantor_pabean_lookup:
                rec.kode_kantor = rec.kantor_pabean_lookup.kode_kantor


    kantor_bongkar_lookup = fields.Many2one(
        'ceisa.referensi.kantor.pabean',
        string='Kantor Bongkar',
        compute='_compute_kantor_bongkar_lookup',
        inverse='_inverse_kantor_bongkar_lookup',
        store=False
    )

    @api.depends('kode_kantor_bongkar')
    def _compute_kantor_bongkar_lookup(self):
        for rec in self:
            rec.kantor_bongkar_lookup = self.env['ceisa.referensi.kantor.pabean'].search([
                ('kode_kantor', '=', rec.kode_kantor_bongkar)
            ], limit=1)



    def _inverse_kantor_bongkar_lookup(self):
        for rec in self:
            if rec.kantor_bongkar_lookup:
                rec.kode_kantor_bongkar = rec.kantor_bongkar_lookup.kode_kantor

    kode_pel_bongkar = fields.Char(string='Kode Pelabuhan Bongkar', default='')

    pelabuhan_bongkar_lookup = fields.Many2one(
        'ceisa.referensi.pelabuhan',
        string='Pelabuhan Bongkar',
        compute='_compute_pelabuhan_bongkar_lookup',
        inverse='_inverse_pelabuhan_bongkar_lookup',
        store=False,
    )


    @api.onchange('pelabuhan_bongkar_lookup')
    def _onchange_pelabuhan_bongkar(self):
        for rec in self:
            if rec.pelabuhan_bongkar_lookup:
                rec.kode_pel_bongkar = rec.pelabuhan_bongkar_lookup.kode_pelabuhan


    @api.depends('kode_pel_bongkar')
    def _compute_pelabuhan_bongkar_lookup(self):
        for rec in self:
            rec.pelabuhan_bongkar_lookup = self.env['ceisa.referensi.pelabuhan'].search([
                ('kode_pelabuhan', '=', rec.kode_pel_bongkar)
            ], limit=1)


    def _inverse_pelabuhan_bongkar_lookup(self):
        for rec in self:
            if rec.pelabuhan_bongkar_lookup:
                rec.kode_pel_bongkar = rec.pelabuhan_bongkar_lookup.kode_pelabuhan
    

    kode_tujuan_pengiriman = fields.Char(string='Kode Tujuan Pengiriman', default='')

    tujuan_pengiriman_lookup = fields.Many2one(
        'ceisa.referensi.tujuan.pengiriman',
        string='Tujuan Pengiriman',
        compute='_compute_tujuan_lookup',
        inverse='_inverse_tujuan_lookup',
        store=False
    )

    @api.depends('kode_tujuan_pengiriman', 'kode_dokumen')
    def _compute_tujuan_lookup(self):
        for rec in self:
            domain = [
                ('kode_tujuan_pengiriman', '=', rec.kode_tujuan_pengiriman),
                ('kode_dokumen', '=', rec.kode_dokumen),
            ]
            rec.tujuan_pengiriman_lookup = self.env['ceisa.referensi.tujuan.pengiriman'].search(domain, limit=1)

    def _inverse_tujuan_lookup(self):
        for rec in self:
            if rec.tujuan_pengiriman_lookup:
                rec.kode_tujuan_pengiriman = rec.tujuan_pengiriman_lookup.kode_tujuan_pengiriman

    kota_ttd = fields.Char(string='Tempat', default='')
    nama_ttd = fields.Char(string='Nama', default='')
    netto = fields.Float(string='Berat Bersih (KGM)', digits=(18, 4), default=0.0000)
    nik = fields.Char(default='')
    nomor_aju = fields.Char(size=50, default='')
    seri = fields.Integer(default=0)
    tanggal_aju = fields.Date(default=fields.Date.today)
    tanggal_ttd = fields.Date(string='Tanggal', default=fields.Date.today)
    user_portal = fields.Char(default='')
    volume = fields.Float(string='Volume (M3)', digits=(18, 4), default=0.0000)
    biaya_tambahan = fields.Float(digits=(18, 2), default=0.00)
    biaya_pengurang = fields.Float(digits=(18, 2), default=0.00)
    vd = fields.Float(digits=(18, 4), default=0.0000)
    uang_muka = fields.Float(string='Nilai Uang Muka', digits=(18, 4), default=0.0000)
    nilai_jasa = fields.Float(string='Nilai Jasa', digits=(18, 4), default=0.0000)
    harga_perolehan = fields.Float(string='Harga perolehan', digits=(18, 4), default=0.0000)
    nomor_daftar = fields.Char(default='')
    tanggal_daftar = fields.Date()
    kode_status = fields.Char(default='')
    jsonresult = fields.Json()
    #Tambahan BC 23
    nomor_bc11 = fields.Char(default='')
    pos_bc11 = fields.Char(default='', size=4)
    tanggal_bc11 = fields.Date()
    kode_tutup_pu = fields.Char(default='')
    tanggal_tiba = fields.Date()
    tutup_pu_lookup = fields.Many2one('ceisa.referensi.tutup.pu', string='TutupPu', compute='_compute_tutup_pu_lookup', inverse='_inverse_tutup_pu_lookup', store=False)
    @api.depends('kode_tutup_pu')
    def _compute_tutup_pu_lookup(self):
        for rec in self:
            rec.tutup_pu_lookup = self.env['ceisa.referensi.tutup.pu'].search([
                ('kode_tutup_pu', '=', rec.kode_tutup_pu)
            ], limit=1)

    def _inverse_tutup_pu_lookup(self):
        for rec in self:
            if rec.tutup_pu_lookup:
                rec.kode_tutup_pu = rec.tutup_pu_lookup.kode_tutup_pu
    
    kode_pel_muat = fields.Char(default='')
    pelabuhan_muat_lookup = fields.Many2one('ceisa.referensi.pelabuhan', string='Pelabuhan Muat', compute='_compute_pelabuhan_muat_lookup', inverse='_inverse_pelabuhan_muat_lookup', store=False)
    
    @api.depends('kode_pel_muat')
    def _compute_pelabuhan_muat_lookup(self):
        for rec in self:
            rec.pelabuhan_muat_lookup = self.env['ceisa.referensi.pelabuhan'].search([
                ('kode_pelabuhan', '=', rec.kode_pel_muat)
            ], limit=1)

    def _inverse_pelabuhan_muat_lookup(self):
        for rec in self:
            if rec.pelabuhan_muat_lookup:
                rec.kode_pel_muat = rec.pelabuhan_muat_lookup.kode_pelabuhan


    kode_pel_transit = fields.Char(default='')
    pelabuhan_transit_lookup = fields.Many2one('ceisa.referensi.pelabuhan', string='Pelabuhan Transit', compute='_compute_pelabuhan_transit_lookup', inverse='_inverse_pelabuhan_transit_lookup', store=False)
    @api.depends('kode_pel_transit')
    def _compute_pelabuhan_transit_lookup(self):
        for rec in self:
            rec.pelabuhan_transit_lookup = self.env['ceisa.referensi.pelabuhan'].search([
                ('kode_pelabuhan', '=', rec.kode_pel_transit)
            ], limit=1)

    def _inverse_pelabuhan_transit_lookup(self):
        for rec in self:
            if rec.pelabuhan_transit_lookup:
                rec.kode_pel_transit = rec.pelabuhan_transit_lookup.kode_pelabuhan

    kode_tps = fields.Char(default='')
    tps_lookup = fields.Many2one('ceisa.referensi.tps', string='Tempat Penimbunan', compute='_compute_tps_lookup', inverse='_inverse_tps_lookup', store=False)
    @api.depends('kode_tps')
    def _compute_tps_lookup(self):
        for rec in self:
            rec.tps_lookup = self.env['ceisa.referensi.tps'].search([
                ('kode_tps', '=', rec.kode_tps)
            ], limit=1)

    def _inverse_tps_lookup(self):
        for rec in self:
            if rec.tps_lookup:
                rec.kode_tps = rec.tps_lookup.kode_tps

    kode_valuta = fields.Char(default='')
    valuta_lookup = fields.Many2one('ceisa.referensi.valuta', string='Jenis Valuta', compute='_compute_valuta_lookup', inverse='_inverse_valuta_lookup', store=False)
    @api.depends('kode_valuta')
    def _compute_valuta_lookup(self):
        for rec in self:
            rec.valuta_lookup = self.env['ceisa.referensi.valuta'].search([
                ('kode_valuta', '=', rec.kode_valuta)
            ], limit=1)

    def _inverse_valuta_lookup(self):
        for rec in self:
            if rec.valuta_lookup:
                rec.kode_valuta = rec.valuta_lookup.kode_valuta
    
    kode_incoterm = fields.Char(default='')
    incoterm_lookup = fields.Many2one('ceisa.referensi.incoterm', string='Jenis Harga', compute='_compute_incoterm_lookup', inverse='_inverse_incoterm_lookup', store=False)
    @api.depends('kode_incoterm')
    def _compute_incoterm_lookup(self):
        for rec in self:
            rec.incoterm_lookup = self.env['ceisa.referensi.incoterm'].search([
                ('kode_incoterm', '=', rec.kode_incoterm)
            ], limit=1)

    def _inverse_incoterm_lookup(self):
        for rec in self:
            if rec.incoterm_lookup:
                rec.kode_incoterm = rec.incoterm_lookup.kode_incoterm
  
    nilai_barang = fields.Float(digits=(38, 2), default=0.00)
    ndpbm = fields.Float(digits=(10, 4), default=0.0000)
    fob = fields.Float(digits=(18, 2), default=0.00)
    kode_asuransi = fields.Char(default='')
    asuransi_lookup = fields.Many2one('ceisa.referensi.asuransi', string='Jenis Asuransi', compute='_compute_asuransi_lookup', inverse='_inverse_asuransi_lookup', store=False)
    @api.depends('kode_asuransi')
    def _compute_asuransi_lookup(self):
        for rec in self:
            rec.asuransi_lookup = self.env['ceisa.referensi.asuransi'].search([
                ('kode_asuransi', '=', rec.kode_asuransi)
            ], limit=1)

    def _inverse_asuransi_lookup(self):
        for rec in self:
            if rec.asuransi_lookup:
                rec.kode_asuransi = rec.asuransi_lookup.kode_asuransi
    
    kode_kena_pajak = fields.Char(default='')
    kena_pajak_lookup = fields.Many2one('ceisa.referensi.kena.pajak', string='Jasa Kena Pajak', compute='_compute_kena_pajak_lookup', inverse='_inverse_kena_pajak_lookup', store=False)
    @api.depends('kode_kena_pajak')
    def _compute_kena_pajak_lookup(self):
        for rec in self:
            rec.kena_pajak_lookup = self.env['ceisa.referensi.kena.pajak'].search([
                ('kode_kena_pajak', '=', rec.kode_kena_pajak)
            ], limit=1)

    def _inverse_kena_pajak_lookup(self):
        for rec in self:
            if rec.kena_pajak_lookup:
                rec.kode_kena_pajak = rec.kena_pajak_lookup.kode_kena_pajak

    subpos_bc11_1 = fields.Char(string='Subpos 1', size=4)
    subpos_bc11_2 = fields.Char(string='Subpos 2', size=4)





    entitas_ids = fields.One2many('ceisa.entitas', 'header_id', string='Entitas')
    kemasan_ids = fields.One2many('ceisa.kemasan', 'header_id', string='Kemasan')
    kontainer_ids = fields.One2many('ceisa.kontainer', 'header_id', string='Kontainer')
    dokumen_ids = fields.One2many('ceisa.dokumen', 'header_id', string='Dokumen')
    pungutan_ids = fields.One2many('ceisa.pungutan', 'header_id', string='Pungutan')
    pengangkut_ids = fields.One2many('ceisa.pengangkut', 'header_id', string='Pengangkut')
    barang_ids = fields.One2many('ceisa.barang', 'header_id', string='Barang')

    entitas_1_nomor_identitas = fields.Char(string="Nomor Identitas", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_1_nama = fields.Char(string="Nama", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_1_alamat = fields.Char(string="Alamat", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_1_nomor_ijin_entitas = fields.Char(string="Nomor Ijin TPB", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_1_tanggal_ijin_entitas = fields.Date(string="Tanggal Skep TPB", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_1_nib_entitas = fields.Char(string="NIB", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_1_nitku = fields.Char(string="NITKU", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_1_jenis_identitas_lookup = fields.Many2one('ceisa.referensi.jenis.identitas', string='Jenis Identitas', compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_1_entitas_lookup = fields.Many2one('ceisa.referensi.entitas', string='Jenis Entitas', compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_2_nomor_identitas = fields.Char(string="NPWP", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_2_nama = fields.Char(string="Nama", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_2_alamat = fields.Char(string="Alamat", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_2_nitku = fields.Char(string="NITKU", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_2_jenis_identitas_lookup = fields.Many2one('ceisa.referensi.jenis.identitas', string='Jenis Identitas', compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_2_entitas_lookup = fields.Many2one('ceisa.referensi.entitas', string='Jenis Entitas', compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_2_kode_negara_lookup = fields.Many2one('ceisa.referensi.negara', string='Negara', compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_3_nomor_identitas = fields.Char(string="NPWP", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_3_nama = fields.Char(string="Nama", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_3_alamat = fields.Char(string="Alamat", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_3_nitku = fields.Char(string="NITKU", compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_3_jenis_identitas_lookup = fields.Many2one('ceisa.referensi.jenis.identitas', string='Jenis Identitas', compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)
    entitas_3_entitas_lookup = fields.Many2one('ceisa.referensi.entitas', string='Jenis Entitas', compute='_compute_entitas_display', inverse='_inverse_entitas_display', store=True)

    @api.depends('entitas_ids')
    def _compute_entitas_display(self):
        for rec in self:
            ents = rec.entitas_ids.sorted(lambda e: e.id)

            # ENTITAS 1
            if len(ents) > 0:
                rec.entitas_1_nomor_identitas = ents[0].nomor_identitas
                rec.entitas_1_nama = ents[0].nama_entitas
                rec.entitas_1_alamat = ents[0].alamat_entitas
                rec.entitas_1_nomor_ijin_entitas = ents[0].nomor_ijin_entitas
                rec.entitas_1_tanggal_ijin_entitas = ents[0].tanggal_ijin_entitas
                rec.entitas_1_nib_entitas = ents[0].nib_entitas
                rec.entitas_1_nitku = ents[0].nitku
                rec.entitas_1_jenis_identitas_lookup = self.env['ceisa.referensi.jenis.identitas'].search([
                    ('kode_jenis_identitas', '=', ents[0].kode_jenis_identitas)
                ], limit=1)
                rec.entitas_1_entitas_lookup = self.env['ceisa.referensi.entitas'].search([
                    ('kode_entitas', '=', ents[0].kode_entitas)
                ], limit=1)


                
            else:
                rec.entitas_1_nomor_identitas = False
                rec.entitas_1_nama = False
                rec.entitas_1_alamat = False
                rec.entitas_1_nomor_ijin_entitas = False
                rec.entitas_1_tanggal_ijin_entitas = False
                rec.entitas_1_nib_entitas = False
                rec.entitas_1_nitku = False
                rec.entitas_1_jenis_identitas_lookup = False
                rec.entitas_1_entitas_lookup = False
            # ENTITAS 2
            if len(ents) > 1:
                rec.entitas_2_nomor_identitas = ents[1].nomor_identitas
                rec.entitas_2_nama = ents[1].nama_entitas
                rec.entitas_2_alamat = ents[1].alamat_entitas
                rec.entitas_2_nitku = ents[1].nitku
                rec.entitas_2_jenis_identitas_lookup = self.env['ceisa.referensi.jenis.identitas'].search([
                    ('kode_jenis_identitas', '=', ents[1].kode_jenis_identitas)
                ], limit=1)
                rec.entitas_2_entitas_lookup = self.env['ceisa.referensi.entitas'].search([
                    ('kode_entitas', '=', ents[1].kode_entitas)
                ], limit=1)
                rec.entitas_2_kode_negara_lookup = self.env['ceisa.referensi.negara'].search([
                    ('kode_negara', '=', ents[1].kode_negara)
                ], limit=1)
            else:
                rec.entitas_2_nomor_identitas = False
                rec.entitas_2_nama = False
                rec.entitas_2_alamat = False
                rec.entitas_2_nitku = False
                rec.entitas_2_jenis_identitas_lookup = False
                rec.entitas_2_entitas_lookup = False
                rec.entitas_2_kode_negara_lookup = False
            # ENTITAS 3
            if len(ents) > 2:
                rec.entitas_3_nomor_identitas = ents[2].nomor_identitas
                rec.entitas_3_nama = ents[2].nama_entitas
                rec.entitas_3_alamat = ents[2].alamat_entitas
                rec.entitas_3_nitku = ents[2].nitku
                rec.entitas_3_jenis_identitas_lookup = self.env['ceisa.referensi.jenis.identitas'].search([
                    ('kode_jenis_identitas', '=', ents[2].kode_jenis_identitas)
                ], limit=1)
                rec.entitas_3_entitas_lookup = self.env['ceisa.referensi.entitas'].search([
                    ('kode_entitas', '=', ents[2].kode_entitas)
                ], limit=1)
            else:
                rec.entitas_3_nomor_identitas = False
                rec.entitas_3_nama = False
                rec.entitas_3_alamat = False
                rec.entitas_3_nitku = False
                rec.entitas_3_jenis_identitas_lookup = False
                rec.entitas_3_entitas_lookup = False

    def _inverse_entitas_display(self):
        for rec in self:
            ents = rec.entitas_ids.sorted(lambda e: e.id)
            # ENTITAS 1
            if ents:
                if rec.entitas_1_nomor_identitas:
                    ents[0].nomor_identitas = rec.entitas_1_nomor_identitas
                if rec.entitas_1_nama:
                    ents[0].nama_entitas = rec.entitas_1_nama
                if rec.entitas_1_alamat:
                    ents[0].alamat_entitas = rec.entitas_1_alamat
                if rec.entitas_1_nomor_ijin_entitas:
                    ents[0].nomor_ijin_entitas = rec.entitas_1_nomor_ijin_entitas
                if rec.entitas_1_tanggal_ijin_entitas:
                    ents[0].tanggal_ijin_entitas = rec.entitas_1_tanggal_ijin_entitas
                if rec.entitas_1_nib_entitas:
                    ents[0].nib_entitas = rec.entitas_1_nib_entitas
                if rec.entitas_1_nitku:
                    ents[0].nitku = rec.entitas_1_nitku
                if rec.entitas_1_jenis_identitas_lookup:
                    ents[0].kode_jenis_identitas = rec.entitas_1_jenis_identitas_lookup.kode_jenis_identitas
                if rec.entitas_1_entitas_lookup:
                    ents[0].kode_entitas = rec.entitas_1_entitas_lookup.kode_entitas
                

            # ENTITAS 2
            if len(ents) > 1:
                if rec.entitas_2_nomor_identitas:
                    ents[1].nomor_identitas = rec.entitas_2_nomor_identitas
                if rec.entitas_2_nama:
                    ents[1].nama_entitas = rec.entitas_2_nama
                if rec.entitas_2_alamat:
                    ents[1].alamat_entitas = rec.entitas_2_alamat
                if rec.entitas_2_nitku:
                    ents[1].nitku = rec.entitas_2_nitku
                if rec.entitas_2_jenis_identitas_lookup:
                    ents[1].kode_jenis_identitas = rec.entitas_2_jenis_identitas_lookup.kode_jenis_identitas
                if rec.entitas_2_entitas_lookup:
                    ents[1].kode_entitas = rec.entitas_2_entitas_lookup.kode_entitas
                if rec.entitas_2_kode_negara_lookup:
                    ents[1].kode_negara = rec.entitas_2_kode_negara_lookup.kode_negara

            # ENTITAS 3
            if len(ents) > 2:
                if rec.entitas_3_nomor_identitas:
                    ents[2].nomor_identitas = rec.entitas_3_nomor_identitas
                if rec.entitas_3_nama:
                    ents[2].nama_entitas = rec.entitas_3_nama
                if rec.entitas_3_alamat:
                    ents[2].alamat_entitas = rec.entitas_3_alamat
                if rec.entitas_3_nitku:
                    ents[2].nitku = rec.entitas_3_nitku
                if rec.entitas_3_jenis_identitas_lookup:
                    ents[2].kode_jenis_identitas = rec.entitas_3_jenis_identitas_lookup.kode_jenis_identitas
                if rec.entitas_3_entitas_lookup:
                    ents[2].kode_entitas = rec.entitas_3_entitas_lookup.kode_entitas




    
    pengangkut_kode_cara_angkut_lookup = fields.Many2one('ceisa.referensi.cara.angkut', string='Cara Pengangkutan', compute='_compute_pengangkut_display', inverse='_inverse_pengangkut_display', store=True)
    pengangkut_nama_pengangkut = fields.Char(string='Nama Sarana Angkut', compute='_compute_pengangkut_display', inverse='_inverse_pengangkut_display', store=True)
    pengangkut_nomor_pengangkut = fields.Char(string='Nomor Sarana Angkut', compute='_compute_pengangkut_display', inverse='_inverse_pengangkut_display', store=True)
    pengangkut_kode_negara_lookup = fields.Many2one('ceisa.referensi.negara', string='Bendera', compute='_compute_pengangkut_display', inverse='_inverse_pengangkut_display', store=True)

    @api.depends('pengangkut_ids', 'kode_dokumen')
    def _compute_pengangkut_display(self):
        for rec in self:
            # Reset default dulu
            rec.pengangkut_kode_cara_angkut_lookup = False
            rec.pengangkut_nama_pengangkut = False
            rec.pengangkut_nomor_pengangkut = False
            rec.pengangkut_kode_negara_lookup = False

            if rec.kode_dokumen == '23':
                pengs = rec.pengangkut_ids.sorted(lambda e: e.id)

                if len(pengs) > 0:
                    rec.pengangkut_kode_cara_angkut_lookup = self.env['ceisa.referensi.cara.angkut'].search([
                        ('kode_cara_angkut', '=', pengs[0].kode_cara_angkut)
                    ], limit=1)

                    rec.pengangkut_nama_pengangkut = pengs[0].nama_pengangkut
                    rec.pengangkut_nomor_pengangkut = pengs[0].nomor_pengangkut

                    rec.pengangkut_kode_negara_lookup = self.env['ceisa.referensi.negara'].search([
                        ('kode_negara', '=', pengs[0].kode_bendera)
                    ], limit=1)
    
    def _inverse_pengangkut_display(self):
        for rec in self:
            if rec.kode_dokumen == '23':
                pengs = rec.pengangkut_ids.sorted(lambda e: e.id)
                if pengs:
                    if rec.pengangkut_kode_cara_angkut_lookup:
                        pengs[0].kode_cara_angkut = rec.pengangkut_kode_cara_angkut_lookup.kode_cara_angkut
                    if rec.pengangkut_nama_pengangkut:
                        pengs[0].nama_pengangkut = rec.pengangkut_nama_pengangkut
                    if rec.pengangkut_nomor_pengangkut:
                        pengs[0].nomor_pengangkut = rec.pengangkut_nomor_pengangkut
                    if rec.pengangkut_kode_negara_lookup:
                        pengs[0].kode_bendera = rec.pengangkut_kode_negara_lookup.kode_negara


    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        company = self.env['ceisa.company.master'].search([], limit=1)
        if company:
            res['kode_kantor'] = company.kode_kantor
            res['kota_ttd'] = company.kota_perusahaan
        return res


    @api.model_create_multi
    def create(self, vals_list):
        company = self.env['ceisa.company.master'].search([], limit=1)
        records = super().create(vals_list)

        for rec in records:
            # Set default values if not provided
            if not rec.kode_kantor and company:
                rec.kode_kantor = company.kode_kantor
            if not rec.kota_ttd and company:
                rec.kota_ttd = company.kota_perusahaan     

            # Determine kode_entitas based on dokumen code
            kode_dok = (rec.kode_dokumen or '').strip()
            if kode_dok == '40':
                kode_entitas = [3, 7, 9]
            elif kode_dok == '23':
                kode_entitas = [3, 5, 7]
            else:
                kode_entitas = [3, 7, 9]  # default fallback

            # Create entitas
            entitas_vals = [
                {
                    'header_id': rec.id,
                    'seri_entitas': 1,
                    'kode_entitas': kode_entitas[0],
                    'kode_jenis_identitas': '6',
                    'nomor_identitas': company.npwp_perusahaan if company else '',
                    'nama_entitas': company.nama_perusahaan if company else '',
                    'alamat_entitas': company.alamat_perusahaan if company else '',
                    'nomor_ijin_entitas': company.nomor_ijin_entitas if company else '',
                    'tanggal_ijin_entitas': company.tanggal_ijin_entitas if company else '',
                    'nitku': company.nitku if company else '',
                    'nib_entitas': company.nib if company else '',
                },
                {
                    'header_id': rec.id,
                    'seri_entitas': 2,
                    'kode_entitas': kode_entitas[1],
                    'kode_jenis_identitas': '6',
                },
                {
                    'header_id': rec.id,
                    'seri_entitas': 3,
                    'kode_entitas': kode_entitas[2],
                    'kode_jenis_identitas': '6',
                    'kode_status': '9',
                    'nomor_identitas': company.npwp_perusahaan if company else '',
                    'nama_entitas': company.nama_perusahaan if company else '',
                    'alamat_entitas': company.alamat_perusahaan if company else '',
                    'nitku': company.nitku if company else '',
                    'tanggal_ijin_entitas': company.tanggal_ijin_entitas if company else '',
                }
            ]
            self.env['ceisa.entitas'].create(entitas_vals)

            # Create pengangkut
            pengangkut_vals = [{'header_id': rec.id, 'seri_pengangkut': 1}]
            self.env['ceisa.pengangkut'].create(pengangkut_vals)

            # Invalidate records if needed
            rec.invalidate_recordset(['nomor_aju'])
            rec.sudo().invalidate_recordset()

        return records

    def _generate_json_ceisa(self):
        for rec in self:
            self.env.cr.execute("SELECT ceisa_header_json_bc40(%s)", [rec.id])

    def _get_token(self):
        company = self.env['ceisa.company.master'].search([], limit=1)
        if not company:
            raise UserError("Data perusahaan tidak ditemukan.")

        payload = {
            "username": company.username_ceisa,
            "password": company.password_ceisa
        }

        try:
            response = requests.post(
                "https://apis-gw.beacukai.go.id/nle-oauth/v1/user/login",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
        except requests.RequestException as e:
            raise UserError(f"Gagal login ke API: {str(e)}")

        response_json = response.json()
        item = response_json.get('item', {})
        access_token = item.get('access_token')
        refresh_token = item.get('refresh_token')

        if not access_token or not refresh_token:
            raise UserError("Token tidak ditemukan dalam respons API.")

        company.write({
            'access_token': access_token,
            'refresh_token': refresh_token,
        })

        return access_token

    def _send_document_to_ceisa(self, access_token):
        for rec in self:
            jsonresult = rec.jsonresult
            if not jsonresult:
                raise UserError("JSON result dari ceisa.header kosong.")

            headers = {
                'Authorization': f'Bearer {access_token}',
            }

            try:
                response = requests.post(
                    "https://apis-gw.beacukai.go.id/openapi/document",
                    headers=headers,
                    json=jsonresult,
                    timeout=60
                )
                response.raise_for_status()
            except requests.RequestException as e:
                raise UserError(f"Gagal mengirim dokumen ke Beacukai: {str(e)}")

            response_json = response.json()
            if response_json.get('status') != 'success':
                raise UserError(f"API error: {response_json.get('message', 'Unknown error')}")

    def _validate_ceisa_document(self):
        for rec in self:
            # Validate required fields in CeisaHeader
            if not rec.nomor_aju:
                raise UserError("Nomor Aju belum diisi.")
            if not rec.bruto:
                raise UserError("Berat Kotor harus diisi.")
            if not rec.kode_jenis_tpb:
                raise UserError("Kode Jenis TPB harus diisi.")
            if not rec.harga_penyerahan:
                raise UserError("Harga Penyerahan harus diisi.")
            if not rec.jabatan_ttd:
                raise UserError("Jabatan TTD harus diisi.")
            if not rec.kode_dokumen:
                raise UserError("Kode Dokumen harus diisi.")
            if not rec.kode_kantor:
                raise UserError("Kode Kantor harus diisi.")
            if not rec.kode_tujuan_pengiriman:
                raise UserError("Kode Tujuan Pengiriman harus diisi.")
            if not rec.kota_ttd:
                raise UserError("Kota TTD harus diisi.")
            if not rec.nama_ttd:
                raise UserError("Nama TTD harus diisi.")
            if not rec.netto:
                raise UserError("Berat Bersih harus diisi.")
            if not rec.nomor_aju:
                raise UserError("Nomor Aju harus diisi.")
            if not rec.tanggal_ttd:
                raise UserError("Tanggal TTD harus diisi.")

            # Validate required fields in CeisaEntitas
            if not rec.entitas_ids:
                raise UserError("Entitas belum diisi.")
            for entitas in rec.entitas_ids:
                if not entitas.alamat_entitas:
                    raise UserError("Alamat Entitas harus diisi.")
                if not entitas.kode_entitas:
                    raise UserError("Kode Entitas harus diisi.")
                if not entitas.kode_jenis_identitas:
                    raise UserError("Kode Jenis Identitas harus diisi.")
                if not entitas.nama_entitas:
                    raise UserError("Nama Entitas harus diisi.")
                if not entitas.nomor_identitas:
                    raise UserError("Nomor Identitas harus diisi.")
                if not entitas.seri_entitas:
                    raise UserError("Seri Entitas harus diisi.")

            # Validate required fields in CeisaPengangkut
            for pengangkut in rec.pengangkut_ids:
                if not pengangkut.nama_pengangkut:
                    raise UserError("Nama Pengangkut harus diisi.")
                if not pengangkut.nomor_pengangkut:
                    raise UserError("Nomor Pengangkut harus diisi.")
                if not pengangkut.seri_pengangkut:
                    raise UserError("Seri Pengangkut harus diisi.")

            # Validate required fields in CeisaKemasan
            for kemasan in rec.kemasan_ids:
                if not kemasan.jumlah_kemasan:
                    raise UserError("Jumlah Kemasan harus diisi.")
                if not kemasan.kode_jenis_kemasan:
                    raise UserError("Kode Jenis Kemasan harus diisi.")
                if not kemasan.seri_kemasan:
                    raise UserError("Seri Kemasan harus diisi.")

            # Validate required fields in CeisaPungutan
            for pungutan in rec.pungutan_ids:
                if not pungutan.kode_fasilitas_tarif:
                    raise UserError("Kode Fasilitas Tarif harus diisi.")
                if not pungutan.kode_jenis_pungutan:
                    raise UserError("Kode Jenis Pungutan harus diisi.")
                if not pungutan.nilai_pungutan:
                    raise UserError("Nilai Pungutan harus diisi.")

            # Validate required fields in CeisaBarang
            for barang in rec.barang_ids:
                if not barang.harga_penyerahan:
                    raise UserError("Harga Penyerahan harus diisi.")
                if not barang.jumlah_kemasan:
                    raise UserError("Jumlah Kemasan harus diisi.")
                if not barang.jumlah_satuan:
                    raise UserError("Jumlah Satuan harus diisi.")
                if not barang.kode_barang:
                    raise UserError("Kode Barang harus diisi.")
                if not barang.kode_dokumen:
                    raise UserError("Kode Dokumen harus diisi.")
                if not barang.kode_jenis_kemasan:
                    raise UserError("Kode Jenis Kemasan harus diisi.")
                if not barang.kode_satuan_barang:
                    raise UserError("Kode Satuan Barang harus diisi.")
                if not barang.netto:
                    raise UserError("Netto harus diisi.")
                if not barang.pos_tarif:
                    raise UserError("Pos Tarif harus diisi.")
                if not barang.seri_barang:
                    raise UserError("Seri Barang harus diisi.")
                if not barang.spesifikasi_lain:
                    raise UserError("Spesifikasi Lain harus diisi.")
                if not barang.tipe:
                    raise UserError("Tipe harus diisi.")
                if not barang.ukuran:
                    raise UserError("Ukuran harus diisi.")
                if not barang.uraian:
                    raise UserError("Uraian harus diisi.")


                # Validate required fields in barang_tarif_ids
                for tarif in barang.barang_tarif_ids:
                    if not tarif.kode_jenis_tarif:
                        raise UserError("Kode Jenis Tarif harus diisi.")
                    if not tarif.jumlah_satuan:
                        raise UserError("Jumlah Satuan harus diisi.")
                    if not tarif.kode_fasilitas_tarif:
                        raise UserError("Kode Fasilitas Tarif harus diisi.")
                    if not tarif.kode_satuan_barang:
                        raise UserError("Kode Satuan Barang harus diisi.")
                    if not tarif.seri_barang:
                        raise UserError("Seri Barang harus diisi.")
                    if not tarif.tarif:
                        raise UserError("Tarif harus diisi.")
                    if not tarif.tarif_fasilitas:
                        raise UserError("Tarif Fasilitas harus diisi.")
                    if not tarif.kode_jenis_pungutan:
                        raise UserError("Kode Jenis Pungutan harus diisi.")
                    
    def action_generate_json_document_ceisa(self):
        self._validate_ceisa_document()       # validasi semua dulu
        self._generate_json_ceisa()           # generate JSON setelah data valid
        return self._show_popup("Generate Success.", "Success")
    
    def action_post_document_ceisa(self):
        self._validate_ceisa_document()       # validasi semua dulu
        self._generate_json_ceisa()           # generate JSON setelah data valid
        access_token = self._get_token()      # ambil token
        self._send_document_to_ceisa(access_token)  # kirim dokumen

        return self._show_popup("Dokumen berhasil dikirim ke Beacukai.", "Success")
            

    def _show_popup(self, message, title):
            # Menggunakan display_notification untuk menampilkan popup notifikasi
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'message': message,
                    'sticky': False,  # Tidak perlu sticky jika ingin popup menghilang otomatis
                }
            }
    
    def action_generate_ndpbm(self):
        for record in self:
            # Force simpan perubahan di form (jika ada) sebelum ambil kurs
            record._ceisa_header_save()

            # Validasi kode_valuta harus diisi
            if not record.kode_valuta:
                raise UserError("Valuta kosong")

            # Ambil data company
            company = self.env['ceisa.company.master'].search([], limit=1)
            if not company:
                raise UserError("Data perusahaan tidak ditemukan.")

            # Langsung login ulang untuk mendapatkan token
            payload = {
                "username": company.username_ceisa,
                "password": company.password_ceisa
            }
            try:
                response = requests.post(
                    "https://apis-gw.beacukai.go.id/nle-oauth/v1/user/login",
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                item = response.json().get('item', {})
                access_token = item.get('access_token')
                refresh_token = item.get('refresh_token')

                if not access_token or not refresh_token:
                    raise UserError("Token tidak ditemukan dalam respons API.")

                company.write({
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                })
                _logger.info("Token berhasil disimpan: %s", access_token)
            except requests.RequestException as e:
                raise UserError(f"Gagal login ke API: {str(e)}")

            # Panggil API kurs
            try:
                kurs_url = f"https://apis-gw.beacukai.go.id/openapi/kurs/{record.kode_valuta}"
                headers = {
                    'Authorization': f'Bearer {access_token}'
                }
                kurs_response = requests.get(kurs_url, headers=headers, timeout=60)
                kurs_response.raise_for_status()

                kurs_json = kurs_response.json()
                if kurs_json.get("status") != "true":
                    raise UserError(f"Gagal mengambil data kurs: {kurs_json.get('message')}")

                data = kurs_json.get("data", [])
                if not data or not data[0].get("nilaiKurs"):
                    raise UserError("Nilai kurs tidak ditemukan.")

                nilai_kurs = float(data[0].get("nilaiKurs"))
                record.ndpbm = nilai_kurs
                _logger.info("NDPBM berhasil diupdate: %s", nilai_kurs)

            except requests.RequestException as e:
                raise UserError(f"Gagal mengakses API Kurs: {str(e)}")



    def _ceisa_header_save(self):
        self.ensure_one()
        self.write({})


    @api.onchange(
        'nilai_barang', 
        'biaya_tambahan', 
        'biaya_pengurang', 
        'freight', 
        'asuransi',
        'ndpbm'
    )
    def _onchange_hitung_fob_cif_penyerahan(self):
        for rec in self:
            # Pastikan kode_dokumen adalah 23
            if rec.kode_dokumen == '23':
                # Perhitungan FOB
                rec.fob = (rec.nilai_barang or 0.00) + (rec.biaya_tambahan or 0.00) - (rec.biaya_pengurang or 0.00)
                # Perhitungan CIF
                rec.cif = rec.fob + (rec.freight or 0.00) + (rec.asuransi or 0.00)
                # Perhutungan Nilai Pabean
                rec.harga_penyerahan = rec.cif * (rec.ndpbm or 0.0000)


    @api.depends(
    'nilai_barang', 
    'biaya_tambahan', 
    'biaya_pengurang', 
    'freight', 
    'asuransi', 
    'ndpbm'
    )
    def _compute_fob_cif_harga_penyerahan(self):
        for rec in self:
            # Pastikan kode_dokumen adalah 23
            if rec.kode_dokumen == '23':
                # Perhitungan FOB
                rec.fob = (rec.nilai_barang or 0.00) + (rec.biaya_tambahan or 0.00) - (rec.biaya_pengurang or 0.00)
                # Perhitungan CIF
                rec.cif = rec.fob + (rec.freight or 0.00) + (rec.asuransi or 0.00)
                # Perhutungan Nilai Pabean
                rec.harga_penyerahan = rec.cif * (rec.ndpbm or 0.0000)




    # def action_get_status_document_ceisa(self):
    #     # Contoh logika get status

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE FUNCTION public.ceisa_header_json_bc40(pid_header int4)
            RETURNS void AS $$
            DECLARE
                vJsonResult JSONB;
            BEGIN
                SELECT jsonb_build_object(
                    'asalData', 'S',
                    'asuransi', h.asuransi,
                    'bruto', h.bruto,
                    'cif', h.cif,
                    'kodeJenisTpb', h.kode_jenis_tpb,
                    'freight', h.freight,
                    'hargaPenyerahan', h.harga_penyerahan,
                    'idPengguna', h.id_pengguna,
                    'jabatanTtd', h.jabatan_ttd,
                    'jumlahKontainer', h.jumlah_kontainer,
                    'kodeDokumen', h.kode_dokumen,
                    'kodeKantor', h.kode_kantor,
                    'kodeTujuanPengiriman', h.kode_tujuan_pengiriman,
                    'kotaTtd', h.kota_ttd,
                    'namaTtd', h.nama_ttd,
                    'netto', h.netto,
                    'nik', h.nik,
                    'nomorAju', h.nomor_aju,
                    'seri', h.seri,
                    'tanggalAju', h.tanggal_aju,
                    'tanggalTtd', h.tanggal_ttd,
                    'userPortal', h.user_portal,
                    'volume', h.volume,
                    'biayaTambahan', h.biaya_tambahan,
                    'biayaPengurang', h.biaya_pengurang,
                    'vd', h.vd,
                    'uangMuka', h.uang_muka,
                    'nilaiJasa', h.nilai_jasa,
                    'entitas', (
                        SELECT COALESCE(jsonb_agg(jsonb_build_object(
                            'alamatEntitas', e.alamat_entitas,
                            'kodeEntitas', e.kode_entitas,
                            'kodeJenisApi', e.kode_jenis_api,
                            'kodeNegara', e.kode_negara,
                            'kodeJenisIdentitas', e.kode_jenis_identitas,
                            'kodeStatus', e.kode_status,
                            'namaEntitas', e.nama_entitas,
                            'nibEntitas', e.nib_entitas,
                            'nomorIdentitas', e.nomor_identitas,
                            'nomorIjinEntitas', e.nomor_ijin_entitas,
                            'tanggalIjinEntitas', e.tanggal_ijin_entitas,
                            'seriEntitas', e.seri_entitas
                        ) ORDER BY e.id::int), '[]'::jsonb)
                        FROM ceisa_entitas e
                        WHERE e.header_id = pid_header
                    ),
                    'kemasan', (
                        SELECT COALESCE(jsonb_agg(jsonb_build_object(
                            'jumlahKemasan', k.jumlah_kemasan,
                            'kodeJenisKemasan', k.kode_jenis_kemasan,
                            'seriKemasan', k.seri_kemasan,
                            'merkKemasan', k.merk_kemasan
                        ) ORDER BY k.id::int), '[]'::jsonb)
                        FROM ceisa_kemasan k
                        WHERE k.header_id = pid_header
                    ),
                    'kontainer', (
                        SELECT COALESCE(jsonb_agg(jsonb_build_object(
                            'kodeTipeKontainer', k.kode_tipe_kontainer,
                            'kodeUkuranKontainer', k.kode_ukuran_kontainer,
                            'seriKontainer', k.seri_kontainer,
                            'nomorKontainer', k.nomor_kontainer,
                            'kodeJenisKontainer', k.kode_jenis_kontainer
                        ) ORDER BY k.id::int), '[]'::jsonb)
                        FROM ceisa_kontainer k
                        WHERE k.header_id = pid_header
                    ),
                    'dokumen', (
                        SELECT COALESCE(jsonb_agg(jsonb_build_object(
                            'idDokumen', d.seri_dokumen::text,
                            'kodeDokumen', d.kode_dokumen,
                            'nomorDokumen', d.nomor_dokumen,
                            'seriDokumen', d.seri_dokumen,
                            'tanggalDokumen', d.tanggal_dokumen
                        ) ORDER BY d.id::int), '[]'::jsonb)
                        FROM ceisa_dokumen d
                        WHERE d.header_id = pid_header
                    ),
                    'pungutan', (
                        SELECT COALESCE(jsonb_agg(jsonb_build_object(
                            'kodeFasilitasTarif', p.kode_fasilitas_tarif,
                            'kodeJenisPungutan', p.kode_jenis_pungutan,
                            'nilaiPungutan', p.nilai_pungutan
                        ) ORDER BY p.id::int), '[]'::jsonb)
                        FROM ceisa_pungutan p
                        WHERE p.header_id = pid_header
                    ),
                    'pengangkut', (
                        SELECT COALESCE(jsonb_agg(jsonb_build_object(
                            'kodeBendera', COALESCE(pg.kode_bendera, ''),
                            'namaPengangkut', pg.nama_pengangkut,
                            'nomorPengangkut', pg.nomor_pengangkut,
                            'kodeCaraAngkut', pg.kode_cara_angkut,
                            'seriPengangkut', pg.seri_pengangkut
                        ) ORDER BY pg.id::int), '[]'::jsonb)
                        FROM ceisa_pengangkut pg
                        WHERE pg.header_id = pid_header
                    ),
                    'barang', (
                        SELECT COALESCE(jsonb_agg(jsonb_build_object(
                            'asuransi', b.asuransi,
                            'bruto', b.bruto,
                            'cif', b.cif,
                            'diskon', b.diskon,
                            'hargaEkspor', b.harga_ekspor,
                            'hargaPenyerahan', b.harga_penyerahan,
                            'hargaSatuan', b.harga_satuan,
                            'isiPerKemasan', b.isi_per_kemasan,
                            'jumlahKemasan', b.jumlah_kemasan,
                            'jumlahRealisasi', b.jumlah_realisasi,
                            'jumlahSatuan', b.jumlah_satuan,
                            'kodeBarang', b.kode_barang,
                            'kodeDokumen', b.kode_dokumen,
                            'kodeJenisKemasan', b.kode_jenis_kemasan,
                            'kodeSatuanBarang', b.kode_satuan_barang,
                            'merk', b.merk,
                            'netto', b.netto,
                            'nilaiBarang', b.nilai_barang,
                            'posTarif', b.pos_tarif,
                            'seriBarang', b.seri_barang,
                            'spesifikasiLain', b.spesifikasi_lain,
                            'tipe', b.tipe,
                            'ukuran', b.ukuran,
                            'uraian', b.uraian,
                            'volume', b.volume,
                            'cifRupiah', b.cif_rupiah,
                            'hargaPerolehan', b.harga_perolehan,
                            'kodeAsalBahanBaku', b.kode_asal_bahan_baku,
                            'ndpbm', b.ndpbm,
                            'uangMuka', b.uang_muka,
                            'nilaiJasa', b.nilai_jasa,
                            'barangTarif', (
                                SELECT COALESCE(jsonb_agg(jsonb_build_object(
                                    'kodeJenisTarif', t.kode_jenis_tarif,
                                    'jumlahSatuan', t.jumlah_satuan,
                                    'kodeFasilitasTarif', t.kode_fasilitas_tarif,
                                    'kodeSatuanBarang', t.kode_satuan_barang,
                                    'nilaiBayar', t.nilai_bayar,
                                    'nilaiFasilitas', t.nilai_fasilitas,
                                    'nilaiSudahDilunasi', t.nilai_sudah_dilunasi,
                                    'seriBarang', t.seri_barang,
                                    'tarif', t.tarif,
                                    'tarifFasilitas', t.tarif_fasilitas,
                                    'kodeJenisPungutan', t.kode_jenis_pungutan
                                ) ORDER BY t.id::int), '[]'::jsonb)
                                FROM ceisa_barang_tarif t
                                WHERE t.barang_id = b.id
                            )
                        ) ORDER BY b.id::int), '[]'::jsonb)
                        FROM ceisa_barang b
                        WHERE b.header_id = pid_header
                    )
                )
                INTO vJsonResult
                FROM ceisa_header h
                WHERE h.id = pid_header;

                IF vJsonResult IS NOT NULL THEN
                    UPDATE ceisa_header
                    SET jsonresult = vJsonResult
                    WHERE id = pid_header;
                ELSE
                    RAISE NOTICE 'No data found for header ID: %', pid_header;
                END IF;

            EXCEPTION
                WHEN OTHERS THEN
                    RAISE NOTICE 'Error encountered: %', SQLERRM;
            END;
            $$
            LANGUAGE plpgsql
            VOLATILE
            COST 100;
        """)

    def init(self):
        self.env.cr.execute("""
        CREATE OR REPLACE FUNCTION "public"."ceisa_header_json_bc23"("pid_header" int4)
        RETURNS "pg_catalog"."void" AS $BODY$
        DECLARE
            vJsonResult JSONB;
        BEGIN
            SELECT jsonb_build_object(
                'asalData', 'S',
                'asuransi', h.asuransi,
                'bruto', h.bruto,
                'cif', h.cif,
                'freight', h.freight,
                'hargaPenyerahan', h.harga_penyerahan,
                'jabatanTtd', h.jabatan_ttd,
                'jumlahKontainer', h.jumlah_kontainer,
                'kodeDokumen', h.kode_dokumen,
                'kodeKantor', h.kode_kantor,
                'kodeTujuanPengiriman', h.kode_tujuan_pengiriman,
                'kotaTtd', h.kota_ttd,
                'namaTtd', h.nama_ttd,
                'netto', h.netto,
                'nik', h.nik,
                'nomorAju', h.nomor_aju,
                'seri', h.seri,
                'tanggalAju', h.tanggal_aju,
                'tanggalTtd', h.tanggal_ttd,
                'volume', h.volume,
                'biayaTambahan', h.biaya_tambahan,
                'biayaPengurang', h.biaya_pengurang,
                'vd', h.vd,
                'uangMuka', h.uang_muka,
                'nilaiJasa', h.nilai_jasa,
                'fob', h.fob,
                'ndpbm', h.ndpbm,
                'tanggalTiba', h.tanggal_tiba,
                'kodePelMuat', h.kode_pel_muat,
                'kodePelBongkar', h.kode_pel_bongkar,
                'kodePelTransit', h.kode_pel_transit,
                'kodeTps', h.kode_tps,
                'kodeTujuanTpb', h.kode_tujuan_tpb,
                'kodeTutupPu', h.kode_tutup_pu,
                'kodeValuta', h.kode_valuta,
                'kodeAsuransi', h.kode_asuransi,
                'kodeIncoterm', h.kode_incoterm,
                'kodeKantorBongkar', h.kode_kantor_bongkar,
                'nilaiBarang', h.nilai_barang,
                'nomorBc11', h.nomor_bc11,
                'posBc11', h.pos_bc11,
                'subposBc11', COALESCE(h.subpos_bc11_1, '') || COALESCE(h.subpos_bc11_2, ''),
                'tanggalBc11', h.tanggal_bc11,
                'entitas', (
                    SELECT COALESCE(jsonb_agg(jsonb_build_object(
                        'alamatEntitas', e.alamat_entitas,
                        'kodeEntitas', e.kode_entitas,
                        'kodeJenisApi', e.kode_jenis_api,
                        'kodeNegara', e.kode_negara,
                        'kodeJenisIdentitas', e.kode_jenis_identitas,
                        'kodeStatus', e.kode_status,
                        'namaEntitas', e.nama_entitas,
                        'nibEntitas', e.nib_entitas,
                        'nomorIdentitas', e.nomor_identitas,
                        'nomorIjinEntitas', e.nomor_ijin_entitas,
                        'tanggalIjinEntitas', e.tanggal_ijin_entitas,
                        'seriEntitas', e.seri_entitas
                    ) ORDER BY e.id::int), '[]'::jsonb)
                    FROM ceisa_entitas e
                    WHERE e.header_id = pid_header
                ),

                -- KEMASAN
                'kemasan', (
                    SELECT COALESCE(jsonb_agg(jsonb_build_object(
                        'jumlahKemasan', k.jumlah_kemasan,
                        'kodeJenisKemasan', k.kode_jenis_kemasan,
                        'seriKemasan', k.seri_kemasan,
                        'merkKemasan', k.merk_kemasan
                    )), '[]'::jsonb)
                    FROM ceisa_kemasan k
                    WHERE k.header_id = pid_header
                ),

                -- KONTAINER
                'kontainer', (
                    SELECT COALESCE(jsonb_agg(jsonb_build_object(
                        'kodeTipeKontainer', k.kode_tipe_kontainer,
                        'kodeUkuranKontainer', k.kode_ukuran_kontainer,
                        'seriKontainer', k.seri_kontainer,
                        'nomorKontainer', k.nomor_kontainer,
                        'kodeJenisKontainer', k.kode_jenis_kontainer
                    )), '[]'::jsonb)
                    FROM ceisa_kontainer k
                    WHERE k.header_id = pid_header
                ),

                -- DOKUMEN
                'dokumen', (
                    SELECT COALESCE(jsonb_agg(jsonb_build_object(
                        'idDokumen', d.seri_dokumen::text,
                        'kodeDokumen', d.kode_dokumen,
                        'nomorDokumen', d.nomor_dokumen,
                        'seriDokumen', d.seri_dokumen,
                        'tanggalDokumen', d.tanggal_dokumen
                    )), '[]'::jsonb)
                    FROM ceisa_dokumen d
                    WHERE d.header_id = pid_header
                ),

                -- PUNGUTAN
                'pungutan', (
                    SELECT COALESCE(jsonb_agg(jsonb_build_object(
                        'kodeFasilitasTarif', p.kode_fasilitas_tarif,
                        'kodeJenisPungutan', p.kode_jenis_pungutan,
                        'nilaiPungutan', p.nilai_pungutan
                    )), '[]'::jsonb)
                    FROM ceisa_pungutan p
                    WHERE p.header_id = pid_header
                ),

                -- PENGANGKUT
                'pengangkut', (
                    SELECT COALESCE(jsonb_agg(jsonb_build_object(
                        'kodeBendera', COALESCE(pg.kode_bendera, ''),
                        'namaPengangkut', pg.nama_pengangkut,
                        'nomorPengangkut', pg.nomor_pengangkut,
                        'kodeCaraAngkut', pg.kode_cara_angkut,
                        'seriPengangkut', pg.seri_pengangkut
                    )), '[]'::jsonb)
                    FROM ceisa_pengangkut pg
                    WHERE pg.header_id = pid_header
                ),

                -- BARANG
                'barang', (
                    SELECT COALESCE(jsonb_agg(jsonb_build_object(
                        'asuransi', b.asuransi,
                        'bruto', b.bruto,
                        'cif', b.cif,
                        'diskon', b.diskon,
                        'hargaEkspor', b.harga_ekspor,
                        'hargaPenyerahan', b.harga_penyerahan,
                        'hargaSatuan', b.harga_satuan,
                        'isiPerKemasan', b.isi_per_kemasan,
                        'jumlahKemasan', b.jumlah_kemasan,
                        'jumlahRealisasi', b.jumlah_realisasi,
                        'jumlahSatuan', b.jumlah_satuan,
                        'kodeBarang', b.kode_barang,
                        'kodeDokumen', b.kode_dokumen,
                        'kodeJenisKemasan', b.kode_jenis_kemasan,
                        'kodeSatuanBarang', b.kode_satuan_barang,
                        'merk', b.merk,
                        'netto', b.netto,
                        'nilaiBarang', b.nilai_barang,
                        'posTarif', b.pos_tarif,
                        'seriBarang', b.seri_barang,
                        'spesifikasiLain', b.spesifikasi_lain,
                        'tipe', b.tipe,
                        'ukuran', b.ukuran,
                        'uraian', b.uraian,
                        'volume', b.volume,
                        'cifRupiah', b.cif_rupiah,
                        'hargaPerolehan', b.harga_perolehan,
                        'kodeAsalBahanBaku', b.kode_asal_bahan_baku,
                        'ndpbm', b.ndpbm,
                        'uangMuka', b.uang_muka,
                        'nilaiJasa', b.nilai_jasa,
                        'fob', b.fob,
                        'freight', b.freight,
                        'kodeKategoriBarang', b.kode_kategori_barang,
                        'kodeNegaraAsal', b.kode_negara_asal,
                        'kodePerhitungan', b.kode_perhitungan,
                        'nilaiTambah', b.nilai_tambah,
                        'barangTarif', (
                            SELECT COALESCE(jsonb_agg(jsonb_build_object(
                                'kodeJenisTarif', t.kode_jenis_tarif,
                                'jumlahSatuan', t.jumlah_satuan,
                                'kodeFasilitasTarif', t.kode_fasilitas_tarif,
                                'kodeSatuanBarang', t.kode_satuan_barang,
                                'nilaiBayar', t.nilai_bayar,
                                'nilaiFasilitas', t.nilai_fasilitas,
                                'nilaiSudahDilunasi', t.nilai_sudah_dilunasi,
                                'seriBarang', t.seri_barang,
                                'tarif', t.tarif,
                                'tarifFasilitas', t.tarif_fasilitas,
                                'kodeJenisPungutan', t.kode_jenis_pungutan
                            ) ORDER BY t.id::int), '[]'::jsonb)
                            FROM ceisa_barang_tarif t
                            WHERE t.barang_id = b.id
                        ),
                        'barangDokumen', (
                            SELECT COALESCE(jsonb_agg(jsonb_build_object(
                                'seriDokumen', bd.seri_dokumen
                            )), '[]'::jsonb)
                            FROM ceisa_barang_dokumen bd
                            WHERE bd.barang_id = b.id
                        )
                    )), '[]'::jsonb)
                    FROM ceisa_barang b
                    WHERE b.header_id = pid_header
                )
            )
            INTO vJsonResult
            FROM ceisa_header h
            WHERE h.id = pid_header;

            IF vJsonResult IS NOT NULL THEN
                UPDATE ceisa_header
                SET jsonresult = vJsonResult
                WHERE id = pid_header;
            ELSE
                RAISE NOTICE 'No data found for header ID: %', pid_header;
            END IF;

        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Error encountered: %', SQLERRM;
        END;
        $BODY$
        LANGUAGE plpgsql VOLATILE
        COST 100
        """)

        self.env.cr.execute("""
            CREATE OR REPLACE FUNCTION set_nomor_aju()
            RETURNS TRIGGER AS $$
            DECLARE
                npwp TEXT;
                tgl_str TEXT := TO_CHAR(NOW(), 'YYYYMMDD');
                urut INT;
                urut_str TEXT;
                kode_dokumen_str TEXT;
                numbering_id INT;
       
            BEGIN
                -- Ambil NPWP dari ceisa_company_master
                SELECT LEFT(npwp_perusahaan, 6) INTO npwp FROM ceisa_company_master ORDER BY id LIMIT 1;
                IF npwp IS NULL THEN
                    npwp := '000000';
                END IF;

                -- Format kode_dokumen ke 6 digit
                kode_dokumen_str := LPAD(NEW.kode_dokumen, 6, '0');

                -- Ambil counter dari ceisa_numbering_master
                SELECT id, counter INTO numbering_id, urut
                FROM ceisa_numbering_master
                WHERE kode_dokumen = NEW.kode_dokumen
                ORDER BY id
                LIMIT 1;

                IF numbering_id IS NULL THEN
                    RAISE EXCEPTION 'Gagal generate nomor aju: Data numbering tidak ditemukan untuk kode_dokumen = %', NEW.kode_dokumen;
                END IF;

                urut_str := LPAD(urut::TEXT, 6, '0');
                NEW.nomor_aju := kode_dokumen_str || npwp || tgl_str || urut_str;

                -- Update counter ke counter + 1
                UPDATE ceisa_numbering_master SET counter = urut + 1 WHERE id = numbering_id;

                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        self.env.cr.execute("""
            DROP TRIGGER IF EXISTS trg_set_nomor_aju ON ceisa_header;
            CREATE TRIGGER trg_set_nomor_aju
            BEFORE INSERT ON ceisa_header
            FOR EACH ROW EXECUTE FUNCTION set_nomor_aju();
        """)



        self.env.cr.execute("""
            CREATE OR REPLACE FUNCTION generate_pungutan(p_header_id INTEGER)
            RETURNS VOID AS $$
            DECLARE
                v_harga_penyerahan NUMERIC(18, 4) := 0;
                v_nilai_jasa NUMERIC(18, 4) := 0;
                v_uang_muka NUMERIC(18, 4) := 0;
                v_harga_perolehan NUMERIC(18, 2) := 0;
                v_volume NUMERIC(20, 4) := 0;
                v_netto NUMERIC(20, 4) := 0;
                v_nilai_pabean NUMERIC(18, 4) := 0;
                v_nilai_impor NUMERIC(18, 4) := 0;
                v_bm NUMERIC(18, 4) := 0;
                v_pph NUMERIC(18, 4) := 0;
                v_ppn NUMERIC(18, 4) := 0;
                v_bm_tarif NUMERIC(18, 4) := 0;
                v_pph_tarif NUMERIC(18, 4) := 0;
                v_ppn_tarif NUMERIC(18, 4) := 0;
                v_bm_fasilitas_tarif VARCHAR := ''; -- Menggunakan tipe VARCHAR
                v_pph_fasilitas_tarif VARCHAR := ''; -- Menggunakan tipe VARCHAR
                v_ppn_fasilitas_tarif VARCHAR := ''; -- Menggunakan tipe VARCHAR
            BEGIN
                -- Cek apakah kode_dokumen adalah 40
                IF EXISTS (SELECT 1 FROM ceisa_header WHERE id = p_header_id AND kode_dokumen = '40') THEN
                    -- 1. Hapus pungutan lama jenis PPN
                    DELETE FROM ceisa_pungutan
                    WHERE header_id = p_header_id;

                    -- 2. Insert ulang berdasarkan barang & tarif untuk PPN
                    INSERT INTO ceisa_pungutan (header_id, kode_jenis_pungutan, nilai_pungutan, kode_fasilitas_tarif)
                    SELECT
                        b.header_id,
                        'PPN',
                        SUM(b.harga_penyerahan * t.tarif / t.tarif_fasilitas),
                        t.kode_fasilitas_tarif -- Ambil kode_fasilitas_tarif dari ceisa_barang
                    FROM ceisa_barang b
                    JOIN ceisa_barang_tarif t ON t.barang_id = b.id
                    JOIN ceisa_header h ON h.id = b.header_id
                    WHERE b.header_id = p_header_id
                    AND t.kode_jenis_pungutan = 'PPN'
                    GROUP BY b.header_id, t.kode_fasilitas_tarif; -- Kelompokkan berdasarkan kode_fasilitas_tarif yang ada di ceisa_barang

                    -- 3. Update ceisa_header dari total ceisa_barang
                    SELECT
                        COALESCE(SUM(harga_penyerahan), 0),
                        COALESCE(SUM(nilai_jasa), 0),
                        COALESCE(SUM(uang_muka), 0),
                        COALESCE(SUM(harga_perolehan), 0),
                        COALESCE(SUM(volume), 0),
                        COALESCE(SUM(netto), 0)
                    INTO
                        v_harga_penyerahan,
                        v_nilai_jasa,
                        v_uang_muka,
                        v_harga_perolehan,
                        v_volume,
                        v_netto
                    FROM ceisa_barang
                    WHERE header_id = p_header_id;

                    UPDATE ceisa_header
                    SET
                        harga_penyerahan = v_harga_penyerahan,
                        nilai_jasa = v_nilai_jasa,
                        uang_muka = v_uang_muka,
                        harga_perolehan = v_harga_perolehan,
                        volume = v_volume,
                        netto = v_netto
                    WHERE id = p_header_id;

                -- Cek apakah kode_dokumen adalah 23
                ELSIF EXISTS (SELECT 1 FROM ceisa_header WHERE id = p_header_id AND kode_dokumen = '23') THEN
                    -- 1. Hapus pungutan lama
                    DELETE FROM ceisa_pungutan
                    WHERE header_id = p_header_id;

                    -- 2. Ambil Nilai Pabean
                    SELECT
                        COALESCE(harga_penyerahan, 0) INTO v_nilai_pabean
                    FROM ceisa_header
                    WHERE id = p_header_id;

                    -- 3. Hitung Nilai BM 
                    SELECT 
                        COALESCE(SUM(t.tarif / t.tarif_fasilitas), 0) INTO v_bm_tarif
                    FROM ceisa_barang_tarif t
                    JOIN ceisa_barang b ON t.barang_id = b.id
                    WHERE b.header_id = p_header_id
                    AND t.kode_jenis_pungutan = 'BM';

                    -- 
                    v_bm := CEIL(v_nilai_pabean * v_bm_tarif / 1000) * 1000;                      

                    -- 4. Hitung Nilai Impor (Nilai Pabean + Nilai BM)
                    v_nilai_impor := v_nilai_pabean + v_bm;

                    -- 5. Hitung PPH
                    SELECT 
                        COALESCE(SUM(t.tarif / t.tarif_fasilitas), 0) INTO v_pph_tarif
                    FROM ceisa_barang_tarif t
                    JOIN ceisa_barang b ON t.barang_id = b.id
                    WHERE b.header_id = p_header_id
                    AND t.kode_jenis_pungutan = 'PPH';

                    v_pph := CEIL(v_nilai_impor * v_pph_tarif / 1000) * 1000;

                    -- 6. Hitung PPN
                    SELECT 
                        COALESCE(SUM(t.tarif / t.tarif_fasilitas), 0) INTO v_ppn_tarif
                    FROM ceisa_barang_tarif t
                    JOIN ceisa_barang b ON t.barang_id = b.id
                    WHERE b.header_id = p_header_id
                    AND t.kode_jenis_pungutan = 'PPN';

                    v_ppn := CEIL(v_nilai_impor * v_ppn_tarif / 1000) * 1000;

                    -- 7. Ambil kode_fasilitas_tarif dari ceisa_barang berdasarkan kode_jenis_pungutan
                    -- Untuk BM
                    SELECT
                        t.kode_fasilitas_tarif INTO v_bm_fasilitas_tarif
                    FROM ceisa_barang b
                    JOIN ceisa_barang_tarif t ON t.barang_id = b.id
                    WHERE b.header_id = p_header_id
                    AND t.kode_jenis_pungutan = 'BM'
                    LIMIT 1;

                    -- Untuk PPH
                    SELECT
                        t.kode_fasilitas_tarif INTO v_pph_fasilitas_tarif
                    FROM ceisa_barang b
                    JOIN ceisa_barang_tarif t ON t.barang_id = b.id
                    WHERE b.header_id = p_header_id
                    AND t.kode_jenis_pungutan = 'PPH'
                    LIMIT 1;

                    -- Untuk PPN
                    SELECT
                        t.kode_fasilitas_tarif INTO v_ppn_fasilitas_tarif
                    FROM ceisa_barang b
                    JOIN ceisa_barang_tarif t ON t.barang_id = b.id
                    WHERE b.header_id = p_header_id
                    AND t.kode_jenis_pungutan = 'PPN'
                    LIMIT 1;

                    -- 8. Insert Pungutan BM
                    INSERT INTO ceisa_pungutan (header_id, kode_jenis_pungutan, nilai_pungutan, kode_fasilitas_tarif)
                    VALUES
                        (p_header_id, 'BM', v_bm, v_bm_fasilitas_tarif); -- Ambil kode_fasilitas_tarif dari ceisa_barang

                    -- 9. Insert Pungutan PPH
                    INSERT INTO ceisa_pungutan (header_id, kode_jenis_pungutan, nilai_pungutan, kode_fasilitas_tarif)
                    VALUES
                        (p_header_id, 'PPH', v_pph, v_pph_fasilitas_tarif); -- Ambil kode_fasilitas_tarif dari ceisa_barang

                    -- 10. Insert Pungutan PPN
                    INSERT INTO ceisa_pungutan (header_id, kode_jenis_pungutan, nilai_pungutan, kode_fasilitas_tarif)
                    VALUES
                        (p_header_id, 'PPN', v_ppn, v_ppn_fasilitas_tarif); -- Ambil kode_fasilitas_tarif dari ceisa_barang

                    SELECT
                        COALESCE(SUM(netto), 0)
                    INTO
                        v_netto
                    FROM ceisa_barang
                    WHERE header_id = p_header_id;

                    UPDATE ceisa_header
                    SET
                        netto = v_netto
                    WHERE id = p_header_id;

                END IF;
            END;
        $$ LANGUAGE plpgsql;
        """)



    def action_open_item_reference_wizard(self):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pilih Barang Referensi',
                'res_model': 'item.reference.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_header_id': self.id,
                }
            }

    def action_generate_pungutan(self):
        for rec in self:
            self.env.cr.execute("SELECT generate_pungutan(%s)", [rec.id])


    pungutan_pivot_ids = fields.One2many(
        'vw.pungutan.pivot',
        'header_id',
        string='Pivot Pungutan'
    )



class CeisaEntitas(models.Model):
    _name = 'ceisa.entitas'
    _description = 'Entitas'

    header_id = fields.Many2one('ceisa.header')
    alamat_entitas = fields.Char(default='')
    kode_entitas = fields.Char(default='')
    kode_jenis_api = fields.Char(default='02')
    kode_negara = fields.Char(default='')
    kode_jenis_identitas = fields.Char(default='')
    kode_status = fields.Char(default='')
    nama_entitas = fields.Char(default='')
    nib_entitas = fields.Char(default='')
    nomor_identitas = fields.Char(default='')
    nomor_ijin_entitas = fields.Char(default='')
    tanggal_ijin_entitas = fields.Date()
    seri_entitas = fields.Integer()
    nitku = fields.Char(default='')



class CeisaKemasan(models.Model):
    _name = 'ceisa.kemasan'
    _description = 'Kemasan'

    header_id = fields.Many2one('ceisa.header')
    jumlah_kemasan = fields.Integer()
    kode_jenis_kemasan = fields.Char(string='Kode Jenis Kemasan', default='')
    kemasan_lookup = fields.Many2one(
        'ceisa.referensi.kemasan',
        string='Jenis Kemasan',
        compute='_compute_kemasan_lookup',
        inverse='_inverse_kemasan_lookup',
        store=False,
    )

    @api.depends('kode_jenis_kemasan')
    def _compute_kemasan_lookup(self):
        for rec in self:
            rec.kemasan_lookup = self.env['ceisa.referensi.kemasan'].search([
                ('kode_kemasan', '=', rec.kode_jenis_kemasan)
            ], limit=1)

    def _inverse_kemasan_lookup(self):
        for rec in self:
            if rec.kemasan_lookup:
                rec.kode_jenis_kemasan = rec.kemasan_lookup.kode_kemasan
    
    seri_kemasan = fields.Integer()
    merk_kemasan = fields.Char(default='')

    @api.onchange('header_id')
    def _onchange_set_seri_kemasan(self):
        if self.header_id and not self.seri_kemasan:
            other_docs = self.header_id.kemasan_ids.filtered(lambda d: d != self)
            self.seri_kemasan = len(other_docs) + 1



class CeisaKontainer(models.Model):
    _name = 'ceisa.kontainer'
    _description = 'Kontainer'

    header_id = fields.Many2one('ceisa.header')
    seri_kontainer = fields.Integer()
    nomor_kontainer = fields.Char(default='')
    
    kode_ukuran_kontainer = fields.Char(default='')
    ukuran_kontainer_lookup = fields.Many2one(
        'ceisa.referensi.ukuran.kontainer',
        string='Ukuran Kontainer',
        compute='_compute_ukuran_lookup',
        inverse='_inverse_ukuran_lookup',
        store=False,
    )

    @api.depends('kode_ukuran_kontainer')
    def _compute_ukuran_lookup(self):
        for rec in self:
            rec.ukuran_kontainer_lookup = self.env['ceisa.referensi.ukuran.kontainer'].search([
                ('kode_ukuran_kontainer', '=', rec.kode_ukuran_kontainer)
            ], limit=1)

    def _inverse_ukuran_lookup(self):
        for rec in self:
            if rec.ukuran_kontainer_lookup:
                rec.kode_ukuran_kontainer = rec.ukuran_kontainer_lookup.kode_ukuran_kontainer
    
    kode_jenis_kontainer = fields.Char(default='')
    jenis_kontainer_lookup = fields.Many2one(
        'ceisa.referensi.jenis.kontainer',
        string='Jenis Kontainer',
        compute='_compute_jenis_lookup',
        inverse='_inverse_jenis_lookup',
        store=False,
    )

    @api.depends('kode_jenis_kontainer')
    def _compute_jenis_lookup(self):
        for rec in self:
            rec.jenis_kontainer_lookup = self.env['ceisa.referensi.jenis.kontainer'].search([
                ('kode_jenis_kontainer', '=', rec.kode_jenis_kontainer)
            ], limit=1)

    def _inverse_jenis_lookup(self):
        for rec in self:
            if rec.jenis_kontainer_lookup:
                rec.kode_jenis_kontainer = rec.jenis_kontainer_lookup.kode_jenis_kontainer
    
    kode_tipe_kontainer = fields.Char(default='')
    tipe_kontainer_lookup = fields.Many2one(
    'ceisa.referensi.tipe.kontainer',
    string='Tipe Kontainer',
    compute='_compute_tipe_lookup',
    inverse='_inverse_tipe_lookup',
    store=False,
    )

    @api.depends('kode_tipe_kontainer')
    def _compute_tipe_lookup(self):
        for rec in self:
            rec.tipe_kontainer_lookup = self.env['ceisa.referensi.tipe.kontainer'].search([
                ('kode_tipe_kontainer', '=', rec.kode_tipe_kontainer)
            ], limit=1)

    def _inverse_tipe_lookup(self):
        for rec in self:
            if rec.tipe_kontainer_lookup:
                rec.kode_tipe_kontainer = rec.tipe_kontainer_lookup.kode_tipe_kontainer
    
    @api.onchange('header_id')
    def _onchange_set_seri_kontainer(self):
        if self.header_id and not self.seri_kontainer:
            other_docs = self.header_id.kontainer_ids.filtered(lambda d: d != self)
            self.seri_kontainer = len(other_docs) + 1



class CeisaDokumen(models.Model):
    _name = 'ceisa.dokumen'
    _description = 'Dokumen'

    header_id = fields.Many2one('ceisa.header')
    kode_dokumen = fields.Char(string='Kode Dokumen', default='')

    dokumen_lookup = fields.Many2one(
        'ceisa.referensi.dokumen',
        string='Jenis Dokumen',
        compute='_compute_dokumen_lookup',
        inverse='_inverse_dokumen_lookup',
        store=False
    )

    @api.depends('kode_dokumen')
    def _compute_dokumen_lookup(self):
        for rec in self:
            rec.dokumen_lookup = self.env['ceisa.referensi.dokumen'].search([
                ('kode_dokumen', '=', rec.kode_dokumen)
            ], limit=1)

    def _inverse_dokumen_lookup(self):
        for rec in self:
            if rec.dokumen_lookup:
                rec.kode_dokumen = rec.dokumen_lookup.kode_dokumen
    
    nomor_dokumen = fields.Char(default='')
    seri_dokumen = fields.Integer()
    tanggal_dokumen = fields.Date()

    @api.onchange('header_id')
    def _onchange_set_seri_dokumen(self):
        if self.header_id and not self.seri_dokumen:
            other_docs = self.header_id.dokumen_ids.filtered(lambda d: d != self)
            self.seri_dokumen = len(other_docs) + 1



class CeisaPungutan(models.Model):
    _name = 'ceisa.pungutan'
    _description = 'Pungutan'

    header_id = fields.Many2one('ceisa.header')
    kode_fasilitas_tarif = fields.Char(default='')
    kode_jenis_pungutan = fields.Char(default='')
    nilai_pungutan = fields.Float(digits=(18, 2), default=0.00)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW vw_pungutan_pivot AS
            SELECT
            ceisa_pungutan."id", 
            ceisa_pungutan.header_id,
            COALESCE(
                CASE
                    WHEN ceisa_pungutan.kode_fasilitas_tarif = '3' THEN ceisa_pungutan.nilai_pungutan
                    ELSE NULL
                END, 0
            ) AS ditangguhkan,
            COALESCE(
                CASE
                    WHEN ceisa_pungutan.kode_fasilitas_tarif = '7' THEN ceisa_pungutan.nilai_pungutan
                    ELSE NULL
                END, 0
            ) AS dibebaskan,
            COALESCE(
                CASE
                    WHEN ceisa_pungutan.kode_fasilitas_tarif = '5' THEN ceisa_pungutan.nilai_pungutan
                    ELSE NULL
                END, 0
            ) AS sudah_dilunasi,
            COALESCE(
                CASE
                    WHEN ceisa_pungutan.kode_fasilitas_tarif = '6' THEN ceisa_pungutan.nilai_pungutan
                    ELSE NULL
                END, 0
            ) AS tidak_dipungut,
            ceisa_pungutan.kode_jenis_pungutan
        FROM
            ceisa_pungutan;
        """)


class CeisaPengangkut(models.Model):
    _name = 'ceisa.pengangkut'
    _description = 'Pengangkut'

    header_id = fields.Many2one('ceisa.header')

    kode_bendera = fields.Char(string='Kode Bendera', default='')
    bendera_lookup = fields.Many2one(
        'ceisa.referensi.negara',
        string='Negara Bendera',
        compute='_compute_bendera_lookup',
        inverse='_inverse_bendera_lookup',
        store=False
    )

    @api.depends('kode_bendera')
    def _compute_bendera_lookup(self):
        for rec in self:
            rec.bendera_lookup = self.env['ceisa.referensi.negara'].search([
                ('kode_negara', '=', rec.kode_bendera)
            ], limit=1)

    def _inverse_bendera_lookup(self):
        for rec in self:
            if rec.bendera_lookup:
                rec.kode_bendera = rec.bendera_lookup.kode_negara

    nama_pengangkut = fields.Char(default='')
    nomor_pengangkut = fields.Char(default='')
    kode_cara_angkut = fields.Char(string='Kode Cara Angkut', default='')
    cara_angkut_lookup = fields.Many2one(
        'ceisa.referensi.cara.angkut',
        string='Cara Angkut',
        compute='_compute_cara_angkut_lookup',
        inverse='_inverse_cara_angkut_lookup',
        store=False
    )

    @api.depends('kode_cara_angkut')
    def _compute_cara_angkut_lookup(self):
        for rec in self:
            rec.cara_angkut_lookup = self.env['ceisa.referensi.cara.angkut'].search([
                ('kode_cara_angkut', '=', rec.kode_cara_angkut)
            ], limit=1)

    def _inverse_cara_angkut_lookup(self):
        for rec in self:
            if rec.cara_angkut_lookup:
                rec.kode_cara_angkut = rec.cara_angkut_lookup.kode_cara_angkut
    
    seri_pengangkut = fields.Integer()

    @api.onchange('header_id')
    def _onchange_set_seri_pengangkut(self):
        if self.header_id and not self.seri_pengangkut:
            other_docs = self.header_id.pengangkut_ids.filtered(lambda d: d != self)
            self.seri_pengangkut = len(other_docs) + 1




class CeisaBarang(models.Model):
    _name = 'ceisa.barang'
    _description = 'Barang'

    header_id = fields.Many2one('ceisa.header')
    barang_tarif_ids = fields.One2many('ceisa.barang.tarif', 'barang_id', string='Barang Tarif')
    barang_dokumen_ids = fields.One2many('ceisa.barang.dokumen', 'barang_id', string='Barang Dokumen')

    asuransi = fields.Float(digits=(18, 2), default=0.00, string="Asuransi")
    bruto = fields.Float(digits=(20, 4), default=0.0000)
    cif = fields.Float(digits=(18, 2), default=0.00, string="CIF")
    diskon = fields.Float(digits=(18, 2), default=0.00)
    harga_ekspor = fields.Float(digits=(18, 4), default=0.0000)
    harga_penyerahan = fields.Float(digits=(18, 4), default=0.0000, string="Harga Penyerahan")
    harga_satuan = fields.Float(digits=(18, 4), default=0.0000, string="Harga Satuan")
    isi_per_kemasan = fields.Float(digits=(18, 2), default=0.00)
    jumlah_kemasan = fields.Float(digits=(18, 2), default=0.00)
    jumlah_realisasi = fields.Float(digits=(18, 4), default=0.0000)
    jumlah_satuan = fields.Float(digits=(24, 4), default=0.0000)
    kode_barang = fields.Char(default='')
    kode_dokumen = fields.Char(default='')
    kode_jenis_kemasan = fields.Char(default='')
    kode_satuan_barang = fields.Char(default='')
    merk = fields.Char(default='')
    netto = fields.Float(digits=(20, 4), default=0.0000)
    nilai_barang = fields.Float(digits=(18, 2), default=0.00, string="Harga FOB")
    pos_tarif = fields.Char(string="Pos Tarif/Hs", default='')
    seri_barang = fields.Integer()
    spesifikasi_lain = fields.Char(default='')
    tipe = fields.Char(default='')
    ukuran = fields.Char(default='')
    uraian = fields.Char(default='')
    volume = fields.Float(digits=(20, 4), default=0.0000)
    cif_rupiah = fields.Float(digits=(18, 2), default=0.00, compute='_compute_cif_rupiah', store=True)
    harga_perolehan = fields.Float(digits=(18, 2), default=0.00)
    kode_asal_bahan_baku = fields.Char(default='')
    ndpbm = fields.Float(digits=(10, 4), default=0.0000)
    uang_muka = fields.Float(digits=(18, 4), default=0.0000)
    nilai_jasa = fields.Float(digits=(18, 4), default=0.0000)
    #tambahan 23
    freight = fields.Float(digits=(18, 2), default=0.00, string="Freight")
    fob = fields.Float(digits=(18, 2), default=0.00, string="FOB")
    kode_perhitungan = fields.Char(default='')
    nilai_tambah = fields.Float(digits=(18, 2), string="Biaya Tambahan")

    @api.onchange('jumlah_satuan')
    def _onchange_jumlah_satuan(self):
        if self.jumlah_satuan and self.header_id and self.header_id.fob:
            try:
                self.harga_satuan = self.header_id.fob / self.jumlah_satuan
            except ZeroDivisionError:
                self.harga_satuan = 0.0
        else:
            self.harga_satuan = 0.0

    @api.depends('cif', 'header_id.ndpbm')
    def _compute_cif_rupiah(self):
        for record in self:
            if record.cif and record.header_id.ndpbm:
                record.cif_rupiah = record.cif * record.header_id.ndpbm
            else:
                record.cif_rupiah = 0.00

    @api.model
    def create(self, vals):
        # Ensure kode_dokumen is set based on header_id
        if 'header_id' in vals:
            header = self.env['ceisa.header'].browse(vals['header_id'])
            vals['kode_dokumen'] = header.kode_dokumen

        record = super().create(vals)

        if not record.barang_tarif_ids:
            kode = record.header_id.kode_dokumen
            if kode == '40':
                self.env['ceisa.barang.tarif'].create({
                    'barang_id': record.id,
                    'kode_jenis_pungutan': 'PPN',
                    'tarif': 11,
                    'kode_fasilitas_tarif': '6',
                    'tarif_fasilitas': 100,
                    'kode_jenis_tarif': '1'
                })
            elif kode == '23':
                self.env['ceisa.barang.tarif'].create([
                    {
                        'barang_id': record.id,
                        'kode_jenis_pungutan': 'BM',
                        'tarif': 5,
                        'kode_fasilitas_tarif': '3',
                        'tarif_fasilitas': 100,
                        'kode_jenis_tarif': '1'
                        
                    },
                    {
                        'barang_id': record.id,
                        'kode_jenis_pungutan': 'PPH',
                        'tarif': 2.5,
                        'kode_fasilitas_tarif': '6',
                        'tarif_fasilitas': 100,
                        'kode_jenis_tarif': '1'
                    },
                    {
                        'barang_id': record.id,
                        'kode_jenis_pungutan': 'PPN',
                        'tarif': 11,
                        'kode_fasilitas_tarif': '6',
                        'tarif_fasilitas': 100,
                        'kode_jenis_tarif': '1'
                    },
                    # {
                    #     'barang_id': record.id,
                    #     'kode_jenis_pungutan': 'PPNBM',
                    #     'kode_jenis_tarif': '1',
                    # },


                ])
        return record

    @api.onchange('header_id')
    def _onchange_header_id(self):
        if self.header_id and not self.seri_barang:
            other_docs = self.header_id.barang_ids.filtered(lambda d: d != self)
            self.seri_barang = len(other_docs) + 1
            
            if self.header_id.kode_dokumen == '40':
                self.kode_asal_bahan_baku = '1'
                self.kode_perhitungan = '0'
            elif self.header_id.kode_dokumen == '23':
                self.kode_perhitungan = '0'
                self.kode_asal_bahan_baku = '0'
                self.freight = self.header_id.freight
                self.fob = self.header_id.fob
                self.asuransi = self.header_id.asuransi
                self.cif = self.header_id.cif
                self.harga_penyerahan = self.header_id.harga_penyerahan
                self.nilai_barang = self.header_id.nilai_barang
                self.ndpbm = self.header_id.ndpbm
                self.nilai_tambah = self.header_id.biaya_tambahan
            


        # Hanya isi tarif jika belum ada
        if not self.barang_tarif_ids:
            kode = self.header_id.kode_dokumen
            pungutans = []
            if kode == '40':
                pungutans = [(0, 0, {
                    'kode_jenis_pungutan': 'PPN',
                    'tarif': 11,
                    'kode_fasilitas_tarif': '6',
                    'tarif_fasilitas': 100,
                    'kode_jenis_tarif': '1',
                })]
            elif kode == '23':
                pungutans = [
                    (0, 0, {
                        'kode_jenis_pungutan': 'BM',
                        'tarif': 5,
                        'kode_fasilitas_tarif': '3',
                        'tarif_fasilitas': 100,
                        'kode_jenis_tarif': '1',
                    }),
                    (0, 0, {
                        'kode_jenis_pungutan': 'PPH',
                        'tarif': 2.5,
                        'kode_fasilitas_tarif': '6',
                        'tarif_fasilitas': 100,
                        'kode_jenis_tarif': '1',
                    }),
                    (0, 0, {
                        'kode_jenis_pungutan': 'PPN',
                        'tarif': 11,
                        'kode_fasilitas_tarif': '6',
                        'tarif_fasilitas': 100,
                        'kode_jenis_tarif': '1',
                    }),

                    # (0, 0, {
                    #     'kode_jenis_pungutan': 'PPNBM',
                    # }),


                ]
            self.barang_tarif_ids = pungutans

    kode_jenis_kemasan = fields.Char(string='Kode Jenis Kemasan')
    #--------------------------------------------------------
    kemasan_lookup = fields.Many2one(
        'ceisa.referensi.kemasan',
        string='Jenis Kemasan',
        compute='_compute_kemasan_lookup',
        inverse='_inverse_kemasan_lookup',
        store=False,
    )

    @api.depends('kode_jenis_kemasan')
    def _compute_kemasan_lookup(self):
        for rec in self:
            rec.kemasan_lookup = self.env['ceisa.referensi.kemasan'].search([
                ('kode_kemasan', '=', rec.kode_jenis_kemasan)
            ], limit=1)

    def _inverse_kemasan_lookup(self):
        for rec in self:
            if rec.kemasan_lookup:
                rec.kode_jenis_kemasan = rec.kemasan_lookup.kode_kemasan
    #-------------------------------------------------------------
    satuan_barang_lookup = fields.Many2one(
        'ceisa.referensi.satuan',
        string='Satuan Barang',
        compute='_compute_satuan_lookup',
        inverse='_inverse_satuan_lookup',
        store=False,
    )

    @api.depends('kode_satuan_barang')
    def _compute_satuan_lookup(self):
        for rec in self:
            rec.satuan_barang_lookup = self.env['ceisa.referensi.satuan'].search([
                ('kode_satuan', '=', rec.kode_satuan_barang)
            ], limit=1)

    def _inverse_satuan_lookup(self):
        for rec in self:
            if rec.satuan_barang_lookup:
                rec.kode_satuan_barang = rec.satuan_barang_lookup.kode_satuan
    
    kode_kategori_barang = fields.Char(default='')
    kategori_barang_lookup = fields.Many2one('ceisa.referensi.kategori.barang', string='Kategori Barang', compute='_compute_kategori_barang_lookup', inverse='_inverse_kategori_barang_lookup', store=False)
    @api.depends('kode_kategori_barang')
    def _compute_kategori_barang_lookup(self):
        for rec in self:
            rec.kategori_barang_lookup = self.env['ceisa.referensi.kategori.barang'].search([
                ('kode_kategori_barang', '=', rec.kode_kategori_barang)
            ], limit=1)

    def _inverse_kategori_barang_lookup(self):
        for rec in self:
            if rec.kategori_barang_lookup:
                rec.kode_kategori_barang = rec.kategori_barang_lookup.kode_kategori_barang

    kode_negara_asal = fields.Char(default='')
    negara_asal_lookup = fields.Many2one('ceisa.referensi.negara', string='Negara', compute='_compute_negara_asal_lookup', inverse='_inverse_negara_asal_lookup', store=False)
    @api.depends('kode_negara_asal')
    def _compute_negara_asal_lookup(self):
        for rec in self:
            rec.negara_asal_lookup = self.env['ceisa.referensi.negara'].search([
                ('kode_negara', '=', rec.kode_negara_asal)
            ], limit=1)

    def _inverse_negara_asal_lookup(self):
        for rec in self:
            if rec.negara_asal_lookup:
                rec.kode_negara_asal = rec.negara_asal_lookup.kode_negara

    @api.onchange('header_id')
    def _onchange_set_seri_seri_barang(self):
        if self.header_id and not self.seri_barang:
            other_docs = self.header_id.barang_ids.filtered(lambda d: d != self)
            self.seri_barang = len(other_docs) + 1

class CeisaBarangTarif(models.Model):
    _name = 'ceisa.barang.tarif'
    _description = 'Barang Tarif'

    barang_id = fields.Many2one('ceisa.barang')
    
    jumlah_satuan = fields.Float(digits=(24, 4), default=0.0000)
    kode_fasilitas_tarif = fields.Char(default='')
    kode_satuan_barang = fields.Char(default='')
    nilai_bayar = fields.Float(digits=(18, 2), default=0.00)
    nilai_fasilitas = fields.Float(digits=(18, 2), default=0.00)
    nilai_sudah_dilunasi = fields.Float(digits=(18, 2), default=0.00)
    seri_barang = fields.Integer()
    tarif = fields.Float(digits=(18, 2), default=0.00)
    tarif_fasilitas = fields.Float(digits=(5, 2), default=0.00)

    kode_jenis_pungutan = fields.Char(default='')
    jenis_pungutan_lookup = fields.Many2one(
        'ceisa.referensi.jenis.pungutan',
        string='Jenis Pungutan',
        compute='_compute_jenis_pungutan_lookup',
        inverse='_inverse_jenis_pungutan_lookup',
        store=False,
    )

    @api.depends('kode_jenis_pungutan')
    def _compute_jenis_pungutan_lookup(self):
        for rec in self:
            rec.jenis_pungutan_lookup = self.env['ceisa.referensi.jenis.pungutan'].search([
                ('kode_jenis_pungutan', '=', rec.kode_jenis_pungutan)
            ], limit=1)

    def _inverse_jenis_pungutan_lookup(self):
        for rec in self:
            if rec.jenis_pungutan_lookup:
                rec.kode_jenis_pungutan = rec.jenis_pungutan_lookup.kode_jenis_pungutan


    kode_jenis_tarif = fields.Char(default='1')
    # Lookup untuk dropdown
    jenis_tarif_lookup = fields.Many2one(
        'ceisa.referensi.jenis.tarif',
        string='Jenis Tarif',
        compute='_compute_jenis_tarif_lookup',
        inverse='_inverse_jenis_tarif_lookup',
        store=False,
    )

    @api.depends('kode_jenis_tarif')
    def _compute_jenis_tarif_lookup(self):
        for rec in self:
            rec.jenis_tarif_lookup = self.env['ceisa.referensi.jenis.tarif'].search([
                ('kode_jenis_tarif', '=', rec.kode_jenis_tarif)
            ], limit=1)

    def _inverse_jenis_tarif_lookup(self):
        for rec in self:
            if rec.jenis_tarif_lookup:
                rec.kode_jenis_tarif = rec.jenis_tarif_lookup.kode_jenis_tarif


    
    

    @api.onchange('barang_id')
    def _onchange_barang_id(self):
        if self.barang_id:
            self.seri_barang = self.barang_id.seri_barang
            self.jumlah_satuan = self.barang_id.jumlah_satuan
            self.kode_satuan_barang = self.barang_id.kode_satuan_barang
    
    tarif_fasilitas_scaled = fields.Float("Tarif Fasilitas (Scaled)", compute='_compute_tarif_fasilitas_scaled', store=False)

    @api.depends('tarif_fasilitas')
    def _compute_tarif_fasilitas_scaled(self):
        for record in self:
            # Scale the tarif_fasilitas value to be a fraction
            record.tarif_fasilitas_scaled = record.tarif_fasilitas / 100
    
    tarif_scaled = fields.Float("Tarif (Scaled)", compute='_compute_tarif_scaled', store=False)

    @api.depends('tarif')
    def _compute_tarif_scaled(self):
        for record in self:
            # Scale the tarif value to be a fraction
            record.tarif_scaled = record.tarif / 100

    kode_fasilitas_tarif = fields.Char(string='Kode Fasilitas Tarif')

    # Lookup untuk dropdown
    fasilitas_tarif_lookup = fields.Many2one(
        'ceisa.referensi.fasilitas.tarif',
        string='Fasilitas Tarif',
        compute='_compute_fasilitas_tarif_lookup',
        inverse='_inverse_fasilitas_tarif_lookup',
        store=False,
    )

    @api.depends('kode_fasilitas_tarif')
    def _compute_fasilitas_tarif_lookup(self):
        for rec in self:
            rec.fasilitas_tarif_lookup = self.env['ceisa.referensi.fasilitas.tarif'].search([
                ('kode_fasilitas_tarif', '=', rec.kode_fasilitas_tarif)
            ], limit=1)

    def _inverse_fasilitas_tarif_lookup(self):
        for rec in self:
            if rec.fasilitas_tarif_lookup:
                rec.kode_fasilitas_tarif = rec.fasilitas_tarif_lookup.kode_fasilitas_tarif

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE FUNCTION trg_update_barang_tarif()
            RETURNS TRIGGER AS $$
            BEGIN
            UPDATE ceisa_barang_tarif
            SET
                seri_barang = NEW.seri_barang,
                jumlah_satuan = NEW.jumlah_satuan,
                kode_satuan_barang = NEW.kode_satuan_barang,
                nilai_fasilitas = ROUND(
                                (SELECT tarif * ceisa_barang.harga_penyerahan / 100
                                FROM ceisa_barang
                                WHERE ceisa_barang.id = NEW.id), 2)
            WHERE barang_id = NEW.id;

            RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        self.env.cr.execute("""
            DROP TRIGGER IF EXISTS trg_update_barang_tarif ON ceisa_barang;

            CREATE TRIGGER trg_update_barang_tarif
            AFTER UPDATE ON ceisa_barang
            FOR EACH ROW
            WHEN (
            NEW.seri_barang IS NOT NULL AND
            NEW.jumlah_satuan IS NOT NULL AND
            NEW.kode_satuan_barang IS NOT NULL
            )
            EXECUTE FUNCTION trg_update_barang_tarif();
        """)



class ItemReferenceWizard(models.TransientModel):
    _name = 'item.reference.wizard'
    _description = 'Pilih Barang dari Referensi'

    source = fields.Selection([
        ('po', 'Purchase Order'),
        ('master_item', 'Master Item'),
    ], string='Sumber Referensi', required=True, default='po')

    po_id = fields.Many2one('vw.item.reference.grouped', string="Pilih PO")
    nomor_po = fields.Char(string='Nomor PO', readonly=True)
    header_id = fields.Many2one('ceisa.header', string='Dokumen Header', default=lambda self: self.env.context.get('default_header_id'))
    reference_ids = fields.One2many('item.reference.line', 'wizard_id', string='Barang Referensi')
    show_po_fields = fields.Boolean(compute='_compute_show_po_fields', store=False)

    @api.depends('source')
    def _compute_show_po_fields(self):
        for rec in self:
            rec.show_po_fields = rec.source == 'po'

    def _execute_query(self, query, params=None):
        """Helper method to execute query against MSSQL"""
        conn_str = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=access.clouddesktoponweb.com;UID=rebon;PWD=1rebonjuga;DATABASE=Rebon;encrypt=no;TrustServerCertificate=yes"
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query, params or [])
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def action_search(self):
        self.ensure_one()

        # Validasi wajib source
        if not self.source:
            raise UserError("Silakan pilih sumber referensi terlebih dahulu.")

        if self.source == 'po' and not self.po_id:
            raise UserError("Silakan pilih Purchase Order terlebih dahulu.")

        self.reference_ids.unlink()  # Hapus semua reference sebelumnya

        # Ambil data berdasarkan po_id yang dipilih
        if self.source == 'po' and self.po_id:
            query_group = """
                SELECT kode_barang, uraian, nilai_barang, jumlah_satuan
                FROM vw_item_reference 
                WHERE po_id = ?
            """
            rows_group = self._execute_query(query_group, (self.po_id,))

            # Simpan data ke dalam reference line
            for row in rows_group:
                self.env['item.reference.line'].create({
                    'wizard_id': self.id,
                    'kode_barang': row.kode_barang,
                    'uraian': row.uraian,
                    'jumlah_satuan': row.jumlah_satuan,
                    'nilai_barang': row.nilai_barang,
                    'selected': False,
                })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'item.reference.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('ceisa.view_item_reference_wizard_form').id,
            'target': 'new',
            'context': self.env.context,
        }

    def action_add_to_barang(self):
        header = self.header_id
        next_seri = max(header.barang_ids.mapped('seri_barang') or [0]) + 1

        for line in self.reference_ids.filtered(lambda l: l.selected):
            header.barang_ids.create({
                'header_id': header.id,
                'seri_barang': next_seri,
                'kode_barang': line.kode_barang,
                'pos_tarif': line.kode_barang,
                'uraian': line.uraian,
                'jumlah_satuan': line.jumlah_satuan,
                'harga_penyerahan': line.nilai_barang,
            })
            next_seri += 1

    def action_toggle_select(self):
            self.ensure_one()
            if any(line.selected for line in self.reference_ids):
                # Jika ada yang selected, unselect semua
                for line in self.reference_ids:
                    line.selected = False
            else:
                # Jika semua unselected, select semua
                for line in self.reference_ids:
                    line.selected = True

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'item.reference.wizard',
                'res_id': self.id,
                'view_mode': 'form',
                'view_id': self.env.ref('ceisa.view_item_reference_wizard_form').id,
                'target': 'new',
                'context': self.env.context,
            }

    def _get_po_options(self):
        query_group = "SELECT nomor_po, po_id, id FROM vw_item_reference_grouped"
        rows_group = self._execute_query(query_group)

        # Format data agar bisa ditampilkan di dropdown
        po_options = [(row.id, f"{row.nomor_po} - {row.po_id}") for row in rows_group]
        return po_options

    po_id = fields.Selection(_get_po_options, string="Pilih PO")


class ItemReferenceLine(models.TransientModel):
    _name = 'item.reference.line'
    _description = 'Baris Referensi Barang'

    wizard_id = fields.Many2one('item.reference.wizard', ondelete='cascade')
    selected = fields.Boolean(string='Pilih')
    kode_barang = fields.Char(string='Kode Barang')
    uraian = fields.Char(string='Uraian')
    jumlah_satuan = fields.Float(string='Jumlah Satuan')
    nilai_barang = fields.Float(string='Nilai Barang')



class CeisaCompanyMaster(models.Model):
    _name = 'ceisa.company.master'
    _description = 'Ceisa Company Master'

     #-----------------------------------------------------------------
    nama_perusahaan = fields.Char(required=True)
    npwp_perusahaan = fields.Char(required=True)
    alamat_perusahaan = fields.Char(required=True)
    kota_perusahaan = fields.Char(required=True)
    kode_kantor = fields.Char()

    kantor_pabean_lookup = fields.Many2one(
        'ceisa.referensi.kantor.pabean',
        string='Kantor Pabean',
        compute='_compute_kantor_lookup',
        inverse='_inverse_kantor_lookup',
        required= True,
        store=False
    )

    @api.depends('kode_kantor')
    def _compute_kantor_lookup(self):
        for rec in self:
            rec.kantor_pabean_lookup = self.env['ceisa.referensi.kantor.pabean'].search([
                ('kode_kantor', '=', rec.kode_kantor)
            ], limit=1)

    def _inverse_kantor_lookup(self):
        for rec in self:
            if rec.kantor_pabean_lookup:
                # rec.kode_kantor = rec.kantor_pabean_lookup.kode_kantor
                rec.kode_kantor = rec.kantor_pabean_lookup.kode_kantor if rec.kantor_pabean_lookup else False

    username_ceisa = fields.Char(required = True)
    password_ceisa = fields.Char(required = True)
    nomor_ijin_entitas = fields.Char() 
    tanggal_ijin_entitas = fields.Date()
    nitku = fields.Char()
    nib = fields.Char()
    access_token = fields.Char()
    refresh_token = fields.Char()
    numbering_ids = fields.One2many('ceisa.numbering.master', 'company_id', string="Numbering")

class CeisaNumberingMaster(models.Model):
    _name = 'ceisa.numbering.master'
    _description = 'Ceisa Numbering Master'

     #-----------------------------------------------------------------
    kode_dokumen = fields.Char(required=True)
    counter = fields.Integer(required=True)

    company_id = fields.Many2one('ceisa.company.master', string="Company")


class VwPungutanPivot(models.Model):
    _name = 'vw.pungutan.pivot'
    _auto = False
    _description = 'Ringkasan Pungutan Pivot'

    header_id = fields.Many2one('ceisa.header', string='Header')
    kode_jenis_pungutan = fields.Char(string='Pungutan')
    ditangguhkan = fields.Float()
    sudah_dilunasi = fields.Float()
    dibebaskan = fields.Float()
    tidak_dipungut = fields.Float()


class CeisaBarangDokumen(models.Model):
    _name = 'ceisa.barang.dokumen'
    _description = 'Barang Dokumen'

    barang_id = fields.Many2one('ceisa.barang')
    seri_barang = fields.Integer()
    kode_dokumen = fields.Char(default='')
    nomor_dokumen = fields.Char(default='')
    seri_dokumen = fields.Integer()
    tanggal_dokumen = fields.Date()


