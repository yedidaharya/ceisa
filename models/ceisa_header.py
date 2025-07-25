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

    freight = fields.Float(digits=(18, 2), default=0.00)
    harga_penyerahan = fields.Float(string="Harga Penyerahan", digits=(18, 4), default=0.0000)
    id_pengguna = fields.Char(default='')
    jabatan_ttd = fields.Char(string='Jabatan', default='')
    jumlah_kontainer = fields.Integer(default=0)
    kode_dokumen = fields.Char(default='')

    kode_kantor = fields.Char(string='Kode Kantor', default='')

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

    entitas_ids = fields.One2many('ceisa.entitas', 'header_id', string='Entitas')
    kemasan_ids = fields.One2many('ceisa.kemasan', 'header_id', string='Kemasan')
    kontainer_ids = fields.One2many('ceisa.kontainer', 'header_id', string='Kontainer')
    dokumen_ids = fields.One2many('ceisa.dokumen', 'header_id', string='Dokumen')
    pungutan_ids = fields.One2many('ceisa.pungutan', 'header_id', string='Pungutan')
    pengangkut_ids = fields.One2many('ceisa.pengangkut', 'header_id', string='Pengangkut')
    barang_ids = fields.One2many('ceisa.barang', 'header_id', string='Barang')


    entitas_1_nomor_identitas = fields.Char(
        string="Nomor Identitas",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_1_nama = fields.Char(
        string="Nama",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_1_alamat = fields.Char(
        string="Alamat",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_1_nomor_ijin_entitas = fields.Char(
        string="Nomor Ijin TPB",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_1_tanggal_ijin_entitas = fields.Char(
        string="Tanggal Skep TPB",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_1_nib_entitas = fields.Char(
        string="NIB",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_1_nitku = fields.Char(
        string="NITKU",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_1_jenis_identitas_lookup = fields.Many2one(
    'ceisa.referensi.jenis.identitas',
    string='Jenis Identitas',
    compute='_compute_entitas_display',
    inverse='_inverse_entitas_display',
    store=False,
    )


    entitas_2_nomor_identitas = fields.Char(
        string="NPWP",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_2_nama = fields.Char(
        string="Nama",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_2_alamat = fields.Char(
        string="Alamat",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_2_nitku = fields.Char(
        string="NITKU",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )

    entitas_2_jenis_identitas_lookup = fields.Many2one(
    'ceisa.referensi.jenis.identitas',
    string='Jenis Identitas',
    compute='_compute_entitas_display',
    inverse='_inverse_entitas_display',
    store=False,
    )

    entitas_3_nomor_identitas = fields.Char(
        string="NPWP",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_3_nama = fields.Char(
        string="Nama",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_3_alamat = fields.Char(
        string="Alamat",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_3_nitku = fields.Char(
        string="NITKU",
        compute='_compute_entitas_display',
        inverse='_inverse_entitas_display',
        store=False,
    )
    entitas_3_jenis_identitas_lookup = fields.Many2one(
    'ceisa.referensi.jenis.identitas',
    string='Jenis Identitas',
    compute='_compute_entitas_display',
    inverse='_inverse_entitas_display',
    store=False,
    )

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

                # Perbaikan disini — ambil dari entitas, bukan dari header
                if ents[0].kode_jenis_identitas:
                    rec.entitas_1_jenis_identitas_lookup = self.env['ceisa.referensi.jenis.identitas'].search([
                        ('kode_jenis_identitas', '=', ents[0].kode_jenis_identitas)
                    ], limit=1)
                else:
                    rec.entitas_1_jenis_identitas_lookup = False
            else:
                rec.entitas_1_nomor_identitas = False
                rec.entitas_1_nama = False
                rec.entitas_1_alamat = False
                rec.entitas_1_nomor_ijin_entitas = False
                rec.entitas_1_tanggal_ijin_entitas = False
                rec.entitas_1_nib_entitas = False
                rec.entitas_1_nitku = False
                rec.entitas_1_jenis_identitas_lookup = False

            # ENTITAS 2
            if len(ents) > 1:
                rec.entitas_2_nomor_identitas = ents[1].nomor_identitas
                rec.entitas_2_nama = ents[1].nama_entitas
                rec.entitas_2_alamat = ents[1].alamat_entitas
                rec.entitas_2_nitku = ents[1].nitku
                if ents[1].kode_jenis_identitas:
                    rec.entitas_2_jenis_identitas_lookup = self.env['ceisa.referensi.jenis.identitas'].search([
                        ('kode_jenis_identitas', '=', ents[1].kode_jenis_identitas)
                    ], limit=1)
                else:
                    rec.entitas_2_jenis_identitas_lookup = False
            else:
                rec.entitas_2_nomor_identitas = False
                rec.entitas_2_nama = False
                rec.entitas_2_alamat = False
                rec.entitas_2_nitku = False

            # ENTITAS 3
            if len(ents) > 2:
                rec.entitas_3_nomor_identitas = ents[2].nomor_identitas
                rec.entitas_3_nama = ents[2].nama_entitas
                rec.entitas_3_alamat = ents[2].alamat_entitas
                rec.entitas_3_nitku = ents[2].nitku
                if ents[2].kode_jenis_identitas:
                    rec.entitas_3_jenis_identitas_lookup = self.env['ceisa.referensi.jenis.identitas'].search([
                        ('kode_jenis_identitas', '=', ents[2].kode_jenis_identitas)
                    ], limit=1)
                else:
                    rec.entitas_3_jenis_identitas_lookup = False
            else:
                rec.entitas_3_nomor_identitas = False
                rec.entitas_3_nama = False
                rec.entitas_3_alamat = False
                rec.entitas_3_nitku = False



    def _inverse_entitas_display(self):
        for rec in self:
            ents = rec.entitas_ids.sorted(lambda e: e.id)
            if ents and rec.entitas_1_nama:
                ents[0].nomor_identitas = rec.entitas_1_nomor_identitas
                ents[0].nama_entitas = rec.entitas_1_nama
                ents[0].alamat_entitas = rec.entitas_1_alamat
                ents[0].nomor_ijin_entitas = rec.entitas_1_nomor_ijin_entitas
                ents[0].tanggal_ijin_entitas = rec.entitas_1_tanggal_ijin_entitas
                ents[0].nib_entitas = rec.entitas_1_nib_entitas
                ents[0].nitku = rec.entitas_1_nitku
                ents[0].kode_jenis_identitas = rec.entitas_1_jenis_identitas_lookup
                
            if len(ents) > 1 and rec.entitas_2_nama:
                ents[1].nomor_identitas = rec.entitas_2_nomor_identitas
                ents[1].nama_entitas = rec.entitas_2_nama
                ents[1].alamat_entitas = rec.entitas_2_alamat
                ents[1].nitku = rec.entitas_2_nitku

            if len(ents) > 2 and rec.entitas_3_nama:
                ents[2].nomor_identitas = rec.entitas_3_nomor_identitas
                ents[2].nama_entitas = rec.entitas_3_nama
                ents[2].alamat_entitas = rec.entitas_3_alamat
                ents[2].nitku = rec.entitas_3_nitku


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
            # Default jika belum ada
            if not rec.kode_kantor and company:
                rec.kode_kantor = company.kode_kantor
            if not rec.kota_ttd and company:
                rec.kota_ttd = company.kota_perusahaan     
            # Tentukan kode_entitas berdasarkan dokumen
            kode_dok = (rec.kode_dokumen or '').strip()
            if kode_dok == '40':
                kode_entitas = [3, 7, 9]
            elif kode_dok == '23':
                kode_entitas = [3, 5, 9]
            else:
                kode_entitas = [3, 7, 9]  # default fallback

            # Tambahkan entitas 1, 2, dan 3
            entitas_vals = []

            # Entitas 1 -
            entitas_vals.append({
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
            })

            # Entitas 2 -
            entitas_vals.append({
                'header_id': rec.id,
                'seri_entitas': 2,
                'kode_entitas': kode_entitas[1],
                'kode_jenis_identitas': '6',
            })

            # Entitas 3 -
            entitas_vals.append({
                'header_id': rec.id,
                'seri_entitas': 3,
                'kode_entitas': kode_entitas[2],
                'kode_jenis_identitas': '6',
                'nomor_identitas': company.npwp_perusahaan if company else '',
                'nama_entitas': company.nama_perusahaan if company else '',
                'alamat_entitas': company.alamat_perusahaan if company else '',
                'nitku': company.nitku if company else '',
            })

            self.env['ceisa.entitas'].create(entitas_vals)

            rec.invalidate_recordset(['nomor_aju'])

        return records
    

    def action_post_document_ceisa(self):
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
            # if not rec.seri:
            #     raise UserError("Seri harus diisi.")
            # if not rec.tanggal_aju:
            #     raise UserError("Tanggal Aju harus diisi.")
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
                # if not entitas.kode_jenis_api:
                #     raise UserError("Kode Jenis API harus diisi.")
                if not entitas.kode_jenis_identitas:
                    raise UserError("Kode Jenis Identitas harus diisi.")
                if not entitas.nama_entitas:
                    raise UserError("Nama Entitas harus diisi.")
                # if not entitas.nib_entitas:
                #     raise UserError("NIB Entitas harus diisi.")
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
                # if not barang.nilai_barang:
                #     raise UserError("Nilai Barang harus diisi.")
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
                if not barang.volume:
                    raise UserError("Volume harus diisi.")

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
                    # if not tarif.nilai_bayar:
                    #     raise UserError("Nilai Bayar harus diisi.")
                    # if not tarif.nilai_fasilitas:
                    #     raise UserError("Nilai Fasilitas harus diisi.")
                    # if not tarif.nilai_sudah_dilunasi:
                    #     raise UserError("Nilai Sudah Dilunasi harus diisi.")
                    if not tarif.seri_barang:
                        raise UserError("Seri Barang harus diisi.")
                    if not tarif.tarif:
                        raise UserError("Tarif harus diisi.")
                    if not tarif.tarif_fasilitas:
                        raise UserError("Tarif Fasilitas harus diisi.")
                    if not tarif.kode_jenis_pungutan:
                        raise UserError("Kode Jenis Pungutan harus diisi.")

            # Directly call the PostgreSQL function
            self.env.cr.execute(
                "SELECT ceisa_header_json_bc40(%s);", (rec.id,)
            )
            # Fetch company data
            company = self.env['ceisa.company.master'].search([], limit=1)
            if not company:
                raise UserError("Data perusahaan tidak ditemukan.")
            
            # Fetch new tokens if not available
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
            _logger.info("Token berhasil disimpan: %s", access_token)
            return self._show_popup("Token berhasil disimpan: %s" % access_token, "Success")


            # # Get jsonresult from the rec object
            # jsonresult = rec.jsonresult
            # if not jsonresult:
            #     raise UserError("JSON result from ceisa.header is empty.")
            
            # # Prepare headers and send the document
            # headers = {
            #     'Authorization': f'Bearer {access_token}',
            #     'Content-Type': 'application/json',
            # }
            
            # try:
            #     response = requests.post(
            #         "https://apis-gw.beacukai.go.id/openapi/document",
            #         headers=headers,
            #         data=jsonresult,  # Use the jsonresult as the raw body
            #         timeout=60
            #     )
            #     response.raise_for_status()  # Raise an error for bad status codes
            # except requests.RequestException as e:
            #     raise UserError(f"Failed to send document data to Beacukai API: {str(e)}")
            
            # # Handle the API response
            # response_json = response.json()
            # if response_json.get('status') == 'success':
            #     _logger.info("Data successfully sent to Beacukai API: %s", response_json)
            # else:
            #     raise UserError(f"API error: {response_json.get('message', 'Unknown error')}")

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
                        )), '[]'::jsonb)
                        FROM ceisa_entitas e
                        WHERE e.header_id = pid_header
                    ),
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
                    'dokumen', (
                        SELECT COALESCE(jsonb_agg(jsonb_build_object(
                            'idDokumen', d.id,
                            'kodeDokumen', d.kode_dokumen,
                            'nomorDokumen', d.nomor_dokumen,
                            'seriDokumen', d.seri_dokumen,
                            'tanggalDokumen', d.tanggal_dokumen
                        )), '[]'::jsonb)
                        FROM ceisa_dokumen d
                        WHERE d.header_id = pid_header
                    ),
                    'pungutan', (
                        SELECT COALESCE(jsonb_agg(jsonb_build_object(
                            'kodeFasilitasTarif', p.kode_fasilitas_tarif,
                            'kodeJenisPungutan', p.kode_jenis_pungutan,
                            'nilaiPungutan', p.nilai_pungutan
                        )), '[]'::jsonb)
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
                        )), '[]'::jsonb)
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
                                )), '[]'::jsonb)
                                FROM ceisa_barang_tarif t
                                WHERE t.barang_id = b.id
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
            $$
            LANGUAGE plpgsql
            VOLATILE
            COST 100;
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
                SELECT npwp_perusahaan INTO npwp FROM ceisa_company_master ORDER BY id LIMIT 1;
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
            BEGIN
                -- 1. Hapus pungutan lama jenis PPN
                DELETE FROM ceisa_pungutan
                WHERE header_id = p_header_id AND kode_jenis_pungutan = 'PPN';

                -- 2. Insert ulang berdasarkan barang & tarif
                INSERT INTO ceisa_pungutan (header_id, kode_jenis_pungutan, nilai_pungutan, kode_fasilitas_tarif)
                SELECT
                    b.header_id,
                    'PPN',
                    SUM(b.harga_penyerahan * t.tarif / 100.0),
                    t.kode_fasilitas_tarif
                FROM ceisa_barang b
                JOIN ceisa_barang_tarif t ON t.barang_id = b.id
                JOIN ceisa_header h ON h.id = b.header_id
                WHERE b.header_id = p_header_id
                AND h.kode_dokumen = '40'
                AND t.kode_jenis_pungutan = 'PPN'
                GROUP BY b.header_id, t.kode_fasilitas_tarif;

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
    tanggal_ijin_entitas = fields.Char(default='')
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
                MIN(id) AS id,  -- ini solusi penting
                header_id,
                MAX(CASE WHEN kode_fasilitas_tarif = '3' THEN nilai_pungutan ELSE 0 END) AS ditangguhkan,
                MAX(CASE WHEN kode_fasilitas_tarif = '7' THEN nilai_pungutan ELSE 0 END) AS sudah_dilunasi,
                MAX(CASE WHEN kode_fasilitas_tarif = '5' THEN nilai_pungutan ELSE 0 END) AS dibebaskan,
                MAX(CASE WHEN kode_fasilitas_tarif = '6' THEN nilai_pungutan ELSE 0 END) AS tidak_dipungut,
                MAX(kode_jenis_pungutan) AS kode_jenis_pungutan
            FROM ceisa_pungutan
            GROUP BY header_id;
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

    asuransi = fields.Float(digits=(18, 2), default=0.00)
    bruto = fields.Float(digits=(20, 4), default=0.0000)
    cif = fields.Float(digits=(18, 2), default=0.00)
    diskon = fields.Float(digits=(18, 2), default=0.00)
    harga_ekspor = fields.Float(digits=(18, 4), default=0.0000)
    harga_penyerahan = fields.Float(digits=(18, 4), default=0.0000)
    harga_satuan = fields.Float(digits=(18, 4), default=0.0000)
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
    nilai_barang = fields.Float(digits=(18, 2), default=0.00)
    pos_tarif = fields.Char(string="Pos Tarif/Hs", default='')
    seri_barang = fields.Integer()
    spesifikasi_lain = fields.Char(default='')
    tipe = fields.Char(default='')
    ukuran = fields.Char(default='')
    uraian = fields.Char(default='')
    volume = fields.Float(digits=(20, 4), default=0.0000)
    cif_rupiah = fields.Float(digits=(18, 2), default=0.00)
    harga_perolehan = fields.Float(digits=(18, 2), default=0.00)
    kode_asal_bahan_baku = fields.Char(default='')
    ndpbm = fields.Float(digits=(18, 4), default=0.0000)
    uang_muka = fields.Float(digits=(18, 4), default=0.0000)
    nilai_jasa = fields.Float(digits=(18, 4), default=0.0000)

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
                    'tarif_fasilitas': 100
                })
            elif kode == '23':
                self.env['ceisa.barang.tarif'].create([
                    {
                        'barang_id': record.id,
                        'kode_jenis_pungutan': 'PPN',
                        'nilai_fasilitas': 11,
                        'kode_fasilitas_tarif': '3'
                    },
                    {
                        'barang_id': record.id,
                        'kode_jenis_pungutan': 'BM',
                        'nilai_fasilitas': 5,
                        'kode_fasilitas_tarif': '1'
                    },
                ])
        return record

    @api.onchange('header_id')
    def _onchange_header_id(self):
        if self.header_id and not self.seri_barang:
            other_docs = self.header_id.barang_ids.filtered(lambda d: d != self)
            self.seri_barang = len(other_docs) + 1

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
                        'kode_jenis_pungutan': 'PPN',
                        'nilai_fasilitas': 11,
                        'kode_fasilitas_tarif': '3'
                    }),
                    (0, 0, {
                        'kode_jenis_pungutan': 'BM',
                        'nilai_fasilitas': 5,
                        'kode_fasilitas_tarif': '1'
                    }),
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

    @api.onchange('header_id')
    def _onchange_set_seri_seri_barang(self):
        if self.header_id and not self.seri_barang:
            other_docs = self.header_id.barang_ids.filtered(lambda d: d != self)
            self.seri_barang = len(other_docs) + 1

