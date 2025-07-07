import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="Housing Data Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Title
st.title("🏠 Housing Data Dashboard")
st.markdown("Enter a zip code to filter housing data and view trends")

# Sidebar for input
with st.sidebar:
    st.header("📊 Data Filter")
    zip_code = st.text_input("Enter Zip Code:", value="11530", help="Enter a 5-digit zip code")
    
    # URL input for CSV file
    csv_url = st.text_input(
        "CSV URL:", 
        value="https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Zip_History.csv",
        help="Enter the URL of your CSV file (required)."
    )
    
    # Number of rows to read
    rows_to_read = st.text_input(
        "Number of Rows to Read:", 
        value="-1",
        help="Enter -1 to read the entire file, or specify a number (e.g., 1000 for first 1000 rows)."
    )
    
    load_button = st.button("📥 Load Data", type="primary")

# Main content area
if load_button:
    if not zip_code.isdigit() or len(zip_code) != 5:
        st.error("Please enter a valid 5-digit zip code")
    else:
        with st.spinner("Loading and processing data... Might need to wait a few minutes"):
            try:
                # Create progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Check if URL is provided
                if not csv_url:
                    st.error("Please provide a CSV URL")
                    st.stop()
                
                # Validate rows_to_read input
                try:
                    rows_to_read_int = int(rows_to_read)
                    if rows_to_read_int < -1:
                        st.error("Number of rows must be -1 or a positive number")
                        st.stop()
                except ValueError:
                    st.error("Please enter a valid number for rows to read")
                    st.stop()
                
                # Read CSV file using pandas
                status_text.text("Loading CSV file...")
                try:
                    if rows_to_read_int == -1:
                        # Read entire file
                        df = pd.read_csv(csv_url)
                        status_text.text(f"Loaded entire file ({len(df):,} rows)")
                    else:
                        # Read specified number of rows
                        df = pd.read_csv(csv_url, nrows=rows_to_read_int)
                        status_text.text(f"Loaded {len(df):,} rows from file")
                    
                    progress_bar.progress(0.5)
                    status_text.text("Filtering data by zip code...")
                                        
                    # Filter by zip code - handle leading zeros properly
                    if 'postal_code' in df.columns:
                        # Convert input zip code to string and ensure it's 5 digits with leading zeros
                        zip_code_str = str(zip_code).zfill(5)
                        
                        # Convert CSV postal codes to strings and ensure they're 5 digits with leading zeros
                        df['postal_code_str'] = df['postal_code'].astype(str).str.zfill(5)
                        
                        # Filter by exact string match
                        filtered_df = df[df['postal_code_str'] == zip_code_str].copy()
                        
                        st.write(f"🔍 Debug: Looking for zip code '{zip_code_str}' in postal_code column")
                        st.write(f"🔍 Debug: Found {len(filtered_df)} matching records")
                        
                        # Clean up temporary column
                        if not filtered_df.empty:
                            filtered_df = filtered_df.drop('postal_code_str', axis=1)
                    else:
                        filtered_df = pd.DataFrame()  # Empty DataFrame if no postal code column
                    
                    progress_bar.progress(1.0)
                    status_text.text("Data loaded successfully!")
                    
                except Exception as e:
                    st.error(f"Error reading CSV file: {str(e)}")
                    st.info("Please check your CSV URL and try again.")
                    st.stop()
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                if filtered_df.empty:
                    st.warning(f"No data found for zip code {zip_code}")
                else:
                    # Convert month_date_yyyymm to datetime for better plotting
                    filtered_df['date'] = pd.to_datetime(filtered_df['month_date_yyyymm'], format='%Y%m')
                    filtered_df = filtered_df.sort_values('date')
                    
                    st.success(f"✅ Found {len(filtered_df)} records for zip code {zip_code} (from {len(df):,} total rows loaded)")
                    
                    # Display the filtered data
                    st.subheader("📋 Filtered Data")
                    display_columns = ['month_date_yyyymm', 'median_listing_price', 'median_days_on_market', 'median_listing_price_per_square_foot']
                    
                    # Add the new column if it exists
                    if 'median_listing_price_per_square_foot_yy' in filtered_df.columns:
                        display_columns.append('median_listing_price_per_square_foot_yy')
                    
                    st.dataframe(filtered_df[display_columns])
                    
                    # Create individual line charts for each metric
                    st.subheader("📈 Housing Trends")
                    
                    # Chart 1: Median Listing Price
                    st.markdown("### 💰 Median Listing Price")
                    fig_price = px.line(
                        filtered_df, 
                        x='date', 
                        y='median_listing_price',
                        title=f"Median Listing Price Trend - Zip Code {zip_code}",
                        labels={'median_listing_price': 'Price ($)', 'date': 'Date'},
                        markers=True
                    )
                    fig_price.update_layout(
                        height=400,
                        showlegend=False,
                        xaxis_title="Date",
                        yaxis_title="Price ($)"
                    )
                    fig_price.update_xaxes(tickformat="%b %Y", tickmode="auto")
                    fig_price.update_traces(line=dict(width=3), marker=dict(size=8))
                    st.plotly_chart(fig_price, use_container_width=True)
                    
                    # Chart 2: Median Days on Market
                    st.markdown("### ⏱️ Median Days on Market")
                    fig_days = px.line(
                        filtered_df, 
                        x='date', 
                        y='median_days_on_market',
                        title=f"Median Days on Market Trend - Zip Code {zip_code}",
                        labels={'median_days_on_market': 'Days', 'date': 'Date'},
                        markers=True
                    )
                    fig_days.update_layout(
                        height=400,
                        showlegend=False,
                        xaxis_title="Date",
                        yaxis_title="Days"
                    )
                    fig_days.update_xaxes(tickformat="%b %Y", tickmode="auto")
                    fig_days.update_traces(line=dict(width=3), marker=dict(size=8))
                    st.plotly_chart(fig_days, use_container_width=True)
                    
                    # Chart 3: Median Price per Square Foot
                    st.markdown("### 📐 Median Price per Square Foot")
                    fig_sqft = px.line(
                        filtered_df, 
                        x='date', 
                        y='median_listing_price_per_square_foot',
                        title=f"Median Price per Square Foot Trend - Zip Code {zip_code}",
                        labels={'median_listing_price_per_square_foot': 'Price per Sq Ft ($)', 'date': 'Date'},
                        markers=True
                    )
                    fig_sqft.update_layout(
                        height=400,
                        showlegend=False,
                        xaxis_title="Date",
                        yaxis_title="Price per Sq Ft ($)"
                    )
                    fig_sqft.update_xaxes(tickformat="%b %Y", tickmode="auto")
                    fig_sqft.update_traces(line=dict(width=3), marker=dict(size=8))
                    st.plotly_chart(fig_sqft, use_container_width=True)
                    
                    # Chart 4: Median Price per Square Foot (YY version) - if column exists
                    if 'median_listing_price_per_square_foot_yy' in filtered_df.columns:
                        st.markdown("### 📊 Median Price per Square Foot (YY)")
                        
                        # Create bar chart with color coding
                        fig_sqft_yy = go.Figure()
                        
                        # Add bars with color coding based on positive/negative values
                        for i, row in filtered_df.iterrows():
                            value = row['median_listing_price_per_square_foot_yy']
                            color = 'red' if value < 0 else 'green'
                            
                            fig_sqft_yy.add_trace(go.Bar(
                                x=[row['date']],
                                y=[value],
                                marker_color=color,
                                showlegend=False
                            ))
                        
                        fig_sqft_yy.update_layout(
                            title=f"Median Price per Square Foot (YY) Trend - Zip Code {zip_code}",
                            height=400,
                            xaxis_title="Date",
                            yaxis_title="Percentage (%)",
                            bargap=0.1
                        )
                        fig_sqft_yy.update_xaxes(tickformat="%b %Y", tickmode="auto")
                        
                        st.plotly_chart(fig_sqft_yy, use_container_width=True)
                    
                    # Summary statistics
                    st.subheader("📊 Summary Statistics")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_price = filtered_df['median_listing_price'].mean()
                        price_change = filtered_df['median_listing_price'].pct_change().iloc[-1] if len(filtered_df) > 1 else 0
                        st.metric(
                            "Avg Listing Price",
                            f"${avg_price:,.0f}",
                            f"{price_change*100:.1f}%" if len(filtered_df) > 1 else "N/A"
                        )
                    
                    with col2:
                        avg_days = filtered_df['median_days_on_market'].mean()
                        days_change = filtered_df['median_days_on_market'].pct_change().iloc[-1] if len(filtered_df) > 1 else 0
                        st.metric(
                            "Avg Days on Market",
                            f"{avg_days:.0f} days",
                            f"{days_change*100:.1f}%" if len(filtered_df) > 1 else "N/A"
                        )
                    
                    with col3:
                        avg_price_sqft = filtered_df['median_listing_price_per_square_foot'].mean()
                        sqft_change = filtered_df['median_listing_price_per_square_foot'].pct_change().iloc[-1] if len(filtered_df) > 1 else 0
                        st.metric(
                            "Avg Price per Sq Ft",
                            f"${avg_price_sqft:.0f}",
                            f"{sqft_change*100:.1f}%" if len(filtered_df) > 1 else "N/A"
                        )
                    
                    # Add fourth column for YY metric if it exists
                    if 'median_listing_price_per_square_foot_yy' in filtered_df.columns:
                        col4 = st.columns(1)[0]
                        with col4:
                            avg_price_sqft_yy = filtered_df['median_listing_price_per_square_foot_yy'].mean()
                            sqft_yy_change = filtered_df['median_listing_price_per_square_foot_yy'].pct_change().iloc[-1] if len(filtered_df) > 1 else 0
                            st.metric(
                                "Avg Price per Sq Ft (YY)",
                                f"{avg_price_sqft_yy:.1f}%",
                                f"{sqft_yy_change*100:.1f}%" if len(filtered_df) > 1 else "N/A"
                            )
                    
                    # Additional insights
                    st.subheader("🔍 Market Insights")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Price Trends:**")
                        if len(filtered_df) > 1:
                            latest_price = filtered_df['median_listing_price'].iloc[-1]
                            earliest_price = filtered_df['median_listing_price'].iloc[0]
                            total_change = ((latest_price - earliest_price) / earliest_price) * 100
                            st.write(f"Total price change: {total_change:+.1f}%")
                            
                            if total_change > 0:
                                st.write("📈 **Market is appreciating**")
                            else:
                                st.write("📉 **Market is depreciating**")
                    
                    with col2:
                        st.markdown("**Market Speed:**")
                        if len(filtered_df) > 1:
                            latest_days = filtered_df['median_days_on_market'].iloc[-1]
                            earliest_days = filtered_df['median_days_on_market'].iloc[0]
                            days_change = ((latest_days - earliest_days) / earliest_days) * 100
                            st.write(f"Days on market change: {days_change:+.1f}%")
                            
                            if latest_days < 30:
                                st.write("⚡ **Fast-moving market**")
                            elif latest_days < 60:
                                st.write("🏃 **Moderate market speed**")
                            else:
                                st.write("🐌 **Slow-moving market**")
                
            except Exception as e:
                st.error(f"An error occurred while processing the data: {str(e)}")
                st.info("Please check your CSV URL and try again.")

else:
    st.info("👈 Use the sidebar to enter a zip code and CSV URL, then load data")
    
    # Instructions
    st.markdown("""
    ### How to use this app:
    
    1. **Enter Zip Code**: Type a 5-digit zip code in the sidebar (default: 11530)
    2. **CSV URL**: Enter the URL of your CSV file (required)
    3. **Number of Rows**: Enter -1 to read the entire file, or specify a number (e.g., 1000)
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
    """)

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit and Plotly*") 