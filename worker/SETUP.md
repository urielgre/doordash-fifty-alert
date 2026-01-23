# Cloudflare Worker Setup

This worker handles email signups for the 50-Point Alerts landing page.

## Quick Setup (5 minutes)

### 1. Create Cloudflare Account
Go to https://dash.cloudflare.com/sign-up (free)

### 2. Install Wrangler CLI
```bash
npm install -g wrangler
```

### 3. Login to Cloudflare
```bash
wrangler login
```

### 4. Deploy the Worker
```bash
cd worker
wrangler deploy
```

### 5. Set Environment Variables
In Cloudflare dashboard (Workers & Pages > fifty-point-signup > Settings > Variables):

| Variable | Value |
|----------|-------|
| RESEND_API_KEY | `re_BwNFY5du_6DbBSQjPv9ryMrgAHiZfVHMb` |
| RESEND_AUDIENCE_ID | `32f1c633-d088-433a-802e-174606a5add5` |

Or via CLI:
```bash
wrangler secret put RESEND_API_KEY
wrangler secret put RESEND_AUDIENCE_ID
```

### 6. Get Your Worker URL
After deploying, you'll get a URL like:
```
https://fifty-point-signup.<your-account>.workers.dev
```

### 7. Update Landing Page
Edit `index.html` and update the `WORKER_URL` constant:
```javascript
const WORKER_URL = 'https://fifty-point-signup.<your-account>.workers.dev';
```

## Testing

```bash
curl -X POST https://fifty-point-signup.<your-account>.workers.dev \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## Free Tier Limits
- 100,000 requests/day
- More than enough for this project!
