import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import requests
from streamlit_tags import st_tags


# Helper function to get file info (size and last modification time)
def get_file_info(url):
    """Get file size and last modification time from HTTP headers"""
    try:
        response = requests.head(url, timeout=10)
        response.raise_for_status()

        # Get file size
        content_length = response.headers.get("content-length")
        file_size = int(content_length) if content_length else 0

        # Get last modification time
        last_modified = response.headers.get("last-modified")
        if last_modified:
            # Parse the HTTP date format
            from email.utils import parsedate_to_datetime

            mod_time = parsedate_to_datetime(last_modified).timestamp()
        else:
            mod_time = 0

        return file_size, mod_time
    except Exception as e:
        st.warning(f"Could not get file info: {e}")
        return 0, 0


# Helper: Efficiently load and filter CSV for only uncached zip codes in one pass
def load_and_filter_csv_for_zipcodes_with_individual_cache(
    csv_url, zip_codes, rows_to_read_int
):
    current_file_size, current_mod_time = get_file_info(csv_url)
    # Prepare cache keys and determine which zip codes need to be loaded
    cache_keys = {
        z: f"csv_data_{current_mod_time}_{current_file_size}_{z}_{rows_to_read_int}"
        for z in zip_codes
    }
    uncached_zips = [z for z in zip_codes if cache_keys[z] not in st.session_state]
    zip_dfs = {}
    # Load from cache for already-cached zip codes
    for z in zip_codes:
        if cache_keys[z] in st.session_state:
            zip_dfs[z] = st.session_state[cache_keys[z]]
    if uncached_zips:
        st.info(
            f"🔄 Loading and filtering data for zip codes: {', '.join(uncached_zips)} ..."
        )
        filtered_chunks_dict = {z: [] for z in uncached_zips}
        total_rows_processed = 0
        chunk_size = 10000
        chunk_iterator = pd.read_csv(csv_url, chunksize=chunk_size)
        for chunk in chunk_iterator:
            if rows_to_read_int != -1 and total_rows_processed >= rows_to_read_int:
                break
            if rows_to_read_int != -1:
                remaining_rows = rows_to_read_int - total_rows_processed
                if len(chunk) > remaining_rows:
                    chunk = chunk.head(remaining_rows)
            total_rows_processed += len(chunk)
            if "postal_code" in chunk.columns:
                chunk["postal_code_str"] = chunk["postal_code"].astype(str).str.zfill(5)
                for z in uncached_zips:
                    filtered_chunk = chunk[chunk["postal_code_str"] == z].copy()
                    if not filtered_chunk.empty:
                        filtered_chunk = filtered_chunk.drop("postal_code_str", axis=1)
                        filtered_chunks_dict[z].append(filtered_chunk)
            del chunk
        # Build DataFrame for each uncached zip code and cache it
        for z in uncached_zips:
            if filtered_chunks_dict[z]:
                zip_dfs[z] = pd.concat(filtered_chunks_dict[z], ignore_index=True)
            else:
                zip_dfs[z] = pd.DataFrame()
            st.session_state[cache_keys[z]] = zip_dfs[z]
        st.success(
            f"✅ Data loaded and cached for zip codes: {', '.join(uncached_zips)}!"
        )
    else:
        st.info("📋 All zip codes loaded from cache.")
    return zip_dfs


