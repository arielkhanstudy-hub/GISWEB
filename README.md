# Proyek Peta WebGIS Menggunakan Leaflet: Kabupaten Maros

Sistem Informasi Geospasial Berbasis Web (WebGIS) interaktif yang dibangun menggunakan pustaka **Leaflet.js** untuk memenuhi tugas mata kuliah **Pengembangan WebGIS Dasar**.

- **Dosen Pengampu:** Andang Suryana Soma, S.Hut., MP., Ph.D  
- **Institusi:** Fakultas Kehutanan, Universitas Hasanuddin  
- **Wilayah Studi:** Kabupaten Maros, Sulawesi Selatan  

---

## 🚀 Ringkasan Capaian Proyek Sesuai Instruksi Tugas (Slide 19)

| Kebutuhan Tugas | Status | Keterangan Implementasi |
| :--- | :---: | :--- |
| **Peta WebGIS Menggunakan Leaflet** | ✅ Selesai | Menggunakan Leaflet 1.9.4 dengan inisialisasi pusat koordinat Kabupaten Maros `[-5.0005, 119.7253]` dan Zoom 11. |
| **Batas Administrasi Kabupaten/Kota** | ✅ Selesai | Layer batas Kabupaten Maros dan 14 batas Kecamatan (Turikale, Mandai, Bantimurung, Maros Baru, Bontoa, Lau, Simbang, Cenrana, Camba, Mallawa, Tompobulu, Tanralili, Moncongloe, Marusu). |
| **Layer Jaringan Jalan** | ✅ Selesai | Jalan Arteri Primer (Trans Sulawesi Poros Maros-Makassar), Jalan Kolektor Primer (Poros Maros-Bone), Jalur Kereta Api Trans Sulawesi, Jalan Akses Bandara, dan Jalan Pesisir Bontoa. |
| **Layer Jaringan Sungai** | ✅ Selesai | Sungai Maros Utama (DAS Maros Hulu ke Muara Selat Makassar), Sungai Bantimurung (Aliran Kars), Sungai Moncongloe-Tallo Hulu, dan Sungai Muara Tambak Bontoa. |
| **Layer Toponim & Fasilitas Penting** | ✅ Selesai | Marker interaktif dengan custom icon untuk Kantor Bupati Maros, Bandara Sultan Hasanuddin, TN Bantimurung, Geopark Rammang-Rammang UNESCO, Situs Leang-Leang, Stasiun KA Maros, Hutan Riset Fahutan Unhas Bengo-Bengo, RSUD dr. La Palaloi, dan Masjid Al-Markaz. |
| **Layer Tutupan Lahan & Kawasan Hutan** | ✅ Selesai | Klasifikasi tutupan lahan: Taman Nasional Bantimurung Bulusaraung, Hutan Lindung Hulu, Kawasan Karst Geopark Dunia, Sawah Irigasi, Tambak Pesisir, Permukiman Urban, dan Kawasan Khusus Bandara. |
| **Fitur Upload Layer Mandiri** | ✅ Selesai | Pengguna dapat mengunggah berkas **GeoJSON, KML, CSV (koordinat), dan Shapefile (.zip)** langsung ke peta via modal atau drag-and-drop. Dilengkapi tombol sampel instan untuk uji coba! |
| **Presentasi WebGIS dalam Berkas PDF** | ✅ Selesai | Berkas presentasi slide 10 halaman beresolusi tinggi: `Presentasi_WebGIS_Kabupaten_Maros.pdf` lengkap dengan tangkapan layar peta dan tautan WebGIS. |

---

## 📁 Struktur Direktori Proyek

```
webgis-leaflet-kabupaten/
├── index.html                           # Aplikasi utama WebGIS
├── style.css                            # Pengatur gaya visual, tata letak, dan responsivitas
├── app.js                              # Logika Leaflet, kontrol layer, parser upload, pengukuran
├── Jalankan_WebGIS.bat                  # Skrip 1-klik untuk membuka WebGIS & Presentasi
├── presentation.html                    # Penampil slide presentasi berbasis web interaktif
├── Presentasi_WebGIS_Kabupaten_Maros.pdf # Berkas PDF presentasi tugas resmi (Slide 19)
├── generate_presentation_pdf.py         # Skrip generator PDF berbasis ReportLab
├── data/
│   ├── batas_kabupaten.geojson          # Poligon batas Kabupaten Maros
│   ├── batas_kecamatan.geojson          # Poligon 14 batas kecamatan
│   ├── jaringan_jalan.geojson           # Garis hierarki jalan & rel kereta
│   ├── jaringan_sungai.geojson          # Garis hidrologi aliran sungai
│   ├── tutupan_lahan.geojson            # Poligon tutupan lahan & kehutanan
│   ├── toponim_fasilitas.geojson        # Titik marker fasilitas publik & toponim
│   └── sample_uploads/
│       ├── sample_posko_bencana.geojson # Sampel uji upload format GeoJSON
│       ├── sample_zona_wisata.kml       # Sampel uji upload format KML
│       └── sample_titik_layanan.csv     # Sampel uji upload format CSV
└── assets/
    ├── screenshot_overview.png          # Tangkapan layar antarmuka peta lengkap
    ├── screenshot_popup.png             # Tangkapan layar popup interaktif
    └── screenshot_upload.png            # Tangkapan layar fitur upload data spasial
```

