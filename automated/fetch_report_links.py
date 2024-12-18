import feedparser
import requests
from bs4 import BeautifulSoup
import re
import json
import time

# RSS feed URLs
rss_urls = [
    "https://blog.talosintelligence.com/rss/",
    "https://unit42.paloaltonetworks.com/feed/",
    "https://www.cisa.gov/cybersecurity-advisories/all.xml",
    "https://feeds.feedburner.com/threatintelligence/pvexyqv7v0v",
    "https://thedfirreport.com/feed/",
    "https://blog.qualys.com/vulnerabilities-threat-research/feed",
    "https://cybersecuritynews.com/feed/",
    "https://outpost24.com/blog/category/research-and-threat-intel/feed/",
    "https://securelist.com/threat-category/apt-targeted-attacks/feed/",
    "https://securityaffairs.com/category/apt/feed",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.elastic.co/security-labs/rss/feed.xml",
    "https://www.welivesecurity.com/en/rss/feed/",
    "https://cert.gov.ua/api/articles/rss",
    "https://www.nist.gov/blogs/cybersecurity-insights/rss.xml",
    "https://threatpost.com/feed/",
    "https://www.bitdefender.com/nuxt/api/en-us/rss/labs/",
    "https://research.checkpoint.com/feed/",
    "https://feeds.feedburner.com/feedburner/Talos",
    "https://blog.cloudflare.com/tag/security/rss",
    "https://www.microsoft.com/en-us/security/blog/topic/threat-intelligence/feed",
    "https://feeds.feedburner.com/akamai/blog",
    "https://blog.sekoia.io/feed/",
    "http://www.hexacorn.com/blog/feed/",
    "https://posts.specterops.io/feed",
    "https://www.redcanary.co/feed/",
    "https://news.sophos.com/en-us/category/threat-research/feed/",
    "https://www.virusbulletin.com/rss",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.sentinelone.com/labs/feed/",
    "http://feeds.trendmicro.com/TrendMicroSimplySecurity",
    "https://www.volexity.com/blog/feed/",
    "https://harfanglab.io/insidethelab/feed/",
    "https://asec.ahnlab.com/en/category/apt-en/feed/",
    "https://asec.ahnlab.com/en/category/phishing-scam-en/feed",
    "https://asec.ahnlab.com/en/category/trend-en/feed",
    "https://asec.ahnlab.com/en/category/cert-en/feed",
    "https://www.mcafee.com/blogs/other-blogs/mcafee-labs/feed/",
    "https://sed-cms.broadcom.com/rss/v1/blogs/rss.xml",
    "https://threatconnect.com/blog/feed/",
    "https://cert.gov.ua/api/articles/rss",
    "https://www.cert.se/feed.rss",
    "https://www.cert.si/en/category/news/feed/",
    "https://cert.pl/en/rss.xml",
    "https://feeds.english.ncsc.nl/news.rss",
    "https://cert.lv/en/feed/rss/all",
    "https://blogs.jpcert.or.jp/en/atom.xml",
    "https://www.cirt.gov.bd/feed/",
    "https://www.microsoft.com/en-us/security/blog/feed/",
    "https://www.infostealers.com/info-stealers-reports/feed/",
    "https://medium.com/feed/@simone.kraus",
    "https://googleprojectzero.blogspot.com/feeds/posts/default?alt=rss",
    "https://www.securityweek.com/feed/",
    "https://www.genians.co.kr/blog/threat_intelligence/rss.xml",
    "https://medium.com/feed/@gi7w0rm",
    "https://www.intrinsec.com/feed/",
    "https://www.huntress.com/blog/rss.xml",
    "https://isc.sans.edu/rssfeed.xml",
    "https://medium.com/feed/@bi-zone",
    "https://www.ic3.gov/CSA/rss",
    "https://any.run/cybersecurity-blog/category/malware-analysis/feed/",
    "https://www.malwarebytes.com/blog/feed/index.xml",
    "https://www.binarydefense.com/feed/",
    "https://fieldeffect.com/blog/rss.xml",
    "https://blog.avast.com/rss.xml",
    "https://blog.google/threat-analysis-group/rss/",
    "https://blog.group-ib.com/rss.xml",
    "https://news.drweb.com/rss/get/?c=9",
    "https://www.malwaretech.com/feed",
    "https://www.trustwave.com/en-us/resources/blogs/spiderlabs-blog/rss.xml",
    "https://krebsonsecurity.com/feed/"
    #"https://www.cert.ssi.gouv.fr/feed/"

]