# Plotting functions
def create_price_trend_chart(filtered_df, zip_code):
    """Create median listing price trend chart with yearly average lines"""
    # Calculate yearly averages first
    filtered_df["year"] = filtered_df["date"].dt.year
    yearly_averages = filtered_df.groupby("year")["median_listing_price"].mean()

    # Create color mapping for markers based on yearly averages
    def get_marker_color(row):
        year = row["year"]
        if year in yearly_averages:
            return (
                "red"
                if row["median_listing_price"] < yearly_averages[year]
                else "green"
            )
        return "blue"  # fallback color

    filtered_df["marker_color"] = filtered_df.apply(get_marker_color, axis=1)

    fig_price = px.line(
        filtered_df,
        x="date",
        y="median_listing_price",
        title=f"Median Listing Price Trend - Zip Code {zip_code}",
        labels={"median_listing_price": "Price ($)", "date": "Date"},
        markers=True,
    )

    # Add horizontal dotted lines for each year's average (spanning only that year)
    for year, avg_price in yearly_averages.items():
        # Get the start and end dates for this year
        year_data = filtered_df[filtered_df["year"] == year]
        if not year_data.empty:
            start_date = year_data["date"].min()
            end_date = year_data["date"].max()

            # Add horizontal line spanning only this year
            fig_price.add_shape(
                type="line",
                x0=start_date,
                x1=end_date,
                y0=avg_price,
                y1=avg_price,
                line=dict(dash="dot", color="gray", width=2),
                opacity=0.7,
            )

            # Add annotation at the end of the line
            fig_price.add_annotation(
                x=end_date,
                y=avg_price,
                text=f"{year} Avg: ${avg_price:,.0f}",
                showarrow=False,
                xanchor="left",
                yanchor="bottom",
                font=dict(size=10, color="gray"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1,
            )

    fig_price.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Date",
        yaxis_title="Price ($)",
    )
    fig_price.update_xaxes(tickformat="%b %Y", tickmode="auto")
    fig_price.update_traces(line=dict(width=3), marker=dict(size=8))

    # Update marker colors based on yearly averages
    for i, trace in enumerate(fig_price.data):
        trace.marker.color = filtered_df["marker_color"].tolist()

    return fig_price


def create_days_on_market_chart(filtered_df, zip_code):
    """Create median days on market trend chart with yearly average lines"""
    # Calculate yearly averages first
    filtered_df["year"] = filtered_df["date"].dt.year
    yearly_averages = filtered_df.groupby("year")["median_days_on_market"].mean()

    # Create color mapping for markers based on yearly averages
    def get_marker_color(row):
        year = row["year"]
        if year in yearly_averages:
            return (
                "red"
                if row["median_days_on_market"] < yearly_averages[year]
                else "green"
            )
        return "blue"  # fallback color

    filtered_df["marker_color"] = filtered_df.apply(get_marker_color, axis=1)

    fig_days = px.line(
        filtered_df,
        x="date",
        y="median_days_on_market",
        title=f"Median Days on Market Trend - Zip Code {zip_code}",
        labels={"median_days_on_market": "Days", "date": "Date"},
        markers=True,
    )

    # Add horizontal dotted lines for each year's average (spanning only that year)
    for year, avg_days in yearly_averages.items():
        # Get the start and end dates for this year
        year_data = filtered_df[filtered_df["year"] == year]
        if not year_data.empty:
            start_date = year_data["date"].min()
            end_date = year_data["date"].max()

            # Add horizontal line spanning only this year
            fig_days.add_shape(
                type="line",
                x0=start_date,
                x1=end_date,
                y0=avg_days,
                y1=avg_days,
                line=dict(dash="dot", color="gray", width=2),
                opacity=0.7,
            )

            # Add annotation at the end of the line
            fig_days.add_annotation(
                x=end_date,
                y=avg_days,
                text=f"{year} Avg: {avg_days:.0f} days",
                showarrow=False,
                xanchor="left",
                yanchor="bottom",
                font=dict(size=10, color="gray"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1,
            )

    fig_days.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Date",
        yaxis_title="Days",
    )
    fig_days.update_xaxes(tickformat="%b %Y", tickmode="auto")
    fig_days.update_traces(line=dict(width=3), marker=dict(size=8))

    # Update marker colors based on yearly averages
    for i, trace in enumerate(fig_days.data):
        trace.marker.color = filtered_df["marker_color"].tolist()

    return fig_days


