@echo off
echo Starting GeoIP API Server...
echo Database: C:\temp\GeoLite2-City.mmdb
echo URL: http://127.0.0.1:8081
python C:\temp\geo_api\server.py
pause
