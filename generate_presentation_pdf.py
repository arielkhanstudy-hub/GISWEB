import os
import shutil
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.pdfgen import canvas

BASE_DIR = r"C:\Users\ASUS\.gemini\antigravity-ide\scratch\webgis-leaflet-kabupaten"
OUTPUT_PDF_LOCAL = os.path.join(BASE_DIR, "Presentasi_WebGIS_Local.pdf")
OUTPUT_PDF_LEGACY = os.path.join(BASE_DIR, "Presentasi_WebGIS_Kabupaten_Maros.pdf")

PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:
            self.saveState()

            # Top Banner Bar
            self.setFillColor(colors.HexColor("#1b4332"))
            self.rect(0, PAGE_HEIGHT - 38, PAGE_WIDTH, 38, stroke=0, fill=1)
            self.setFillColor(colors.HexColor("#2a9d8f"))
            self.rect(0, PAGE_HEIGHT - 41, PAGE_WIDTH, 3, stroke=0, fill=1)

            self.setFillColor(colors.white)
            self.setFont("Helvetica-Bold", 10)
            self.drawString(30, PAGE_HEIGHT - 24, "WEBGIS LOCAL - SISTEM INFORMASI GEOSPASIAL INTERAKTIF")
            self.setFont("Helvetica", 9)
            # Dosen name is intentionally NOT here, per requirement: only on cover slide
            self.drawRightString(PAGE_WIDTH - 30, PAGE_HEIGHT - 24, "PRAKTEK PENGELOLAAN BIG DATA DAN WEBGIS")

            # Bottom Footer
            self.setFillColor(colors.HexColor("#f1f5f9"))
            self.rect(0, 0, PAGE_WIDTH, 26, stroke=0, fill=1)
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.8)
            self.line(0, 26, PAGE_WIDTH, 26)
            self.setFillColor(colors.HexColor("#475569"))
            self.setFont("Helvetica", 8)
            self.drawString(30, 9, "WebGIS Local Platform  -  Leaflet.js + Flask + GeoPandas + Pyogrio (GDAL) + OGC WMS")
            self.drawRightString(PAGE_WIDTH - 30, 9, f"Slide {self._pageNumber} dari {page_count}")
            self.restoreState()