class CeisaBarangTarif(models.Model):
    _name = 'ceisa.barang.tarif'
    _description = 'Barang Tarif'

    barang_id = fields.Many2one('ceisa.barang')
    kode_jenis_tarif = fields.Char(default='1')
    jumlah_satuan = fields.Float(digits=(24, 4), default=0.0000)
    kode_fasilitas_tarif = fields.Char(default='')
    kode_satuan_barang = fields.Char(default='')
    nilai_bayar = fields.Float(digits=(18, 2), default=0.00)
    nilai_fasilitas = fields.Float(digits=(18, 2), default=0.00)
    nilai_sudah_dilunasi = fields.Float(digits=(18, 2), default=0.00)
    seri_barang = fields.Integer()
    tarif = fields.Float(digits=(18, 2), default=0.00)
    tarif_fasilitas = fields.Float(digits=(5, 2), default=0.00)
    kode_jenis_pungutan = fields.Char(default='PPN')

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






# class ItemReferenceWizard(models.TransientModel):
#     _name = 'item.reference.wizard'
#     _description = 'Pilih Barang dari Referensi'

#     source = fields.Selection([
#         ('po', 'Purchase Order'),
#         ('master_item', 'Master Item'),
#     ], string='Sumber Referensi', required=True, default='po')

#     po_id = fields.Many2one('vw.item.reference.grouped', string="Pilih",
#                                 domain="[('source','=','po')]",
#                                 depends_context='{"default_source": "po"}',
#                                 visibility_condition='source == "po"')

