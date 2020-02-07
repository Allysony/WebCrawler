import re
from urllib.parse import urlparse  # check out this library, will prob use

# use library lxml here

from lxml import html
import multiprocessing


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


""" 
NOTE: 

.iterlinks():
This yields (element, attribute, link, pos) for every link in the document. 
attribute may be None if the link is in the text 
(as will be the case with a <style> tag with @import).
;USE ITERLINKS[2] TO GET LINKS

"""


def extract_next_links(url, resp) -> list:
    # resp is pages content (in html)
    result_next_links = set()
    try:
        # make sure the page exists
        if resp.raw_response is not None:
            # make sure not extracting pages with request errors
            if resp.status in range(200, 399):
                # TODO look at absolute here ???
                # ------- NOTE: got html file of curr doc using lxml document_fromstring -----
                html_content = html.document_fromstring(resp.raw_response.text)
                # ------- NOTE: links on curr doc using lxml iterlinks()[2] ----------
                # add unique extracted links to the list
                for i in html_content.iterlinks():
                    result_next_links.add(i[2])
                print(resp.status, url)
    # TODO We should account for sitemap xml, for now unicode errors are being caught here
    except ValueError:
        pass

    return list(result_next_links)


def is_valid(url):
    try:
        parsed = urlparse(url)
        # The max length of a URL in the address bar is 2048 characters
        if len(url) > 2048:
            return False
        # The URL must be in http or https
        if parsed.scheme not in set(["http", "https"]):
            return False
        # Do not include queries, due to causing infinite requests
        if parsed.query != '':
            return False
        # URL must be within the specified domains
        if parsed.netloc[4:] not in {"stat.uci.edu", "ics.uci.edu", "informatics.uci.edu", "cs.uci.edu"}:
            return False
        # Do not include fragments
        if "#" in parsed.path:
            return False
        # TODO account for sites that are timing out

        # TODO find endless loops maybe make a regex????? EXAMPLE: https://ics.uci.edu/a/a/a/a/a/a/a/a/a/a/a/a/a

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise
