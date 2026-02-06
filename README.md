# Site Analyzer - Deployment Instructions

## What You Have

Two folders:
1. `site-analyzer-backend` - Python API (goes on Railway)
2. `site-analyzer-frontend` - Website (goes on Vercel)

## Step-by-Step Deployment

### Part 1: Deploy Backend to Railway

1. Go to https://railway.app
2. Click "New Project"
3. Choose "Deploy from GitHub repo"
4. Click "Configure GitHub App" 
5. Install Railway on your GitHub account
6. Select the repository you just created
7. Choose the `site-analyzer-backend` folder
8. Railway will automatically detect it's a Python app and deploy it
9. Once deployed, click on your project
10. Click "Settings" → "Networking" → "Generate Domain"
11. **COPY THIS URL** - you'll need it for the frontend (something like: `https://your-app-name.railway.app`)

### Part 2: Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Select your GitHub repository
4. Choose the `site-analyzer-frontend` folder
5. Click "Deploy"
6. Once deployed, you'll get a URL like: `https://your-site.vercel.app`

### Part 3: Connect Frontend to Backend

1. In your GitHub repository, go to `site-analyzer-frontend/script.js`
2. On line 2, update the API_URL:
   ```javascript
   const API_URL = 'https://your-backend-url.railway.app';
   ```
   Replace with YOUR Railway URL from Part 1, Step 11
3. Commit and push this change
4. Vercel will automatically redeploy with the new URL

## Testing

1. Go to your Vercel URL
2. Enter an address in Salt Lake City (e.g., "350 S 400 E, Salt Lake City, UT")
3. Click "Analyze Site"
4. You should see results and be able to download a PDF!

## Troubleshooting

- If you get CORS errors: Make sure the Railway URL is correct in script.js
- If backend won't start: Check Railway logs for errors
- If nothing happens: Open browser console (F12) to see JavaScript errors

## Next Steps

Once it's working:
- Test with multiple addresses
- Share the Vercel URL with construction contacts
- Gather feedback!
