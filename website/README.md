# App website for the Google OAuth consent screen

Static pages that satisfy Google's requirements for publishing the OAuth app:
a homepage that explains the app and is viewable without login, and a privacy policy
on the same domain.

- `index.html` – homepage, explains what the app does
- `privacy.html` – privacy policy
- `style.css` – shared style

## Deploy on Vercel

1. In the Vercel dashboard: **Add New… → Project**.
2. Import this repository (or a separate repo that only holds this `website/` folder).
3. Under **Root Directory** choose `website`. Framework preset: **Other**. There is no build step.
4. Deploy. Vercel gives a URL like `https://<name>.vercel.app`.

## In the Google Cloud Console (Branding page)

- **Application home page:** `https://<name>.vercel.app/`
- **Application privacy policy link:** `https://<name>.vercel.app/privacy.html`
- **Authorized domains:** `<name>.vercel.app`

Then publish the app under **Audience → Publish app**.
Verify ownership of the domain in Google Search Console if asked, and wait up to 24 hours before retrying verification.
