from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import geoip2.database
from fastapi.responses import HTMLResponse
import os
import uvicorn
from typing import List

app = FastAPI(title="Free GeoIP API")

# Cloud providers usually set the PORT env variable. Default to 8081 for local.
PORT = int(os.environ.get("PORT", 8081))

# Handle path for both Local (C:\temp) and Cloud (Current Directory)
DB_FILENAME = "GeoLite2-City.mmdb"
if os.path.exists(r"C:\temp\GeoLite2-City.mmdb"):
    DB_PATH = r"C:\temp\GeoLite2-City.mmdb"
else:
    DB_PATH = DB_FILENAME 

# Global Reader for High Performance
reader = None
if os.path.exists(DB_PATH):
    try:
        reader = geoip2.database.Reader(DB_PATH)
        print(f"Database loaded successfully from {DB_PATH}")
    except Exception as e:
        print(f"CRITICAL: Failed to load database: {e}")
else:
    print(f"WARNING: Database not found at {DB_PATH}. Make sure to upload it!")

class IPRequest(BaseModel):
    ip: str

class BatchIPRequest(BaseModel):
    ips: List[str]

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Free GeoIP API</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; color: #e0e0e0; background-color: #121212; }
            h1 { border-bottom: 2px solid #333; padding-bottom: 10px; color: #ffffff; }
            h2 { margin-top: 2rem; color: #ffffff; }
            .container { background: #1e1e1e; padding: 2rem; border-radius: 8px; border: 1px solid #333; }
            input, textarea { padding: 10px; font-size: 1rem; margin-right: 10px; background: #2d2d2d; border: 1px solid #444; color: #fff; border-radius: 4px; width: 100%; box-sizing: border-box; margin-bottom: 10px; }
            button { background: #0070f3; color: white; border: none; border-radius: 4px; cursor: pointer; padding: 10px; font-size: 1rem; }
            button:hover { background: #0051a2; }
            pre { background: #000; color: #0f0; padding: 1rem; border-radius: 4px; overflow-x: auto; font-size: 0.9rem; border: 1px solid #333; }
            code { background: #2d2d2d; padding: 2px 4px; border-radius: 4px; font-family: monospace; color: #ff79c6; }
            .endpoint { background: #1a2634; padding: 10px; border-left: 4px solid #0070f3; margin-bottom: 10px; }
            .method { font-weight: bold; color: #4dabf7; }
            a { color: #4dabf7; }
        </style>
    </head>
    <body>
        <h1>Free GeoIP API</h1>
        <p>
            A simple, self-hosted API to retrieve location data from IP addresses using the MaxMind GeoLite2 database.
            <br>
            <a href="https://github.com/thebubbsy/free-geoip-api" target="_blank" style="color: #0070f3; text-decoration: none;"><strong>View Source on GitHub ↗</strong></a>
        </p>
        
        <div class="container">
            <h3>Try it out (Single IP)</h3>
            <p>Enter an IP address to lookup:</p>
            <input type="text" id="ipInput" placeholder="8.8.8.8" value="8.8.8.8">
            <button onclick="lookup()">Lookup IP</button>
            <div id="result"></div>
        </div>

        <div class="container" style="margin-top: 20px;">
            <h3>Batch Processing</h3>
            <p>Enter multiple IPs (comma separated) to batch process:</p>
            <textarea id="batchInput" rows="3" placeholder="8.8.8.8, 1.1.1.1, 24.48.0.1">8.8.8.8, 1.1.1.1</textarea>
            <button onclick="lookupBatch()">Lookup Batch</button>
            <div id="batchResult"></div>
        </div>

        <h2>API Documentation</h2>

        <div class="endpoint">
            <span class="method">GET</span> <code>/locate/{ip}</code>
        </div>
        <p>Retrieve location data for a specific IP address via URL parameter.</p>
        <pre>curl https://free-geoip-api.onrender.com/locate/8.8.8.8</pre>

        <div class="endpoint">
            <span class="method">POST</span> <code>/locate</code>
        </div>
        <p>Retrieve location data via JSON body.</p>
        <pre>curl -X POST https://free-geoip-api.onrender.com/locate \
     -H "Content-Type: application/json" \
     -d '{"ip": "1.1.1.1"}'</pre>
     
        <div class="endpoint">
            <span class="method">POST</span> <code>/batch</code>
        </div>
        <p>Retrieve location data for up to 100 IPs in a single request. Highly optimized for speed.</p>
        <pre>curl -X POST https://free-geoip-api.onrender.com/batch \
     -H "Content-Type: application/json" \
     -d '{"ips": ["1.1.1.1", "8.8.8.8"]}'</pre>

        <script>
            async function lookup() {
                const ip = document.getElementById('ipInput').value;
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = 'Loading...';
                
                try {
                    const res = await fetch('/locate/' + ip);
                    const data = await res.json();
                    resultDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (e) {
                    resultDiv.innerHTML = '<p style="color:red">Error fetching data</p>';
                }
            }
            
            async function lookupBatch() {
                const raw = document.getElementById('batchInput').value;
                const ips = raw.split(',').map(s => s.trim()).filter(s => s.length > 0);
                const resultDiv = document.getElementById('batchResult');
                resultDiv.innerHTML = 'Processing ' + ips.length + ' IPs...';
                
                try {
                    const res = await fetch('/batch', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ips: ips })
                    });
                    const data = await res.json();
                    resultDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (e) {
                    resultDiv.innerHTML = '<p style="color:red">Error fetching batch data</p>';
                }
            }
        </script>
    </body>
    </html>
    ""

def resolve_ip(ip: str):
    if not reader:
         # Fallback if DB load failed
         return {"ip": ip, "error": "Database not loaded"}
         
    try:
        response = reader.city(ip)
        return {
            "ip": ip,
            "city": response.city.name if response.city.name else "Unknown",
            "region": response.subdivisions.most_specific.name if response.subdivisions else "Unknown",
            "country": response.country.name if response.country.name else "Unknown",
            "iso_code": response.country.iso_code if response.country.iso_code else "Unknown",
            "location": {
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
                "time_zone": response.location.time_zone,
                "accuracy_radius": response.location.accuracy_radius
            }
        }
    except geoip2.errors.AddressNotFoundError:
        return {"ip": ip, "error": "Not Found"}
    except Exception as e:
        return {"ip": ip, "error": str(e)}

@app.get("/locate/{ip}")
async def locate_get(ip: str):
    res = resolve_ip(ip)
    if "error" in res and res["error"] == "Not Found":
        raise HTTPException(status_code=404, detail="IP not found")
    return res

@app.post("/locate")
async def locate_post(request: IPRequest):
    return resolve_ip(request.ip)

@app.post("/batch")
async def batch_post(request: BatchIPRequest):
    # Optimized for high-throughput
    # Processing list in-memory without IO overhead per-request
    return [resolve_ip(ip) for ip in request.ips]

if __name__ == "__main__":
    print(f"Starting server on port {PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
# Forced update for Render deployment v1.1