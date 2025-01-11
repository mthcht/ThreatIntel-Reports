import os
import requests
from urllib.parse import urlparse
import PyPDF2
import io
import logging
import re
from PyPDF2 import PdfReader
import time
import json
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    filename="download_reports.log",
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

# Function to sanitize directory names
def sanitize_directory_name(name):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)

# Function to obfuscate IP address in text
def obfuscate_ip(text, ip_address):
    obfuscated_ip = re.sub(r'\d', '*', ip_address)  # Replace all digits with '*'
    return text.replace(ip_address, obfuscated_ip)

# Function to remove side-tags section from JPCERT HTML content
def remove_side_tags_section(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    side_tags_section = soup.find('section', id='side-tags')
    if side_tags_section:
        side_tags_section.decompose()  # Remove the side-tags section
    return str(soup)

# Get the public IP address
try:
    public_ip = requests.get('https://api.ipify.org').text
except requests.RequestException as e:
    logger.error(f"Failed to retrieve public IP address: {e}")
    public_ip = "___UNKNOWN_IP___"

# Define the directories
automated_directory = os.path.abspath(os.getcwd())
output_directory = os.path.abspath(os.path.join(automated_directory, "..", "Intel Reports"))
os.makedirs(output_directory, exist_ok=True)

# Load or create the tracking file
tracking_file = os.path.join(automated_directory, "tracking.json")
if os.path.exists(tracking_file):
    with open(tracking_file, "r") as f:
        tracked_links = json.load(f)
else:
    tracked_links = {}

# Iterate over all .txt files in the automated directory
for txt_file in os.listdir(automated_directory):
    if txt_file.endswith(".txt"):
        txt_file_path = os.path.join(automated_directory, txt_file)
        with open(txt_file_path, "r", encoding="utf-8", errors="ignore") as f:
            sorted_links = [line.strip() for line in f.readlines()]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

        # Create directories and download content
        for link in sorted_links:
            if link in tracked_links and tracked_links[link].get("status") == "processed":
                logger.info(f"Link {link} has already been processed, skipping...")
                continue

            parsed_url = urlparse(link)
            domain = sanitize_directory_name(parsed_url.netloc.replace(".", "_"))
            path = sanitize_directory_name(parsed_url.path.strip("/").replace("/", "_"))
            if not path:
                path = "root"

            # Create full directories for domain and path without character limits
            domain_dir = os.path.join(output_directory, domain)
            os.makedirs(domain_dir, exist_ok=True)
            link_dir = os.path.join(domain_dir, path)
            os.makedirs(link_dir, exist_ok=True)

            # Save the link to link.md
            link_md_path = os.path.join(link_dir, "link.md")
            with open(link_md_path, "w", encoding="utf-8") as f:
                f.write(f"[Link to the article]({link})\n")

            logger.info(f"Saved link to {link_md_path}")

            # Download the content of the link
            try:
                logger.info(f"Attempting to download content from {link}")
                response = requests.get(link, headers=headers, timeout=10, allow_redirects=True)
                response.raise_for_status()
                content_type = response.headers.get('content-type')

                # Handle possible redirections
                if response.history:
                    logger.warning(f"The link {link} was redirected to {response.url}")
                    link = response.url

                # Determine the file extension based on content type
                if 'application/pdf' in content_type:
                    file_extension = ".pdf"
                    content_path = os.path.join(link_dir, f"content{file_extension}")
                    with open(content_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"Downloaded PDF content and saved to {content_path}")

                    # Extract text from the PDF and save it
                    try:
                        pdf_reader = PdfReader(io.BytesIO(response.content))
                        extracted_text = ""
                        for page in pdf_reader.pages:
                            extracted_text += page.extract_text() + "\n"
                        extracted_text = obfuscate_ip(extracted_text, public_ip)  # Obfuscate the IP address
                        text_path = os.path.join(link_dir, "txt_content_from_pdf_extracted.txt")
                        with open(text_path, "w", encoding="utf-8") as f:
                            f.write(extracted_text)
                        logger.info(f"Extracted text from PDF and saved to {text_path}")
                    except PyPDF2.errors.PdfReadError as e:
                        logger.error(f"Failed to extract text from PDF {link}: {e}")
                        tracked_links[link] = {"status": "failed", "reason": str(e)}
                        continue
                else:
                    file_extension = ".txt"
                    content_path = os.path.join(link_dir, f"content{file_extension}")
                    text_content = response.text

                    # Remove side-tags section if the link is from JPCERT
                    if "blogs.jpcert.or.jp" in parsed_url.netloc:
                        text_content = remove_side_tags_section(text_content)

                    text_content = obfuscate_ip(text_content, public_ip)  # Obfuscate the IP address in HTML text content
                    with open(content_path, "w", encoding="utf-8") as f:
                        f.write(text_content)
                    logger.info(f"Downloaded HTML content and saved to {content_path}")

                # Mark the link as processed
                tracked_links[link] = {
                    "domain": domain,
                    "path": path,
                    "content_type": content_type,
                    "status": "processed"
                }

            except requests.exceptions.TooManyRedirects:
                logger.error(f"Too many redirects for {link}, skipping...")
                tracked_links[link] = {"status": "failed", "reason": "Too many redirects"}
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to download {link}: {e}")
                tracked_links[link] = {"status": "failed", "reason": str(e)}
            except Exception as e:
                logger.error(f"An unexpected error occurred for {link}: {e}")
                tracked_links[link] = {"status": "failed", "reason": str(e)}

            # Pause to avoid being blocked by rate limiting
            time.sleep(2)

        logger.info(f"Total unique links processed from {txt_file}: {len(sorted_links)}")

# Save the updated tracking information
with open(tracking_file, "w") as f:
    json.dump(tracked_links, f, indent=4)
