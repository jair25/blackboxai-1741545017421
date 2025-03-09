#!/usr/bin/env python3
import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pytrends.request import TrendReq
import pandas as pd
from tabulate import tabulate

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("config.json not found. Using default values.")
        return {
            "default_region": "US",
            "default_language": "en-US",
            "timeframe": "today 12-m",
            "category": 0
        }
    except json.JSONDecodeError:
        logger.error("Invalid JSON in config.json. Using default values.")
        return {
            "default_region": "US",
            "default_language": "en-US",
            "timeframe": "today 12-m",
            "category": 0
        }

def get_keyword_data(keyword, config):
    """
    Fetch keyword research data using pytrends with retries
    """
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            # Initialize pytrends with minimal configuration
            pytrends = TrendReq(hl='en-US')
            
            # Add delay between attempts
            time.sleep(retry_delay)
            
            # Build payload with minimal parameters
            pytrends.build_payload(
                kw_list=[keyword],
                timeframe='today 3-m'  # Use shorter timeframe
            )
            
            # Get data one at a time with delays
            interest_df = pytrends.interest_over_time()
            time.sleep(2)
            
            related_queries = pytrends.related_queries()
            time.sleep(2)
            
            regional_interest = pytrends.interest_by_region()
            
            if interest_df is not None or related_queries is not None:
                return {
                    'interest_over_time': interest_df,
                    'related_queries': related_queries[keyword] if keyword in related_queries else None,
                    'regional_interest': regional_interest
                }
                
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            else:
                logger.error("All attempts failed to fetch data")
                return None

def display_results(data, keyword):
    """
    Display the keyword research results in a formatted manner
    """
    if data is None:
        logger.error("No data to display")
        return

    print(f"\n=== Keyword Research Results for '{keyword}' ===\n")

    # Display Related Queries (Top)
    print("\n=== Top Related Keywords ===")
    if data['related_queries'] and hasattr(data['related_queries'], 'top'):
        top_queries = data['related_queries'].top
        if top_queries is not None and not top_queries.empty:
            print(tabulate(top_queries.head(10), headers='keys', tablefmt='grid'))
        else:
            print("No top related queries found")
    else:
        print("No top related queries data available")

    # Display Related Queries (Rising)
    print("\n=== Rising Related Keywords ===")
    if data['related_queries'] and hasattr(data['related_queries'], 'rising'):
        rising_queries = data['related_queries'].rising
        if rising_queries is not None and not rising_queries.empty:
            print(tabulate(rising_queries.head(10), headers='keys', tablefmt='grid'))
        else:
            print("No rising related queries found")
    else:
        print("No rising related queries data available")

    # Display Regional Interest
    print("\n=== Regional Interest ===")
    if not data['regional_interest'].empty:
        regional_data = data['regional_interest'].sort_values(by=keyword, ascending=False).head(10)
        print(tabulate(regional_data, headers='keys', tablefmt='grid'))
    else:
        print("No regional interest data available")

    # Display Interest Over Time Summary
    print("\n=== Interest Over Time Summary ===")
    if not data['interest_over_time'].empty:
        interest_summary = data['interest_over_time'][keyword].describe()
        print(tabulate([[k, v] for k, v in interest_summary.items()], 
                      headers=['Metric', 'Value'], 
                      tablefmt='grid'))
    else:
        print("No interest over time data available")

def main():
    """Main function to run the keyword research tool"""
    parser = argparse.ArgumentParser(description='Keyword Research Tool using Google Trends')
    parser.add_argument('keyword', help='The keyword to research')
    parser.add_argument('--region', help='Region to analyze (default: from config)')
    parser.add_argument('--timeframe', help='Timeframe to analyze (default: from config)')
    args = parser.parse_args()

    # Load configuration
    config = load_config()
    
    # Override config with command line arguments if provided
    if args.region:
        config['default_region'] = args.region
    if args.timeframe:
        config['timeframe'] = args.timeframe

    logger.info(f"Starting keyword research for: {args.keyword}")
    
    # Get keyword data
    data = get_keyword_data(args.keyword, config)
    
    # Display results
    display_results(data, args.keyword)

if __name__ == "__main__":
    main()
