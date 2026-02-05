# Free GeoIP API

A lightweight, self-hosted REST API for IP geolocation, powered by FastAPI and the MaxMind GeoLite2 database.

## 🚀 Features

*   **Free to Host:** Designed to run on free tier cloud providers (like Render.com).
*   **Fast:** Built with FastAPI and Uvicorn.
*   **Simple API:** Supports both `GET` and `POST` requests.
*   **No External API Limits:** Since you host the database, you don't hit rate limits from third-party GeoIP providers.

## 🛠️ Local Setup

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/thebubbsy/free-geoip-api.git
    cd free-geoip-api
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Server:**
    ```bash
    python server.py
    ```
    Access the UI at `http://127.0.0.1:8081`.

## ☁️ Deployment (Free on Render.com)

1.  **Push this code to GitHub.**
2.  **Sign up for [Render.com](https://render.com).**
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repository.
5.  **Settings:**
    *   **Runtime:** Python 3
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `python server.py`
6.  Click **Create Web Service**.

Render will deploy your API and give you a URL (e.g., `https://free-geoip-api.onrender.com`).

## 📖 API Reference

### Get Location (GET)
```http
GET /locate/{ip_address}
```
**Example:**
```bash
curl https://free-geoip-api.onrender.com/locate/8.8.8.8
```

### Get Location (POST)
```http
POST /locate
```
**Body:**
```json
{
  "ip": "8.8.8.8"
}
```

## ⚖️ License
This project uses the MaxMind GeoLite2 database. Ensure you comply with their license if distributing the database file.
