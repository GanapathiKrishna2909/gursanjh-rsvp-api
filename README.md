# Gursanjh's 1st Birthday RSVP API

Backend API for the RSVP system. Uses JSONBin for cloud storage.

## Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FGanapathiKrishna2909%2Fgursanjh-rsvp-api)

## Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/GanapathiKrishna2909/gursanjh-rsvp-api)

## API Endpoints

- `GET /api/stats` — Public guest count
- `POST /api/rsvp` — Submit RSVP
- `GET /api/rsvps?password=xxx` — Admin: view all RSVPs
- `DELETE /api/rsvp/{id}?password=xxx` — Admin: remove RSVP
