# Vercel Deployment Instructions

This project is optimized for deployment on Vercel.

## Deployment Steps

1. **Push to GitHub**: Push your code to a GitHub repository.
2. **Connect to Vercel**: Go to [Vercel](https://vercel.com), click "Add New" -> "Project", and select your repository.
3. **Environment Variables**: In the Vercel project settings, add the following environment variables:
   - `SUPABASE_URL`: Your Supabase Project URL.
   - `SUPABASE_KEY`: Your Supabase API Key (service_role or anon key).
4. **Deploy**: Click "Deploy".

## Project Structure for Vercel
- `vercel.json`: Configuration for routing and builds.
- `api/index.py`: Entry point for the Flask application.
- `static/`: Served directly by Vercel's Edge Network for maximum performance.
- `templates/`: Flask templates.

## Database Setup
Make sure to execute the `schema.sql` in your Supabase SQL Editor before deploying to ensure the live database functionality works. If these are not set, the app will gracefully fall back to mock data.
