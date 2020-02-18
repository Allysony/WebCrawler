from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time


# this file does the crawling calls the scraper

# this is what we would alter to multi thread


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.longest_page_wc = 0
        self.longest_pages = []
        self.SUPER_DICTIONARY = dict()
        super().__init__(daemon=True)

    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                get_logger(" ", 'WordDict').info(str(sorted(self.SUPER_DICTIONARY.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)))
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            scraped_urls, list_of_word_lists = scraper(tbd_url, resp)

            curr_wc = 0
            for word_list in list_of_word_lists:
                curr_wc += len(word_list)
                for word in word_list:
                    if word in self.SUPER_DICTIONARY:
                        self.SUPER_DICTIONARY[word] += 1
                    else:
                        self.SUPER_DICTIONARY[word] = 1

            if curr_wc > self.longest_page_wc:
                get_logger(" world count: URL ", 'longest_page').info('{} : {}'.format(curr_wc, tbd_url))
                self.longest_pages.append(tbd_url)
                self.longest_page_wc = curr_wc

            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
