import re
from urllib.parse import urlparse
from lxml import html
from simhash import Simhash
import requests


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp) -> list:
    # resp is pages content (in html)
    result_next_links = set()
    try:
        # make sure the page exists
        if resp.raw_response is not None:
            # ------- NOTE: got html file of curr doc using lxml document_fromstring -----
            html_content = html.document_fromstring(resp.raw_response.text)
            # make links absolute
            html_content.make_links_absolute(url, resolve_base_href=True)
            # ------- NOTE: links on curr doc using lxml iterlinks()[2] ----------
            # add unique extracted links to the list
            for i in html_content.iterlinks():
                result_next_links.add(i[2])
                print(i)
    # TODO We should account for sitemap xml, for now unicode errors are being caught here
    except ValueError:
        pass
    return list(result_next_links)


def is_valid(url):
    try:
        parsed = urlparse(url)
        # The URL must be in http or https
        if parsed.scheme not in set(["http", "https"]):
            return False
        # The max length of a URL in the address bar is 2048 characters
        if len(url) > 2048:
            return False
        # Do not include queries, due to causing infinite requests
        if parsed.query != '':
            return False
        # URL must be within the specified domains and paths
        if parsed.netloc[4:] not in {"stat.uci.edu", "ics.uci.edu", "informatics.uci.edu", "cs.uci.edu"} \
                and parsed.netloc not in {"today.uci.edu/department/information_computer_sciences"}:
            return False
        # Do not include fragments
        if parsed.fragment != '':
            return False
        # make sure not extracting pages with request errors
        if requests.get(url, timeout=300).status_code not in range(200, 399):
            return False
        # Do not include endless loops EXAMPLE: https://ics.uci.edu/a/a/a/a/a/a/a/a/a/a/a/a/a
        # ------- NOTE: I used "\w" to catch first group of chars of (length between 1 to inf),
        #               then compare next non capturing group with that first group by using "\1"
        #               Only a match if 2 or more non capturing groups matches that first group.
        #               Repeat for each group. EXAMPLE OF MATCH: /foo/bar/aba/aba/aba -------------------
        if re.match(r"(\w+)(?:\W+\1){2,}", parsed.path.lower()):
            return False

        # TODO find duplicate pages

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
    # implementing a timeout to detect and avoid stalling
    except TimeoutError:
        # stalling too long. took longer than 5 minutes
        print("TimeoutError for ", parsed)
        return False
    except TypeError:
        print("TypeError for ", parsed)
        raise