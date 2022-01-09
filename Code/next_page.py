import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def next_page(url, pg=2):
    """
    Search through text on URL to identify the link to the next page. If this
    fails or if the link to the next page is simply '#', assume last page.
    """
    r = requests.get(url)
    r_html = r.text
    soup = BeautifulSoup(r_html, features="lxml")
    links = soup.find_all("a")
    for i in links: # Identify next page link using 3 methods
        try: # 1. Link may just be the page number and nothing else
            if re.compile(str(pg)).fullmatch(
                    re.sub('[^A-Za-z0-9]+', '', i.string)):
                herf_next = i
        except:
            pass
        try: # 2. Link is nextchapter
            if re.compile("nextchapter").match(
                    re.sub('[^A-Za-z0-9]+', '', i.string.lower)):
                herf_next = i
            elif re.compile("next chapter").match(
                    re.sub('[^A-Za-z0-9]+', '', i.string.lower)):
                herf_next = i
            elif re.compile("next_chapter").match(
                    re.sub('[^A-Za-z0-9]+', '', i.string.lower)):
                herf_next = i
        except:
            pass
        try: # 3. Check if it includes the word 'next'
            if 'next' in str(i.get_text).lower():
                herf_next = i
        except:
            pass
    # Form a complete URL 
    try: # Assume page was found if not an UnboundLocalError will occur
        href = herf_next.attrs.get("href") 
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        last_pg_chk = herf_next.attrs.get("href")  == '#'
    except UnboundLocalError:
        last_pg_chk = True
        href = "NaN" # Placeholder 
    return href, last_pg_chk