/**
 * WebGIS Local - Aplikasi Peta Interaktif Berbasis Leaflet
 * Tugas Mata Kuliah: PRAKTEK PENGELOLAAN BIG DATA DAN WEBGIS
 * Mahasiswa: Ariel Khan | NIM: V126241001
 * Dosen: Andang Suryana Soma, S.Hut., MP., Ph.D
 */

// =============================================================================
// 1. Inisialisasi Peta & Konfigurasi Dasar (Slide 7 & 8)
// =============================================================================
const DEFAULT_CENTER = [-5.0005, 119.7253]; // Titik Pusat Inisial Peta
const DEFAULT_ZOOM = 11;

const map = L.map('map', {
  center: DEFAULT_CENTER,
  zoom: DEFAULT_ZOOM,
  zoomControl: false, // Kita pindahkan / kelola secara kustom
  attributionControl: true
});

// Tambahkan kontrol zoom kustom di pojok kanan atas
L.control.zoom({ position: 'topright' }).addTo(map);

// Tambahkan kontrol skala peta (Scale Bar) di pojok kiri bawah
L.control.scale({ imperial: false, metric: true, position: 'bottomleft' }).addTo(map);

// =============================================================================
// 2. Pengaturan Z-Index Lapisan Peta Menggunakan Leaflet Panes (Slide 16)
// Memastikan layer polygon tidak menutupi garis dan titik marker
// =============================================================================
map.createPane('tutupanLahanPane');
map.getPane('tutupanLahanPane').style.zIndex = 400;

map.createPane('administrasiPane');
map.getPane('administrasiPane').style.zIndex = 420;

map.createPane('sungaiPane');
map.getPane('sungaiPane').style.zIndex = 450;

map.createPane('jalanPane');
map.getPane('jalanPane').style.zIndex = 480;

map.createPane('userUploadPane');
map.getPane('userUploadPane').style.zIndex = 520;

map.createPane('toponimPane');
map.getPane('toponimPane').style.zIndex = 600;

// =============================================================================
// 3. Konfigurasi Basemaps / Peta Dasar
// Mendukung TileLayer standar dan OGC Web Map Service (WMS)
// =============================================================================
const basemaps = {
  osm: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'
  }),
  satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19,
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP'
  }),
  topo: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19,
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom'
  }),
  dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd'
  }),
  // WMS Basemap: Mundialis Topo-OSM (OGC WMS 1.1.1/1.3.0 Standard)
  wms_topo: L.tileLayer.wms('https://ows.mundialis.de/services/service', {
    layers: 'TOPO-OSM-WMS',
    format: 'image/png',
    transparent: false,
    maxZoom: 18,
    attribution: 'Topografi WMS &copy; Mundialis &copy; OpenStreetMap'
  }),
  // WMS Basemap: Mundialis SRTM30 Colored Hillshade (OGC WMS)
  wms_hillshade: L.tileLayer.wms('https://ows.mundialis.de/services/service', {
    layers: 'SRTM30-Colored-Hillshade',
    format: 'image/png',
    transparent: false,
    maxZoom: 18,
    attribution: 'SRTM30 Hillshade WMS &copy; Mundialis &copy; NASA SRTM'
  })
};

// Aktifkan default basemap OSM
basemaps.osm.addTo(map);
let currentBasemap = 'osm';

// =============================================================================
// 4. Layanan WMS (Web Map Service) Terintegrasi
// Menggunakan server WMS publik terverifikasi dan aktif 100%
// =============================================================================

// WMS 1: Radar Cuaca Real-Time (IEM NEXRAD n0r) - AKTIF
const wmsPrecipitation = L.tileLayer.wms('https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi', {
  layers: 'nexrad-n0r',
  format: 'image/png',
  transparent: true,
  opacity: 0.65,
  zIndex: 410,
  attribution: 'Weather Radar &copy; Iowa Environmental Mesonet (IEM)'
});

// WMS 2: NASA GIBS MODIS Citra Satelit Terra True Color (EPSG:3857) - AKTIF
const wmsOsm = L.tileLayer.wms('https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi', {
  layers: 'MODIS_Terra_CorrectedReflectance_TrueColor',
  format: 'image/jpeg',
  transparent: false,
  opacity: 0.75,
  zIndex: 390,
  version: '1.3.0',
  attribution: 'Citra Satelit &copy; NASA GIBS EOSDIS'
});

// WMS 3: Mundialis OpenStreetMap Terbuka (OGC WMS) - AKTIF
const wmsOrtofoto = L.tileLayer.wms('https://ows.mundialis.de/services/service', {
  layers: 'OSM-WMS',
  format: 'image/png',
  transparent: false,
  opacity: 0.8,
  zIndex: 380,
  attribution: 'Peta WMS &copy; Mundialis &copy; OpenStreetMap'
});

// =============================================================================
// 5. Variabel Global State & Penyimpanan Layer
// =============================================================================
const layers = {
  kabupaten: null,
  kecamatan: null,
  jalan: null,
  sungai: null,
  tutupan: null,
  toponim: null,
  wmsPrecip: wmsPrecipitation,
  wmsOsm: wmsOsm,
  wmsOrtofoto: wmsOrtofoto
};

const rawGeoJsonData = {
  kabupaten: null,
  kecamatan: null,
  jalan: null,
  sungai: null,
  tutupan: null,
  toponim: null
};

const userUploadedLayers = [];