def create_price_per_sqft_chart(filtered_df, zip_code):
    """Create median price per square foot trend chart with yearly average lines"""
    # Calculate yearly averages first
    filtered_df["year"] = filtered_df["date"].dt.year
    yearly_averages = filtered_df.groupby("year")[
        "median_listing_price_per_square_foot"
    ].mean()

    # Create color mapping for markers based on yearly averages
    def get_marker_color(row):
        year = row["year"]
        if year in yearly_averages:
            return (
                "red"
                if row["median_listing_price_per_square_foot"] < yearly_averages[year]
                else "green"
            )
        return "blue"  # fallback color

    filtered_df["marker_color"] = filtered_df.apply(get_marker_color, axis=1)

    fig_sqft = px.line(
        filtered_df,
        x="date",
        y="median_listing_price_per_square_foot",
        title=f"Median Price per Square Foot Trend - Zip Code {zip_code}",
        labels={
            "median_listing_price_per_square_foot": "Price per Sq Ft ($)",
            "date": "Date",
        },
        markers=True,
    )

    # Add horizontal dotted lines for each year's average (spanning only that year)
    for year, avg_price in yearly_averages.items():
        # Get the start and end dates for this year
        year_data = filtered_df[filtered_df["year"] == year]
        if not year_data.empty:
            start_date = year_data["date"].min()
            end_date = year_data["date"].max()

            # Add horizontal line spanning only this year
            fig_sqft.add_shape(
                type="line",
                x0=start_date,
                x1=end_date,
                y0=avg_price,
                y1=avg_price,
                line=dict(dash="dot", color="gray", width=2),
                opacity=0.7,
            )

            # Add annotation at the end of the line
            fig_sqft.add_annotation(
                x=end_date,
                y=avg_price,
                text=f"{year} Avg: ${avg_price:.0f}",
                showarrow=False,
                xanchor="left",
                yanchor="bottom",
                font=dict(size=10, color="gray"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1,
            )

    fig_sqft.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Date",
        yaxis_title="Price per Sq Ft ($)",
    )
    fig_sqft.update_xaxes(tickformat="%b %Y", tickmode="auto")
    fig_sqft.update_traces(line=dict(width=3), marker=dict(size=8))

    # Update marker colors based on yearly averages
    for i, trace in enumerate(fig_sqft.data):
        trace.marker.color = filtered_df["marker_color"].tolist()

    return fig_sqft


def create_price_per_sqft_yy_chart(filtered_df, zip_code):
    """Create median price per square foot (YY) bar chart with color coding"""
    fig_sqft_yy = go.Figure()

    # Add bars with color coding based on positive/negative values
    for i, row in filtered_df.iterrows():
        value = row["median_listing_price_per_square_foot_yy"]
        color = "red" if value < 0 else "green"

        fig_sqft_yy.add_trace(
            go.Bar(
                x=[row["date"]],
                y=[value],
                marker_color=color,
                showlegend=False,
            )
        )

    fig_sqft_yy.update_layout(
        title=f"Median Price per Square Foot (YY) Trend - Zip Code {zip_code}",
        height=400,
        xaxis_title="Date",
        yaxis_title="Percentage (%)",
        bargap=0.1,
    )
    fig_sqft_yy.update_xaxes(tickformat="%b %Y", tickmode="auto")
    # Format y-axis to show percentages (multiply by 100 and add % symbol)
    fig_sqft_yy.update_yaxes(tickformat=".0%")

    return fig_sqft_yy


