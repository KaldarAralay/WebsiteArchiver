import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import cssutils

# Initialize robots.txt parser
rp = RobotFileParser()

def can_fetch(url):
    # Ensure the url has a scheme
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = 'http://' + url

    # Get robots.txt url
    robots_url = urljoin(url, '/robots.txt')

    # Set url to robots.txt
    rp.set_url(robots_url)

    # Read robots.txt
    rp.read()

    # Return whether the user-agent "*" is allowed to fetch the url
    return rp.can_fetch("*", url)


def download_resource(url, local_path):
    print(f"Downloading resource: {url}")
    if can_fetch(url):
        try:
            response = requests.get(url, stream=True)

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            print(f"Failed to download {url}. Error: {str(e)}")
            
def download_and_update_css(url, local_path):
    print(f"Downloading and updating CSS: {url}")
    if can_fetch(url):
        try:
            response = requests.get(url)
            css = response.text

            # Parse the CSS with cssutils
            stylesheet = cssutils.parseString(css)

            # Iterate over all rules in the stylesheet
            for rule in stylesheet:
                if rule.type == rule.STYLE_RULE:
                    # Iterate over all properties in the rule
                    for property in rule.style:
                        if 'url(' in property.value:
                            # Extract the URL from the property value
                            resource_url = re.search(r'url\((.*?)\)', property.value).group(1)
                            # Join the URL with the resource URL to handle relative URLs
                            resource_url = urljoin(url, resource_url)
                            local_resource_path = os.path.join(os.path.dirname(local_path), os.path.basename(resource_url))

                            download_resource(resource_url, local_resource_path)

                            # Update the property value with the local path
                            property.value = property.value.replace(resource_url, os.path.basename(resource_url))

            # Save the updated CSS to a local file
            with open(local_path, 'w') as f:
                f.write(css)
        except Exception as e:
            print(f"Failed to download {url}. Error: {str(e)}")

def scrape(urls):
    # Check if single URL is passed and convert it into list
    if isinstance(urls, str):
        urls = [urls]

    for start_url in urls:
        print(f"Starting to scrape website: {start_url}")
        # A queue of URLs to scrape next
        urls_to_scrape = [start_url]

        # A set of URLs we've already scraped
        scraped_urls = set()

        while urls_to_scrape:
            # Get the next URL to scrape
            url = urls_to_scrape.pop(0)
            print(f"Scraping URL: {url}")

            if url in scraped_urls:
                # We've already scraped this URL, skip it
                print(f"URL already scraped: {url}")
                continue

            if not can_fetch(url):
                # We're not allowed to scrape this URL, skip it
                print(f"URL disallowed by robots.txt: {url}")
                continue

        # Send a GET request to the URL
        response = requests.get(url)

        # Parse the HTML content of the page with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Create a directory for the URL
        parsed_url = urlparse(url)
        dir_name = parsed_url.netloc + parsed_url.path
        if not dir_name.endswith('/'):
            dir_name = dir_name.rsplit('/', 1)[0]
        dir_name = dir_name.replace('/', '_')
        os.makedirs(dir_name, exist_ok=True)
        print(f"Created directory: {dir_name}")

        # Save the HTML content to a local file
        with open(os.path.join(dir_name, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"Saved HTML content for URL: {url}")

        # Add the URL to the set of scraped URLs
        scraped_urls.add(url)

                # Download all linked resources and update their URLs in the HTML
        for tag_name, attr_name in [('img', 'src'), ('script', 'src'), ('link', 'href')]:
            for tag in soup.find_all(tag_name):
                resource_url = tag.get(attr_name)
                if resource_url:
                    # Join the URL with the resource URL to handle relative URLs
                    resource_url = urljoin(url, resource_url)
                    local_path = os.path.join(dir_name, os.path.basename(resource_url))

                    if resource_url.endswith('.css'):
                        download_and_update_css(resource_url, local_path)
                    else:
                        download_resource(resource_url, local_path)

                    # Update the resource URL in the HTML to point to the local path
                    tag[attr_name] = os.path.basename(resource_url)


        # Find all hyperlinks on the page and add them to the list of URLs to scrape
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href')
            if href and not href.startswith('#'):
                # Join the URL with the href to handle relative URLs
                new_url = urljoin(url, href)
                urls_to_scrape.append(new_url)
                print(f"Found new URL to scrape: {new_url}")

        # Save the HTML content again with updated resource URLs
        with open(os.path.join(dir_name, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"Updated HTML content for URL: {url}")

# Start scraping
scrape(['https://www.site1.com/', 'https://www.site2.blog/'])
