import os
import sys
import json
import argparse
import requests
import logging
import time
import re
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(filename='archive_log.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Function to push to The Internet Archive (Wayback Machine)
def internet_archive(url):
    logging.info("Pushing to the Wayback Machine...")
    # First, check if the URL is already archived
    check_url = f"https://web.archive.org/web/{url}"
    try:
        check_response = requests.get(check_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        if check_response.status_code == 200:
            logging.info(f"URL already archived in Wayback Machine: {check_url}")
            return check_url
        elif check_response.status_code == 404:
            logging.info("URL not found in Wayback Machine, proceeding to save it.")
        else:
            logging.warning(f"Unexpected status code when checking archive status on Wayback Machine: {check_response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Check request failed: {e}")
        return None
    
    # If not already archived, push the URL to Wayback Machine
    save_url = f"https://web.archive.org/save/{url}"
    try:
        response = requests.get(save_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        logging.debug(f"Received response from Wayback Machine: {response.status_code}")
        if response.status_code == 200:
            result = response.headers.get("Content-Location")
            if result:
                archive_url = f"https://web.archive.org{result}"
                logging.info(f"Archived URL: {archive_url}")
                return archive_url
            else:
                logging.warning("Failed to retrieve archive link.")
        else:
            logging.error(f"Failed to archive. Status code: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
    return None

# Function to push to archive.is using its API
def archive_is(url):
    logging.info("Pushing to archive.ph...")
    # First, check if the URL is already archived
    check_url = f"https://archive.ph/{url}"
    try:
        check_response = requests.get(check_url, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        if check_response.status_code == 200:
            logging.info(f"URL already archived in archive.ph: {check_url}")
            return check_url
        elif check_response.status_code == 404:
            logging.info("URL not found in archive.ph, proceeding to save it.")
        else:
            logging.warning(f"Unexpected status code when checking archive status on archive.ph: {check_response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Check request failed: {e}")
        return None
    
    # If not already archived, push the URL to archive.ph
    archive_url = "https://archive.ph/submit/"
    try:
        response = requests.post(archive_url, data={'url': url}, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        logging.debug(f"Received response from archive.is: {response.status_code}")
        if response.status_code == 200:
            final_url = response.url.replace('http://', 'https://')
            logging.info(f"Archived URL: {final_url}")
            return final_url
        else:
            logging.error(f"Failed to archive on archive.is. Status code: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
    return None

# Function to push to Ghost Archive using its service
def ghost_archive(url):
    logging.info("Pushing to Ghost Archive...")
    # First, check if the URL is already archived
    check_url = f"https://ghostarchive.org/search?term={url}"
    try:
        check_response = requests.get(check_url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.59 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        if check_response.status_code == 200:
            try:
                if check_response.text.strip():
                    # Attempt to parse the HTML response
                    soup = BeautifulSoup(check_response.text, 'html.parser')
                    results = soup.find_all('a', href=True)
                    for result in results:
                        if '/archive/' in result['href']:
                            archived_url = f"https://ghostarchive.org{result['href']}"
                            logging.info(f"URL already archived in Ghost Archive: {archived_url}")
                            return archived_url
                    logging.warning("No valid archive link found in the response.")
                else:
                    logging.warning("Empty response received when checking archive status on Ghost Archive.")
            except Exception as e:
                logging.error(f"Failed to parse HTML response from Ghost Archive check: {e}")
        else:
            logging.warning(f"Failed to check archive status on Ghost Archive. Status code: {check_response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Check request failed: {e}")
        return None

    # If not already archived, push the URL to Ghost Archive
    archive_url = "https://ghostarchive.org/archive2"
    payload = {
        'archive': url
    }
    headers = {
        'Host': 'ghostarchive.org',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Not?A_Brand";v="99", "Chromium";v="130"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://ghostarchive.org',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.59 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://ghostarchive.org/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Priority': 'u=0, i'
    }
    try:
        response = requests.post(archive_url, data=payload, headers=headers, timeout=30, allow_redirects=True)
        logging.debug(f"Received response from Ghost Archive: {response.status_code}")

        # Handling the redirect and retrieving the final URL
        if response.status_code == 200:
            archive_link = response.url
            logging.info(f"Archived URL: {archive_link}")
            return archive_link
        elif response.status_code == 404:
            logging.error("Failed to archive on Ghost Archive. The requested resource was not found (404). The service might not support this URL.")
        else:
            logging.error(f"Failed to archive on Ghost Archive. Status code: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")

    return None


# Function to clean URLs (strip markdown links, etc.)
def clean_url(url):
    # Remove markdown link formatting if present
    match = re.match(r'\[.*?\]\((https?://.*?)\)', url)
    if match:
        return match.group(1)
    return url

# Function to find all link.md files and archive the URLs inside
def process_folders(base_path):
    base_path = os.path.abspath(os.path.normpath(base_path.strip('"')))  # Convert to absolute path, normalize, and strip any trailing quotes
    logging.info(f"Starting to process folders in base path: {base_path}")
    if not os.path.exists(base_path):
        logging.error(f"The base path does not exist: {base_path}")
        # Debug to manually list parent directory contents
        parent_dir = os.path.dirname(base_path)
        if os.path.exists(parent_dir):
            logging.debug(f"Listing contents of parent directory: {parent_dir}")
            for item in os.listdir(parent_dir):
                logging.debug(f"Found item in parent directory: {item}")
        return
    for root, _, files in os.walk(base_path):
        logging.debug(f"Walking through directory: {root}")
        if "link.md" in files:
            link_file_path = os.path.join(root, "link.md")
            logging.info(f"Found link.md at {link_file_path}")
            try:
                with open(link_file_path, "r") as link_file:
                    url = link_file.read().strip()
                    if not url:
                        logging.warning(f"No URL found in {link_file_path}")
                        continue
                    # Clean the URL
                    cleaned_url = clean_url(url)
                    logging.info(f"Archiving URL from {link_file_path}: {cleaned_url}")
                    
                    # Check if URL is already archived
                    archived_links_path = os.path.join(root, "archived_links.txt")
                    if os.path.exists(archived_links_path):
                        with open(archived_links_path, "r") as archived_file:
                            if cleaned_url in archived_file.read():
                                logging.info(f"URL already archived locally: {cleaned_url}. Skipping...")
                                continue
                    
                    # Use the new Ghost Archive function
                    archive_result = ghost_archive(cleaned_url)

                    # Write archived links to archived_links.txt in the same folder
                    if archive_result:
                        with open(archived_links_path, "a") as file:
                            file.write(f"ghostarchive: {cleaned_url} -> {archive_result}\n")
                        logging.info(f"Archived links saved to {archived_links_path}")
            except Exception as e:
                logging.error(f"Failed to process {link_file_path}: {e}")

# Main function to handle command line arguments and call archiving functions
def main():
    parser = argparse.ArgumentParser(description="Archive a webpage on multiple online web archives")
    parser.add_argument("--list", action="store_true", default=False, help="Enable this flag if the target is a file with a list of URLs")
    parser.add_argument("--folder", action="store", help="Specify the base folder to search for link.md files and archive their URLs")
    parser.add_argument("target", nargs="?", help="The URL to archive or the path to a list of URLs")
    args = parser.parse_args()

    if args.folder:
        # Clean up the folder path by removing any extra quotes
        folder_path = args.folder.strip('"')
        logging.info(f"Processing folder: {folder_path}")
        process_folders(folder_path)
    else:
        urls = []

        if args.list:
            if not os.path.exists(args.target):
                logging.error("The specified file does not exist.")
                sys.exit(-1)
            try:
                with open(args.target, "r") as file:
                    urls = [line.strip() for line in file if line.strip()]
                logging.info(f"Loaded {len(urls)} URLs from list file: {args.target}")
            except Exception as e:
                logging.error(f"Failed to read URLs from file {args.target}: {e}")
                sys.exit(-1)
        else:
            if args.target:
                urls.append(args.target)
            else:
                logging.error("No target specified.")
                sys.exit(-1)

        for url in urls:
            cleaned_url = clean_url(url)
            logging.info(f"Archiving {cleaned_url}...")

            # Check if URL is already archived
            archived_links_path = "archived_links.txt"
            if os.path.exists(archived_links_path):
                with open(archived_links_path, "r") as archived_file:
                    if cleaned_url in archived_file.read():
                        logging.info(f"URL already archived locally: {cleaned_url}. Skipping...")
                        continue

            # Use the Ghost Archive function
            archive_result = ghost_archive(cleaned_url)

            # Write archived link to archived_links.txt
            if archive_result:
                try:
                    with open(archived_links_path, "a") as file:
                        file.write(f"ghostarchive: {cleaned_url} -> {archive_result}\n")
                    logging.info("Archived links saved to archived_links.txt")
                except Exception as e:
                    logging.error(f"Failed to write archived links for {cleaned_url}: {e}")

if __name__ == "__main__":
    main()