def create_median_square_feet_chart(filtered_df, zip_code):
    """Create median square feet trend chart with yearly average lines and colored markers"""
    # Calculate yearly averages first
    filtered_df["year"] = filtered_df["date"].dt.year
    yearly_averages = filtered_df.groupby("year")["median_square_feet"].mean()

    # Create color mapping for markers based on yearly averages
    def get_marker_color(row):
        year = row["year"]
        if year in yearly_averages:
            return (
                "red" if row["median_square_feet"] < yearly_averages[year] else "green"
            )
        return "blue"  # fallback color

    filtered_df["marker_color"] = filtered_df.apply(get_marker_color, axis=1)

    fig_sqft = px.line(
        filtered_df,
        x="date",
        y="median_square_feet",
        title=f"Median Square Feet Trend - Zip Code {zip_code}",
        labels={
            "median_square_feet": "Median Sq Ft",
            "date": "Date",
        },
        markers=True,
    )

    # Add horizontal dotted lines for each year's average (spanning only that year)
    for year, avg_sqft in yearly_averages.items():
        year_data = filtered_df[filtered_df["year"] == year]
        if not year_data.empty:
            start_date = year_data["date"].min()
            end_date = year_data["date"].max()
            fig_sqft.add_shape(
                type="line",
                x0=start_date,
                x1=end_date,
                y0=avg_sqft,
                y1=avg_sqft,
                line=dict(dash="dot", color="gray", width=2),
                opacity=0.7,
            )
            fig_sqft.add_annotation(
                x=end_date,
                y=avg_sqft,
                text=f"{year} Avg: {avg_sqft:.0f} sq ft",
                showarrow=False,
                xanchor="left",
                yanchor="bottom",
                font=dict(size=10, color="gray"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1,
            )

    fig_sqft.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Date",
        yaxis_title="Median Sq Ft",
    )
    fig_sqft.update_xaxes(tickformat="%b %Y", tickmode="auto")
    fig_sqft.update_traces(line=dict(width=3), marker=dict(size=8))

    # Update marker colors based on yearly averages
    for i, trace in enumerate(fig_sqft.data):
        trace.marker.color = filtered_df["marker_color"].tolist()

    return fig_sqft


def display_summary_metrics(filtered_df):
    """Display summary statistics in columns"""
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_price = filtered_df["median_listing_price"].mean()
        price_change = (
            filtered_df["median_listing_price"].pct_change().iloc[-1]
            if len(filtered_df) > 1
            else 0
        )
        st.metric(
            "Avg Listing Price",
            f"${avg_price:,.0f}",
            (f"{price_change*100:.1f}%" if len(filtered_df) > 1 else "N/A"),
        )

    with col2:
        avg_days = filtered_df["median_days_on_market"].mean()
        days_change = (
            filtered_df["median_days_on_market"].pct_change().iloc[-1]
            if len(filtered_df) > 1
            else 0
        )
        st.metric(
            "Avg Days on Market",
            f"{avg_days:.0f} days",
            (f"{days_change*100:.1f}%" if len(filtered_df) > 1 else "N/A"),
        )

    with col3:
        avg_price_sqft = filtered_df["median_listing_price_per_square_foot"].mean()
        sqft_change = (
            filtered_df["median_listing_price_per_square_foot"].pct_change().iloc[-1]
            if len(filtered_df) > 1
            else 0
        )
        st.metric(
            "Avg Price per Sq Ft",
            f"${avg_price_sqft:.0f}",
            (f"{sqft_change*100:.1f}%" if len(filtered_df) > 1 else "N/A"),
        )

    # Add fourth column for YY metric if it exists
    if "median_listing_price_per_square_foot_yy" in filtered_df.columns:
        col4 = st.columns(1)[0]
        with col4:
            avg_price_sqft_yy = filtered_df[
                "median_listing_price_per_square_foot_yy"
            ].mean()
            sqft_yy_change = (
                filtered_df["median_listing_price_per_square_foot_yy"]
                .pct_change()
                .iloc[-1]
                if len(filtered_df) > 1
                else 0
            )
            st.metric(
                "Avg Price per Sq Ft (YY)",
                f"{avg_price_sqft_yy:.1f}%",
                (f"{sqft_yy_change*100:.1f}%" if len(filtered_df) > 1 else "N/A"),
            )


