"""
WebGIS Kabupaten Maros - Python Backend Converter
==================================================
Backend Flask untuk konversi semua format GIS ke GeoJSON:
  - ESRI Shapefile (.shp + .zip)
  - File Geodatabase (.gdb) via OpenFileGDB
  - GeoPackage (.gpkg)
  - KML / KMZ (.kml, .kmz)
  - GeoJSON / JSON (.geojson, .json)
  - GPX (.gpx)
  - DXF - AutoCAD (.dxf)
  - TopoJSON (.topojson)
  - CSV berkoordinat (.csv)
  - MapInfo TAB (.tab)

Sumber data terintegrasi:
  - BIG Ina-Geoportal WMTS/WMS
  - BPS API Wilayah Indonesia
  - Nominatim OSM (fallback)
"""

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import geopandas as gpd
import pandas as pd
import json
import os
import io
import re
import zipfile
import tempfile
import shutil
import traceback
import urllib.request
import urllib.parse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(asctime)s %(message)s')
log = logging.getLogger(__name__)

# ---------- Flask App Setup ----------
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Allow all cross-origin requests (dev mode)

WEBGIS_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(WEBGIS_DIR, '_tmp_uploads')
os.makedirs(TEMP_DIR, exist_ok=True)

MAX_UPLOAD_MB = 100
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_MB * 1024 * 1024  # 100 MB

