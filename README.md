# Frontend Application

---

## Tech Stack

* **Framework:** React
* **Build Tool:** Vite
* **Styling:** Tailwind CSS (update if different)
* **API Communication:** Axios / Fetch

---

## Project Structure

```
frontend/
│
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Route pages
│   ├── services/        # API calls
│   └── main.jsx         # Entry point
│
├── public/
├── package.json
└── vite.config.js
```

---

## Setup & Installation

### 1. Navigate to frontend

```bash
cd frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Run development server

```bash
npm run dev
```

App runs at:

```
http://localhost:5173
```
----




# Backend Service

---

## Tech Stack

* **Language:** Python
* **Framework:** FastAPI
* **Server:** Uvicorn
* **Containerization:** Docker

---

## Project Structure

```
backend/
│
├── app/                # Main application code
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container configuration
├── .env                # Environment variables
└── run.py              # Entry point
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd backend
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

API docs:

```
http://127.0.0.1:8000/docs
```

---

## Environment Variables

Create a `.env` file and configure:

```
DATABASE_URL=
SECRET_KEY=
DEBUG=True
```