def display_market_insights(filtered_df):
    """Display market insights and analysis"""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Price Trends:**")
        if len(filtered_df) > 1:
            latest_price = filtered_df["median_listing_price"].iloc[-1]
            earliest_price = filtered_df["median_listing_price"].iloc[0]
            total_change = ((latest_price - earliest_price) / earliest_price) * 100
            st.write(f"Total price change: {total_change:+.1f}%")

            if total_change > 0:
                st.write("📈 **Market is appreciating**")
            else:
                st.write("📉 **Market is depreciating**")

    with col2:
        st.markdown("**Market Speed:**")
        if len(filtered_df) > 1:
            latest_days = filtered_df["median_days_on_market"].iloc[-1]
            earliest_days = filtered_df["median_days_on_market"].iloc[0]
            days_change = ((latest_days - earliest_days) / earliest_days) * 100
            st.write(f"Days on market change: {days_change:+.1f}%")

            if latest_days < 30:
                st.write("⚡ **Fast-moving market**")
            elif latest_days < 60:
                st.write("🏃 **Moderate market speed**")
            else:
                st.write("🐌 **Slow-moving market**")


def display_all_charts(filtered_df, zip_code):
    """Display all charts for the housing data"""
    st.subheader("📈 Housing Trends")

    st.markdown("### 💰 Median Listing Price")
    fig_price = create_price_trend_chart(filtered_df, zip_code)
    st.plotly_chart(fig_price, use_container_width=True)

    st.markdown("### 📐 Median Price per Square Foot")
    fig_sqft = create_price_per_sqft_chart(filtered_df, zip_code)
    st.plotly_chart(fig_sqft, use_container_width=True)

    st.markdown("### 🏠 Median Square Feet")
    fig_sqft_median = create_median_square_feet_chart(filtered_df, zip_code)
    st.plotly_chart(fig_sqft_median, use_container_width=True)

    st.markdown("### 📊 Median Price per Square Foot (YY)")
    fig_sqft_yy = create_price_per_sqft_yy_chart(filtered_df, zip_code)
    st.plotly_chart(fig_sqft_yy, use_container_width=True)

    st.markdown("### ⏱️ Median Days on Market")
    fig_days = create_days_on_market_chart(filtered_df, zip_code)
    st.plotly_chart(fig_days, use_container_width=True)


# Page configuration
st.set_page_config(page_title="Housing Data Dashboard", page_icon="🏠", layout="wide")

# Title
st.title("🏠 Housing Data Dashboard")
st.markdown("Enter a zip code to filter housing data and view trends")

# Sidebar for input
with st.sidebar:
    st.header("📊 Data Filter")
    zip_codes = st_tags(
        label="Enter zip codes:",
        text="Press enter to add more",
        value=["10001", "02638", "07078", "33578", "11530"],
        suggestions=[],
        maxtags=20,
        key="zip_tags",
    )
    # Clean and validate zip codes
    zip_codes = [z.strip() for z in zip_codes if z.strip()]

    # URL input for CSV file
    csv_url = st.text_input(
        "CSV URL:",
        value="https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Zip_History.csv",
        help="Enter the URL of your CSV file (required).",
    )

    # Number of rows to read
    rows_to_read = st.text_input(
        "Number of Rows to Read:",
        value="-1",
        help="Enter -1 to read the entire file, or specify a number (e.g., 1000 for first 1000 rows).",
    )

    load_button = st.button("📥 Load Data", type="primary")

