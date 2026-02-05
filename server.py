from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import geoip2.database
from fastapi.responses import HTMLResponse
import os
import uvicorn

app = FastAPI(title="Free GeoIP API")

# Cloud providers usually set the PORT env variable. Default to 8081 for local.
PORT = int(os.environ.get("PORT", 8081))

# Handle path for both Local (C:\temp) and Cloud (Current Directory)
DB_FILENAME = "GeoLite2-City.mmdb"
if os.path.exists(r"C:\temp\GeoLite2-City.mmdb"):
    DB_PATH = r"C:\temp\GeoLite2-City.mmdb"
else:
    DB_PATH = DB_FILENAME 

# Check if DB exists
if not os.path.exists(DB_PATH):
    print(f"WARNING: Database not found at {DB_PATH}. Make sure to upload it!")

class IPRequest(BaseModel):
    ip: str

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
            body { font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; color: #333; }
            h1 { border-bottom: 2px solid #eaeaea; padding-bottom: 10px; }
            h2 { margin-top: 2rem; }
            .container { background: #f9f9f9; padding: 2rem; border-radius: 8px; border: 1px solid #eee; }
            input, button { padding: 10px; font-size: 1rem; margin-right: 10px; }
            button { background: #0070f3; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0051a2; }
            pre { background: #2d2d2d; color: #f8f8f2; padding: 1rem; border-radius: 4px; overflow-x: auto; font-size: 0.9rem; }
            code { background: #eaeaea; padding: 2px 4px; border-radius: 4px; font-family: monospace; }
            .endpoint { background: #e7f5ff; padding: 10px; border-left: 4px solid #0070f3; margin-bottom: 10px; }
            .method { font-weight: bold; color: #0070f3; }
        </style>
    </head>
    <body>
        <h1>Free GeoIP API</h1>
        <p>A simple, self-hosted API to retrieve location data from IP addresses using the MaxMind GeoLite2 database.</p>
        
        <div class="container">
            <h3>Try it out</h3>
            <p>Enter an IP address to lookup:</p>
            <input type="text" id="ipInput" placeholder="8.8.8.8" value="8.8.8.8">
            <button onclick="lookup()">Lookup IP</button>
            <div id="result"></div>
        </div>

        <h2>API Documentation</h2>

        <div class="endpoint">
            <span class="method">GET</span> <code>/locate/{ip}</code>
        </div>
        <p>Retrieve location data for a specific IP address via URL parameter.</p>
        <pre>curl https://your-app-url.onrender.com/locate/8.8.8.8</pre>

        <div class="endpoint">
            <span class="method">POST</span> <code>/locate</code>
        </div>
        <p>Retrieve location data via JSON body.</p>
        <pre>curl -X POST https://your-app-url.onrender.com/locate \
     -H "Content-Type: application/json" \
     -d '{"ip": "1.1.1.1"}'</pre>

        <h3>Response Format</h3>
        <pre>{
  "ip": "8.8.8.8",
  "city": "Glenmont",
  "region": "Ohio",
  "country": "United States",
  "iso_code": "US",
  "location": {
    "latitude": 40.5369,
    "longitude": -82.1286,
    "time_zone": "America/New_York",
    "accuracy_radius": 1000
  }
}</pre>

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
        </script>
    </body>
    </html>
    """

def get_location_data(ip: str):
    if not os.path.exists(DB_PATH):
         raise HTTPException(status_code=500, detail="Database file not found on server.")
         
    try:
        with geoip2.database.Reader(DB_PATH) as reader:
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
        raise HTTPException(status_code=404, detail="IP Address not found in database")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/locate/{ip}")
async def locate_get(ip: str):
    return get_location_data(ip)

@app.post("/locate")
async def locate_post(request: IPRequest):
    return get_location_data(request.ip)

if __name__ == "__main__":
    print(f"Starting server on port {PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
