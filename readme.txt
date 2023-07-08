
# Web Archiver

This Python script, `archiver.py`, is a web scraper that visits specified URLs, downloads HTML content and linked resources such as images, CSS files, and JavaScript files, and saves these files locally. It respects `robots.txt` files, which specify which parts of a website a bot is allowed to access.

The script contains the following main functions:

1. `can_fetch(url)`: Checks whether a URL is allowed to be accessed according to its `robots.txt` file.
2. `download_resource(url, local_path)`: Downloads a resource from a given URL and saves it to a local file.
3. `download_and_update_css(url, local_path)`: Downloads a CSS file, updates URLs within it to point to locally downloaded resources, and saves the updated CSS file locally.
4. `scrape(urls)`: The main scraping function. It visits each URL in the list, downloads the HTML content and linked resources, and saves them locally. It also updates the URLs in the HTML to point to the locally downloaded resources.

## Usage

Run the script by executing `python3 archiver.py` in your terminal. Currently, the script is set to scrape the websites https://www.site1.com/ and https://www.site2.blog/. To change the websites to be scraped, edit the list of URLs in the `scrape()` function call at the bottom of the script.

## Requirements

Python 3.6 or later is required. The script also depends on several Python libraries, which are listed in the `requirements.txt` file. Install them using pip with the command `pip install -r requirements.txt`.