// =============================================================================
// 6. Fungsi Pemuatan Data GeoJSON Bawaan (Data Spasial Kabupaten Maros)
// =============================================================================
async function loadGeoJsonLayers() {
  try {
    // 6.1 Batas Kabupaten Maros
    const resKab = await fetch('data/batas_kabupaten.geojson');
    const dataKab = await resKab.json();
    rawGeoJsonData.kabupaten = dataKab;
    layers.kabupaten = L.geoJSON(dataKab, {
      pane: 'administrasiPane',
      style: {
        color: '#111827',
        weight: 3.5,
        dashArray: '6, 6',
        fill: false,
        opacity: 0.95
      }
    }).addTo(map);

    // 6.2 Batas Kecamatan (14 Kecamatan)
    const resKec = await fetch('data/batas_kecamatan.geojson');
    const dataKec = await resKec.json();
    rawGeoJsonData.kecamatan = dataKec;
    renderKecamatanStats(dataKec.features);
    layers.kecamatan = L.geoJSON(dataKec, {
      pane: 'administrasiPane',
      style: (feature) => ({
        fillColor: feature.properties.COLOR || '#2a9d8f',
        fillOpacity: 0.45,
        color: '#ffffff',
        weight: 1.8,
        opacity: 0.9
      }),
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        const popupContent = `
          <div class="gis-popup-card">
            <div class="gis-popup-header" style="background: linear-gradient(135deg, #1b4332 0%, #2d6a4f 100%);">
              <span class="gis-popup-category">Batas Administrasi</span>
              <div class="gis-popup-title">${p.KECAMATAN}</div>
            </div>
            <div class="gis-popup-body">
              <table class="gis-popup-table">
                <tr><td>Ibukota:</td><td><strong>${p.IBUKOTA}</strong></td></tr>
                <tr><td>Jumlah Penduduk:</td><td><strong>${Number(p.PENDUDUK_2023 || p.JUMLAH_PENDUDUK || 0).toLocaleString('id-ID')} Jiwa</strong></td></tr>
                <tr><td>Luas Wilayah:</td><td>${p.LUAS_KM2} km²</td></tr>
                <tr><td>Kepadatan:</td><td>${p.KEPADATAN_KM2 || p.KEPADATAN_JIWA_KM2 || '-'} Jiwa/km²</td></tr>
                <tr><td>Desa / Kelurahan:</td><td>${p.DESA_KELURAHAN} Desa</td></tr>
                <tr><td>Laki-laki / Perempuan:</td><td>${Number(p.LAKI_LAKI || 0).toLocaleString('id-ID')} / ${Number(p.PEREMPUAN || 0).toLocaleString('id-ID')}</td></tr>
                <tr><td>Rasio Kelamin:</td><td>${p.RASIO_KELAMIN || '-'}</td></tr>
              </table>
              <p style="font-size: 0.72rem; color: #475569; margin-top: 4px; line-height: 1.3;">
                ${p.KETERANGAN || ''}
              </p>
            </div>
            <div class="gis-popup-footer">
              <span class="gis-popup-btn" onclick="zoomToFeatureBounds('${layer._leaflet_id}')">
                <i class="fa-solid fa-expand"></i> Zoom Wilayah
              </span>
              <span style="font-size: 0.68rem; color: #94a3b8;">📊 ${p.SUMBER_DATA || 'BPS Maros 2024'}</span>
            </div>
          </div>
        `;
        layer.bindPopup(popupContent);

        // Highlight saat hover
        layer.on({
          mouseover: function (e) {
            const l = e.target;
            l.setStyle({ fillOpacity: 0.75, weight: 3, color: '#f59e0b' });
            if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
              l.bringToFront();
            }
          },
          mouseout: function (e) {
            layers.kecamatan.resetStyle(e.target);
          }
        });
      }
    }).addTo(map);

    // 6.3 Jaringan Jalan & Jalur Kereta Api
    const resJalan = await fetch('data/jaringan_jalan.geojson');
    const dataJalan = await resJalan.json();
    rawGeoJsonData.jalan = dataJalan;
    layers.jalan = L.geoJSON(dataJalan, {
      pane: 'jalanPane',
      style: (feature) => {
        const p = feature.properties;
        return {
          color: p.COLOR || '#e63946',
          weight: p.WEIGHT || 3,
          opacity: 0.9,
          dashArray: p.DASH || null
        };
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        const popupContent = `
          <div class="gis-popup-card">
            <div class="gis-popup-header" style="background: linear-gradient(135deg, #c1121f 0%, #780000 100%);">
              <span class="gis-popup-category">Jaringan Transportasi</span>
              <div class="gis-popup-title">${p.NAMA || p.NAMA_JALAN}</div>
            </div>
            <div class="gis-popup-body">
              <table class="gis-popup-table">
                <tr><td>Fungsi Jalan:</td><td><strong>${p.FUNGSI}</strong></td></tr>
                <tr><td>Status:</td><td>${p.STATUS}</td></tr>
                <tr><td>Panjang:</td><td>${p.PANJANG_KM} km</td></tr>
                <tr><td>Lebar Jalur:</td><td>${p.LEBAR_M} meter</td></tr>
                <tr><td>Permukaan:</td><td>${p.PERMUKAAN}</td></tr>
              </table>
            </div>
          </div>
        `;
        layer.bindPopup(popupContent);
      }
    }).addTo(map);

    // 6.4 Jaringan Sungai & Hidrologi
    const resSungai = await fetch('data/jaringan_sungai.geojson');
    const dataSungai = await resSungai.json();
    rawGeoJsonData.sungai = dataSungai;
    layers.sungai = L.geoJSON(dataSungai, {
      pane: 'sungaiPane',
      style: (feature) => {
        const p = feature.properties;
        return {
          color: p.COLOR || '#0077b6',
          weight: p.WEIGHT || 3,
          opacity: 0.85
        };
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        const popupContent = `
          <div class="gis-popup-card">
            <div class="gis-popup-header" style="background: linear-gradient(135deg, #0077b6 0%, #03045e 100%);">
              <span class="gis-popup-category">Hidrologi & Sungai</span>
              <div class="gis-popup-title">${p.NAMA || p.NAMA_SUNGAI}</div>
            </div>
            <div class="gis-popup-body">
              <table class="gis-popup-table">
                <tr><td>Klasifikasi:</td><td><strong>${p.ORDE}</strong></td></tr>
                <tr><td>Estimasi Panjang:</td><td>${p.PANJANG_KM} km</td></tr>
                <tr><td>Debit Rata-rata:</td><td>${p.DEBIT_RATA2 || '-'}</td></tr>
                <tr><td>Peran DAS:</td><td>${p.STATUS}</td></tr>
              </table>
            </div>
          </div>
        `;
        layer.bindPopup(popupContent);
      }
    }).addTo(map);

    // 6.5 Tutupan Lahan & Kehutanan
    const resTutupan = await fetch('data/tutupan_lahan.geojson');
    const dataTutupan = await resTutupan.json();
    rawGeoJsonData.tutupan = dataTutupan;
    layers.tutupan = L.geoJSON(dataTutupan, {
      pane: 'tutupanLahanPane',
      style: (feature) => {
        const p = feature.properties;
        return {
          fillColor: p.COLOR || '#1b4332',
          fillOpacity: p.OPACITY || 0.6,
          color: '#ffffff',
          weight: 1.2,
          opacity: 0.7
        };
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        const popupContent = `
          <div class="gis-popup-card">
            <div class="gis-popup-header" style="background: linear-gradient(135deg, #1b4332 0%, #40916c 100%);">
              <span class="gis-popup-category">Tutupan Lahan & Hutan</span>
              <div class="gis-popup-title">${p.KELAS || p.KLASIFIKASI}</div>
            </div>
            <div class="gis-popup-body">
              <table class="gis-popup-table">
                <tr><td>Kode SNI:</td><td><code>${p.KODE_SNI}</code></td></tr>
                <tr><td>Pengelola:</td><td>${p.PENGELOLA}</td></tr>
                <tr><td>Luas Kawasan:</td><td>${(p.LUAS_HA || p.LUAS_ESTIMASI_HA || 0)?.toLocaleString('id-ID')} Ha</td></tr>
                <tr><td>Status Hukum:</td><td>${p.STATUS_HUKUM}</td></tr>
              </table>
              <p style="font-size: 0.72rem; color: #475569; margin-top: 4px; line-height: 1.3;">
                ${p.DESKRIPSI || ''}
              </p>
            </div>
          </div>
        `;
        layer.bindPopup(popupContent);
      }
    }).addTo(map);

    // 6.6 Toponim & Fasilitas Penting (Marker Interaktif Sesuai Slide 15)
    const resToponim = await fetch('data/toponim_fasilitas.geojson');
    const dataToponim = await resToponim.json();
    rawGeoJsonData.toponim = dataToponim;

    layers.toponim = L.geoJSON(dataToponim, {
      pane: 'toponimPane',
      pointToLayer: (feature, latlng) => {
        const p = feature.properties;
        // Buat custom marker divIcon estetik
        const markerHtml = `
          <div style="
            background-color: ${p.icon_color || '#e63946'};
            width: 32px;
            height: 32px;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            border: 2px solid #ffffff;
            cursor: pointer;
            transition: transform 0.2s;
          ">
            <i class="fa-solid fa-${p.icon || 'location-dot'}" style="
              transform: rotate(45deg);
              color: #ffffff;
              font-size: 13px;
            "></i>
          </div>
        `;

        const customIcon = L.divIcon({
          className: 'custom-poi-marker',
          html: markerHtml,
          iconSize: [32, 32],
          iconAnchor: [16, 32],
          popupAnchor: [0, -32]
        });

        const marker = L.marker(latlng, {
          icon: customIcon,
          zIndexOffset: 1000 // Menjamin marker selalu di posisi paling atas (Slide 16)
        });

        const popupContent = `
          <div class="gis-popup-card">
            <div class="gis-popup-header" style="background: linear-gradient(135deg, ${p.icon_color || '#1b4332'} 0%, #081c15 100%);">
              <span class="gis-popup-category">${p.kategori}</span>
              <div class="gis-popup-title">${p.nama}</div>
            </div>
            <div class="gis-popup-body">
              <table class="gis-popup-table">
                <tr><td>Alamat:</td><td>${p.alamat}</td></tr>
                <tr><td>Kontak:</td><td>${p.telp || p.kontak || '-'}</td></tr>
                <tr><td>Koordinat:</td><td><code>${latlng.lat.toFixed(5)}, ${latlng.lng.toFixed(5)}</code></td></tr>
              </table>
              <p style="font-size: 0.72rem; color: #475569; margin-top: 4px; line-height: 1.3;">
                ${p.deskripsi}
              </p>
            </div>
            <div class="gis-popup-footer">
              ${p.website ? `<a href="${p.website}" target="_blank" class="gis-popup-btn">
                <i class="fa-solid fa-arrow-up-right-from-square"></i> Info Web
              </a>` : ''}
              <span class="gis-popup-btn" onclick="map.flyTo([${latlng.lat}, ${latlng.lng}], 16)">
                <i class="fa-solid fa-magnifying-glass-plus"></i> Fokus
              </span>
            </div>
          </div>
        `;
        marker.bindPopup(popupContent);
        return marker;
      }
    }).addTo(map);

    // Refresh UI Tabel Atribut & Legenda
    populateAttributeTable('kecamatan');
    buildDynamicLegend();
    showToast('Seluruh layer data spasial bawaan berhasil dimuat!', 'success');

  } catch (error) {
    console.error('Gagal memuat layer GeoJSON:', error);
    showToast('Terjadi kendala saat membaca data GeoJSON lokal.', 'error');
  }
}

