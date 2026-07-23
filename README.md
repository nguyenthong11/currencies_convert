# Currency Converter App

A simple, clean currency converter built with Streamlit, SQLite, and the Fixer.io API.

## Features

- Fetches and caches currency symbols in a local SQLite database
- Converts between any two supported currencies using real-time exchange rates
- **Two conversion methods**: "latest" (manual calculation from EUR-based rates, works on free tier) and "convert" (direct API endpoint)
- **In-memory caching** with 24-hour TTL for conversion results to reduce API calls
- User-friendly interface with dropdowns, numeric input, and a **Swap currencies** button
- Error handling for missing API keys, invalid requests, network errors, and timeouts
- Configuration via `.streamlit/secrets.toml` file for API key management

## Setup

1. **Clone or download this repository** (or just the `currency_converter` directory).

2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a free API key from [Fixer.io](https://fixer.io/)** and set it in a `.streamlit/secrets.toml` file:
   ```toml
   FIXER_IO_ACCESS_KEY = "your_api_key_here"
   ```
   Alternatively, export it as an environment variable:
   ```bash
   export FIXER_IO_ACCESS_KEY="your_api_key_here"
   ```

4. **Initialize the database** (this will create the SQLite database and populate it with currency symbols):
   ```bash
   python init_db.py
   ```
   Note: The database initialization is also triggered automatically when you run the app for the first time.

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your default web browser. Select the currencies, enter an amount, and click "Convert". Use the **⇄ Swap** button to quickly exchange the from/to currencies.

### Test the conversion module directly

You can also test the conversion logic without the UI:
```bash
python convert.py
```

## Project Structure

- `app.py`: Main Streamlit application with UI, currency selection, swap functionality, and conversion display
- `convert.py`: Currency conversion logic with Fixer.io API integration, in-memory caching (24hr TTL), and two conversion methods (`latest` and `convert`)
- `init_db.py`: Initializes the SQLite database and caches currency symbols from Fixer.io (idempotent)
- `db_helper.py`: Helper functions for database operations (fetching symbols, checking currency support)
- `requirements.txt`: Python dependencies (streamlit, requests, python-dotenv)
- `.streamlit/secrets.toml`: Environment variables (API key) - **not committed to git**
- `currency_cache.db`: SQLite database caching currency symbols (auto-generated)

## How It Works

### Conversion Methods

1. **`latest` (default)**: Fetches EUR-based rates from `/latest` endpoint and calculates the cross-rate manually. This works reliably on Fixer.io's free tier which locks `base=EUR`.
2. **`convert`**: Uses the direct `/convert` endpoint. On free-tier keys, this often returns a frozen historical rate rather than the current rate.

### Caching

- **Currency symbols**: Cached in `currency_cache.db` (SQLite) to avoid repeated API calls for the symbol list
- **Conversion results**: Cached in-memory with a 24-hour TTL in `convert.py` to reduce redundant API calls during a session

### Database Initialization

The database is initialized automatically on first app run via `@st.cache_resource`, or manually via `python init_db.py`. It's idempotent — safe to run multiple times.

## Troubleshooting

- **No currency symbols showing**: Run `python init_db.py` to see detailed errors.
- **Conversion fails**: Ensure `FIXER_IO_ACCESS_KEY` is set correctly in `.streamlit/secrets.toml`. Check network connectivity.
- **Database errors**: Make sure you have write permissions in the directory.
- **Stale rates**: The free tier of Fixer.io updates rates once per day. The app's in-memory cache also has a 24-hour TTL.

## License

This project is for educational purposes. Please refer to Fixer.io's terms of service for API usage.
