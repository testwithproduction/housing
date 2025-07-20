# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Streamlit web application for visualizing housing market data from CSV files. The application:
- Reads CSV files from URLs using pandas
- Filters data by multiple zip codes
- Displays interactive charts showing housing market trends
- Provides market analysis and insights
- Supports caching for performance optimization

## Development Commands

### Running the Application
```bash
streamlit run streamlit_app.py
```
The app will be available at `http://localhost:8501`

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Python Dependencies
- streamlit>=1.28.0 (web framework)
- pandas>=2.0.0 (data processing)
- plotly>=5.15.0 (interactive charts)
- requests>=2.31.0 (HTTP requests)
- streamlit-tags>=1.2.7 (tag input component)

## Code Architecture

### Main Application Structure
- **`streamlit_app.py`**: Single main file containing all application logic (~714 lines)
- **Key Functions**:
  - `load_and_filter_csv_for_zipcodes_with_individual_cache()`: Efficient CSV loading with individual zip code caching
  - Chart creation functions: `create_price_trend_chart()`, `create_days_on_market_chart()`, `create_price_per_sqft_chart()`, etc.
  - Display functions: `display_summary_metrics()`, `display_market_insights()`, `display_all_charts()`

### Data Processing Architecture
- **Streaming CSV Processing**: Uses pandas chunked reading (10,000 rows per chunk)
- **Individual Zip Code Caching**: Each zip code is cached separately using file modification time and size as cache keys
- **Multi-Zip Code Support**: Processes multiple zip codes in parallel, only loading uncached data
- **Date Conversion**: Converts `month_date_yyyymm` format to datetime for visualization

### Required CSV Data Format
The application expects CSV files with these columns:
- `postal_code`: 5-digit zip codes
- `month_date_yyyymm`: Date in YYYYMM format (e.g., 202301)
- `median_listing_price`: Median listing prices
- `median_days_on_market`: Days properties stay on market
- `median_listing_price_per_square_foot`: Price per square foot
- `median_listing_price_per_square_foot_yy`: Year-over-year price change (optional)
- `median_square_feet`: Median square footage (optional)

### Chart Types and Features
- **Price Trend Charts**: Line charts with yearly average reference lines and color-coded markers
- **Market Speed Charts**: Days on market with market condition analysis
- **Year-over-Year Charts**: Bar charts with positive/negative color coding
- **Square Footage Charts**: Median size trends with yearly averages
- All charts include interactive hover details and responsive design

### Performance Optimizations
- **File-level caching** based on HTTP headers (file size + last modified time)
- **Individual zip code caching** prevents re-processing of already loaded data
- **Chunk-based processing** for large CSV files
- **Row limiting** option for very large datasets
- **Progress indicators** for user feedback during data loading

## Key Implementation Details

### Cache Strategy
Cache keys format: `"csv_data_{mod_time}_{file_size}_{zip_code}_{rows_limit}"`
- Invalidates cache when source file changes
- Each zip code cached independently
- Reduces redundant processing across sessions

### Multi-Zip Code Interface
- Uses `streamlit-tags` for zip code input
- Creates separate tabs for each zip code
- Parallel processing of multiple zip codes
- Validates 5-digit zip code format

### Chart Color Coding
- Green markers: Above yearly average
- Red markers: Below yearly average
- Yearly average lines: Gray dotted lines with annotations
- Bar charts: Red for negative values, green for positive

## Error Handling
- Network request timeouts and retries
- CSV format validation
- Missing column handling
- Empty dataset handling for specific zip codes
- Input validation for zip codes and row limits