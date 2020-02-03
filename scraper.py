import re
from urllib.parse import urlparse  # check out this library, will prob use

# use library lxml here

from lxml import html


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
    result_next_links = []
    print("url: ", url)
    print("resp:", resp)

    if resp.raw_response is not None:
        # html file of curr doc using lxml document_fromstring
        html_content = html.document_fromstring(resp.raw_response.text)
        # links on curr doc using lxml iterlinks()[2]
        for i in html_content.iterlinks():
            result_next_links.append(i[2])
            print(i[2])
    return result_next_links


def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
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