// =============================================================================
// 7. Pengendali Layer (Layer Controls) & Event Listener (Slide 13)
// =============================================================================
function setupLayerControls() {
  // Toggle Switch Layer Tematik
  const toggleMap = {
    layerToggleToponim: 'toponim',
    layerToggleJalan: 'jalan',
    layerToggleSungai: 'sungai',
    layerToggleKecamatan: 'kecamatan',
    layerToggleTutupan: 'tutupan',
    layerToggleKabupaten: 'kabupaten',
    layerToggleWmsPrecip: 'wmsPrecip',
    layerToggleWmsOsm: 'wmsOsm',
    layerToggleWmsOrtofoto: 'wmsOrtofoto'
  };

  for (const [elemId, layerKey] of Object.entries(toggleMap)) {
    const el = document.getElementById(elemId);
    if (!el) continue;

    el.addEventListener('change', (e) => {
      const targetLayer = layers[layerKey];
      if (!targetLayer) return;

      if (e.target.checked) {
        map.addLayer(targetLayer);
      } else {
        map.removeLayer(targetLayer);
      }
      buildDynamicLegend();
    });
  }

  // Slider Opacity Transparansi Per Layer
  document.querySelectorAll('.opacity-slider-box input[type="range"]').forEach(slider => {
    slider.addEventListener('input', (e) => {
      const layerName = e.target.dataset.layer;
      const opacity = parseFloat(e.target.value);
      const targetLayer = layers[layerName];

      if (!targetLayer) return;

      if (targetLayer.setStyle) {
        targetLayer.setStyle({ fillOpacity: opacity, opacity: opacity });
      } else if (targetLayer.setOpacity) {
        targetLayer.setOpacity(opacity);
      } else if (layerName === 'toponim') {
        // Atur opacity marker
        targetLayer.eachLayer(m => {
          if (m.setOpacity) m.setOpacity(opacity);
        });
      }
    });
  });

  // Tombol Zoom to Extent Per Layer
  document.querySelectorAll('.btn-zoom-layer').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const layerName = btn.dataset.zoomLayer;
      const targetLayer = layers[layerName];
      if (targetLayer && map.hasLayer(targetLayer)) {
        map.fitBounds(targetLayer.getBounds(), { padding: [40, 40] });
      } else {
        showToast('Layer sedang dinonaktifkan. Aktifkan terlebih dahulu.', 'info');
      }
    });
  });

  // Basemap Selector Switching
  document.querySelectorAll('.basemap-option').forEach(card => {
    card.addEventListener('click', () => {
      const selected = card.dataset.basemap;
      if (selected === currentBasemap) return;

      // Hapus basemap aktif
      map.removeLayer(basemaps[currentBasemap]);
      // Pasang basemap baru
      basemaps[selected].addTo(map);
      basemaps[selected].bringToBack();
      currentBasemap = selected;

      // Update active UI card
      document.querySelectorAll('.basemap-option').forEach(c => c.classList.remove('active'));
      card.classList.add('active');

      showToast(`Peta dasar diubah ke ${card.querySelector('span').innerText}`, 'info');
    });
  });
}