#     nomor_po = fields.Char(string='Nomor PO', readonly=True)
#     header_id = fields.Many2one('ceisa.header', string='Dokumen Header', default=lambda self: self.env.context.get('default_header_id'))
#     reference_ids = fields.One2many('item.reference.line', 'wizard_id', string='Barang Referensi')
#     show_po_fields = fields.Boolean(compute='_compute_show_po_fields', store=False)

#     @api.depends('source')
#     def _compute_show_po_fields(self):
#         for rec in self:
#             rec.show_po_fields = rec.source == 'po'

#     def action_search(self):
#         self.ensure_one()

#         # validasi wajib source
#         if not self.source:
#             raise UserError("Silakan pilih sumber referensi terlebih dahulu.")

        
#         if self.source == 'po' and not self.po_id:
#             raise UserError("Silakan pilih Purchase Order terlebih dahulu.")

#         self.reference_ids.unlink()

#         domain = [('source', '=', self.source)]
#         if self.source == 'po' and self.po_id:
#             domain.append(('nomor_po', '=', self.po_id.nomor_po))  # Gunakan nomor_po


#         refs = self.env['vw.item.reference'].search(domain)
#         for ref in refs:
#             self.env['item.reference.line'].create({
#                 'wizard_id': self.id,
#                 'kode_barang': ref.kode_barang,
#                 'uraian': ref.uraian,
#                 'nilai_barang': ref.nilai_barang,
#                 'selected': False,
#             })

