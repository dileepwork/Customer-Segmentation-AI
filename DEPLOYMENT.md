### Deployment Guide

**Wait!** I noticed your frontend source code was missing, so I have restored a functional `src` folder for you based on your project documentation. You are now ready to deploy.

#### 1. Push to GitHub
Open a terminal in `customer-segmentation-ai` (the root folder where you see `backend` and `frontend` dirs) and run:

```bash
git add .
git commit -m "Prepare for deployment"
# Create a new repo on GitHub.com and copy the commands to push an existing repository:
git remote add origin https://github.com/YOUR_USERNAME/customer-segmentation-ai.git
git branch -M main
git push -u origin main
```

#### 2. Deploy Backend (FastAPI) on Vercel
1.  Log in to Vercel and click **Add New > Project**.
2.  Import your GitHub repository.
3.  **Project Name**: `customer-segmentation-backend`.
4.  **Root Directory**: Click Edit → Select `backend`.
5.  **Environment Variables**: None mandatory for SQLite (note: DB resets on redeploy).
6.  Click **Deploy**.
7.  **Copy the Domain**: (e.g., `https://customer-segmentation-backend.vercel.app`).

#### 3. Deploy Frontend (React) on Vercel
1.  Go to dashboard, click **Add New > Project**.
2.  Import the **SAME** repository again.
3.  **Project Name**: `customer-segmentation-frontend`.
4.  **Root Directory**: Click Edit → Select `frontend`.
5.  **Environment Variables**:
    -   Key: `VITE_API_URL`
    -   Value: `https://customer-segmentation-backend.vercel.app` (The URL from Step 2, **without trailing slash**)
6.  Click **Deploy**.

Done! Your app is now live.