// =============================================================================
// 8. Fitur Upload & Import Berkas Spasial (GeoJSON, KML, CSV, Shapefile)
// Sesuai Spesifikasi Tugas Slide 19
// =============================================================================
function setupUploadFeature() {
  const modal = document.getElementById('uploadModal');
  const btnOpen = document.getElementById('btnOpenUploadModal');
  const btnClose = document.getElementById('btnCloseUploadModal');
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');

  // Buka & Tutup Modal
  btnOpen.addEventListener('click', () => modal.classList.add('active'));
  btnClose.addEventListener('click', () => modal.classList.remove('active'));
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.remove('active');
  });

  // Klik dropzone untuk memilih file
  dropZone.addEventListener('click', () => fileInput.click());

  // Drag and Drop Effects
  ['dragenter', 'dragover'].forEach(event => {
    dropZone.addEventListener(event, (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
  });
  ['dragleave', 'drop'].forEach(event => {
    dropZone.addEventListener(event, (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
    });
  });

  // Tangani file drop
  dropZone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) handleIncomingFile(files[0]);
  });

  // Tangani file input change
  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) handleIncomingFile(e.target.files[0]);
  });

  // Tombol Uji Coba Cepat Sampel
  document.getElementById('btnLoadSampleBencana').addEventListener('click', () => {
    loadSampleUpload('data/sample_uploads/sample_risiko_bencana.geojson', 'Risiko Bencana Maros (GeoJSON)', '#d90429');
    modal.classList.remove('active');
  });

  const btnShp = document.getElementById('btnLoadSampleShp');
  if (btnShp) {
    btnShp.addEventListener('click', async () => {
      modal.classList.remove('active');
      showToast('Memuat sampel Batas Desa (SHP ZIP)...', 'info');
      try {
        const resp = await fetch('data/sample_uploads/sample_desa_maros.zip');
        const blob = await resp.blob();
        const file = new File([blob], 'sample_desa_maros.zip', { type: 'application/zip' });
        await handleIncomingFile(file);
      } catch (err) {
        showToast('Gagal memuat sampel SHP: ' + err.message, 'error');
      }
    });
  }

  document.getElementById('btnLoadSampleKml').addEventListener('click', () => {
    loadSampleUpload('data/sample_uploads/sample_rtrw_maros.kml', 'RTRW Maros (KML)', '#2a9d8f');
    modal.classList.remove('active');
  });

  document.getElementById('btnLoadSampleCsv').addEventListener('click', () => {
    loadSampleUpload('data/sample_uploads/sample_puskesmas_maros.csv', 'Puskesmas Maros (CSV)', '#0077b6');
    modal.classList.remove('active');
  });

  const btnGdb = document.getElementById('btnLoadSampleGdb');
  if (btnGdb) {
    btnGdb.addEventListener('click', async () => {
      modal.classList.remove('active');
      showToast('Memuat sampel Geodatabase (GDB ZIP)...', 'info');
      try {
        const resp = await fetch('data/sample_uploads/sample_maros_geodatabase.zip');
        const blob = await resp.blob();
        const file = new File([blob], 'sample_maros_geodatabase.zip', { type: 'application/zip' });
        await handleIncomingFile(file);
      } catch (err) {
        showToast('Gagal memuat sampel GDB: ' + err.message, 'error');
      }
    });
  }
}

// Pemroses Berkas Masuk
async function handleIncomingFile(file) {
  const fileName = file.name;
  const ext = fileName.split('.').pop().toLowerCase();
  showToast(`Memproses berkas ${fileName}...`, 'info');

  try {
    let geojsonData = null;

    // 1. Coba konversi via Backend Python Flask terlebih dahulu (Mendukung SEMUA format GIS)
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('layer_name', fileName.replace(/\.[^/.]+$/, ''));
      const resp = await fetch('http://127.0.0.1:5050/api/convert', { method: 'POST', body: formData, signal: AbortSignal.timeout(15000) });
      if (resp.ok) {
        const result = await resp.json();
        if (result && result.geojson) {
          addUploadedGeoJsonToMap(result.geojson, fileName);
          document.getElementById('uploadModal').classList.remove('active');
          return;
        }
      }
    } catch (backendErr) {
      console.log('Backend Python tidak tersedia, menggunakan parser frontend:', backendErr.message);
    }

    // 2. Fallback parser frontend
    if (ext === 'geojson' || ext === 'json') {
      const text = await file.text();
      geojsonData = JSON.parse(text);
    } else if (ext === 'kml') {
      const text = await file.text();
      const dom = new DOMParser().parseFromString(text, 'text/xml');
      geojsonData = toGeoJSON.kml(dom);
    } else if (ext === 'csv') {
      const text = await file.text();
      geojsonData = parseCsvToGeoJson(text);
    } else if (ext === 'zip') {
      const arrayBuffer = await file.arrayBuffer();
      geojsonData = await shp(arrayBuffer);
      if (Array.isArray(geojsonData)) {
        const allFeats = geojsonData.flatMap(g => g.features || []);
        geojsonData = { type: 'FeatureCollection', features: allFeats };
      }
    } else {
      showToast('Format berkas membutuhkan server backend. Pastikan server.py berjalan untuk ' + ext, 'error');
      return;
    }

    if (geojsonData) {
      addUploadedGeoJsonToMap(geojsonData, fileName);
      document.getElementById('uploadModal').classList.remove('active');
    }
  } catch (error) {
    console.error('Error membaca file spasial:', error);
    showToast(`Gagal membaca berkas: ${error.message}`, 'error');
  }
}

// Parser CSV ke GeoJSON
function parseCsvToGeoJson(csvText) {
  const parsed = Papa.parse(csvText, { header: true, skipEmptyLines: true });
  const rows = parsed.data;
  const features = [];

  for (const row of rows) {
    // Cari kolom latitude dan longitude secara fleksibel
    let lat = null, lng = null;
    for (const key of Object.keys(row)) {
      const k = key.toLowerCase().trim();
      if (k === 'lat' || k === 'latitude' || k === 'y') lat = parseFloat(row[key]);
      if (k === 'lng' || k === 'long' || k === 'longitude' || k === 'x') lng = parseFloat(row[key]);
    }

    if (!isNaN(lat) && !isNaN(lng) && lat !== null && lng !== null) {
      features.push({
        type: 'Feature',
        properties: row,
        geometry: {
          type: 'Point',
          coordinates: [lng, lat]
        }
      });
    }
  }

  if (features.length === 0) {
    throw new Error('Kolom koordinat Latitude/Longitude tidak ditemukan pada file CSV.');
  }

  return {
    type: 'FeatureCollection',
    features: features
  };
}

// Muat Sampel Spasial
async function loadSampleUpload(url, label, color) {
  try {
    const res = await fetch(url);
    const ext = url.split('.').pop().toLowerCase();
    let geojsonData = null;

    if (ext === 'geojson') {
      geojsonData = await res.json();
    } else if (ext === 'kml') {
      const text = await res.text();
      const dom = new DOMParser().parseFromString(text, 'text/xml');
      geojsonData = toGeoJSON.kml(dom);
    } else if (ext === 'csv') {
      const text = await res.text();
      geojsonData = parseCsvToGeoJson(text);
    }

    if (geojsonData) {
      addUploadedGeoJsonToMap(geojsonData, label, color);
    }
  } catch (e) {
    console.error('Gagal memuat sampel upload:', e);
    showToast('Gagal memuat berkas sampel.', 'error');
  }
}