#         # RETURN agar tetap di wizard
#         return {
#             'type': 'ir.actions.act_window',
#             'res_model': 'item.reference.wizard',
#             'res_id': self.id,
#             'view_mode': 'form',
#             'view_id': self.env.ref('ceisa.view_item_reference_wizard_form').id,
#             'target': 'new',
#             'context': self.env.context,
#         }


#     def action_add_to_barang(self):
#         header = self.header_id
#         next_seri = max(header.barang_ids.mapped('seri_barang') or [0]) + 1

#         for line in self.reference_ids.filtered(lambda l: l.selected):
#             header.barang_ids.create({
#                 'header_id': header.id,
#                 'seri_barang': next_seri,
#                 'kode_barang': line.kode_barang,
#                 'kode_hs': (line.kode_barang or '')[:8],
#                 'uraian': line.uraian,
#                 'nilai_barang': line.nilai_barang,
#             })
#             next_seri += 1

#     def action_toggle_select(self):
#         self.ensure_one()
#         if any(line.selected for line in self.reference_ids):
#             # Jika ada yang selected, unselect semua
#             for line in self.reference_ids:
#                 line.selected = False
#         else:
#             # Jika semua unselected, select semua
#             for line in self.reference_ids:
#                 line.selected = True

#         return {
#             'type': 'ir.actions.act_window',
#             'res_model': 'item.reference.wizard',
#             'res_id': self.id,
#             'view_mode': 'form',
#             'view_id': self.env.ref('ceisa.view_item_reference_wizard_form').id,
#             'target': 'new',
#             'context': self.env.context,
#         }


# class VwItemReference(models.Model):
#     _name = 'vw.item.reference'
#     _auto = False  # karena view
#     _description = 'Referensi Barang Gabungan'
#     _rec_name = 'nomor_po'

#     kode_barang = fields.Char()
#     po_id = fields.Char()
#     nomor_po = fields.Char()
#     uraian = fields.Char()
#     nilai_barang = fields.Float()
#     source = fields.Selection([('po', 'PO'), ('master', 'Master Item')])



# class VwItemReferenceGrouped(models.Model):
#     _name = 'vw.item.reference.grouped'
#     _auto = False
#     _description = 'Item Reference (Grouped)'
#     _rec_name = 'nomor_po'

#     po_id = fields.Char()
#     nomor_po = fields.Char()
#     source = fields.Selection([('po', 'PO'), ('master', 'Master Item')])

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
    _description = 'company'

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
                rec.kode_kantor = rec.kantor_pabean_lookup.kode_kantor

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
    _description = 'numbering'

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







