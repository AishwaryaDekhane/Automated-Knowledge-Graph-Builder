import requests     #To make HTTP requests
from bs4 import BeautifulSoup       #To parse HTML content
import time     #To handle delays
import logging      #To log messages
import re       #To handle regular expressions
import pandas as pd     #o create and manipulate DataFrames for saving data to CSV

# Set up basic logging configuration to log messages to the console
logging.basicConfig(filename='./KG.log', level=logging.INFO)

# Function to fetch a webpage with retries and delay
def fetch_webpage(url, retries=3, delay=2):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers) # Send GET request to the URL
            response.raise_for_status()  # Raise an error for bad status codes
            return response.text # Return the HTML content of the webpage
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching the webpage (Attempt {attempt + 1}/{retries}): {e}")
            time.sleep(delay)  # Wait for a specified delay before retrying
    return None

# Function to parse HTML content using BeautifulSoup
def parse_html(content):
    return BeautifulSoup(content, 'html.parser')

# Function to extract data (title, headings, paragraphs) from the parsed HTML
def extract_data(soup):
    data = {'title': [soup.title.string if soup.title else 'No title found']}
    data['headings'] = [heading.text.strip() for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    data['paragraphs'] = [paragraph.text.strip() for paragraph in soup.find_all('p')]
    return data

# Function to save extracted data to a CSV file
def save_to_csv(url, data):
    #create a valid filename
    filename = re.sub(r'\W+', '_', url) + ".csv"
    
    # Add URL to the data
    data['url'] = [url]
    
    # Create a DataFrame with the data
    df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data.items()]))
    
    # Save DataFrame to CSV
    df.to_csv(filename, index=False, encoding='utf-8')
    return filename

# Main function to scrape a website
def scrape_website(url):
    content = fetch_webpage(url)    # Fetch the webpage content
    if content:
        soup = parse_html(content)
        data = extract_data(soup)
        csv_file = save_to_csv(url, data)   # Save extracted data to a CSV file
        return csv_file     # Return the name of the CSV file
    return None     # Return None if fetching the webpage fails

# Main entry point of the script
if __name__ == "__main__":
    url = input("Enter the URL to scrape: ")        # Prompt the user to enter a URL
    csv_file = scrape_website(url)      # Scrape the website and save data to a CSV file
    print(csv_file)
    if csv_file:
        logging.info(f"Data saved to {csv_file}")
    else:
        logging.info("Failed to scrape the website.")