def create_presentation():
    doc = SimpleDocTemplate(
        OUTPUT_PDF_LOCAL,
        pagesize=landscape(A4),
        leftMargin=30, rightMargin=30,
        topMargin=46, bottomMargin=32
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=26, leading=33,
        textColor=colors.HexColor("#1b4332"), alignment=1)
    subtitle_style = ParagraphStyle('CoverSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=12, leading=17,
        textColor=colors.HexColor("#264653"), alignment=1)
    slide_heading = ParagraphStyle('SlideHeading', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=17, leading=21,
        textColor=colors.HexColor("#1b4332"))
    slide_subheading = ParagraphStyle('SlideSubHeading', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=13.5,
        textColor=colors.HexColor("#64748b"))
    body_style = ParagraphStyle('SlideBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13,
        textColor=colors.HexColor("#1e293b"))
    bullet_style = ParagraphStyle('SlideBullet', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12.5,
        textColor=colors.HexColor("#334155"))
    code_style = ParagraphStyle('SlideCode', parent=styles['Normal'],
        fontName='Courier', fontSize=7.5, leading=10.5,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"))
    card_title_style = ParagraphStyle('CardTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10, leading=13.5,
        textColor=colors.HexColor("#1b4332"))

    story = []

    # =========================================================================
    # SLIDE 1: COVER
    # =========================================================================
    story.append(Spacer(1, 35))
    badge_data = [[Paragraph("<para align='center'><font color='#2a9d8f' size='10.5'><b>PENUGASAN MATA KULIAH: PRAKTEK PENGELOLAAN BIG DATA DAN WEBGIS</b></font></para>", body_style)]]
    badge_table = Table(badge_data, colWidths=[540])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#e8f5e9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#a7f3d0")),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))
    center_table = Table([[badge_table]], colWidths=[PAGE_WIDTH - 60])
    center_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(center_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("WebGIS Local<br/>Platform Sistem Informasi Geospasial Interaktif", title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Visualisasi Multi-Layer, Layanan OGC Web Map Service (WMS), Analisis Spasial Lokal,<br/>"
        "dan Mesin Konversi Otomatis Input Data Geospasial Manual Multi-Format Berbasis GDAL",
        subtitle_style))
    story.append(Spacer(1, 30))

    # Single-line Dosen mention on Cover Slide ONLY
    info_box_data = [
        [
            Paragraph("<b>Identitas Mahasiswa:</b><br/>"
                      "Nama: <b><font color='#1b4332'>Ariel Khan</font></b><br/>"
                      "NIM: <b><font color='#1b4332'>V126241001</font></b><br/>"
                      "Program: Sarjana Terapan / Vokasi", body_style),
            Paragraph("<b>Dosen Pengampu:</b><br/>"
                      "<b><font color='#1b4332'>Andang Suryana Soma, S.Hut., MP., Ph.D</font></b><br/>"
                      "Fakultas Kehutanan Universitas Hasanuddin", body_style),
            Paragraph("<b>Spesifikasi Teknologi:</b><br/>"
                      "Leaflet.js 1.9.4 · Python Flask 3.x<br/>"
                      "Pyogrio 0.13.0 (GDAL C-Engine) · GeoPandas<br/>"
                      "<b>Status:</b> Operasional 100% Teruji", body_style)
        ]
    ]
    info_table = Table(info_box_data, colWidths=[240, 260, 240])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 12), ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(info_table)
    story.append(Spacer(1, 24))
    story.append(Paragraph("<para align='center'><font color='#64748b' size='8.5'>Tahun Akademik 2026 &bull; Laporan Presentasi Komprehensif WebGIS Local</font></para>", body_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: IDENTITAS MAHASISWA & PENUGASAN AKADEMIK (KHUSUS)
    # =========================================================================
    story.append(Paragraph("1. Identitas Mahasiswa &amp; Ruang Lingkup Penugasan", slide_heading))
    story.append(Paragraph("Profil pengembang dan matriks pemenuhan capaian pembelajaran mata kuliah Praktek Pengelolaan Big Data dan WebGIS", slide_subheading))
    story.append(Spacer(1, 12))

    col_id1 = [
        Paragraph("<b>Data Lengkap Mahasiswa:</b>", card_title_style), Spacer(1, 5),
        Paragraph("&bull; <b>Nama Mahasiswa:</b> Ariel Khan", bullet_style),
        Paragraph("&bull; <b>Nomor Induk Mahasiswa (NIM):</b> V126241001", bullet_style),
        Paragraph("&bull; <b>Mata Kuliah:</b> PRAKTEK PENGELOLAAN BIG DATA DAN WEBGIS", bullet_style),
        Paragraph("&bull; <b>Dosen Pengampu:</b> Andang Suryana Soma, S.Hut., MP., Ph.D", bullet_style),
        Paragraph("&bull; <b>Institusi:</b> Fakultas Kehutanan, Universitas Hasanuddin", bullet_style),
        Spacer(1, 10),
        Paragraph("<b>Latar Belakang Proyek WebGIS Local:</b>", card_title_style), Spacer(1, 5),
        Paragraph("&bull; WebGIS konvensional seringkali bersifat statis dan terkunci pada satu batas teritorial tertentu (vendor lock-in).", bullet_style),
        Paragraph("&bull; Proyek <b>WebGIS Local</b> dibangun sebagai platform pemetaan yang agnostik wilayah: pengguna dapat mengunggah (input manual) berbagai berkas data spasial eksternal kapan saja tanpa batasan cakupan geografis.", bullet_style),
        Paragraph("&bull; Dilengkapi dataset acuan awal terstruktur sebagai demonstrasi integrasi big data spasial tingkat lanjut.", bullet_style)
    ]

    col_id2 = [
        Paragraph("<b>Kompetensi &amp; Capaian Pembelajaran yang Dipenuhi:</b>", card_title_style), Spacer(1, 5),
        Paragraph("<b>1. Pengelolaan Format Big Data Spasial:</b><br/>Membangun sistem konversi backend yang mampu memproses format ESRI GDB, Shapefile ZIP, GeoPackage, KML/KMZ, GeoJSON, CSV, DXF, GPX, dan TAB menjadi format ramah web.", bullet_style), Spacer(1, 4),
        Paragraph("<b>2. Integrasi Standar OGC Web Map Service (WMS):</b><br/>Menghubungkan layanan WMS publik aktif (IEM Radar Cuaca, NASA GIBS MODIS Citra Satelit, Mundialis OSM &amp; Topografi) tanpa beban komputasi lokal.", bullet_style), Spacer(1, 4),
        Paragraph("<b>3. Kartografi Web &amp; Z-Index Management:</b><br/>Mengatur Leaflet Custom Panes agar geometri titik, garis, dan poligon tersusun rapi tanpa tumpang tindih visual.", bullet_style), Spacer(1, 4),
        Paragraph("<b>4. Analisis Spasial &amp; Interaktivitas Real-Time:</b><br/>Menyediakan alat ukur jarak/luas geodesik, spatial buffering, live search, serta tabel data atribut interaktif dengan ekspor CSV.", bullet_style)
    ]

    t_id = Table([[col_id1, col_id2]], colWidths=[365, 395])
    t_id.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#e8f5e9")),
        ('BOX', (0,0), (0,0), 1, colors.HexColor("#cbd5e1")),
        ('BOX', (1,0), (1,0), 1, colors.HexColor("#a7f3d0")),
        ('PADDING', (0,0), (-1,-1), 12)
    ]))
    story.append(t_id)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: ARSITEKTUR SISTEM WEBGIS LOCAL
    # =========================================================================
    story.append(Paragraph("2. Arsitektur Sistem &amp; Paradigma Desain", slide_heading))
    story.append(Paragraph("Dual-Tier Architecture: Frontend interaktif independen + Backend konverter spasial berperforma tinggi", slide_subheading))
    story.append(Spacer(1, 10))

    arch_box_data = [
        [
            Paragraph("<b>FRONTEND LAYER (Client-Side)</b>", card_title_style),
            Paragraph("<b>KOMUNIKASI RESTful API</b>", card_title_style),
            Paragraph("<b>SPATIAL ENGINE (Backend)</b>", card_title_style),
            Paragraph("<b>LAYANAN WMS EKSTERNAL</b>", card_title_style)
        ],
        [
            Paragraph("• <b>Leaflet.js 1.9.4:</b> Core visualisasi peta interaktif.<br/>"
                      "• <b>Custom Panes:</b> Manajemen Z-Index berlapis.<br/>"
                      "• <b>Client Parsers:</b> toGeoJSON (KML/KMZ), PapaParse (CSV), shpjs.<br/>"
                      "• <b>Modular UI:</b> Tab Sidebar, Floating Map Tools, Attribute Table Drawer.", bullet_style),
            Paragraph("• <b>Protokol:</b> HTTP POST multipart/form-data.<br/>"
                      "• <b>Endpoint:</b> <code>/api/convert</code> &amp; <code>/api/health</code>.<br/>"
                      "• <b>Payload:</b> Berkas biner spasial (ZIP/GPKG/DXF dll).<br/>"
                      "• <b>Respons:</b> GeoJSON FeatureCollection berstandar RFC 7946.", bullet_style),
            Paragraph("• <b>Python Flask 3.x:</b> Microservices REST API.<br/>"
                      "• <b>Pyogrio 0.13.0:</b> Driver GDAL C-API berkecepatan tinggi.<br/>"
                      "• <b>GeoPandas 1.1.4:</b> Manipulasi struktur geodataframe.<br/>"
                      "• <b>Shapely 2.x:</b> Validasi geometri dan reproyeksi WGS84.", bullet_style),
            Paragraph("• <b>IEM NEXRAD:</b> Radar cuaca presipitasi real-time.<br/>"
                      "• <b>NASA GIBS:</b> Citra satelit MODIS Terra harian.<br/>"
                      "• <b>Mundialis OGC:</b> Peta OpenStreetMap &amp; SRTM30 Hillshade.<br/>"
                      "• <b>Esri Basemaps:</b> World Imagery &amp; Topographic.", bullet_style)
        ]
    ]
    t_arch = Table(arch_box_data, colWidths=[190, 185, 195, 190])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b4332")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#f8fafc")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    note_data = [[Paragraph(
        "<b>Filosofi Desain WebGIS Local:</b> Sistem tidak dirancang eksklusif untuk satu batas wilayah tertentu. "
        "Meskipun menyediakan data sampel bawaan sebagai tolok ukur, fitur unggulan utama aplikasi ini adalah <b>kemampuan input data manual</b>. "
        "Pengguna dapat memasukkan dataset spasial dari wilayah mana pun di seluruh Indonesia atau dunia, dan peta akan langsung menyesuaikan batas (fitBounds) secara otomatis.",
        body_style
    )]]
    t_note = Table(note_data, colWidths=[760])
    t_note.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#86efac")),
        ('PADDING', (0,0), (-1,-1), 8)
    ]))
    story.append(t_note)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: INPUT DATA MANUAL & KONVERSI MULTI-FORMAT
    # =========================================================================
    story.append(Paragraph("3. Fitur Input Data Manual &amp; Konversi Multi-Format", slide_heading))
    story.append(Paragraph("Mendukung 9 format data geospasial terpopuler dengan deteksi otomatis dan penanganan layer dinamis", slide_subheading))
    story.append(Spacer(1, 10))

    format_table_data = [
        [Paragraph("<b>Format Berkas</b>", card_title_style), Paragraph("<b>Ekstensi</b>", card_title_style), Paragraph("<b>Metode Pemrosesan</b>", card_title_style), Paragraph("<b>Keterangan Teknis &amp; Kompatibilitas</b>", card_title_style)],
        [Paragraph("ESRI Shapefile", bullet_style), Paragraph("<code>.zip</code> (shp, shx, dbf, prj)", code_style), Paragraph("Backend (Pyogrio / GeoPandas)", bullet_style), Paragraph("Wajib dibundel ZIP; membaca atribut tabel DBF dan membaca proyeksi PRJ.", bullet_style)],
        [Paragraph("File Geodatabase", bullet_style), Paragraph("<code>.zip</code> (berisi direktori .gdb)", code_style), Paragraph("Backend (Pyogrio OpenFileGDB)", bullet_style), Paragraph("Mengekstrak direktori biner ESRI, mendeteksi semua layer via list_layers(), multi-layer output.", bullet_style)],
        [Paragraph("OGC GeoPackage", bullet_style), Paragraph("<code>.gpkg</code> (SQLite Container)", code_style), Paragraph("Backend (Pyogrio GDAL SQLite)", bullet_style), Paragraph("Format modern standar terbuka OGC; menyimpan multi-layer vektor dan metadata lengkap.", bullet_style)],
        [Paragraph("Google Earth KML", bullet_style), Paragraph("<code>.kml</code> (XML Placemark)", code_style), Paragraph("Frontend (toGeoJSON) / Backend", bullet_style), Paragraph("Parsing tag Placemark, ExtendedData, LineString, Polygon, dan Point style.", bullet_style)],
        [Paragraph("Google Earth KMZ", bullet_style), Paragraph("<code>.kmz</code> (Zipped KML)", code_style), Paragraph("Backend (Zipfile + Pyogrio)", bullet_style), Paragraph("Didekompresi otomatis di backend, KML internal diekstraksi menjadi GeoJSON.", bullet_style)],
        [Paragraph("GeoJSON / TopoJSON", bullet_style), Paragraph("<code>.geojson, .json</code>", code_style), Paragraph("Frontend Langsung (Native Leaflet)", bullet_style), Paragraph("Diparsing langsung oleh browser klien; performa rendering instan tanpa jeda server.", bullet_style)],
        [Paragraph("Tabel CSV Koordinat", bullet_style), Paragraph("<code>.csv, .txt</code>", code_style), Paragraph("Frontend (PapaParse) / Backend", bullet_style), Paragraph("Mendeteksi otomatis kolom koordinat: lat/latitude/y dan lng/longitude/lon/x.", bullet_style)],
        [Paragraph("CAD / GPS / MapInfo", bullet_style), Paragraph("<code>.dxf, .gpx, .tab (.zip)</code>", code_style), Paragraph("Backend (Pyogrio / Fiona GDAL)", bullet_style), Paragraph("Mendukung data jalur GPS (Waypoints/Tracks) dan berkas CAD AutoCAD DXF.", bullet_style)],
    ]
    t_fmt = Table(format_table_data, colWidths=[130, 160, 170, 300])
    t_fmt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b4332")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_fmt)
    story.append(Spacer(1, 8))

    pipe_data = [[Paragraph(
        "<b>Alur Pemrosesan Input Data Manual:</b> Pengguna memilih berkas melalui Drag &amp; Drop Modal &rarr; Frontend mengecek ekstensi &rarr; "
        "Jika berkas biner (ZIP/GDB/GPKG/DXF), dikirim ke API <code>/api/convert</code> &rarr; Pyogrio mendeteksi CRS dan mentransformasikan ke EPSG:4326 (WGS84) &rarr; "
        "Pembersihan nilai NaN/Infinity &rarr; Injeksi layer baru ke daftar <b>Layer Upload Pengguna</b> dengan warna pembeda otomatis dan tombol zoom fokus.",
        body_style
    )]]
    t_pipe = Table(pipe_data, colWidths=[760])
    t_pipe.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93c5fd")),
        ('PADDING', (0,0), (-1,-1), 7)
    ]))
    story.append(t_pipe)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: SOLUSI BACA ESRI FILE GEODATABASE (GDB)
    # =========================================================================
    story.append(Paragraph("4. Rekayasa Penanganan ESRI File Geodatabase (GDB)", slide_heading))
    story.append(Paragraph("Mengatasi keterbatasan format biner direktori proprietary ESRI di web menggunakan Pyogrio GDAL Engine", slide_subheading))
    story.append(Spacer(1, 12))

    col_gdb1 = [
        Paragraph("<b>Tantangan Teknis ESRI File Geodatabase:</b>", card_title_style), Spacer(1, 4),
        Paragraph("&bull; GDB bukan merupakan satu file tunggal, melainkan direktori berisi puluhan file biner internal (<code>.gdbtable</code>, <code>.gdbtablx</code>, <code>.gdbindexes</code>).", bullet_style),
        Paragraph("&bull; Browser web tidak memiliki API asli untuk membaca struktur biner ESRI tersebut secara langsung di sisi klien.", bullet_style),
        Paragraph("&bull; Pustaka Python konvensional (fiona lama) kerap gagal atau menghasilkan galat format jika driver OpenFileGDB tidak terkonfigurasi sempurna.", bullet_style),
        Spacer(1, 8),
        Paragraph("<b>Solusi Menggunakan Pyogrio v0.13.0:</b>", card_title_style), Spacer(1, 4),
        Paragraph("&bull; Pyogrio terhubung langsung ke mesin GDAL C-API tanpa overhead Python murni, memberikan kecepatan konversi 5x hingga 10x lebih cepat.", bullet_style),
        Paragraph("&bull; Fungsi <code>pyogrio.list_layers()</code> menghasilkan array nama layer yang langsung diurai secara aman:", bullet_style),
        Spacer(1, 4),
        Paragraph("<code>raw = pyogrio.list_layers(gdb_path)<br/>"
                  "layer_names = [r[0] if isinstance(r,(list,np.ndarray)) else r for r in raw]</code>", code_style)
    ]

    col_gdb2 = [
        Paragraph("<b>Bukti Pengujian &amp; Hasil Konversi Sampel:</b>", card_title_style), Spacer(1, 4),
        Paragraph("&bull; Disediakan berkas uji: <code>sample_maros_geodatabase.zip</code>.", bullet_style),
        Paragraph("&bull; <b>Layer 1 (fasilitas_titik):</b> 4 fitur titik fasilitas penting (Bandara, Kantor Bupati, RSUD, TN Bantimurung).", bullet_style),
        Paragraph("&bull; <b>Layer 2 (kawasan_zona):</b> 3 poligon zona spasial wilayah.", bullet_style),
        Paragraph("&bull; <b>Hasil Respons API:</b> Status HTTP 200 OK dengan format multi-layer:", bullet_style),
        Spacer(1, 4),
        Paragraph("<code>{<br/>"
                  "&nbsp;&nbsp;\"status\": \"success\",<br/>"
                  "&nbsp;&nbsp;\"total_layers\": 2,<br/>"
                  "&nbsp;&nbsp;\"layers\": [<br/>"
                  "&nbsp;&nbsp;&nbsp;&nbsp;{\"name\": \"fasilitas_titik\", \"geojson\": {...}},<br/>"
                  "&nbsp;&nbsp;&nbsp;&nbsp;{\"name\": \"kawasan_zona\", \"geojson\": {...}}<br/>"
                  "&nbsp;&nbsp;]<br/>"
                  "}</code>", code_style),
        Spacer(1, 6),
        Paragraph("&bull; <b>Visualisasi Frontend:</b> Kedua layer otomatis dibuatkan toggle independen pada sidebar dan langsung diproyeksikan di atas peta Leaflet.", bullet_style)
    ]

    t_gdb = Table([[col_gdb1, col_gdb2]], colWidths=[375, 385])
    t_gdb.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (0,0), 1, colors.HexColor("#cbd5e1")),
        ('BOX', (1,0), (1,0), 1, colors.HexColor("#86efac")),
        ('PADDING', (0,0), (-1,-1), 12)
    ]))
    story.append(t_gdb)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: INTEGRASI LAYANAN OGC WMS (WEB MAP SERVICE) TERVERIFIKASI
    # =========================================================================
    story.append(Paragraph("5. Integrasi Layanan OGC Web Map Service (WMS) Aktif", slide_heading))
    story.append(Paragraph("Pemanfaatan server pemetaan geospasial eksternal untuk efisiensi Big Data tanpa beban bandwidth lokal", slide_subheading))
    story.append(Spacer(1, 10))

    wms_detail_data = [
        [Paragraph("<b>Nama Layanan WMS</b>", card_title_style), Paragraph("<b>Server URL &amp; Parameter</b>", card_title_style), Paragraph("<b>Spesifikasi Teknis</b>", card_title_style), Paragraph("<b>Status Akses</b>", card_title_style)],
        [
            Paragraph("<b>IEM NEXRAD Radar Cuaca</b><br/>Iowa Environmental Mesonet", bullet_style),
            Paragraph("<code>https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi</code><br/>Layer: <code>nexrad-n0r</code>", code_style),
            Paragraph("Format: image/png, transparent: true, WMS 1.1.1. Menampilkan radar presipitasi cuaca real-time.", bullet_style),
            Paragraph("<font color='#16a34a'><b>AKTIF (200 OK)</b></font>", bullet_style)
        ],
        [
            Paragraph("<b>NASA GIBS MODIS Terra</b><br/>NASA Earth Observing System", bullet_style),
            Paragraph("<code>https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi</code><br/>Layer: <code>MODIS_Terra_CorrectedReflectance_TrueColor</code>", code_style),
            Paragraph("Format: image/jpeg, WMS 1.3.0, CRS EPSG:3857. Citra komposit satelit harian resolusi 250m bebas awan.", bullet_style),
            Paragraph("<font color='#16a34a'><b>AKTIF (200 OK)</b></font>", bullet_style)
        ],
        [
            Paragraph("<b>Mundialis OpenStreetMap WMS</b><br/>Mundialis GmbH &amp; Co. KG", bullet_style),
            Paragraph("<code>https://ows.mundialis.de/services/service</code><br/>Layer: <code>OSM-WMS</code>", code_style),
            Paragraph("Format: image/png, transparent: false, OGC WMS 1.1.1/1.3.0. Peta jalan dunia berbasis OpenStreetMap.", bullet_style),
            Paragraph("<font color='#16a34a'><b>AKTIF (200 OK)</b></font>", bullet_style)
        ],
        [
            Paragraph("<b>Mundialis SRTM30 Hillshade</b><br/>Mundialis Elevation Service", bullet_style),
            Paragraph("<code>https://ows.mundialis.de/services/service</code><br/>Layer: <code>SRTM30-Colored-Hillshade</code>", code_style),
            Paragraph("Format: image/png, OGC WMS standard. Model elevasi digital global berwarna dengan efek bayangan relief kontur.", bullet_style),
            Paragraph("<font color='#16a34a'><b>AKTIF (200 OK)</b></font>", bullet_style)
        ]
    ]
    t_wms = Table(wms_detail_data, colWidths=[170, 240, 250, 100])
    t_wms.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b4332")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_wms)
    story.append(Spacer(1, 10))

    wms_exp_data = [[Paragraph(
        "<b>Pentingnya OGC WMS untuk Pengelolaan Big Data Geospasial:</b><br/>"
        "Alih-alih mentransfer miliaran titik simpul vektor ke peramban pengguna yang dapat menyebabkan browser melambat (memory exhaustion), "
        "layanan WMS merender peta secara server-side dan mengirimkan potongan citra georeferensi yang ringan sesuai viewport aktif. "
        "Implementasi pada WebGIS Local menggunakan fungsi <code>L.tileLayer.wms(url, options)</code> dengan kontrol layer toggle independen di sidebar.",
        body_style
    )]]
    t_wmsexp = Table(wms_exp_data, colWidths=[760])
    t_wmsexp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#86efac")),
        ('PADDING', (0,0), (-1,-1), 8)
    ]))
    story.append(t_wmsexp)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: SISTEM PETA DASAR (BASEMAPS)
    # =========================================================================
    story.append(Paragraph("6. Sistem Peta Dasar (Basemaps) Multi-Sumber", slide_heading))
    story.append(Paragraph("Pilihan peta dasar standar carto-tiles dan WMS untuk berbagai konteks analisis geospasial", slide_subheading))
    story.append(Spacer(1, 12))

    base_cards = [
        [
            Paragraph("<b>OpenStreetMap Standard</b>", card_title_style),
            Paragraph("<b>Esri World Imagery</b>", card_title_style),
            Paragraph("<b>Esri Topographic Map</b>", card_title_style)
        ],
        [
            Paragraph("• Peta jalan standar komunitas global.<br/>• Detail jaringan jalan lokal, nama jalan, dan batas wilayah.<br/>• Ringan dan cepat dimuat.<br/>• Ideal untuk navigasi umum.", bullet_style),
            Paragraph("• Citra satelit foto udara resolusi tinggi.<br/>• Sumber gabungan: USDA, USGS, GeoEye, DigitalGlobe.<br/>• Ideal untuk verifikasi tutupan lahan fisik dan objek riil di lapangan.", bullet_style),
            Paragraph("• Menampilkan garis kontur elevasi, pegunungan, dan toponim topografi.<br/>• Sangat berguna untuk analisis geomorfologi, hidrologi, dan survei kehutanan.", bullet_style)
        ],
        [
            Paragraph("<b>CartoDB Dark Matter</b>", card_title_style),
            Paragraph("<b>Mundialis Topo-OSM (WMS)</b>", card_title_style),
            Paragraph("<b>Mundialis SRTM Hillshade</b>", card_title_style)
        ],
        [
            Paragraph("• Tema gelap elegan dengan kontras tinggi.<br/>• Membuat layer tematik berwarna cerah (jalan jingga, titik merah) terlihat sangat menonjol.<br/>• Mengurangi kelelahan mata operator.", bullet_style),
            Paragraph("• Peta dasar topografi hibrida yang dilayani via protokol OGC WMS.<br/>• Menggabungkan relief bayangan bukit dan informasi jalan OpenStreetMap.", bullet_style),
            Paragraph("• Peta relief bayangan dari data elevasi Shuttle Radar Topography Mission (SRTM).<br/>• Menampilkan visualisasi relief 3D 2D datar.", bullet_style)
        ]
    ]
    t_base = Table(base_cards, colWidths=[250, 250, 260])
    t_base.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b4332")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#1b4332")),
        ('TEXTCOLOR', (0,2), (-1,2), colors.white),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_base)
    story.append(Spacer(1, 12))

    base_note = [[Paragraph(
        "<b>Mekanisme Switching Tanpa Hilang State:</b> Pemilihan basemap menggunakan pemanggilan <code>map.removeLayer(currentBasemap)</code> "
        "dan <code>newBasemap.addTo(map); newBasemap.bringToBack();</code> sehingga seluruh data vektor tematik dan layer upload pengguna tetap utuh di posisinya.",
        body_style
    )]]
    t_bn = Table(base_note, colWidths=[760])
    t_bn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93c5fd")),
        ('PADDING', (0,0), (-1,-1), 8)
    ]))
    story.append(t_bn)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: HIERARKI KARTOGRAFI & LEAFLET PANES (Z-INDEX)
    # =========================================================================
    story.append(Paragraph("7. Hierarki Kartografi &amp; Leaflet Custom Panes", slide_heading))
    story.append(Paragraph("Solusi definitif pencegahan tumpang tindih geometri poligon, polyline, dan point marker", slide_subheading))
    story.append(Spacer(1, 10))

    col_z1 = [
        Paragraph("<b>Masalah Klasik Rendering WebGIS:</b>", card_title_style), Spacer(1, 4),
        Paragraph("&bull; Secara default, Leaflet me-render layer sesuai urutan waktu pemuatan data (asynchronous timing).", bullet_style),
        Paragraph("&bull; Jika poligon besar dimuat belakangan, poligon tersebut dapat menutupi titik marker fasilitas atau garis jalan.", bullet_style),
        Paragraph("&bull; Akibatnya, pengguna tidak bisa mengklik marker fasilitas karena terhalang oleh poligon di atasnya.", bullet_style),
        Spacer(1, 8),
        Paragraph("<b>Implementasi Leaflet Custom Panes:</b>", card_title_style), Spacer(1, 4),
        Paragraph("&bull; Dibuat pane khusus dengan Z-Index bertingkat:", bullet_style),
        Spacer(1, 4),
        Paragraph("<code>map.createPane('toponimPane');<br/>"
                  "map.getPane('toponimPane').style.zIndex = 600;<br/>"
                  "map.createPane('userUploadPane');<br/>"
                  "map.getPane('userUploadPane').style.zIndex = 550;</code>", code_style)
    ]

    z_table_data = [
        [Paragraph("<b>Pane Name</b>", card_title_style), Paragraph("<b>Z-Index</b>", card_title_style), Paragraph("<b>Tipe Layer Geospasial</b>", card_title_style)],
        [Paragraph("<code>toponimPane</code>", code_style), Paragraph("600", bullet_style), Paragraph("Marker Titik Fasilitas Penting &amp; Ikon FontAwesome", bullet_style)],
        [Paragraph("<code>userUploadPane</code>", code_style), Paragraph("550", bullet_style), Paragraph("Layer Hasil Upload Pengguna (Titik &amp; Garis)", bullet_style)],
        [Paragraph("<code>overlayPane (Jalan)</code>", code_style), Paragraph("480", bullet_style), Paragraph("Jaringan Jalan Arteri, Poros, &amp; Rel Kereta", bullet_style)],
        [Paragraph("<code>overlayPane (Sungai)</code>", code_style), Paragraph("450", bullet_style), Paragraph("Jaringan Hidrologi &amp; Aliran Sungai Utama", bullet_style)],
        [Paragraph("<code>overlayPane (Kecamatan)</code>", code_style), Paragraph("420", bullet_style), Paragraph("Poligon Batas Wilayah Administrasi", bullet_style)],
        [Paragraph("<code>overlayPane (Tutupan)</code>", code_style), Paragraph("400", bullet_style), Paragraph("Poligon Tutupan Lahan &amp; Kawasan Hutan", bullet_style)],
        [Paragraph("<code>tilePane</code>", code_style), Paragraph("200", bullet_style), Paragraph("Peta Dasar (Basemaps OSM / Satelit / WMS)", bullet_style)]
    ]
    t_z = Table(z_table_data, colWidths=[120, 55, 200])
    t_z.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b4332")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))

    t_s8 = Table([[col_z1, t_z]], colWidths=[375, 385])
    t_s8.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (0,0), 1, colors.HexColor("#cbd5e1")),
        ('PADDING', (0,0), (-1,-1), 10)
    ]))
    story.append(t_s8)
    story.append(Spacer(1, 8))

    ctrl_note = [[Paragraph(
        "<b>Kontrol Transparansi &amp; Zoom Mandiri:</b> Setiap layer dilengkapi slider opasitas (0.1 &ndash; 1.0) "
        "sehingga pengguna dapat menumpuk beberapa layer poligon sekaligus sambil tetap melihat citra satelit atau jalan di bawahnya. "
        "Tombol <i>Zoom-to-Extent</i> mengarahkan kamera peta ke batas bounding box layer secara instan.",
        body_style
    )]]
    t_cn = Table(ctrl_note, colWidths=[760])
    t_cn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#86efac")),
        ('PADDING', (0,0), (-1,-1), 7)
    ]))
    story.append(t_cn)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 9: DATASET ACUAN AWAL (DEFAULT SPATIAL LAYERS)
    # =========================================================================
    story.append(Paragraph("8. Dataset Acuan Awal (Default Reference Layers)", slide_heading))
    story.append(Paragraph("Integrasi 5 layer tematik bawaan sebagai tolok ukur pengujian kartografi dan tabel atribut", slide_subheading))
    story.append(Spacer(1, 10))

    ref_table_data = [
        [Paragraph("<b>Nama Layer</b>", card_title_style), Paragraph("<b>Tipe Geometri</b>", card_title_style), Paragraph("<b>Jumlah Objek</b>", card_title_style), Paragraph("<b>Sumber Data Resmi</b>", card_title_style), Paragraph("<b>Atribut &amp; Informasi Utama</b>", card_title_style)],
        [Paragraph("Batas Administrasi Kecamatan", bullet_style), Paragraph("MultiPolygon", code_style), Paragraph("14 Kecamatan", bullet_style), Paragraph("BPS 2024 &amp; Ina-Geoportal BIG", bullet_style), Paragraph("Nama kecamatan, jumlah penduduk, luas wilayah, kepadatan/km², jumlah desa.", bullet_style)],
        [Paragraph("Jaringan Jalan &amp; Kereta Api", bullet_style), Paragraph("MultiLineString", code_style), Paragraph("10 Ruas Utama", bullet_style), Paragraph("Kementerian PUPR &amp; Ditjen KA", bullet_style), Paragraph("Jalan Nasional/Provinsi, Jalan Poros Trans-Sulawesi, Jalur Kereta Api.", bullet_style)],
        [Paragraph("Jaringan Sungai &amp; Air", bullet_style), Paragraph("MultiLineString", code_style), Paragraph("6 Aliran Utama", bullet_style), Paragraph("Balai Wilayah Sungai (BBWS)", bullet_style), Paragraph("Sungai Maros Utama, Sungai Bantimurung, Sungai Moncongloe, ordo sungai.", bullet_style)],
        [Paragraph("Toponim &amp; Titik Fasilitas", bullet_style), Paragraph("Point (Marker)", code_style), Paragraph("25 Lokasi", bullet_style), Paragraph("Pemerintah Daerah &amp; BPS", bullet_style), Paragraph("Kantor Bupati, RSUD, Puskesmas, Bandara Int'l, Pelabuhan, Geopark UNESCO.", bullet_style)],
        [Paragraph("Tutupan Lahan &amp; Kawasan Hutan", bullet_style), Paragraph("MultiPolygon", code_style), Paragraph("10 Zona Area", bullet_style), Paragraph("Kementerian LHK (KLHK)", bullet_style), Paragraph("Taman Nasional, Hutan Lindung, Hutan Produksi, Permukiman, Sawah Irigasi.", bullet_style)],
    ]
    t_ref = Table(ref_table_data, colWidths=[150, 95, 85, 150, 280])
    t_ref.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b4332")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(t_ref)
    story.append(Spacer(1, 10))

    drawer_info = [
        [
            Paragraph("<b>Tabel Data Atribut Interaktif:</b><br/>"
                      "• Terintegrasi di bagian bawah layar melalui drawer yang dapat dibuka-tutup.<br/>"
                      "• Memilih layer aktif (Kecamatan, Jalan, Sungai, Fasilitas, Tutupan Lahan) secara dinamis.<br/>"
                      "• Dilengkapi fitur <b>Live Filter pencarian</b> cepat tanpa me-reload peramban.<br/>"
                      "• Tombol <b>Lihat</b> pada tiap baris langsung mengarahkan kamera (flyTo) dan membuka popup fitur.", bullet_style),
            Paragraph("<b>Ekspor CSV &amp; Interoperabilitas Data:</b><br/>"
                      "• Fitur <b>Ekspor CSV</b> mengonversi tabel atribut layer aktif ke format standar CSV RFC 4180.<br/>"
                      "• Sanitasi nilai teks dan karakter khusus agar kompatibel dibuka di Microsoft Excel, LibreOffice, atau QGIS.<br/>"
                      "• Penamaan berkas otomatis: <code>WebGIS_Local_[nama_layer].csv</code>.", bullet_style)
        ]
    ]
    t_di = Table(drawer_info, colWidths=[380, 380])
    t_di.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_di)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 10: FITUR ANALISIS SPASIAL & PENGUKURAN
    # =========================================================================
    story.append(Paragraph("9. Fitur Analisis Spasial &amp; Utilitas Pemetaan", slide_heading))
    story.append(Paragraph("Alat pengukuran geodesik, buffering spasial, live search, dan pelacak koordinat kursor", slide_subheading))
    story.append(Spacer(1, 12))

    tool_boxes = [
        [
            Paragraph("<b>Alat Ukur Jarak Geodesik</b>", card_title_style),
            Paragraph("<b>Alat Ukur Luas Poligon</b>", card_title_style),
            Paragraph("<b>Analisis Spasial Buffering</b>", card_title_style)
        ],
        [
            Paragraph("• Mengukur panjang garis multi-segmen.<br/>"
                      "• Menggunakan rumus Geodesik (Haversine/Vincenty) bola bumi.<br/>"
                      "• Konversi otomatis meter &amp; kilometer.<br/>"
                      "• Tooltip mengambang mengikuti ujung kursor mouse.<br/>"
                      "• Tombol pembersih garis ukur sekali klik.", bullet_style),
            Paragraph("• Mengukur luas poligon arbitrer dari klik pengguna.<br/>"
                      "• Perhitungan luas bidang spherical polygon projection.<br/>"
                      "• Satuan dinamis: meter persegi (m²), Hektar (Ha), dan km².<br/>"
                      "• Visualisasi poligon semi-transparan dengan garis putus-putus.", bullet_style),
            Paragraph("• Membuat radius jangkauan pengaruh dari fitur fasilitas terpilih.<br/>"
                      "• Opsi radius instan: 1 km, 2 km, dan 5 km.<br/>"
                      "• Berguna untuk analisis jangkauan layanan kesehatan (Puskesmas), zona bahaya bencana, atau area penyangga hutan.", bullet_style)
        ],
        [
            Paragraph("<b>Pencarian Fitur Live (Search)</b>", card_title_style),
            Paragraph("<b>Pelacak Koordinat Real-Time</b>", card_title_style),
            Paragraph("<b>Legenda Kartografi Dinamis</b>", card_title_style)
        ],
        [
            Paragraph("• Mencari objek spasial berdasarkan nama secara realtime.<br/>"
                      "• Filter instan pada memori JavaScript client.<br/>"
                      "• Klik pada kartu hasil pencarian langsung mengarahkan kamera peta ke objek dan membuka popup informasi lengkap.", bullet_style),
            Paragraph("• Menampilkan koordinat Latitude &amp; Longitude WGS84 di pojok kanan bawah secara real-time saat mouse digerakkan.<br/>"
                      "• Presisi 5 desimal (~1 meter akurasi).<br/>"
                      "• Indikator Zoom Level aktif saat pengguna memperbesar/memperkecil peta.", bullet_style),
            Paragraph("• Panel legenda mengambang yang menyesuaikan secara otomatis dengan layer yang sedang aktif.<br/>"
                      "• Menampilkan simbol kartografi standar: kotak warna poligon, garis jalan/sungai, dan ikon marker titik fasilitas.", bullet_style)
        ]
    ]
    t_tb = Table(tool_boxes, colWidths=[250, 250, 260])
    t_tb.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b4332")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#1b4332")),
        ('TEXTCOLOR', (0,2), (-1,2), colors.white),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_tb)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 11: MATRIKS PELACAKAN FUNGSI (FUNCTION TRACKING)
    # =========================================================================
    story.append(Paragraph("10. Matriks Pelacakan Fungsi (Function Tracking)", slide_heading))
    story.append(Paragraph("Status verifikasi pengujian seluruh modul dan fungsionalitas sistem WebGIS Local", slide_subheading))
    story.append(Spacer(1, 10))

    matrix_data = [
        [Paragraph("<b>No</b>", card_title_style), Paragraph("<b>Fungsi Sistem WebGIS</b>", card_title_style), Paragraph("<b>Modul / Komponen</b>", card_title_style), Paragraph("<b>Hasil Verifikasi &amp; Bukti Operasional</b>", card_title_style), Paragraph("<b>Status</b>", card_title_style)],
        [Paragraph("1", bullet_style), Paragraph("Inisialisasi Peta &amp; Navigasi", bullet_style), Paragraph("<code>app.js (initMap)</code>", code_style), Paragraph("Peta Leaflet 1.9.4 aktif, pan, zoom, scale bar metrik bekerja sempurna.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("2", bullet_style), Paragraph("Switching Peta Dasar (Basemaps)", bullet_style), Paragraph("<code>basemaps (app.js)</code>", code_style), Paragraph("6 opsi basemap (OSM, Satellite, Topo, Dark, WMS Topo, WMS Hillshade) lancar.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("3", bullet_style), Paragraph("Visualisasi 5 Layer Tematik Bawaan", bullet_style), Paragraph("<code>loadAllDefaultLayers</code>", code_style), Paragraph("Layer Administrasi, Jalan, Sungai, Toponim, Tutupan Lahan termuat dan valid.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("4", bullet_style), Paragraph("Z-Index Management (Leaflet Panes)", bullet_style), Paragraph("<code>map.createPane</code>", code_style), Paragraph("toponimPane (600) di atas garis (480) dan poligon (400); tidak tertutup.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("5", bullet_style), Paragraph("Slider Transparansi &amp; Zoom Layer", bullet_style), Paragraph("<code>setupLayerControls</code>", code_style), Paragraph("Opasitas tiap layer dapat diatur independen; tombol Zoom to Extent aktif.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("6", bullet_style), Paragraph("Layanan OGC WMS Terverifikasi", bullet_style), Paragraph("<code>L.tileLayer.wms</code>", code_style), Paragraph("IEM Radar Cuaca, NASA GIBS Satelit, Mundialis OSM/Hillshade aktif 200 OK.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("7", bullet_style), Paragraph("Upload Multi-Format Spasial", bullet_style), Paragraph("<code>setupUploadFeature</code>", code_style), Paragraph("Mendukung SHP ZIP, KML, KMZ, GeoJSON, CSV, DXF, GPX, TAB via REST API.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("8", bullet_style), Paragraph("Konversi ESRI File Geodatabase (GDB)", bullet_style), Paragraph("<code>server.py (pyogrio)</code>", code_style), Paragraph("Direktori .gdb di-unzip, list_layers diekstrak, 2 layer tampil di peta.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("9", bullet_style), Paragraph("Drawer Tabel Atribut &amp; Filter", bullet_style), Paragraph("<code>populateAttributeTable</code>", code_style), Paragraph("Tabel responsif di bawah peta, live filter pencarian baris berfungsi seketika.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("10", bullet_style), Paragraph("Ekspor Data ke Format CSV", bullet_style), Paragraph("<code>exportCurrentTableToCsv</code>", code_style), Paragraph("Mengunduh file WebGIS_Local_[layer].csv berstandar RFC 4180 ke komputer.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("11", bullet_style), Paragraph("Pengukuran Jarak &amp; Luas Poligon", bullet_style), Paragraph("<code>setupMeasurementTools</code>", code_style), Paragraph("Menghitung meter/km garis dan m²/Ha/km² poligon geodesik secara akurat.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("12", bullet_style), Paragraph("Fitur Buffer Spasial Multi-Radius", bullet_style), Paragraph("<code>showFeatureBuffer</code>", code_style), Paragraph("Radius 1 km, 2 km, 5 km terproyeksi instan di sekeliling titik fasilitas.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
        [Paragraph("13", bullet_style), Paragraph("Pelacak Koordinat &amp; Zoom Level", bullet_style), Paragraph("<code>setupCoordinateDisplay</code>", code_style), Paragraph("Menampilkan Latitude/Longitude presisi 5 desimal saat kursor digerakkan.", bullet_style), Paragraph("<font color='#16a34a'><b>100% OK</b></font>", bullet_style)],
    ]
    t_mat = Table(matrix_data, colWidths=[25, 175, 135, 335, 90])
    t_mat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1b4332")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('PADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('ALIGN', (-1,0), (-1,-1), 'CENTER')
    ]))
    story.append(t_mat)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 12: KESIMPULAN & TAUTAN AKSES
    # =========================================================================
    story.append(Paragraph("11. Kesimpulan &amp; Tautan Akses Sistem", slide_heading))
    story.append(Paragraph("Rangkuman keunggulan arsitektur WebGIS Local serta lembar pengesahan penugasan akademik", slide_subheading))
    story.append(Spacer(1, 10))

    link_data = [[Paragraph(
        "<b>Tautan Akses Operasional WebGIS Local:</b><br/>"
        "&bull; <b>URL Server Utama (WebGIS + REST API):</b> <font color='#0077b6'><u>http://127.0.0.1:5050/</u></font> (Flask Server)<br/>"
        "&bull; <b>URL Server Antarmuka Statis:</b> <font color='#0077b6'><u>http://127.0.0.1:3000/index.html</u></font> (Python HTTP Server)<br/>"
        "&bull; <b>Slide Presentasi Interaktif:</b> <font color='#0077b6'><u>http://127.0.0.1:3000/presentation.html</u></font><br/>"
        "&bull; <b>API Konverter Multi-Format:</b> <code>POST http://127.0.0.1:5050/api/convert</code><br/>"
        "&bull; <b>API Health Check:</b> <font color='#16a34a'><u>http://127.0.0.1:5050/api/health</u></font><br/>"
        "&bull; <b>Peluncur Otomatis:</b> Klik ganda <code>Jalankan_WebGIS.bat</code> pada direktori utama aplikasi.",
        body_style
    )]]
    t_lk = Table(link_data, colWidths=[760])
    t_lk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#3b82f6")),
        ('PADDING', (0,0), (-1,-1), 10)
    ]))
    story.append(t_lk)
    story.append(Spacer(1, 12))

    summary_concl = [
        [
            Paragraph("<b>Kesimpulan Pengembangan WebGIS Local:</b><br/>"
                      "1. <b>Agnostik Wilayah &amp; Fleksibel:</b> Sistem berhasil dibangun tanpa keterikatan pada satu wilayah saja. Pengguna bebas mengunggah data spasial manual untuk memetakan daerah mana pun.<br/>"
                      "2. <b>Performa GDAL C-Engine:</b> Pemanfaatan Pyogrio v0.13.0 terbukti andal dalam mengekstraksi format kompleks ESRI File Geodatabase (GDB) dan Shapefile secara multi-layer.<br/>"
                      "3. <b>Keandalan OGC WMS:</b> Mengintegrasikan 4 server WMS aktif publik (IEM NEXRAD, NASA GIBS, Mundialis OSM &amp; Hillshade) yang terverifikasi mengembalikan respons 200 OK.<br/>"
                      "4. <b>Keunggulan Kartografi:</b> Hierarki Z-Index via Leaflet Custom Panes menjamin marker dan garis tidak akan pernah tertutup poligon.<br/>"
                      "5. <b>Interaktivitas Komprehensif:</b> Dilengkapi analisis buffering, pengukuran geodesik, tabel atribut dengan live search, dan ekspor CSV.", bullet_style),
            Paragraph("<b>Lembar Pengesahan Tugas Akademik:</b><br/>"
                      "Disusun untuk memenuhi persyaratan penugasan mata kuliah:<br/>"
                      "<b>PRAKTEK PENGELOLAAN BIG DATA DAN WEBGIS</b><br/><br/>"
                      "<b>Mahasiswa Penyusun:</b><br/>"
                      "Nama: <b>Ariel Khan</b><br/>"
                      "NIM: <b>V126241001</b><br/><br/>"
                      "<b>Dosen Pengampu:</b><br/>"
                      "<b>Andang Suryana Soma, S.Hut., MP., Ph.D</b><br/>"
                      "<i>Fakultas Kehutanan Universitas Hasanuddin</i><br/><br/>"
                      "<font color='#64748b' size='7.5'><i>\"Spatial Data is the Foundation of Smart Decision Making.\"</i></font>", body_style)
        ]
    ]
    t_sc = Table(summary_concl, colWidths=[490, 270])
    t_sc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#e8f5e9")),
        ('BOX', (0,0), (0,0), 1, colors.HexColor("#cbd5e1")),
        ('BOX', (1,0), (1,0), 1, colors.HexColor("#a7f3d0")),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_sc)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF Berhasil Dibuat: {OUTPUT_PDF_LOCAL}")

    # Copy to legacy name so both filenames work
    try:
        shutil.copyfile(OUTPUT_PDF_LOCAL, OUTPUT_PDF_LEGACY)
        print(f"PDF Berhasil Disinkronkan: {OUTPUT_PDF_LEGACY}")
    except Exception as e:
        print(f"Gagal menyalin ke legacy: {e}")


if __name__ == "__main__":
    create_presentation()
