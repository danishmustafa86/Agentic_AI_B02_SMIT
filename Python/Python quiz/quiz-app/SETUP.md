# Quiz App - Database Setup Guide

## Problem Fixed
Previously, student quiz results were being stored in a local file (`data/quiz-results.json`), which **doesn't persist on Vercel**. This has been replaced with a persistent PostgreSQL database.

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Set Up Vercel Postgres Database

#### Option A: Using Vercel CLI (Recommended)
```bash
npm i -g vercel
vercel link  # Link your project to Vercel
vercel env pull  # Pull environment variables
```

#### Option B: Manual Setup via Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Integrations** → **Databases**
4. Click **Add** → **Postgres**
5. Click **Create New** and create a Postgres database
6. Copy the connection string
7. Go to **Settings** → **Environment Variables**
8. Add the connection string as `POSTGRES_URL`

### 3. Environment Variables
Make sure your `.env.local` file (or Vercel environment variables) includes:
```
POSTGRES_URL=postgresql://...
```

### 4. Deploy to Vercel
```bash
git push  # This will trigger auto-deployment on Vercel
```

Or manually:
```bash
vercel deploy --prod
```

## What Changed

### Updated Files:
- **`lib/db.ts`** - New database utility functions
- **`app/api/submit-quiz/route.ts`** - Now uses database
- **`app/api/get-results/route.ts`** - Now uses database
- **`app/api/delete-result/route.ts`** - Now uses database
- **`app/api/export-excel/route.ts`** - Now uses database
- **`package.json`** - Added `@vercel/postgres` dependency

### Database Schema
```sql
CREATE TABLE quiz_results (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  roll_no VARCHAR(50) NOT NULL UNIQUE,
  score INTEGER NOT NULL,
  percentage INTEGER NOT NULL,
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Testing Locally

1. If you want to test with a local database, install PostgreSQL locally
2. Update `POSTGRES_URL` in `.env.local` to point to your local database
3. Run `npm run dev`
4. The database table will be created automatically on first API call

## Verify It's Working

1. Go to your Vercel dashboard
2. Select your project → **Databases**
3. Click on your Postgres database
4. Click **Data** to browse the `quiz_results` table
5. After a student submits a quiz, you should see the record appear here

## Admin Dashboard
- Student results now persist and will appear in the admin dashboard even after deployment
- You can view all submitted results, delete records, and export to Excel
- All data is securely stored in your Vercel Postgres database
