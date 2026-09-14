# Atlas Weather

A polished, responsive Streamlit weather app with worldwide city search, live current conditions, and a five-day forecast powered by [Open-Meteo](https://open-meteo.com/). Tokyo is shown by default, and a hardcoded fallback keeps the app useful when the weather service is unavailable.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Open [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
2. Select the `atlas-weather` repository and the `main` branch.
3. Set the main file to `app.py` and click **Deploy**.

No API key or secrets are required.

## Secure accounts

Authentication uses Supabase Auth, which hashes passwords and manages sessions. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` for local Streamlit use, add the same `SUPABASE_URL` and `SUPABASE_ANON_KEY` as Streamlit Cloud secrets, and replace the two placeholders near the bottom of `index.html` for the static app. Never commit the real anon key or any service-role key; Supabase Auth stores the password hashes in its managed `auth.users` table.

## Live apps

- Static web app: https://ugh777.github.io/atlas-weather/
- Streamlit app: https://atlas-weather-ugh.streamlit.app/
- Source repository: https://github.com/ugh777/atlas-weather
