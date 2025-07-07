# 🏠 Housing Data Dashboard

A Streamlit application that reads CSV files from URLs using pandas, filters data by zip code, and displays interactive housing market trends and insights.

## ✨ Features

- **📊 Simple CSV Reading**: Uses pandas to read CSV files directly from URLs
- **🏘️ Zip Code Filtering**: Filter housing data by specific zip codes
- **📈 Interactive Charts**: Beautiful line charts showing housing market trends over time
- **📋 Data Display**: Clean table view of filtered data
- **📊 Summary Statistics**: Key metrics with trend indicators
- **🔍 Market Insights**: Automated analysis of market conditions
- **⚡ Real-time Progress**: Progress indicators during data processing
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd housing
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser**
   - The app will automatically open at `http://localhost:8501`
   - If it doesn't open automatically, navigate to the URL shown in your terminal

## 📖 How to Use

### Basic Usage

1. **Enter Zip Code**: Type a 5-digit zip code in the sidebar (default: 11530)
2. **Enter CSV URL**: Provide the URL of your CSV file
3. **Load Data**: Click the "Load Data" button
4. **View Results**: Explore the charts, data table, and insights

### CSV Data Requirements

1. **Prepare Your CSV File**: Ensure it has the required columns:
   - `postal_code`: 5-digit zip codes
   - `month_date_yyyymm`: Date in YYYYMM format (e.g., 202301 for January 2023)
   - `median_listing_price`: Median listing prices
   - `median_days_on_market`: Days properties stay on market
   - `median_listing_price_per_square_foot`: Price per square foot

2. **Host Your CSV**: Upload your CSV file to a web server or cloud storage:
   - **Google Drive**: Upload and make it publicly accessible, then get the sharing link
   - **Dropbox**: Upload and create a public link
   - **GitHub**: Upload to a repository and use the raw file URL
   - **AWS S3**: Upload to a public bucket
   - **Any web server**: Host the CSV file and provide the direct download URL

3. **Get the URL**: Copy the direct download URL for your CSV file

4. **Use in App**: 
   - Enter the URL in the "CSV URL" field in the sidebar
   - Enter your desired zip code
   - Click "Load Data"

### Example CSV Format

```csv
postal_code,month_date_yyyymm,median_listing_price,median_days_on_market,median_listing_price_per_square_foot
11530,202301,450000,45,250
11530,202302,460000,42,255
11530,202303,470000,40,260
11531,202301,480000,50,245
11531,202302,485000,48,248
```

## 🏗️ Architecture

### Files Structure

```
housing/
├── app.py                    # Main Streamlit application
├── streaming_csv_reader.py   # Streaming CSV processing logic
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── LICENSE                  # License information
```

### Key Components

1. **`app.py`**: Main Streamlit interface with charts and data display
2. **Simple pandas CSV reading**: Direct CSV loading and filtering

## 🔧 Technical Details

### CSV Reading Implementation

The app uses pandas to read CSV files directly:

- **Direct Loading**: Reads the entire CSV file into memory
- **Simple Filtering**: Filters data by zip code after loading
- **Progress Tracking**: Simple progress indicators during loading
- **Error Handling**: Graceful handling of network issues and malformed data

### Performance Characteristics

- **Fast Loading**: Uses pandas' optimized CSV reading
- **Simple Processing**: Straightforward filtering approach
- **Memory Usage**: Loads entire file into memory (suitable for most CSV files)
- **Easy Maintenance**: Simple, readable code

## 📊 Data Visualization

The app creates three interactive line charts:

1. **Median Listing Price**: Shows price trends over time
2. **Median Days on Market**: Displays market speed trends
3. **Median Price per Square Foot**: Shows price density trends

### Chart Features

- **Interactive**: Hover for detailed values
- **Responsive**: Automatically adjusts to screen size
- **Professional**: Clean, publication-ready styling
- **Accessible**: Clear labels and color coding

## 🎯 Market Insights

The app provides automated market analysis:

### Price Trends
- **Appreciating Market**: When prices are increasing
- **Depreciating Market**: When prices are decreasing
- **Percentage Change**: Total price change over the period

### Market Speed
- **Fast-moving Market**: Properties sell in <30 days
- **Moderate Market**: Properties sell in 30-60 days
- **Slow-moving Market**: Properties take >60 days to sell

## 🛠️ Customization

### Modifying the App

1. **Add New Metrics**: Edit the `required_columns` list in `streaming_csv_reader.py`
2. **Change Chart Styles**: Modify the Plotly chart configurations in `app.py`
3. **Add New Insights**: Extend the market insights section in `app.py`

### Configuration Options

- **Chunk Size**: Adjust `chunk_size` in `StreamingCSVReader` for different memory/performance trade-offs
- **Progress Updates**: Modify the progress update frequency in the streaming logic
- **Chart Colors**: Customize the color scheme in the Plotly chart definitions

## 🐛 Troubleshooting

### Common Issues

1. **"No data found for zip code"**
   - Check that your zip code exists in the CSV file
   - Verify the zip code format (5 digits)

2. **"Error fetching CSV from URL"**
   - Ensure the URL is accessible
   - Check that the URL points to a CSV file
   - Verify the CSV file format matches requirements

3. **"Memory error"**
   - The streaming implementation should handle large files
   - If issues persist, try reducing the chunk size

4. **"Invalid CSV format"**
   - Verify your CSV has the required column headers
   - Check for proper CSV formatting (commas, quotes, etc.)

### Getting Help

- Check the console output for detailed error messages
- Verify your CSV file format matches the requirements
- Ensure all dependencies are installed correctly

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the error messages in the console
3. Verify your CSV file format and URL accessibility

---

**Built with ❤️ using Streamlit and Plotly** 