# Non-RSS blog URLs
non_rss_urls = [
    "https://www.proofpoint.com/us/blog/threat-insight#",
    "https://www.reversinglabs.com/blog/tag/threat-research",
    "https://www.splunk.com/en_us/blog/author/secmrkt-research.html",
    "https://www.jpcert.or.jp/english/update.html",
    "https://www.forcepoint.com/blog/x-labs",
    "https://www.crowdstrike.com/en-us/blog/category.counter-adversary-operations/",
    "https://threatlabz.zscaler.com/blogs",
    "https://www.deepinstinct.com/blog",
    "https://www-eclecticiq-com.sandbox.hs-sites.com/blog?type=intelligence-research#overview"
    #https://hunt.io/blog
    #"https://claroty.com/team82/research/"
    #"https://www.nccgroup.com/us/research-blog/?resource=18345&category=18146#hub"
    #"https://www.security.com/threat-intelligence"
    #"https://www.orangecyberdefense.com/global/blog?tx_solr%5Bfilter%5D%5B0%5D=tags%3AIntelligence-led+Security"
    #"https://blogs.blackberry.com/en/home"
    #"https://www.seqrite.com/blog/category/technical/"
    #"https://blog.morphisec.com/topic/threat-research"
    #todo...
    
]

# Scraping Functions

def scrape_reversinglabs_blog(blog_url, file):
    print(f"Scraping ReversingLabs Threat Research blog: {blog_url}")
    try:
        response = requests.get(blog_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate blog article links
        for article in soup.select('div.blog__listing-item article.blog__item h3 a'):
            href = article['href']
            full_url = href if href.startswith("http") else f"https://www.reversinglabs.com{href}"
            print(f"Found link: {full_url}")
            file.write(full_url + '\n')
    except requests.RequestException as e:
        print(f"Failed to scrape {blog_url}: {e}")

def scrape_akamai_rss(feed_url, file):
    print(f"Parsing Akamai RSS feed: {feed_url}")
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'xml')

        # Locate <item> tags and extract article links that match the specified pattern
        for item in soup.find_all('item'):
            link_tag = item.find('link')
            if link_tag:
                article_link = link_tag.get_text(strip=True)
                if article_link.startswith("https://www.akamai.com/blog/security"):
                    print(f"Found Akamai security article link: {article_link}")
                    file.write(article_link + '\n')

    except requests.RequestException as e:
        print(f"Failed to scrape {feed_url}: {e}")

