

# Vase Design System with Eye Tracking

This repository contains an Interactive Evolutionary Design (IED) system driven by eye-tracking . The project utilizes a **FastAPI** backend and a **React** frontend.


> [!info] 
> > As the experiments of this research were conducted in China, the code and interface instructions of this project are all in Chinese. Please read them in translation.
Some of the previous developed comments have been retained in this project. If there are any unclear points, please feel free to contact me. 
## Branch Structure & Algorithm Mapping

The three primary algorithms discussed in the paper are hosted on separate branches. Each branch contains the specific React frontend and FastAPI backend logic for that variant.

| Branch Name   | Algorithm Variant | Backend Port |
| :------------ | :---------------- | :----------- |
| **`T-IGA`**   | Traditional IGA   | **8000**     |
| **`AOI-IGA`** | AOI-based IGA     | **8001**     |
| **`SA-IGA`**  | SA-based IGA      | **8002**     |

---

## Prerequisites

Before starting the project, please ensure you have the following installed:

*   **Python 3.10** (Required for backend dependencies)
*   **Node.js** (Required for frontend development and building)
*   The Python packages listed in `requirements.txt`.

---

## Installation & Setup

Since the React code resides in the `client` folder within each branch, you must build the frontend before starting the server.

### 1. Frontend Build (React)

Navigate to the `client` directory within your checked-out branch and build the static files.

```bash
cd client
npm install
npm run build

```
### 2. Critical Path Fix for React Build

**Important:** Due to the specific version of React used in this project, a manual adjustment is required after each build to ensure the frontend loads correctly.

After running `npm run build`, you must edit the generated HTML file to remove the leading forward slash (`/`) from static asset paths.

1.  Open the file: `client/build/static/index.html`
2.  Locate the script and link tags referencing static assets (e.g., `src="/static/js/main...`).
3.  **Remove the leading `/`** from the path.
4.  eg:
    *   **Change from:** `src="/static/js/main.6a7baab3.js"`
    *   **Change to:** `src="static/js/main.6a7baab3.js"`
5.  Save the file.

---

## Starting the Project

The backend must be started from the project root directory (where the `main.py` or equivalent FastAPI entry point is located).

### Branch: T-IGA (Port 8000)

```bash
# Frontend run under your main directory.
npm start
```

1.  **Activate your Python virtual environment.**
2.  Ensure you are in the project root directory.
3.  Start the Uvicorn server:

```bash
# Please activate your Python environment first.

cd backend 
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```


**Access:** Open your browser and navigate to `http://127.0.0.1:8000` (or the specific route defined in your FastAPI docs).

---

### Branch: AOI-IGA (Port 8001)

```bash
# Frontend run under your main directory.
npm start
```

1.  **Activate your Python virtual environment.**
2.  Ensure you are in the project root directory.
3.  Start the Uvicorn server:

```bash
# Please activate your Python environment first.

cd backend 
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

**Access:** Open your browser and navigate to `http://127.0.0.1:8001`.

---

### Branch: SA-IGA (Port 8002)

```bash
# Frontend run under your main directory.
npm start
```

1.  **Activate your Python virtual environment.**
2.  Ensure you are in the project root directory.
3.  Start the Uvicorn server:

```bash
# Please activate your Python environment first.

cd backend 
uvicorn main:app --reload --host 127.0.0.1 --port 8002
```

**Access:** Open your browser and navigate to `http://127.0.0.1:8002`.


