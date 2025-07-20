#!/usr/bin/env python3
"""
Launcher script for Streamlit app with warning suppression
"""
import warnings
import os
import sys

# Suppress urllib3 warning
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')

# Suppress other common warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Set environment variables to reduce noise
os.environ['PYTHONWARNINGS'] = 'ignore'

if __name__ == '__main__':
    # Import and run streamlit
    import streamlit.web.cli as stcli
    
    # Prepare streamlit arguments
    sys.argv = [
        'streamlit',
        'run',
        'streamlit_app.py',
        '--server.headless=true',
        '--browser.gatherUsageStats=false',
        '--server.address=localhost'
    ] + sys.argv[1:]  # Pass through any additional arguments
    
    # Run streamlit
    sys.exit(stcli.main())