#!/usr/bin/env python3
import requests
import json
import argparse
from tabulate import tabulate

def get_keyword_suggestions(keyword):
    """Get keyword suggestions from Google Autocomplete"""
    try:
        # Google Autocomplete API endpoint
        url = "http://suggestqueries.google.com/complete/search"
        
        params = {
            'client': 'firefox',  # Using firefox client for JSON response
            'q': keyword,
            'hl': 'en'  # English language
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/91.0'
        }
        
        print(f"Fetching suggestions for: {keyword}")
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data[1] if len(data) > 1 else []
            
            # Get search volume estimate (based on position in suggestions)
            results = []
            for i, suggestion in enumerate(suggestions):
                # Rough volume estimate based on position
                volume = "High" if i < 3 else "Medium" if i < 6 else "Low"
                # Rough competition estimate based on length of query
                competition = "High" if len(suggestion.split()) > 3 else "Medium" if len(suggestion.split()) > 2 else "Low"
                
                results.append({
                    'keyword': suggestion,
                    'volume': volume,
                    'competition': competition,
                    'words': len(suggestion.split())
                })
            
            return results
        else:
            print(f"Error: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching suggestions: {str(e)}")
        return None

def display_results(data, keyword):
    """Display the results in a formatted table"""
    if not data:
        print(f"No suggestions found for keyword: {keyword}")
        return
        
    print(f"\n=== Keyword Research Results for '{keyword}' ===\n")
    
    # Prepare table data
    table_data = []
    for item in data:
        table_data.append([
            item['keyword'],
            item['volume'],
            item['competition'],
            item['words']
        ])
    
    # Display table
    headers = ['Suggested Keyword', 'Est. Volume', 'Est. Competition', 'Word Count']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Display summary
    print("\nSummary:")
    print(f"- Total suggestions found: {len(data)}")
    print(f"- Long-tail keywords (3+ words): {sum(1 for x in data if x['words'] >= 3)}")
    print(f"- Short-tail keywords (1-2 words): {sum(1 for x in data if x['words'] < 3)}")

def main():
    parser = argparse.ArgumentParser(description='Get keyword suggestions and research data')
    parser.add_argument('keyword', help='Keyword to research')
    args = parser.parse_args()
    
    data = get_keyword_suggestions(args.keyword)
    display_results(data, args.keyword)

if __name__ == "__main__":
    main()
