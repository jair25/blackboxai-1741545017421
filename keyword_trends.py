#!/usr/bin/env python3
import requests
import json
import argparse
from datetime import datetime, timedelta
from tabulate import tabulate

def get_keyword_data(keyword):
    """Get keyword trend data"""
    try:
        # Use a simpler API endpoint
        url = f"https://trends.google.com/trends/api/dailytrends"
        params = {
            'hl': 'en-US',
            'geo': 'US',
            'ed': datetime.now().strftime('%Y%m%d')
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"Fetching trends data for: {keyword}")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            # Clean the response data
            data = response.text[5:]  # Remove ")]}'"
            json_data = json.loads(data)
            
            # Extract trending searches
            trending = json_data.get('default', {}).get('trendingSearchesDays', [])
            
            # Filter results related to our keyword
            related_trends = []
            for day in trending:
                searches = day.get('trendingSearches', [])
                for search in searches:
                    title = search.get('title', {}).get('query', '').lower()
                    if keyword.lower() in title:
                        related_trends.append({
                            'query': title,
                            'traffic': search.get('formattedTraffic', 'N/A'),
                            'related': [topic.get('query') for topic in search.get('relatedQueries', [])]
                        })
            
            return related_trends
            
        else:
            print(f"Error: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None

def display_results(data, keyword):
    """Display the results in a formatted table"""
    if not data:
        print(f"No trending data found for keyword: {keyword}")
        return
        
    print(f"\n=== Trend Results for '{keyword}' ===\n")
    
    # Prepare table data
    table_data = []
    for trend in data:
        related = ', '.join(trend['related'][:3]) if trend['related'] else 'None'
        table_data.append([
            trend['query'],
            trend['traffic'],
            related
        ])
    
    # Display table
    headers = ['Search Term', 'Traffic', 'Related Queries']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))

def main():
    parser = argparse.ArgumentParser(description='Get keyword trend data')
    parser.add_argument('keyword', help='Keyword to research')
    args = parser.parse_args()
    
    data = get_keyword_data(args.keyword)
    display_results(data, args.keyword)

if __name__ == "__main__":
    main()