---

## 🛠️ Panduan Menjalankan Aplikasi WebGIS

### Cara 1: Menggunakan Skrip 1-Klik (Paling Praktis)
1. Buka folder `webgis-leaflet-kabupaten/` di File Explorer.
2. Klik ganda file **`Jalankan_WebGIS.bat`**.
3. Browser akan otomatis terbuka menampilkan peta WebGIS.

### Cara 2: Membuka Langsung Berkas HTML
1. Klik kanan pada file **`index.html`** &rarr; pilih **Open with** &rarr; **Google Chrome** (atau Microsoft Edge / Firefox).

### Cara 3: Menggunakan Server Lokal Python
Jika ingin menjalankan melalui local server:
```bash
cd C:\Users\ASUS\.gemini\antigravity-ide\scratch\webgis-leaflet-kabupaten
python -m http.server 3000 --bind 127.0.0.1
```
Buka tautan: [http://127.0.0.1:3000/index.html](http://127.0.0.1:3000/index.html)

---

## 🌟 Fitur Utama WebGIS

1. **4 Pilihan Peta Dasar (Basemaps)**:
   - OpenStreetMap Standard
   - Esri World Imagery (Satelit HD)
   - Esri Topographic (Relief Kontur)
   - Esri Dark Canvas (Mode Gelap)
2. **Pengaturan Z-Index Lapisan (Slide 16)**:
   - Menggunakan *Leaflet Custom Panes* sehingga poligon tutupan lahan (`zIndex: 400`) tidak menutupi garis jalan (`zIndex: 480`) maupun marker titik toponim (`zIndex: 600`).
3. **Layanan WMS (Web Map Service OGC) (Slide 11-14)**:
   - Terintegrasi WMS radar cuaca realtime dan WMS OpenStreetMap menggunakan `L.tileLayer.wms()`.
4. **Pop-up Detail Informatif (Slide 15)**:
   - Menyajikan kartu informasi berisi tabel atribut, nama resmi, koordinat presisi, deskripsi naratif objek, serta tombol "Kunjungi Info" dan "Fokus Lokasi".
5. **Alat Pengukuran Interaktif (Measurement Tools)**:
   - Ukur Jarak (panjang garis dalam meter dan kilometer).
   - Ukur Luas Poligon (luas area dalam m², Hektar, dan km²).
6. **Tabel Atribut (Bottom Sheet Drawer)**:
   - Menampilkan seluruh baris atribut spasial mirip software SIG desktop (QGIS/ArcGIS) dengan fitur pencarian dan zoom otomatis.
7. **Pencarian Cepat (Live Search)**:
   - Mencari nama kecamatan, jalan, fasilitas publik, dan sungai secara instan.
8. **Legenda Peta Dinamis**:
   - Menampilkan simbol dan klasifikasi warna yang otomatis menyesuaikan dengan layer yang sedang aktif.

---

## 📄 Berkas Presentasi PDF

Sesuai instruksi pada Slide 19:
> *"Hasil kirimkan presentasi webgisnya dalam pdf file berdasarkan peta laman yang dibuat dan sertakan link webgisnya"*

Berkas presentasi telah dihasilkan dan siap dikumpulkan:
- **Lokasi File:** [`Presentasi_WebGIS_Kabupaten_Maros.pdf`](file:///C:/Users/ASUS/.gemini/antigravity-ide/scratch/webgis-leaflet-kabupaten/Presentasi_WebGIS_Kabupaten_Maros.pdf)
- **Penampil Web:** [`presentation.html`](file:///C:/Users/ASUS/.gemini/antigravity-ide/scratch/webgis-leaflet-kabupaten/presentation.html)
- **Tautan WebGIS:** `http://127.0.0.1:3000/index.html`
