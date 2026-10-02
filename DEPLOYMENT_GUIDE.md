# Cloud Deployment Guide: Intelligent Support AI

This guide walks you through deploying the **FastAPI Backend on Render** and the **Enterprise Streamlit Frontend on Streamlit Community Cloud**.

---

## Architecture Overview

```
                        ┌──────────────────────────────────────────────┐
                        │      Streamlit Community Cloud (Frontend)    │
                        │      https://your-app.streamlit.app          │
                        └──────────────────────┬───────────────────────┘
                                               │ REST API / JSON
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │           Render.com (FastAPI Backend)       │
                        │      https://your-backend.onrender.com       │
                        └──────────────────────┬───────────────────────┘
                                               │
                                ┌──────────────┴──────────────┐
                                │                             │
                                ▼                             ▼
                        ┌──────────────┐              ┌──────────────┐
                        │   Groq LLM   │              │  Chroma RAG  │
                        │  gpt-oss-120b│              │  + Hybrid DB │
                        └──────────────┘              └──────────────┘
```

---

## Part 1: Deploy Backend on Render

### Step 1: Create a Render Account
1. Go to [https://render.com](https://render.com) and sign up with your GitHub account.

### Step 2: Create a New Web Service
1. Click **New +** in the top-right corner $\rightarrow$ Select **Web Service**.
2. Connect your GitHub repository: `BesthaMahesh/intelligent_support_ai`.
3. Configure the service settings:
   - **Name**: `intelligent-support-backend` (or any preferred name)
   - **Region**: `Oregon (US West)` or closest to your location
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: `Free`

### Step 3: Add Environment Variables in Render
Under the **Environment Variables** section, add the following key-value pairs:

| Variable Key | Value | Description |
| :--- | :--- | :--- |
| `GROQ_API_KEY` | `your-groq-api-key` | Your production Groq API key |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | High-speed reasoning model |
| `JWT_SECRET_KEY` | `generate-a-32-char-random-secret` | Authentication token signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Session lifetime (24 hours) |
| `APP_ENV` | `production` | Production mode |

### Step 4: Deploy & Copy Backend URL
1. Click **Create Web Service**.
2. Render will build and launch your FastAPI backend.
3. Once deployed, copy your live backend service URL from the top of the dashboard:
   `https://intelligent-support-backend.onrender.com`
4. Verify by visiting `https://intelligent-support-backend.onrender.com/docs` (Swagger UI).

---

## Part 2: Deploy Frontend on Streamlit Community Cloud

### Step 1: Sign in to Streamlit Cloud
1. Go to [https://share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.

### Step 2: Create a New App
1. Click **Create app** (or **New app**).
2. Configure your repository details:
   - **Repository**: `BesthaMahesh/intelligent_support_ai`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom subdomain (e.g., `intelligent-support.streamlit.app`)

### Step 3: Add Secrets & Environment Settings
1. Click **Advanced settings...** before deploying (or go to **Settings $\rightarrow$ Secrets** after creation).
2. In the **Secrets (TOML)** editor, paste the URL of your Render backend and Groq key:

```toml
# Live Render Backend API URL
BACKEND_URL = "https://intelligent-support-backend.onrender.com"

# Groq API Key (Enables in-process hybrid fallback)
GROQ_API_KEY = "your-groq-api-key"
GROQ_MODEL = "openai/gpt-oss-120b"
```

3. Click **Save** and then **Deploy!**

---

## Part 3: Verification Checklist

1. Open your Streamlit live URL.
2. Sign in using the **👤 Customer** quick login (or credentials: `customer@support.ai` / `Customer@123`).
3. Test the **Support Assistant**:
   - Send: *"Where is my order ORD-78231?"*
   - Verify real-time response from backend.
4. Test **Orders & Services**:
   - Verify timeline status for `#ORD-78231` and `#ORD-91245`.
5. Test **Help Center**:
   - Search for *"return policy"* and verify hybrid RAG search results.