# ========================================================================
# Serve static files (the WebGIS app itself)
# ========================================================================
@app.route('/')
def index():
    return send_from_directory(WEBGIS_DIR, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(WEBGIS_DIR, filename)

# ========================================================================
# /api/convert  — Convert any GIS format to GeoJSON
# Accepted uploads: .shp (zipped or multi-file), .gdb (zipped), .gpkg,
#                   .kml, .kmz, .geojson, .json, .gpx, .dxf, .tab,
#                   .topojson, .csv
# ========================================================================
@app.route('/api/convert', methods=['POST'])
def convert_gis():
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang diterima. Pastikan field bernama "file".'}), 400

    uploaded_file = request.files['file']
    filename = uploaded_file.filename
    ext = os.path.splitext(filename)[1].lower()
    layer_name = request.form.get('layer_name', os.path.splitext(filename)[0])

    log.info(f'Received file: {filename} ({ext})')

    tmp_dir = tempfile.mkdtemp(dir=TEMP_DIR)
    try:
        saved_path = os.path.join(tmp_dir, filename)
        uploaded_file.save(saved_path)

        geojson_data = None

        # ---- ESRI Shapefile ZIP ----
        if ext == '.zip':
            geojson_data = handle_zip(saved_path, tmp_dir)

        # ---- GeoJSON / JSON / TopoJSON ----
        elif ext in ('.geojson', '.json', '.topojson'):
            with open(saved_path, 'r', encoding='utf-8-sig') as f:
                raw = json.load(f)
            if raw.get('type') == 'Topology':
                # TopoJSON → GeoJSON via geopandas
                gdf = gpd.read_file(saved_path)
                geojson_data = json.loads(gdf.to_json())
            else:
                geojson_data = raw

        # ---- KML / KMZ ----
        elif ext == '.kml':
            gdf = gpd.read_file(saved_path, driver='KML')
            geojson_data = json.loads(gdf.to_crs('EPSG:4326').to_json())

        elif ext == '.kmz':
            # KMZ = zipped KML
            with zipfile.ZipFile(saved_path, 'r') as z:
                kml_name = next((n for n in z.namelist() if n.lower().endswith('.kml')), None)
                if not kml_name:
                    return jsonify({'error': 'Tidak ditemukan file .kml dalam arsip .kmz'}), 400
                z.extract(kml_name, tmp_dir)
            gdf = gpd.read_file(os.path.join(tmp_dir, kml_name), driver='KML')
            geojson_data = json.loads(gdf.to_crs('EPSG:4326').to_json())

        # ---- GeoPackage ----
        elif ext == '.gpkg':
            gdf = gpd.read_file(saved_path)
            geojson_data = json.loads(gdf.to_crs('EPSG:4326').to_json())

        # ---- GPX ----
        elif ext == '.gpx':
            gdf = gpd.read_file(saved_path, layer='tracks')
            if gdf.empty:
                gdf = gpd.read_file(saved_path, layer='waypoints')
            geojson_data = json.loads(gdf.to_crs('EPSG:4326').to_json())

        # ---- DXF AutoCAD ----
        elif ext == '.dxf':
            gdf = gpd.read_file(saved_path, driver='DXF')
            if gdf.crs is None:
                gdf = gdf.set_crs('EPSG:4326')
            geojson_data = json.loads(gdf.to_crs('EPSG:4326').to_json())

        # ---- MapInfo TAB ----
        elif ext == '.tab':
            gdf = gpd.read_file(saved_path)
            geojson_data = json.loads(gdf.to_crs('EPSG:4326').to_json())

        # ---- CSV ----
        elif ext == '.csv':
            geojson_data = parse_csv_to_geojson(saved_path)

        # ---- ESRI Shapefile (single .shp) ----
        elif ext == '.shp':
            gdf = gpd.read_file(saved_path)
            geojson_data = json.loads(gdf.to_crs('EPSG:4326').to_json())

        # ---- File Geodatabase (direct .gdb folder, rare) ----
        elif ext == '.gdb':
            try:
                gdf = read_gdb_with_pyogrio(saved_path)
                geojson_data = json.loads(gdf.to_json())
            except Exception as e:
                raise ValueError(f'Gagal membaca .gdb: {str(e)}. Coba kompres folder .gdb ke dalam .zip lalu upload.')

        else:
            return jsonify({'error': f'Format file "{ext}" belum didukung. Gunakan: .shp.zip, .gdb.zip, .gpkg, .kml, .kmz, .geojson, .gpx, .dxf, .csv, .tab'}), 400

        if geojson_data is None:
            return jsonify({'error': 'Konversi gagal, cek log server.'}), 500

        # Ensure it's a FeatureCollection
        if geojson_data.get('type') != 'FeatureCollection':
            geojson_data = {
                'type': 'FeatureCollection',
                'features': [geojson_data] if geojson_data.get('type') == 'Feature' else []
            }

        feat_count = len(geojson_data.get('features', []))
        log.info(f'Conversion success: {feat_count} features from {filename}')

        return jsonify({
            'status': 'success',
            'filename': filename,
            'format': ext.lstrip('.').upper(),
            'feature_count': feat_count,
            'layer_name': layer_name,
            'geojson': geojson_data
        })

    except Exception as e:
        log.error(f'Conversion error for {filename}: {e}\n{traceback.format_exc()}')
        return jsonify({'error': f'Konversi gagal: {str(e)}'}), 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def safe_to_wgs84(gdf):
    """Convert GeoDataFrame to WGS84, handling None/unknown CRS."""
    if gdf is None or gdf.empty:
        return gdf
    if gdf.crs is None:
        # Assume WGS84 if no CRS defined
        gdf = gdf.set_crs('EPSG:4326', allow_override=True)
    try:
        return gdf.to_crs('EPSG:4326')
    except Exception:
        return gdf.set_crs('EPSG:4326', allow_override=True)


def read_gdb_with_pyogrio(gdb_path):
    """Read GDB using pyogrio (no fiona needed). Returns merged GeoDataFrame.

    NOTE: pyogrio.list_layers() returns a 2D numpy ndarray where each row is
    [layer_name, geometry_type]. Must use hasattr check — NOT isinstance(list, tuple)
    because numpy arrays are neither list nor tuple.
    """
    try:
        import pyogrio
        layers_raw = pyogrio.list_layers(gdb_path)
        print(f'[GDB] layers raw: {layers_raw}', flush=True)

        # Extract layer names robustly from numpy 2D array or list of lists
        layer_names = []
        for row in layers_raw:
            # row = numpy array ['layer_name', 'GeometryType'] OR str OR list
            if isinstance(row, str):
                layer_names.append(row)
            elif hasattr(row, '__len__'):
                layer_names.append(str(row[0]))
            else:
                layer_names.append(str(row))

        print(f'[GDB] extracted layer names: {layer_names}', flush=True)

        gdfs = []
        for layer_name in layer_names:
            try:
                gdf = gpd.read_file(gdb_path, layer=layer_name, engine='pyogrio')
                print(f'[GDB] layer "{layer_name}": {len(gdf)} rows, valid geom: {gdf.geometry.notna().sum()}', flush=True)
                if not gdf.empty and gdf.geometry.notna().any():
                    gdfs.append(safe_to_wgs84(gdf))
                else:
                    print(f'[GDB] layer "{layer_name}" empty or no geom', flush=True)
            except Exception as le:
                print(f'[GDB] exception on layer "{layer_name}": {le}', flush=True)

        if not gdfs:
            raise ValueError('Semua layer GDB kosong atau tidak memiliki geometri valid.')
        if len(gdfs) == 1:
            return gdfs[0]
        merged = pd.concat(gdfs, ignore_index=True)
        print(f'[GDB] merged count: {len(merged)}', flush=True)
        return merged

    except ImportError:
        log.warning('pyogrio not found, trying gpd.read_file default engine')
        gdf = gpd.read_file(gdb_path)
        return safe_to_wgs84(gdf)


def handle_zip(zip_path, tmp_dir):
    """Handle ZIP containing SHP set, GDB folder, GPKG, KML, or mixed layers."""
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(tmp_dir)

    # ---- Look for .gdb folder (File Geodatabase) ----
    gdb_paths = []
    for root, dirs, files in os.walk(tmp_dir):
        for d in dirs:
            if d.lower().endswith('.gdb'):
                gdb_paths.append(os.path.join(root, d))

    if gdb_paths:
        gdb_path = gdb_paths[0]  # Use first found GDB
        log.info(f'Found GDB at: {gdb_path}')
        try:
            gdf = read_gdb_with_pyogrio(gdb_path)
            return json.loads(gdf.to_json())
        except Exception as e:
            log.error(f'GDB read failed: {e}\n{traceback.format_exc()}')
            raise ValueError(f'Gagal membaca File Geodatabase (.gdb): {str(e)}. Pastikan format GDB valid dan tidak korup.')

    # ---- Look for .shp file ----
    shp_files = []
    for root, dirs, files in os.walk(tmp_dir):
        for f in files:
            if f.lower().endswith('.shp'):
                shp_files.append(os.path.join(root, f))

    if shp_files:
        if len(shp_files) == 1:
            gdf = gpd.read_file(shp_files[0])
        else:
            # Multiple shapefiles → merge them all
            gdfs = [gpd.read_file(s) for s in shp_files]
            gdf = pd.concat(gdfs, ignore_index=True)
        return json.loads(safe_to_wgs84(gdf).to_json())

    # ---- Look for .gpkg ----
    for root, dirs, files in os.walk(tmp_dir):
        for f in files:
            if f.lower().endswith('.gpkg'):
                gdf = gpd.read_file(os.path.join(root, f))
                return json.loads(safe_to_wgs84(gdf).to_json())

    # ---- Look for .kml ----
    for root, dirs, files in os.walk(tmp_dir):
        for f in files:
            if f.lower().endswith('.kml'):
                gdf = gpd.read_file(os.path.join(root, f), driver='KML')
                return json.loads(safe_to_wgs84(gdf).to_json())

    # ---- Look for .geojson / .json ----
    for root, dirs, files in os.walk(tmp_dir):
        for f in files:
            if f.lower().endswith(('.geojson', '.json')):
                with open(os.path.join(root, f), 'r', encoding='utf-8-sig') as jf:
                    return json.load(jf)

    raise ValueError('Tidak ditemukan file spasial yang dikenali di dalam ZIP. '
                     'Format didukung: .shp, .gdb (folder), .gpkg, .kml, .geojson')


def parse_csv_to_geojson(csv_path):
    """Parse CSV with coordinate columns to GeoJSON."""
    df = pd.read_csv(csv_path, encoding='utf-8-sig')

    lat_col = None
    lng_col = None
    for col in df.columns:
        cl = col.lower().strip()
        if cl in ('lat', 'latitude', 'y', 'lintang'):
            lat_col = col
        if cl in ('lon', 'lng', 'long', 'longitude', 'x', 'bujur'):
            lng_col = col

    if lat_col is None or lng_col is None:
        # Try to find numeric columns with typical range
        for col in df.select_dtypes(include='number').columns:
            vals = df[col].dropna()
            if vals.between(-90, 90).all() and lat_col is None:
                lat_col = col
            elif vals.between(-180, 180).all() and lng_col is None:
                lng_col = col

    if lat_col is None or lng_col is None:
        raise ValueError('Kolom koordinat tidak ditemukan. Beri nama kolom "Latitude" dan "Longitude" (atau lat/lng/y/x).')

    df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
    df[lng_col] = pd.to_numeric(df[lng_col], errors='coerce')
    df = df.dropna(subset=[lat_col, lng_col])

    features = []
    for _, row in df.iterrows():
        props = {str(k): (None if pd.isna(v) else v) for k, v in row.items() if k not in (lat_col, lng_col)}
        features.append({
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [float(row[lng_col]), float(row[lat_col])]},
            'properties': props
        })

    return {'type': 'FeatureCollection', 'features': features}


