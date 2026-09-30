@echo off
title WebGIS Kabupaten Maros - Leaflet GIS
color 0A
echo =========================================================================
echo       WEBGIS INTERAKTIF KABUPATEN MAROS (PUSTAKA LEAFLET.JS)
echo       Tugas Pengembangan WebGIS Dasar - Kuliah Geospasial
echo       Dosen Pengampu: Andang Suryana Soma, S.Hut., MP., Ph.D
echo =========================================================================
echo.
echo Membuka aplikasi WebGIS di browser Anda...
echo Jalur Proyek: %~dp0
echo.

:: Coba jalankan server python di background jika python tersedia, atau langsung buka index.html
start "" "index.html"

:: Buka juga tautan file Presentasi PDF
echo Untuk melihat Presentasi PDF:
echo Berkas PDF: Presentasi_WebGIS_Kabupaten_Maros.pdf
echo.
echo Tekan tombol apa saja untuk membuka Presentasi PDF...
pause >nul
start "" "Presentasi_WebGIS_Kabupaten_Maros.pdf"
exit