// Tambahkan GeoJSON Upload ke Peta & Sidebar Control
function addUploadedGeoJsonToMap(geojsonData, layerName, assignedColor) {
  // Pilih warna acak yang cantik jika tidak ditentukan
  const palette = ['#e63946', '#2a9d8f', '#e76f51', '#f4a261', '#457b9d', '#9d4edd', '#00b4d8'];
  const color = assignedColor || palette[userUploadedLayers.length % palette.length];

  const layer = L.geoJSON(geojsonData, {
    pane: 'userUploadPane',
    style: {
      color: color,
      weight: 3,
      fillColor: color,
      fillOpacity: 0.55
    },
    pointToLayer: (feature, latlng) => {
      return L.circleMarker(latlng, {
        radius: 8,
        fillColor: color,
        color: '#ffffff',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.85
      });
    },
    onEachFeature: (feature, l) => {
      const props = feature.properties || {};
      let rows = '';
      for (const [k, v] of Object.entries(props)) {
        rows += `<tr><td>${k}:</td><td><strong>${v}</strong></td></tr>`;
      }
      l.bindPopup(`
        <div class="gis-popup-card">
          <div class="gis-popup-header" style="background: ${color};">
            <span class="gis-popup-category">Layer Upload</span>
            <div class="gis-popup-title">${props.NAMA || props.name || props.NAMA_POSKO || props.NAMA_LOKASI || layerName}</div>
          </div>
          <div class="gis-popup-body">
            <table class="gis-popup-table">${rows || '<tr><td>Data:</td><td>Fitur Spasial</td></tr>'}</table>
          </div>
        </div>
      `);
    }
  }).addTo(map);

  const layerId = 'user_layer_' + Date.now();
  userUploadedLayers.push({ id: layerId, name: layerName, layer: layer, color: color, data: geojsonData });
  rawGeoJsonData[layerId] = geojsonData;

  const tableSelect = document.getElementById('tableLayerSelect');
  if (tableSelect) {
    const opt = document.createElement('option');
    opt.value = layerId;
    opt.id = `opt_${layerId}`;
    opt.textContent = `Upload: ${layerName.length > 20 ? layerName.substring(0, 18) + '...' : layerName}`;
    tableSelect.appendChild(opt);
  }

  // Update UI sidebar
  updateUserLayersListUI();

  // Zoom ke layer yang diupload
  try {
    map.fitBounds(layer.getBounds(), { padding: [40, 40] });
  } catch (err) {
    console.warn('Could not fit bounds on uploaded data:', err);
  }

  showToast(`Layer "${layerName}" berhasil ditambahkan ke peta!`, 'success');
  buildDynamicLegend();
}

// Perbarui Tampilan Daftar Layer Unggahan di Sidebar
function updateUserLayersListUI() {
  const container = document.getElementById('userLayersList');
  const countBadge = document.getElementById('countUserLayers');
  countBadge.innerText = userUploadedLayers.length;

  if (userUploadedLayers.length === 0) {
    container.innerHTML = `
      <p style="font-size: 0.74rem; color: var(--text-muted); text-align: center; padding: 8px;">
        Belum ada layer tambahan. Klik tombol <strong>Upload Layer</strong> di atas untuk menambahkan berkas Anda.
      </p>
    `;
    return;
  }

  container.innerHTML = '';
  userUploadedLayers.forEach((item, index) => {
    const itemEl = document.createElement('div');
    itemEl.className = 'layer-item';
    itemEl.innerHTML = `
      <div class="layer-main-row">
        <div class="layer-label-group">
          <span class="layer-color-badge" style="background: ${item.color};"></span>
          <span class="layer-name" title="${item.name}">${item.name.length > 20 ? item.name.substring(0, 18) + '...' : item.name}</span>
        </div>
        <label class="switch">
          <input type="checkbox" id="toggle_${item.id}" checked>
          <span class="slider-toggle"></span>
        </label>
      </div>
      <div class="layer-sub-controls">
        <button class="btn-zoom-layer" id="zoom_${item.id}">
          <i class="fa-solid fa-crosshairs"></i> Zoom
        </button>
        <button class="btn-zoom-layer" id="del_${item.id}" style="color: #e63946; border-color: #fca5a5;">
          <i class="fa-solid fa-trash"></i> Hapus
        </button>
      </div>
    `;
    container.appendChild(itemEl);

    // Event toggle
    document.getElementById(`toggle_${item.id}`).addEventListener('change', (e) => {
      if (e.target.checked) map.addLayer(item.layer);
      else map.removeLayer(item.layer);
      buildDynamicLegend();
    });

    // Event zoom
    document.getElementById(`zoom_${item.id}`).addEventListener('click', () => {
      map.fitBounds(item.layer.getBounds(), { padding: [40, 40] });
    });

    // Event hapus
    document.getElementById(`del_${item.id}`).addEventListener('click', () => {
      map.removeLayer(item.layer);
      delete rawGeoJsonData[item.id];
      const optEl = document.getElementById(`opt_${item.id}`);
      if (optEl) optEl.remove();
      userUploadedLayers.splice(index, 1);
      updateUserLayersListUI();
      buildDynamicLegend();
      showToast(`Layer "${item.name}" dihapus.`, 'info');
    });
  });
}

// =============================================================================
// 9. Legenda Peta Dinamis (Map Legend)
// =============================================================================
function buildDynamicLegend() {
  const container = document.getElementById('legendBody');
  container.innerHTML = '';

  // Batas Kecamatan
  if (layers.kecamatan && map.hasLayer(layers.kecamatan)) {
    const sec = document.createElement('div');
    sec.innerHTML = `
      <div class="legend-section-title">Batas Kecamatan (BPS 2024)</div>
      <div class="legend-entry"><span class="legend-color-box" style="background:#2a9d8f;"></span><span>14 Kecamatan Kab. Maros</span></div>
    `;
    container.appendChild(sec);
  }

  // Tutupan Lahan
  if (layers.tutupan && map.hasLayer(layers.tutupan)) {
    const sec = document.createElement('div');
    sec.innerHTML = `
      <div class="legend-section-title">Tutupan Lahan & Hutan</div>
      <div class="legend-entry"><span class="legend-color-box" style="background:#1b4332;"></span><span>Taman Nasional & Konservasi</span></div>
      <div class="legend-entry"><span class="legend-color-box" style="background:#2d6a4f;"></span><span>Hutan Lindung Hulu</span></div>
      <div class="legend-entry"><span class="legend-color-box" style="background:#74c69d;"></span><span>Kawasan Karst Geopark</span></div>
      <div class="legend-entry"><span class="legend-color-box" style="background:#d4a373;"></span><span>Pertanian Sawah Irigasi</span></div>
      <div class="legend-entry"><span class="legend-color-box" style="background:#00b4d8;"></span><span>Tambak & Perikanan Pesisir</span></div>
      <div class="legend-entry"><span class="legend-color-box" style="background:#e07a5f;"></span><span>Permukiman & Perkotaan</span></div>
      <div class="legend-entry"><span class="legend-color-box" style="background:#9d4edd;"></span><span>Bandara Sultan Hasanuddin</span></div>
    `;
    container.appendChild(sec);
  }

  // Jaringan Jalan
  if (layers.jalan && map.hasLayer(layers.jalan)) {
    const sec = document.createElement('div');
    sec.innerHTML = `
      <div class="legend-section-title">Jaringan Jalan</div>
      <div class="legend-entry"><span class="legend-line-box" style="background:#e63946;"></span><span>Jalan Trans Sulawesi / Arteri</span></div>
      <div class="legend-entry"><span class="legend-line-box" style="background:#f77f00;"></span><span>Jalan Poros Maros - Bone</span></div>
      <div class="legend-entry"><span class="legend-line-box" style="background:#212529; border: 1px dashed white;"></span><span>Rel KA Trans Sulawesi</span></div>
    `;
    container.appendChild(sec);
  }

  // Jaringan Sungai
  if (layers.sungai && map.hasLayer(layers.sungai)) {
    const sec = document.createElement('div');
    sec.innerHTML = `
      <div class="legend-section-title">Hidrologi</div>
      <div class="legend-entry"><span class="legend-line-box" style="background:#0077b6;"></span><span>Sungai Maros Utama</span></div>
      <div class="legend-entry"><span class="legend-line-box" style="background:#0096c7;"></span><span>Sungai Bantimurung</span></div>
    `;
    container.appendChild(sec);
  }

  // Toponim
  if (layers.toponim && map.hasLayer(layers.toponim)) {
    const sec = document.createElement('div');
    sec.innerHTML = `
      <div class="legend-section-title">Fasilitas & Toponim</div>
      <div class="legend-entry"><i class="fa-solid fa-building-columns legend-point-icon" style="color:#d90429;"></i><span>Pemerintahan (Bupati)</span></div>
      <div class="legend-entry"><i class="fa-solid fa-waterfall legend-point-icon" style="color:#2a9d8f;"></i><span>Wisata & Geopark</span></div>
      <div class="legend-entry"><i class="fa-solid fa-plane-departure legend-point-icon" style="color:#0077b6;"></i><span>Bandara Internasional</span></div>
      <div class="legend-entry"><i class="fa-solid fa-train legend-point-icon" style="color:#6f42c1;"></i><span>Stasiun Kereta Api</span></div>
      <div class="legend-entry"><i class="fa-solid fa-tree legend-point-icon" style="color:#1b4332;"></i><span>Hutan Riset Unhas</span></div>
    `;
    container.appendChild(sec);
  }

  // Layer Unggahan Pengguna
  const activeUserLayers = userUploadedLayers.filter(u => map.hasLayer(u.layer));
  if (activeUserLayers.length > 0) {
    const sec = document.createElement('div');
    sec.innerHTML = `<div class="legend-section-title">Layer Unggahan</div>`;
    activeUserLayers.forEach(u => {
      sec.innerHTML += `
        <div class="legend-entry">
          <span class="legend-color-box" style="background:${u.color};"></span>
          <span>${u.name}</span>
        </div>
      `;
    });
    container.appendChild(sec);
  }

  if (container.children.length === 0) {
    container.innerHTML = `<p style="color: var(--text-muted); font-size: 0.72rem;">Tidak ada layer aktif untuk ditampilkan.</p>`;
  }
}

