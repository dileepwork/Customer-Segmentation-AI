### Deployment Guide

#### 1. Push to GitHub
Open a terminal in `customer-segmentation-ai` (the root folder) and run:

```bash
git add .
git commit -m "Ready for deployment"
# Replace with your actual repo URL
git remote add origin https://github.com/YOUR_USERNAME/customer-segmentation-ai.git
git branch -M main
git push -u origin main
```

#### 2. Database Setup (Supabase)
To make your data persist (Vercel resets local files on every deploy), you need a cloud database.

1.  **Create Project**: Go to [Supabase](https://supabase.com), create a project.
2.  **Run SQL**: Go to SQL Editor in Supabase, copy-paste content from `supabase_schema.sql` and Run.
3.  **Get Keys**: Go to Project Settings -> API. Copy `Project URL` and `service_role key` (or `anon` key if configured).

#### 3. Deploy Backend (FastAPI) on Vercel
1.  **New Project**: In Vercel, import your repo.
2.  **Settings**:
    -   **Project Name**: `customer-segmentation-backend`
    -   **Root Directory**: `backend`
    -   **Framework**: FastAPI (or Other)
3.  **Environment Variables**:
    -   `SUPABASE_URL`: value from Step 2.
    -   `SUPABASE_KEY`: value from Step 2.
4.  **Deploy**. Copy the URL (e.g., `https://backend-xyz.vercel.app`).

#### 4. Deploy Frontend (React) on Vercel
1.  **New Project**: In Vercel, import your repo again.
2.  **Settings**:
    -   **Project Name**: `customer-segmentation-frontend`
    -   **Root Directory**: `frontend`
    -   **Framework**: Vite
    -   **Build Command**: `npm run build`
3.  **Environment Variables**:
    -   `VITE_API_URL`: `https://backend-xyz.vercel.app` (Your backend URL).
4.  **Deploy**.

Your app is live!
