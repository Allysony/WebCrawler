import re
from urllib.parse import urlparse  # check out this library, will prob use

# use library lxml here

from lxml import html

from lxml import etree


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
        if resp.raw_response is not None:  # make sure the page exists
            # html file of curr doc using lxml document_fromstring
            #if resp.status not in range(500, 699):
            if resp.status == 200:
                # look at absolute
                html_content = html.document_fromstring(resp.raw_response.text)
                # links on curr doc using lxml iterlinks()[2]
                for i in html_content.iterlinks():
                    result_next_links.add(i[2])
                print(resp.status, url)

    except ValueError:
        pass

    return list(result_next_links)


def is_valid(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False
        if parsed.query != '':
            return False
        if parsed.netloc[4:] not in {"stat.uci.edu", "ics.uci.edu", "informatics.uci.edu", "cs.uci.edu"}:
            return False

        if "#" in parsed.path:
            return False

        # length
        # implementation required FIND TRAPS HERE!
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
