# JobHunt: live job and internship finder (built with TinyFish)

Tell JobHunt the role, location and seniority you want. It opens live careers pages and job portals,
reads the openings, removes duplicates, and ranks them against your preferences.

## How TinyFish is used

- **Search** discovers extra careers pages and portals for your query.
- **Agent** opens each portal in a real browser, uses its search box and filters, and returns structured listings (title, company, location, apply link).
- **Fetch** reads the posting page of the top matches to confirm your keywords and improve ranking.

All listings come from live web data. Nothing is hardcoded. Results are cached for 6 hours and can be refreshed on demand.

## Setup

1. Python 3.11 or newer.
2. Install dependencies: `python -m pip install -r requirements.txt`
3. Get a key at https://agent.tinyfish.ai/api-keys
4. Copy `.env.example` to `.env` and paste your key (the `.env` file is git-ignored).

## Run

Web app:

    python -m streamlit run app.py

Command line:

    python jobhunt.py --role "python developer" --level intern --location "Delhi" --keywords "django,flask"

## Files

- `jobhunt.py`: Search, Agent and Fetch pipeline, deduplication, scoring, caching
- `app.py`: Streamlit interface
- `.env.example`: template for your API key