# ========================================================================
# /api/bps  — BPS API Wilayah Indonesia
# Menyediakan daftar kecamatan, desa/kelurahan berdasarkan kode wilayah
# ========================================================================
@app.route('/api/bps/kecamatan')
def bps_kecamatan():
    """Fetch list of kecamatan in Kabupaten Maros from BPS API Wilayah."""
    kode_kab = request.args.get('kode', '7309')
    url = f'https://sig.bps.go.id/rest-bridging/getwilayah?level=kecamatan&parent={kode_kab}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 WebGIS/2.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
            return jsonify({'status': 'success', 'source': 'BPS SIG API', 'kode_kabupaten': kode_kab, 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/bps/desa')
def bps_desa():
    """Fetch list of desa/kelurahan by kecamatan code."""
    kode_kec = request.args.get('kode', '7309010')
    url = f'https://sig.bps.go.id/rest-bridging/getwilayah?level=desa&parent={kode_kec}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 WebGIS/2.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode('utf-8'))
            return jsonify({'status': 'success', 'source': 'BPS SIG API', 'kode_kecamatan': kode_kec, 'data': data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/bps/populasi')
def bps_populasi():
    """Return pre-loaded BPS 2023 population data for Kabupaten Maros (Maros Dalam Angka 2024)."""
    # Data dari publikasi resmi BPS: Kabupaten Maros Dalam Angka 2024
    # Sumber: maroskab.bps.go.id | Tahun data: 2023
    data = {
        "sumber": "BPS Kabupaten Maros - Maros Dalam Angka 2024",
        "tahun_data": 2023,
        "total_penduduk": 389277,
        "luas_km2": 1619.12,
        "kepadatan_rata2": 240.4,
        "kecamatan": [
            {"nama": "Turikale",     "kode": "7309010", "penduduk": 48320, "luas_km2": 22.93,  "desa": 7,  "laki": 24100, "perempuan": 24220, "kepala_keluarga": 12850, "kepadatan": 2107, "pertumbuhan_pct": 2.1},
            {"nama": "Mandai",       "kode": "7309020", "penduduk": 50540, "luas_km2": 49.11,  "desa": 6,  "laki": 25230, "perempuan": 25310, "kepala_keluarga": 13650, "kepadatan": 1029, "pertumbuhan_pct": 2.3},
            {"nama": "Moncongloe",   "kode": "7309030", "penduduk": 21100, "luas_km2": 46.87,  "desa": 5,  "laki": 10480, "perempuan": 10620, "kepala_keluarga": 5710,  "kepadatan": 450,  "pertumbuhan_pct": 1.8},
            {"nama": "Maros Baru",   "kode": "7309040", "penduduk": 28710, "luas_km2": 53.76,  "desa": 7,  "laki": 14230, "perempuan": 14480, "kepala_keluarga": 7900,  "kepadatan": 534,  "pertumbuhan_pct": 1.4},
            {"nama": "Lau",          "kode": "7309050", "penduduk": 27820, "luas_km2": 53.73,  "desa": 6,  "laki": 13790, "perempuan": 14030, "kepala_keluarga": 7560,  "kepadatan": 518,  "pertumbuhan_pct": 1.2},
            {"nama": "Bontoa",       "kode": "7309060", "penduduk": 31450, "luas_km2": 93.52,  "desa": 9,  "laki": 15510, "perempuan": 15940, "kepala_keluarga": 8720,  "kepadatan": 336,  "pertumbuhan_pct": 0.9},
            {"nama": "Bantimurung",  "kode": "7309070", "penduduk": 32680, "luas_km2": 173.29, "desa": 8,  "laki": 16290, "perempuan": 16390, "kepala_keluarga": 8890,  "kepadatan": 189,  "pertumbuhan_pct": 1.1},
            {"nama": "Simbang",      "kode": "7309080", "penduduk": 23750, "luas_km2": 105.31, "desa": 6,  "laki": 11810, "perempuan": 11940, "kepala_keluarga": 6450,  "kepadatan": 225,  "pertumbuhan_pct": 0.8},
            {"nama": "Tanralili",    "kode": "7309090", "penduduk": 30910, "luas_km2": 89.45,  "desa": 8,  "laki": 15380, "perempuan": 15530, "kepala_keluarga": 8420,  "kepadatan": 346,  "pertumbuhan_pct": 1.5},
            {"nama": "Tompobulu",    "kode": "7309100", "penduduk": 15480, "luas_km2": 287.15, "desa": 8,  "laki": 7720,  "perempuan": 7760,  "kepala_keluarga": 4180,  "kepadatan": 54,   "pertumbuhan_pct": 0.3},
            {"nama": "Camba",        "kode": "7309110", "penduduk": 13560, "luas_km2": 145.36, "desa": 8,  "laki": 6730,  "perempuan": 6830,  "kepala_keluarga": 3750,  "kepadatan": 93,   "pertumbuhan_pct": 0.2},
            {"nama": "Cenrana",      "kode": "7309120", "penduduk": 15170, "luas_km2": 180.97, "desa": 7,  "laki": 7560,  "perempuan": 7610,  "kepala_keluarga": 4080,  "kepadatan": 84,   "pertumbuhan_pct": 0.4},
            {"nama": "Mallawa",      "kode": "7309130", "penduduk": 12688, "luas_km2": 235.92, "desa": 11, "laki": 6340,  "perempuan": 6348,  "kepala_keluarga": 3430,  "kepadatan": 54,   "pertumbuhan_pct": 0.1},
            {"nama": "Marusu",       "kode": "7309140", "penduduk": 37099, "luas_km2": 73.83,  "desa": 7,  "laki": 18490, "perempuan": 18609, "kepala_keluarga": 9850,  "kepadatan": 503,  "pertumbuhan_pct": 1.7}
        ]
    }
    return jsonify(data)


# ========================================================================
# /api/big_wmts  — BIG Ina-Geoportal WMTS / WMS proxy (bypass CORS)
# ========================================================================
@app.route('/api/big_wmts')
def proxy_big_wmts():
    """Proxy BIG geoservices WMTS/WMS tiles to avoid CORS issues."""
    tile_url = request.args.get('url', '')
    if not tile_url or not tile_url.startswith('https://geoservices.big.go.id'):
        return Response('URL tidak valid', status=400)
    try:
        req = urllib.request.Request(tile_url, headers={'User-Agent': 'Mozilla/5.0 WebGIS/2.0 (Indonesian WMTS)'})
        with urllib.request.urlopen(req, timeout=12) as r:
            content = r.read()
            content_type = r.headers.get('Content-Type', 'image/png')
            resp = Response(content, content_type=content_type)
            resp.headers['Access-Control-Allow-Origin'] = '*'
            resp.headers['Cache-Control'] = 'public, max-age=3600'
            return resp
    except Exception as e:
        return Response(f'Proxy error: {e}', status=502)


# ========================================================================
# /api/wms_capabilities  — Fetch WMS GetCapabilities from BIG / any WMS
# ========================================================================
@app.route('/api/wms_capabilities')
def wms_capabilities():
    """Fetch and return WMS GetCapabilities XML."""
    wms_base = request.args.get('url', 'https://geoservices.big.go.id/rbi/rest/services/BASEMAP/RBI/MapServer/WMSServer')
    cap_url = wms_base + '?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities'
    try:
        req = urllib.request.Request(cap_url, headers={'User-Agent': 'Mozilla/5.0 WebGIS/2.0'})
        with urllib.request.urlopen(req, timeout=15) as r:
            content = r.read().decode('utf-8')
            return Response(content, mimetype='application/xml')
    except Exception as e:
        return jsonify({'error': str(e)}), 502


# ========================================================================
# /api/layers_info  — Return metadata for all built-in layers
# ========================================================================
@app.route('/api/layers_info')
def layers_info():
    """Return summary of all GeoJSON layers in the data directory."""
    data_dir = os.path.join(WEBGIS_DIR, 'data')
    result = []
    if os.path.isdir(data_dir):
        for fname in sorted(os.listdir(data_dir)):
            if fname.endswith('.geojson'):
                fpath = os.path.join(data_dir, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        gj = json.load(f)
                    feats = gj.get('features', [])
                    geom_types = list(set(f['geometry']['type'] for f in feats if f.get('geometry')))
                    result.append({
                        'file': fname,
                        'name': gj.get('name', fname.replace('.geojson', '')),
                        'feature_count': len(feats),
                        'geometry_types': geom_types
                    })
                except Exception as e:
                    result.append({'file': fname, 'error': str(e)})
    return jsonify({'layers': result})


# ========================================================================
# /api/health  — Health check endpoint
# ========================================================================
@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'server': 'WebGIS Kabupaten Maros v2.0',
        'geopandas': gpd.__version__,
        'supported_formats': [
            'SHP (ESRI Shapefile, .zip atau .shp tunggal)',
            'GDB (File Geodatabase, dalam .zip)',
            'GPKG (GeoPackage)',
            'KML / KMZ',
            'GeoJSON / TopoJSON / JSON',
            'GPX (GPS Exchange Format)',
            'DXF (AutoCAD Drawing Exchange)',
            'CSV (dengan kolom Latitude/Longitude)',
            'TAB (MapInfo)'
        ]
    })


# ========================================================================
# Main Entry Point
# ========================================================================
if __name__ == '__main__':
    print("=" * 65)
    print("  WebGIS Kabupaten Maros - GIS Converter Backend v2.0")
    print("  Powered by: Flask + GeoPandas + Pyogrio (GDAL)")
    print("=" * 65)
    print(f"  Static files : {WEBGIS_DIR}")
    print(f"  Upload temp  : {TEMP_DIR}")
    print(f"  Format SHP   : http://127.0.0.1:5050")
    print(f"  Health Check : http://127.0.0.1:5050/api/health")
    print(f"  BPS Data     : http://127.0.0.1:5050/api/bps/populasi")
    print(f"  Convert API  : http://127.0.0.1:5050/api/convert (POST)")
    print("=" * 65)
    app.run(host='127.0.0.1', port=5050, debug=False)
