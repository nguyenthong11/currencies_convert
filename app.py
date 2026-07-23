import os
from datetime import datetime
from dotenv import load_dotenv
import init_db
import requests
import streamlit as st
from db_helper import get_all_symbols
from convert import convert

# Load environment variables from .env file
load_dotenv()
# Database path
db_path = os.getenv("DB_PATH", "currency_cache.db")
# --- One-time per-session initialization ---
@st.cache_resource
def _initialize_app():
    init_db.init_db(db_path=db_path)


_initialize_app()


@st.cache_data
def _load_symbols():
    return get_all_symbols(db_path=db_path)


# Set up the Streamlit app
st.set_page_config(page_title="Currency Converter", page_icon="💱", layout="centered")
st.title("💱 Currency Converter")
st.markdown("Convert currencies using the latest exchange rates from Fixer.io")

# Get the access key from environment variable
access_key = st.secrets["FIXER_IO_ACCESS_KEY"]
if not access_key:
    st.warning(
        "⚠️ Fixer.io API key not found. Please set the FIXER_IO_ACCESS_KEY secret in your app settings."
    )
    st.info("Get a free API key at https://fixer.io/")
    api_key_available = False
else:
    api_key_available = True

# Get all currency symbols from the database
symbols_dict = _load_symbols()
if not symbols_dict:
    st.error(
        "❌ No currency symbols found in the database. Please check your Fixer.io API key and internet connection."
    )
    st.stop()

# Create a sorted list of currency codes for the dropdowns
currency_codes = sorted(symbols_dict.keys())


def _fmt(code):
    return f"{code} - {symbols_dict[code]}"


# --- FIX STEP 1: Initialize the widget keys directly in session state ---
if "base_currency" not in st.session_state:
    st.session_state.base_currency = "XAU" if "XAU" in currency_codes else currency_codes[0]
if "target_currency" not in st.session_state:
    st.session_state.target_currency = "USD" if "USD" in currency_codes else currency_codes[1]


# --- FIX STEP 2: Swap the values directly, not the indices ---
def _swap_currencies():
    """Callback to swap the currency values directly."""
    st.session_state.base_currency, st.session_state.target_currency = (
        st.session_state.target_currency,
        st.session_state.base_currency,
    )


# Create three columns for the input, swap, and output currencies
col1, col_swap, col2 = st.columns([4, 1, 4])

with col1:
    st.subheader("From")
    # --- FIX STEP 3: Assign the `key` parameter to bind state ---
    base_currency = st.selectbox(
        "Base currency",
        options=currency_codes,
        format_func=_fmt,
        key="base_currency",
    )

with col_swap:
    st.write("")  # Vertical alignment
    st.write("")  # Vertical alignment
    st.button(
        "⇄ Swap",
        use_container_width=True,
        help="Swap currencies",
        on_click=_swap_currencies,
    )

with col2:
    st.subheader("To")
    # --- FIX STEP 4: Assign the `key` parameter to bind state ---
    target_currency = st.selectbox(
        "Target currency",
        options=currency_codes,
        format_func=_fmt,
        key="target_currency",
    )

# Amount input
amount = st.number_input("Amount", min_value=0.01, value=1.0, step=0.01)

# Convert button
if st.button("Convert", disabled=not api_key_available):
    if base_currency == target_currency:
        st.warning("Please select two different currencies.")
    else:
        try:
            data = convert(
                amount=amount,
                from_currency=base_currency,
                to_currency=target_currency,
                method="latest",
            )

            if not data.get("success"):
                st.error(f"API Error: {data}")
            else:
                result = data.get("result")
                if result is not None:
                    rate = result / amount if amount != 0 else 0
                    st.success(
                        f"**{amount:.2f} {base_currency}** = **{result:.2f} {target_currency}**"
                    )
                    st.info(f"Exchange rate: 1 {base_currency} = {rate:.4f} {target_currency}")

                    # Display timestamp from API response
                    info = data.get("info", {})
                    timestamp = info.get("timestamp")
                    if timestamp:
                        dt = datetime.fromtimestamp(timestamp)
                        st.caption(f"Rate as of: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                else:
                    st.error("Result not found in the response.")
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

# Footer
st.markdown("---")
st.markdown("Exchange rates powered by [Fixer.io](https://fixer.io/)")