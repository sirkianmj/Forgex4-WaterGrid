# Forgex WaterGrid - MVP v1.0

![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)
![Status: Approved](https://img.shields.io/badge/Status-Approved-brightgreen.svg)
![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Framework: FastAPI](https://img.shields.io/badge/Framework-FastAPI-green.svg)

A **Digital Twin platform** built to model, simulate, and verify the performance of a novel **Atmospheric Water Harvesting (AWH) façade system**.

This software is based on my **invention** — an *Atmospheric Water Harvesting System for Building Facades using PEG-SiO₂ Nanocomposite and Adaptive Mechanisms*.
The concept was formally described in my article on TechRxiv: [DOI: 10.36227/techrxiv.175735328.82069490/v1](https://doi.org/10.36227/techrxiv.175735328.82069490/v1).

The system combines:
- **PEG-SiO₂ nanocomposite coatings** to enhance condensation
- **Adaptive façade mechanisms** to dynamically regulate environmental exposure
- **Digital simulation & verification layers** to model and optimize performance

---

## 🏛️ Invention & Project Vision

The invention addresses a critical challenge: providing scalable, sustainable water generation in urban environments. By integrating nanomaterials with building facades and augmenting them with adaptive controls, buildings themselves can act as **distributed water harvesting infrastructure**.

**Forgex WaterGrid** turns this invention into a **digital twin simulation platform** — making it possible to:
- Forecast water yields based on climate, façade surface, and adaptive settings
- Compare scenarios across cities and regions
- Provide transparent, verifiable models for municipalities, investors, and policymakers
- Build the foundation for future IoT-enabled façade systems

This project therefore serves a **dual role**:
1. As the **software expression of my invention**
2. As the **first digital twin ecosystem** for decentralized atmospheric water harvesting

---

## ✨ Key Features (MVP)

- **Simulation Engine** — Estimates yield using location, weather, and façade geometry
- **Real-World Weather Data** — Live integration with OpenWeatherMap
- **Adaptive Mechanism Modeling** — Reflecting façade control strategies from the invention
- **AI-Powered Anomaly Detection** — Ensures trust in results with Isolation Forest
- **Dashboard Visualization** — Plotly.js and Bootstrap for professional, accessible outputs

---

## 🛠️ Technology Stack & Architecture

- **Frontend:** HTML5, CSS3, Bootstrap 5, Plotly.js
- **Backend:** Python 3.9+, FastAPI
- **Data Validation:** Pydantic
- **AI/ML:** Scikit-learn
- **Deployment:** Vercel / Netlify

**Flow:**
`User Browser` → `Frontend` → `API Gateway` → `Backend Simulation Engine` → `Weather API` → `Result`

---

## 📜 Licensing & Commercial Use

This project is **dual-licensed**:

- **Open Source License:** GNU AGPL v3 (see [LICENSE](LICENSE))
- **Commercial License:** Available for organizations seeking to integrate this technology into closed-source systems or proprietary products

📧 Contact: *[Your Email]*

---

## 🛡️ Security-First Design

- **API-Key Authentication**
- **Input Validation (Pydantic)**
- **Secrets Management via .env**
- **TLS (HTTPS) Encryption**
- **AI Anomaly Detection**

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git
- VS Code or similar

### Installation
```bash
git clone https://github.com/your-username/forgex-watergrid.git
cd forgex-watergrid
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory with the following content:

```
API_KEY="YOUR_SUPER_SECRET_API_KEY"
OPENWEATHERMAP_API_KEY="YOUR_OPENWEATHERMAP_KEY"
```

### Run

```bash
uvicorn api.main:app --reload
```

Then open `index.html` in your browser.

---

## 📖 API Specification

### POST `/simulate`

**Header:** `X-API-Key: <your-secret-api-key>`

**Body:**
```json
{
  "location": "string",
  "surface_area": "float"
}
```

**Response (200 OK):**
```json
{
  "location_provided": "string",
  "current_humidity": "float",
  "estimated_yield_24h_liters": "float",
  "forecast_7_day": [],
  "anomaly_flag": "boolean"
}
```

---

## 🗺️ Roadmap

- [ ] Multi-building / neighborhood digital twins
- [ ] IoT integration with façade-embedded sensors
- [ ] Resilience modeling (cyber + climate)
- [ ] Partnerships with municipalities and UN sustainability projects

---

## 📄 License

This project is licensed under the **AGPL v3 Open Source License**. See the [LICENSE](LICENSE) file for details.
A **commercial license** is also available upon request for proprietary use.

---

## ⚖️ Patent & IP Notice

This invention is the intellectual property of the author. While not yet patented, it is protected under copyright and moral rights. Unauthorized commercial use or patenting of this invention is strictly prohibited.

---

## 👤 Author

**Kian Mansouri Jamshidi**

- Inventor of the *Atmospheric Water Harvesting System for Building Facades Using PEG-SiO₂ Nanocomposite and Adaptive Mechanisms*
- DOI: [10.36227/techrxiv.175735328.82069490/v1](https://doi.org/10.36227/techrxiv.175735328.82069490/v1)
```
