#!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime, timedelta
from tabulate import tabulate

def get_trends_data(keyword):
    """
    Get keyword trends data using direct API request
    """
    try:
        # Format dates
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        # Prepare request URL
        url = "https://trends.google.com/trends/api/explore"
        
        # Parameters for the request
        params = {
            'hl': 'en-US',
            'tz': '-120',
            'req': json.dumps({
                'comparisonItem': [{
                    'keyword': keyword,
                    'geo': '',
                    'time': f'{start_date.strftime("%Y-%m-%d")} {end_date.strftime("%Y-%m-%d")}'
                }],
                'category': 0,
                'property': ''
            }),
            'tz': '-120'
        }
        
        # Make request with custom headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers)
        
        # Check if request was successful
        if response.status_code == 200:
            # Remove leading characters that aren't part of the JSON
            json_data = response.text[5:]
            data = json.loads(json_data)
            
            # Extract and format the data
            result = {
                'keyword': keyword,
                'time_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                'interest': data.get('widgets', [{}])[0].get('request', {}).get('restriction', {}).get('geo', {})
            }
            
            return result
            
        else:
            print(f"Error: Request failed with status code {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None

def display_results(data):
    """
    Display the keyword research results
    """
    if data is None:
        print("No data available")
        return
        
    print("\n=== Keyword Research Results ===\n")
    print(f"Keyword: {data['keyword']}")
    print(f"Time Range: {data['time_range']}")
    print("\nGeographic Interest:")
    
    if data['interest']:
        table_data = [[region, score] for region, score in data['interest'].items()]
        print(tabulate(table_data, headers=['Region', 'Interest Score'], tablefmt='grid'))
    else:
        print("No geographic interest data available")

def main():
    """
    Main function to run the keyword research tool
    """
    keyword = input("Enter a keyword to research: ")
    print(f"\nResearching keyword: {keyword}")
    
    # Add delay to avoid rate limiting
    time.sleep(1)
    
    data = get_trends_data(keyword)
    display_results(data)

if __name__ == "__main__":
    main()