# Main content area
if load_button:
    if not zip_codes or any((not z.isdigit() or len(z) != 5) for z in zip_codes):
        st.error("Please enter valid 5-digit zip code(s)")
    else:
        with st.spinner(
            "Loading and processing data... Might need to wait a few minutes"
        ):
            progress_bar = st.progress(0)
            status_text = st.empty()
            if not csv_url:
                st.error("Please provide a CSV URL")
                st.stop()
            try:
                rows_to_read_int = int(rows_to_read)
                if rows_to_read_int < -1:
                    st.error("Number of rows must be -1 or a positive number")
                    st.stop()
            except ValueError:
                st.error("Please enter a valid number for rows to read")
                st.stop()
            # Efficiently load and filter the CSV for only uncached zip codes in one pass
            zip_dfs = load_and_filter_csv_for_zipcodes_with_individual_cache(
                csv_url, [str(z).zfill(5) for z in zip_codes], rows_to_read_int
            )
            for i, zip_code in enumerate(zip_codes):
                progress_bar.progress((i + 1) / max(1, len(zip_codes)))
            status_text.text("Preparing charts...")
            # Create a tab for each zip code
            tabs = st.tabs([f"Zip {z}" for z in zip_codes])
            for i, zip_code in enumerate(zip_codes):
                zip_code_str = str(zip_code).zfill(5)
                with tabs[i]:
                    filtered_df = zip_dfs[zip_code_str]
                    if filtered_df.empty:
                        st.warning(f"No data found for zip code {zip_code_str}")
                    else:
                        filtered_df["date"] = pd.to_datetime(
                            filtered_df["month_date_yyyymm"], format="%Y%m"
                        )
                        filtered_df = filtered_df.sort_values("date")
                        st.success(
                            f"✅ Found {len(filtered_df)} records for zip code {zip_code_str}"
                        )
                        st.subheader("📋 Filtered Data")
                        display_columns = [
                            "month_date_yyyymm",
                            "median_listing_price",
                            "median_days_on_market",
                            "median_listing_price_per_square_foot",
                        ]
                        if (
                            "median_listing_price_per_square_foot_yy"
                            in filtered_df.columns
                        ):
                            display_columns.append(
                                "median_listing_price_per_square_foot_yy"
                            )
                        if "median_square_feet" in filtered_df.columns:
                            display_columns.append("median_square_feet")
                        st.dataframe(filtered_df[display_columns])
                        display_all_charts(filtered_df, zip_code_str)
            progress_bar.progress(1.0)
            status_text.text("All charts ready!")
            progress_bar.empty()
            status_text.empty()

else:
    st.info("👈 Use the sidebar to enter zip code(s) and CSV URL, then load data")

    # Instructions
    st.markdown(
        """
    ### How to use this app:

    1. **Enter Zip Codes**: Type 5-digit zip codes separated by commas in the sidebar (e.g., 11530,11531)
    2. **CSV URL**: Enter the URL of your CSV file (required)
    3. **Number of Rows**: Enter -1 to read the entire file, or specify a number (e.g., 1000 for first 1000 rows).
    4. **Load Data**: Click the "Load Data" button to fetch and filter the housing data
    5. **View Results**: The app will display:
       - Filtered data table
       - Interactive line charts showing trends
       - Summary statistics
       - Market insights

    ### Features:
    - ✅ **Simple CSV reading** with pandas
    - ✅ **Fast filtering** by zip code
    - ✅ **Interactive charts** with Plotly
    - ✅ **Responsive design**
    - ✅ **Summary metrics** with trend indicators
    - ✅ **Market insights** and analysis

    ### Required CSV Format:
    The CSV file should have these columns:
    - `postal_code`: 5-digit zip codes
    - `month_date_yyyymm`: Date in YYYYMM format
    - `median_listing_price`: Median listing prices
    - `median_days_on_market`: Days properties stay on market
    - `median_listing_price_per_square_foot`: Price per square foot
    - `median_listing_price_per_square_foot_yy`: Price per square foot (YY version) - optional

    ### Performance:
    - Loads CSV file into memory (entire file or specified number of rows)
    - Filters data by zip code after loading
    - Simple and fast for most CSV files
    - Use row limit for very large files to improve performance

    ### Example CSV URL:
    You can use any publicly accessible CSV file. For example:
    - Google Drive (make sure it's publicly accessible)
    - Dropbox (with public link)
    - GitHub raw files
    - AWS S3 public buckets
    """
    )

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit and Plotly*")
