# Currency Converter App

A simple, clean currency converter built with Streamlit, SQLite, and the Fixer.io API.

## Features

- Fetches and caches currency symbols in a local SQLite database
- Converts between any two supported currencies using real-time exchange rates
- User-friendly interface with dropdowns and numeric input
- Error handling for missing API keys and invalid requests

## Setup

1. **Clone or download this repository** (or just the `currency_converter` directory).

2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a free API key from [Fixer.io](https://fixer.io/)** and set it as an environment variable:
   ```bash
   export FIXER_IO_ACCESS_KEY="your_api_key_here"
   ```
   On Windows (Command Prompt):
   ```cmd
   set FIXER_IO_ACCESS_KEY=your_api_key_here
   ```
   On Windows (PowerShell):
   ```powershell
   $env:FIXER_IO_ACCESS_KEY="your_api_key_here"
   ```

4. **Initialize the database** (this will create the SQLite database and populate it with currency symbols):
   ```bash
   python init_db.py
   ```
   Note: The database initialization is also triggered when you run the app for the first time.

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your default web browser. Select the currencies, enter an amount, and click "Convert".

## Project Structure

- `app.py`: Main Streamlit application
- `init_db.py`: Initializes the SQLite database and caches currency symbols
- `db_helper.py`: Helper functions for database operations
- `requirements.txt`: Python dependencies

## Notes

- The app uses the Fixer.io API's `/latest` endpoint for conversion rates.
- Currency symbols are cached in `currency_cache.db` to avoid unnecessary API calls.
- If the database is empty, the app will attempt to fetch symbols from Fixer.io on startup.

## Troubleshooting

- **No currency symbols showing**: Check your Fixer.io API key and internet connection.
- **Conversion fails**: Ensure you have set the `FIXER_IO_ACCESS_KEY` environment variable correctly.
- **Database errors**: Make sure you have write permissions in the directory.

## License

This project is for educational purposes. Please refer to Fixer.io's terms of service for API usage.