// =============================================================================
// 10. Tabel Atribut Interaktif (Attribute Table Drawer)
// =============================================================================
let currentTableData = { layerKey: null, columns: [], rows: [] };

function populateAttributeTable(layerKey, filterQuery = '') {
  const tableHead = document.getElementById('attributeTableHead');
  const tableBody = document.getElementById('attributeTableBody');
  const geojson = rawGeoJsonData[layerKey];

  tableHead.innerHTML = '';
  tableBody.innerHTML = '';

  if (!geojson || !geojson.features || geojson.features.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #94a3b8; padding: 20px;">Tidak ada data atribut untuk layer ini.</td></tr>';
    return;
  }

  // Ambil semua kolom unik dari properties
  const sampleProps = geojson.features[0].properties;
  const columns = Object.keys(sampleProps).filter(k => !['COLOR', 'WEIGHT', 'OPACITY', 'DASH', 'icon_color', 'coords'].includes(k));

  currentTableData = { layerKey, columns, rows: geojson.features };

  // Header
  let headHtml = '<tr><th>Aksi</th>';
  for (const col of columns) {
    headHtml += `<th>${col.replace(/_/g, ' ')}</th>`;
  }
  headHtml += '</tr>';
  tableHead.innerHTML = headHtml;

  // Filter
  const q = filterQuery.toLowerCase().trim();
  const filtered = q
    ? geojson.features.filter(f => Object.values(f.properties || {}).some(v => String(v).toLowerCase().includes(q)))
    : geojson.features;

  if (filtered.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="${columns.length + 1}" style="text-align: center; padding: 15px; color: #94a3b8;">Tidak ada baris yang cocok dengan "${filterQuery}"</td></tr>`;
    return;
  }

  // Body
  filtered.forEach((feat, idx) => {
    const origIdx = geojson.features.indexOf(feat);
    const row = document.createElement('tr');
    let rowHtml = `
      <td>
        <button class="btn-sample" style="padding: 2px 6px; font-size: 0.68rem;" onclick="focusFeatureByIndex('${layerKey}', ${origIdx})">
          <i class="fa-solid fa-crosshairs"></i> Lihat
        </button>
      </td>
    `;
    for (const col of columns) {
      const val = feat.properties[col];
      rowHtml += `<td>${val !== undefined && val !== null ? val : '-'}</td>`;
    }
    row.innerHTML = rowHtml;
    tableBody.appendChild(row);
  });
}

// Export CSV handler
function exportCurrentTableToCsv() {
  if (!currentTableData.rows || !currentTableData.rows.length) {
    showToast('Tidak ada data tabel untuk diekspor.', 'error');
    return;
  }
  const cols = currentTableData.columns;
  const header = cols.join(',');
  const rows = currentTableData.rows.map(f => {
    return cols.map(c => {
      let v = f.properties[c];
      if (v === undefined || v === null) v = '';
      v = String(v).replace(/"/g, '""');
      return `"${v}"`;
    }).join(',');
  });
  const csvContent = 'data:text/csv;charset=utf-8,' + encodeURIComponent([header, ...rows].join('\n'));
  const link = document.createElement('a');
  link.setAttribute('href', csvContent);
  link.setAttribute('download', `WebGIS_Local_${currentTableData.layerKey}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  showToast(`Data "${currentTableData.layerKey}" berhasil diekspor ke CSV!`, 'success');
}

// Fokus ke Fitur Berdasarkan Indeks Tabel
window.focusFeatureByIndex = function (layerKey, index) {
  let targetLayerGroup = layers[layerKey];
  if (!targetLayerGroup) {
    const ul = userUploadedLayers.find(u => u.id === layerKey);
    if (ul) targetLayerGroup = ul.layer;
  }
  if (!targetLayerGroup) return;

  if (!map.hasLayer(targetLayerGroup)) {
    map.addLayer(targetLayerGroup);
    const chk = document.getElementById(`layerToggle${layerKey.charAt(0).toUpperCase() + layerKey.slice(1)}`);
    if (chk) chk.checked = true;
    const userChk = document.getElementById(`toggle_${layerKey}`);
    if (userChk) userChk.checked = true;
  }

  let count = 0;
  targetLayerGroup.eachLayer(layer => {
    if (count === index) {
      if (layer.getBounds) {
        map.fitBounds(layer.getBounds(), { padding: [50, 50], maxZoom: 15 });
      } else if (layer.getLatLng) {
        map.flyTo(layer.getLatLng(), 16);
      }
      setTimeout(() => layer.openPopup(), 300);
    }
    count++;
  });
};

window.zoomToFeatureBounds = function (leafletId) {
  const layer = map._layers[leafletId];
  if (layer && layer.getBounds) {
    map.fitBounds(layer.getBounds(), { padding: [40, 40] });
  }
};

// =============================================================================
// 11. Pengukuran Jarak & Luas Area (Measurement Tools)
// =============================================================================
let measureMode = null; // 'distance' | 'area' | null
let measurePoints = [];
let measureLayerGroup = L.layerGroup().addTo(map);

function setupMeasurementTools() {
  const btnDist = document.getElementById('btnMeasureDistance');
  const btnArea = document.getElementById('btnMeasureArea');

  btnDist.addEventListener('click', () => {
    if (measureMode === 'distance') {
      stopMeasurement();
    } else {
      startMeasurement('distance');
    }
  });

  btnArea.addEventListener('click', () => {
    if (measureMode === 'area') {
      stopMeasurement();
    } else {
      startMeasurement('area');
    }
  });

  map.on('click', (e) => {
    if (!measureMode) return;

    measurePoints.push(e.latlng);
    renderMeasurement();
  });

  map.on('dblclick', (e) => {
    if (measureMode) {
      e.originalEvent.preventDefault();
      showToast('Pengukuran selesai.', 'success');
      measureMode = null;
      map.getContainer().style.cursor = '';
      map.doubleClickZoom.enable();
      document.getElementById('btnMeasureDistance').classList.remove('active');
      document.getElementById('btnMeasureArea').classList.remove('active');
    }
  });
}

function startMeasurement(mode) {
  stopMeasurement();
  measureMode = mode;
  measurePoints = [];
  map.getContainer().style.cursor = 'crosshair';

  if (mode === 'distance') {
    document.getElementById('btnMeasureDistance').classList.add('active');
    showToast('Klik titik-titik pada peta untuk mengukur jarak. Dobel-klik tombol untuk selesai.', 'info');
  } else {
    document.getElementById('btnMeasureArea').classList.add('active');
    showToast('Klik titik-titik poligon pada peta untuk mengukur luas area.', 'info');
  }
}

function stopMeasurement() {
  measureMode = null;
  measurePoints = [];
  measureLayerGroup.clearLayers();
  map.getContainer().style.cursor = '';
  document.getElementById('btnMeasureDistance').classList.remove('active');
  document.getElementById('btnMeasureArea').classList.remove('active');
}

function renderMeasurement() {
  measureLayerGroup.clearLayers();

  if (measurePoints.length === 0) return;

  measurePoints.forEach((pt, i) => {
    L.circleMarker(pt, { radius: 5, color: '#e63946', fillColor: '#ffffff', fillOpacity: 1 }).addTo(measureLayerGroup);
  });

  if (measureMode === 'distance' && measurePoints.length >= 2) {
    const line = L.polyline(measurePoints, { color: '#e63946', weight: 3, dashArray: '5, 8' }).addTo(measureLayerGroup);
    let totalMeters = 0;
    for (let i = 0; i < measurePoints.length - 1; i++) {
      totalMeters += measurePoints[i].distanceTo(measurePoints[i + 1]);
    }
    const distText = totalMeters >= 1000 ? `${(totalMeters / 1000).toFixed(2)} km` : `${Math.round(totalMeters)} meter`;
    const lastPt = measurePoints[measurePoints.length - 1];
    L.popup({ autoClose: false, closeOnClick: false })
      .setLatLng(lastPt)
      .setContent(`<strong>Jarak Total:</strong> ${distText}`)
      .openOn(map);
  } else if (measureMode === 'area' && measurePoints.length >= 3) {
    const poly = L.polygon(measurePoints, { color: '#2a9d8f', fillColor: '#2a9d8f', fillOpacity: 0.35 }).addTo(measureLayerGroup);
    // Hitung estimasi luas menggunakan spherical polygon area
    const areaSqMeters = calculatePolygonArea(measurePoints);
    let areaText = '';
    if (areaSqMeters >= 1000000) {
      areaText = `${(areaSqMeters / 1000000).toFixed(2)} km² (${(areaSqMeters / 10000).toFixed(1)} Ha)`;
    } else {
      areaText = `${(areaSqMeters / 10000).toFixed(2)} Ha (${Math.round(areaSqMeters)} m²)`;
    }
    const centroid = poly.getBounds().getCenter();
    L.popup({ autoClose: false, closeOnClick: false })
      .setLatLng(centroid)
      .setContent(`<strong>Luas Wilayah:</strong> ${areaText}`)
      .openOn(map);
  }
}

// Kalkulasi Luas Poligon Sederhana (Spherical Excess Approximation)
function calculatePolygonArea(latlngs) {
  const radius = 6378137;
  let area = 0;
  if (latlngs.length < 3) return 0;
  for (let i = 0; i < latlngs.length; i++) {
    const p1 = latlngs[i];
    const p2 = latlngs[(i + 1) % latlngs.length];
    area += ((p2.lng - p1.lng) * Math.PI / 180) * (2 + Math.sin(p1.lat * Math.PI / 180) + Math.sin(p2.lat * Math.PI / 180));
  }
  area = Math.abs(area * radius * radius / 2.0);
  return area;
}

// =============================================================================
// 12. Pencarian Live (Search Features)
// =============================================================================
function setupLiveSearch() {
  const searchInput = document.getElementById('searchInput');
  const resultsContainer = document.getElementById('searchResultsList');

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    resultsContainer.innerHTML = '';

    if (!query) {
      resultsContainer.innerHTML = '<p style="font-size: 0.75rem; color: var(--text-muted); text-align: center;">Ketikkan kata kunci di atas untuk mencari entitas spasial secara instan.</p>';
      return;
    }

    const matches = [];

    // Cari di Kecamatan
    if (rawGeoJsonData.kecamatan) {
      rawGeoJsonData.kecamatan.features.forEach((f, idx) => {
        const name = f.properties.KECAMATAN;
        if (name && name.toLowerCase().includes(query)) {
          matches.push({ type: 'Kecamatan', name: name, sub: `Ibukota: ${f.properties.IBUKOTA}`, layerKey: 'kecamatan', index: idx, icon: 'map-location-dot' });
        }
      });
    }

    // Cari di Toponim
    if (rawGeoJsonData.toponim) {
      rawGeoJsonData.toponim.features.forEach((f, idx) => {
        const name = f.properties.nama;
        if (name && name.toLowerCase().includes(query)) {
          matches.push({ type: f.properties.kategori, name: name, sub: f.properties.alamat, layerKey: 'toponim', index: idx, icon: f.properties.icon || 'location-dot' });
        }
      });
    }

    // Cari di Jalan
    if (rawGeoJsonData.jalan) {
      rawGeoJsonData.jalan.features.forEach((f, idx) => {
        const name = f.properties.NAMA || f.properties.NAMA_JALAN;
        if (name && name.toLowerCase().includes(query)) {
          matches.push({ type: 'Jalan', name: name, sub: f.properties.FUNGSI || 'Transportasi', layerKey: 'jalan', index: idx, icon: 'road' });
        }
      });
    }

    // Cari di Sungai
    if (rawGeoJsonData.sungai) {
      rawGeoJsonData.sungai.features.forEach((f, idx) => {
        const name = f.properties.NAMA || f.properties.NAMA_SUNGAI;
        if (name && name.toLowerCase().includes(query)) {
          matches.push({ type: 'Sungai', name: name, sub: `DAS / Orde: ${f.properties.ORDE || '-'}`, layerKey: 'sungai', index: idx, icon: 'water' });
        }
      });
    }

    if (matches.length === 0) {
      resultsContainer.innerHTML = '<p style="font-size: 0.75rem; color: #ef4444; text-align: center; padding: 10px;">Tidak ditemukan entitas dengan kata kunci tersebut.</p>';
      return;
    }

    matches.forEach(m => {
      const card = document.createElement('div');
      card.style.cssText = 'background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 8px 10px; cursor: pointer; transition: all 0.2s;';
      card.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <strong style="font-size: 0.8rem; color: #1e293b;"><i class="fa-solid fa-${m.icon}" style="color: var(--primary); margin-right: 6px;"></i>${m.name}</strong>
          <span style="font-size: 0.65rem; background: #e2e8f0; padding: 1px 6px; border-radius: 10px;">${m.type}</span>
        </div>
        <p style="font-size: 0.7rem; color: #64748b; margin-top: 3px;">${m.sub}</p>
      `;
      card.addEventListener('mouseenter', () => card.style.borderColor = 'var(--primary)');
      card.addEventListener('mouseleave', () => card.style.borderColor = '#e2e8f0');
      card.addEventListener('click', () => {
        focusFeatureByIndex(m.layerKey, m.index);
      });
      resultsContainer.appendChild(card);
    });
  });
}

// =============================================================================
// 13. Koordinat Realtime, Toolbar & Bantuan Navigasi
// =============================================================================
function setupNavigationAndTools() {
  const coordDisplay = document.getElementById('coordDisplay');
  const zoomDisplay = document.getElementById('zoomDisplay');

  // Update koordinat kursor dan zoom level realtime
  map.on('mousemove', (e) => {
    coordDisplay.innerText = `Lat: ${e.latlng.lat.toFixed(5)}, Lng: ${e.latlng.lng.toFixed(5)}`;
  });
  map.on('zoomend', () => {
    zoomDisplay.innerText = `Zoom: ${map.getZoom()}`;
  });

  // Tombol Reset View
  document.getElementById('btnResetView').addEventListener('click', () => {
    map.flyTo(DEFAULT_CENTER, DEFAULT_ZOOM, { duration: 1.2 });
    showToast('Tampilan peta dikembalikan ke posisi awal.', 'info');
  });

  // Fullscreen Mode
  document.getElementById('btnFullscreen').addEventListener('click', () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {
        console.error(err);
      });
    } else {
      document.exitFullscreen();
    }
  });

  // Deteksi Lokasi Pengguna (GPS)
  document.getElementById('btnLocateUser').addEventListener('click', () => {
    map.locate({ setView: true, maxZoom: 15 });
    showToast('Mencari posisi perangkat Anda...', 'info');
  });

  map.on('locationfound', (e) => {
    L.circle(e.latlng, { radius: e.accuracy / 2, color: '#0077b6', fillColor: '#0077b6', fillOpacity: 0.2 }).addTo(map);
    L.marker(e.latlng).addTo(map).bindPopup('<strong>Posisi Anda Saat Ini</strong>').openPopup();
    showToast('Lokasi Anda ditemukan!', 'success');
  });

  map.on('locationerror', () => {
    showToast('Gagal mendeteksi lokasi atau izin geolokasi ditolak.', 'error');
  });

  // Cetak Peta
  document.getElementById('btnPrintMap').addEventListener('click', () => {
    window.print();
  });

  // Sidebar Tabs Switching
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPanel = document.getElementById(btn.dataset.tab);
      if (targetPanel) targetPanel.classList.add('active');
    });
  });

  // Drawer Tabel Atribut
  const tableDrawer = document.getElementById('tableDrawer');
  document.getElementById('btnToggleTable').addEventListener('click', () => {
    tableDrawer.classList.toggle('open');
  });
  document.getElementById('btnCloseTable').addEventListener('click', () => {
    tableDrawer.classList.remove('open');
  });
  document.getElementById('tableLayerSelect').addEventListener('change', (e) => {
    const filterInput = document.getElementById('tableFilterInput');
    populateAttributeTable(e.target.value, filterInput ? filterInput.value : '');
  });

  const filterInput = document.getElementById('tableFilterInput');
  if (filterInput) {
    filterInput.addEventListener('input', (e) => {
      const select = document.getElementById('tableLayerSelect');
      populateAttributeTable(select.value, e.target.value);
    });
  }

  const exportBtn = document.getElementById('btnExportCsv');
  if (exportBtn) {
    exportBtn.addEventListener('click', exportCurrentTableToCsv);
  }

  // Legenda Minimize Toggle
  const legendBox = document.getElementById('floatingLegend');
  const btnMinLegend = document.getElementById('btnMinimizeLegend');
  document.getElementById('btnToggleLegend').addEventListener('click', () => {
    legendBox.style.display = legendBox.style.display === 'none' ? 'flex' : 'none';
  });
  btnMinLegend.addEventListener('click', () => {
    legendBox.classList.toggle('minimized');
    btnMinLegend.querySelector('i').className = legendBox.classList.contains('minimized') ? 'fa-solid fa-chevron-up' : 'fa-solid fa-chevron-down';
  });

  // Modal Bantuan / Informasi Kuliah
  const helpModal = document.getElementById('helpModal');
  document.getElementById('btnOpenHelpModal').addEventListener('click', () => helpModal.classList.add('active'));
  document.getElementById('btnCloseHelpModal').addEventListener('click', () => helpModal.classList.remove('active'));
  helpModal.addEventListener('click', (e) => {
    if (e.target === helpModal) helpModal.classList.remove('active');
  });

  // Responsive Sidebar Toggle
  const sidebar = document.getElementById('sidebar');
  document.getElementById('btnToggleSidebar').addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });
}

// =============================================================================
// 14. Toast Notification Helper
// =============================================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const icon = type === 'success' ? 'circle-check' : (type === 'error' ? 'circle-exclamation' : 'circle-info');
  toast.innerHTML = `<i class="fa-solid fa-${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// =============================================================================
// 15. Eksekusi Saat Dokumen Siap (Bootstrapping)
// =============================================================================
document.addEventListener('DOMContentLoaded', () => {
  setupNavigationAndTools();
  setupLayerControls();
  setupUploadFeature();
  setupMeasurementTools();
  setupLiveSearch();
  loadGeoJsonLayers();
});

// Render Statistik Demografi Penduduk 14 Kecamatan (BPS 2023)
function renderKecamatanStats(features) {
  const container = document.getElementById('statKecamatanList');
  if (!container || !features || !features.length) return;

  const sorted = [...features].sort((a, b) => (b.properties.PENDUDUK_2023 || 0) - (a.properties.PENDUDUK_2023 || 0));
  const maxPop = sorted[0].properties.PENDUDUK_2023 || 1;

  container.innerHTML = sorted.map((f, idx) => {
    const p = f.properties;
    const pop = p.PENDUDUK_2023 || p.JUMLAH_PENDUDUK || 0;
    const pct = ((pop / maxPop) * 100).toFixed(1);
    return `
      <div class="stat-bar-row" style="cursor: pointer;" onclick="focusFeatureByIndex('kecamatan', ${features.indexOf(f)})" title="Klik untuk zoom ke ${p.NAMA_KECAMATAN || p.KECAMATAN}">
        <span class="stat-bar-lbl">${p.NAMA_KECAMATAN || p.KECAMATAN}</span>
        <div class="stat-bar-bg">
          <div class="stat-bar-fill" style="width: ${pct}%;"></div>
        </div>
        <span class="stat-bar-num">${Number(pop).toLocaleString('id-ID')}</span>
      </div>
    `;
  }).join('');
}