def scrape_splunk_blog(blog_url, file):
    print(f"Scraping Splunk blog: {blog_url}")
    try:
        response = requests.get(blog_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for item_div in soup.find_all('div', class_='item'):
            a_tag = item_div.find('a', href=True)
            if a_tag and a_tag['href'].startswith("https://www.splunk.com/en_us/blog/"):
                print(f"Found link: {a_tag['href']}")
                file.write(a_tag['href'] + '\n')
    except requests.RequestException as e:
        print(f"Failed to scrape {blog_url}: {e}")

def scrape_jpcert_blog(blog_url, file):
    print(f"Scraping JPCERT blog: {blog_url}")
    try:
        response = requests.get(blog_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Regex pattern to match links with a date like /en/2024/
        date_pattern = re.compile(r'/en/\d{4}/')

        for link in soup.select('table.table_list td a, ul.list a'):
            if link and 'href' in link.attrs:
                href = link['href']
                full_url = href if href.startswith("http") else f"https://www.jpcert.or.jp{href}"
                
                # Only write links that match the date pattern
                if date_pattern.search(full_url):
                    print(f"Found dated link: {full_url}")
                    file.write(full_url + '\n')
    except requests.RequestException as e:
        print(f"Failed to scrape {blog_url}: {e}")

def scrape_forcepoint_blog(blog_url, file):
    print(f"Scraping Forcepoint X-Labs blog: {blog_url}")
    try:

        response = requests.get(blog_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        unique_links = set()  # Set to store unique links

        # Find article links with specified structure
        for link in soup.select('a[href^="/blog/x-labs/"]'):
            href = link['href']
            full_url = href if href.startswith("http") else f"https://www.forcepoint.com{href}"

            # Exclude the unwanted link and remove duplicates
            if full_url != "https://www.forcepoint.com/blog/x-labs/x-labs" and full_url not in unique_links:
                unique_links.add(full_url)
                print(f"Found link: {full_url}")
                file.write(full_url + '\n')

    except requests.RequestException as e:
        print(f"Failed to scrape {blog_url}: {e}")

def scrape_qualys_rss(feed_url, file):
    print(f"Parsing Qualys RSS feed: {feed_url}")
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'xml')

        # Locate <item> tags and extract article links
        for item in soup.find_all('item'):
            link_tag = item.find('link')
            if link_tag:
                article_link = link_tag.get_text(strip=True)
                print(f"Found Qualys article link: {article_link}")
                file.write(article_link + '\n')

    except requests.RequestException as e:
        print(f"Failed to scrape {feed_url}: {e}")

def scrape_proofpoint_blog(blog_url, file):
    print(f"Scraping Proofpoint Threat Insight blog: {blog_url}")
    try:
        response = requests.get(blog_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        unique_links = set()  # Set to store unique links

        # Find article links with specified structure
        for item in soup.select('div.blog-mosaic__item'):
            link_tag = item.find('a', class_='blog-mosaic__link', href=True)
            title_tag = item.find('div', class_='blog-mosaic__title')
            if link_tag and title_tag:
                href = link_tag['href']
                full_url = href if href.startswith("http") else f"https://www.proofpoint.com{href}"
                title = title_tag.get_text(strip=True)

                # Exclude duplicates
                if full_url not in unique_links:
                    unique_links.add(full_url)
                    print(f"Found link: {full_url} with title: {title}")
                    file.write(f"{full_url}\n")

    except requests.RequestException as e:
        print(f"Failed to scrape {blog_url}: {e}")

def scrape_crowdstrike_blog(blog_url, file):
    print(f"Scraping CrowdStrike Counter-Adversary Operations blog: {blog_url}")
    try:
        response = requests.get(blog_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        unique_links = set()  # Set to store unique links

        # Find article links with specified structure
        for dd in soup.select('dl.vertical_dropdown_list dd'):
            a_tag = dd.find('a', href=True)
            title_tag = dd.find('div', class_='title')
            if a_tag and title_tag:
                href = a_tag['href']
                full_url = href if href.startswith("http") else f"https://www.crowdstrike.com{href}"
                title = title_tag.get_text(strip=True)

                # Exclude duplicates
                if full_url not in unique_links:
                    unique_links.add(full_url)
                    print(f"Found link: {full_url} with title: {title}")
                    file.write(f"{full_url}\n")

    except requests.RequestException as e:
        print(f"Failed to scrape {blog_url}: {e}")

def scrape_zscaler_blog_graphql(api_url, file):
    # not working for research papers :/ - try again later..

    print(f"Scraping Zscaler ThreatLabz blog via GraphQL API: {api_url}")

    # Define GraphQL query to get the blog posts
    graphql_query = {
        "query": """
        {
            blogsGraphql {
                entities {
                    nid
                    title
                    path {
                        alias
                    }
                    fieldCoverImage {
                        entity {
                            url
                        }
                    }
                    entityMetatags {
                        key
                        value
                    }
                }
            }
        }
        """
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    }

    try:
        # Make the POST request to the GraphQL API
        response = requests.post(api_url, headers=headers, json=graphql_query, timeout=10)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        unique_links = set()  # Set to store unique links

        # Extract blog posts information
        posts = data.get('data', {}).get('blogsGraphql', {}).get('entities', [])
        for post in posts:
            title = post.get('title')
            path = post.get('path', {}).get('alias')
            if path and title:
                full_url = f"https://www.zscaler.com{path}"
                if full_url not in unique_links:
                    unique_links.add(full_url)
                    print(f"Found link: {full_url} with title: {title}")
                    file.write(f"{full_url} - {title}\n")

            # Check for additional metadata to find specific URLs
            metatags = post.get('entityMetatags', [])
            for tag in metatags:
                if tag.get('key') in ['og:url', 'canonical']:
                    full_url = tag.get('value')
                    if full_url and full_url not in unique_links:
                        unique_links.add(full_url)
                        print(f"Found link: {full_url} with title: {title}")
                        file.write(f"{full_url}\n")

                # Specifically look for the 'path' alias if 'og:url' or 'canonical' is missing
                elif path and tag.get('key') == 'og:title':
                    full_url = f"https://www.zscaler.com{path}"
                    if full_url not in unique_links:
                        unique_links.add(full_url)
                        print(f"Found link: {full_url} with title: {title}")
                        file.write(f"{full_url}\n")

    except requests.RequestException as e:
        print(f"Failed to scrape {api_url}: {e}")

def scrape_deepinstinct_blog(blog_url, file):
    # not working :/ try again later
    print(f"Scraping Deep Instinct blog: {blog_url}")

    # Define headers for the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }

    graphql_endpoint = "https://www.deepinstinct.com/_next/data/{build_id}/en/blog.json?pid=blog"

    try:
        # Make a GET request to the blog URL to get the build ID
        response = requests.get(blog_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Find the build ID in the page source
        build_id_match = re.search(r'"buildId":"([^"]+)"', response.text)
        if not build_id_match:
            print("Failed to find build ID.")
            return

        build_id = build_id_match.group(1)
        graphql_url = graphql_endpoint.format(build_id=build_id)

        # Make the GET request to the GraphQL API endpoint
        response = requests.get(graphql_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        unique_links = set()  # Set to store unique links

        # Extract blog posts information
        for block in data.get('pageProps', {}).get('landing', {}).get('processed_blocks', []):
            if 'content' in block:
                content = block['content']
                if 'ctaSecondary' in content:
                    cta_secondary = content['ctaSecondary']
                    if 'url' in cta_secondary and cta_secondary['url'].startswith("/blog"):
                        full_url = f"https://www.deepinstinct.com{cta_secondary['url']}"
                        if full_url not in unique_links:
                            unique_links.add(full_url)
                            print(f"Found link: {full_url}")
                            file.write(f"{full_url}\n")
    
    except requests.RequestException as e:
        print(f"Failed to scrape {blog_url}: {e}")

def scrape_blackberry_blog(api_url, file):
    # not working :/ try again later
    print(f"Scraping BlackBerry blog via GraphQL API: {api_url}")

    # Define headers for the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }

    try:
        # Make the GET request to the GraphQL API endpoint
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        unique_links = set()  # Set to store unique links

        # Extract blog posts information
        for blog in data.get('blogFeed', {}).get('blogList', []):
            if 'url' in blog:
                full_url = f"https://blogs.blackberry.com{blog['url']}"
                if full_url not in unique_links:
                    unique_links.add(full_url)
                    print(f"Found link: {full_url}")
                    file.write(f"{full_url}\n")
    
    except requests.RequestException as e:
        print(f"Failed to scrape {api_url}: {e}")

def scrape_mcafee_rss(feed_url, file, retries=3, delay=5):
    """
    Parses the McAfee RSS feed with retry logic and custom headers.
    
    :param feed_url: The URL of the McAfee RSS feed
    :param file: The file object where links will be written
    :param retries: Number of retry attempts if the request fails
    :param delay: Delay in seconds between retries
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }
    for attempt in range(retries):
        try:
            print(f"Parsing McAfee feed (Attempt {attempt + 1}/{retries}): {feed_url}")
            response = requests.get(feed_url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an error if the request fails
            
            # Parse the feed content directly
            feed = feedparser.parse(response.content)
            for entry in feed.entries:
                if hasattr(entry, 'link'):
                    print(f"Found McAfee entry: {entry.link}")
                    file.write(entry.link + '\n')
            return  # Exit after a successful parse
        except requests.RequestException as e:
            print(f"Error parsing McAfee feed on attempt {attempt + 1}: {e}")
            if attempt < retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                print(f"Failed to fetch the McAfee feed after {retries} attempts.")

def scrape_eclecticiq_blog(url,file):
    """
    Scrapes the EclecticIQ blog page for articles under the "Intelligence Research" section.
    Extracts the publication date, title, and URL of each article.
    
    :param file: The file object where links will be written
    :param url: The URL of the EclecticIQ blog page
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error if the request fails
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.find_all('div', class_='relative flex flex-col items-start')
        for article in articles:
            date = article.find('div', class_='mt-1 font-bold text-white/50')
            title = article.find('h3', class_='faux-h6 text-xl leading-tight')
            link = article.find('a', href=True)
            
            if date and title and link:
                date_text = date.text.strip()
                title_text = title.text.strip()
                link_url = link['href'].strip()
                
                # Ensure full URL format
                if not link_url.startswith('http'):
                    link_url = 'https://blog.eclecticiq.com' + link_url

                print(f"Found article: {title_text} ({date_text}) - {link_url}")
                file.write(f"{link_url}\n")

    except requests.RequestException as e:
        print(f"Error scraping EclecticIQ blog: {e}")


# Main Script

file_name = "latest_reports_links.txt"
imported_links_file = "..\\imported\\unique_links.txt"
manually_added_links = "manually_added_to_import.txt"
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

with open(file_name, 'w') as file:

    # Parse RSS feeds
    for rss_url in rss_urls:
        if "qualys.com" in rss_url:
            scrape_qualys_rss(rss_url, file)
        elif "feeds.feedburner.com/akamai" in rss_url:
            scrape_akamai_rss(rss_url, file)
        elif "sed-cms.broadcom.com/rss" in rss_url:
            print(f"Parsing Symantec feed: {rss_url}")
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                if hasattr(entry, 'link') and '/threat-intelligence/' in entry.link:
                    print(f"Found entry: {entry.link}")
                    file.write(entry.link + '\n')
        elif "threatconnect.com/blog/feed/" in rss_url:
            print(f"Parsing threatconnect feed: {rss_url}")
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                if hasattr(entry, 'link') and hasattr(entry, 'tags'):
                    for tag in entry.tags:
                        if 'Threat Intelligence Operations' in tag.term:
                            print(f"Found entry: {entry.link}")
                            file.write(entry.link + '\n')
        elif "mcafee.com/blogs/other-blogs/mcafee-labs/feed" in rss_url:
            scrape_mcafee_rss(rss_url, file)
        else:
            print(f"Parsing RSS feed: {rss_url}")
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                if hasattr(entry, 'link'):
                    print(f"Found entry: {entry.link}")
                    file.write(entry.link + '\n')
    
    # Scrape non-RSS sites
    for blog_url in non_rss_urls:
        if "splunk.com" in blog_url:
            scrape_splunk_blog(blog_url, file)
        elif "jpcert.or.jp" in blog_url:
            scrape_jpcert_blog(blog_url, file)
        elif "forcepoint.com" in blog_url:
            scrape_forcepoint_blog(blog_url, file)
        elif "crowdstrike.com/en-us/blog/" in blog_url:
            scrape_crowdstrike_blog(blog_url, file)
        elif "www.proofpoint.com" in blog_url:
            scrape_proofpoint_blog(blog_url, file)
        elif "threatlabz.zscaler.com/blogs" in blog_url:
            # missing research papers - check later
            scrape_zscaler_blog_graphql("https://threatlabz.zscaler.com/api/graphql/", file)
        elif "reversinglabs.com/blog/tag/threat-research" in blog_url:
            scrape_reversinglabs_blog(blog_url, file)
        elif "www-eclecticiq-com" in blog_url:
            scrape_eclecticiq_blog(blog_url, file)
        #elif "" in blog_url:
        #    scrape_blackberry_blog("https://blogs.blackberry.com/en.model.json", file)
        #elif "www.deepinstinct.com/blog" in blog_url:
        #    scrape_deepinstinct_blog(blog_url, file)

# Append links from the imported file without duplicates
try:
    with open(imported_links_file, 'r') as imported_file:
        imported_links = set(imported_file.read().splitlines())
    with open(manually_added_links, 'r', encoding='utf-8', errors='ignore') as imported_file:
        manually_added_links = set(imported_file.read().splitlines())
    with open(file_name, 'a+', encoding='utf-8', errors='ignore') as file:
        file.seek(0)
        existing_links = set(file.read().splitlines())
        new_links_imported = imported_links - existing_links
        new_links_manually_added = manually_added_links - existing_links

        for link in new_links_imported:
            print(f"Appending imported link: {link}")
            file.write(link + '\n')
        for link in new_links_manually_added:
            print(f"Appending manually added link: {link}")
            file.write(link + '\n')
except FileNotFoundError:
    print(f"The file {imported_links_file} was not found.")
