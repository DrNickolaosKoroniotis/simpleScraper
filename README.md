# simpleScraper
Simple python-implemented scraper and crawler.
## Description 
This software is a simple scraper and crawler I implemented, specifically for retrieving text from Wikipedia articles, primarily for NLP experimentation.
Before any actions can take place, simpleScraper checks the *robots.txt* file and retrieves any **allowed** and **disallowed** paths.
It provides a terminal interface, with a number of options that control how the text will be stored, if crawling is to be performed and to what extent.
## Options

    1.  -h, --help: show this help message and exit
    2. --url , -u:  Set the URL that the scraper will target.
    3. --delay: Set the delay (in seconds) before each request is sent (default 0.5).
    4. --strategy: Set the strategy for extracting text from the websites. Strategy 1 finds every paragraph and accumulates their text, extractng it in a single text document. Strategy 2 creates a new subfolder and one text file per section of text (separating it acording to titles and sections found).
    5. --crawl: Enable or disable the crawling option. If enabled, scraper will crawl through any URL of the same domain as the original URL, up to a depth of 5. To enable, provide any of the following ['1',
                        'True', 'true', 't', 'T', 'y', 'Y', 'yes', 'Yes', 'YES']. To disable, provide any of the following ['0', 'False', 'false', 'f', 'F', 'n', 'N', 'no', 'NO', 'No'].
    6.--breadth: Set the breadth of a crawl. Breadth corresponds to the number of URLs to retrieve from a page, for subsequent scraping.
    7. --depth: Set the depth of a crawl. Depth corresponds to the number of times URLs will be extracted from pages (calculated in rounds).
    8. --separate_store: Option to store results under separate directory, rather than under base domain's root directory (provide enable or disable options as in --crawl).

## Usage
./simpleScraper [-h] --url URL [--delay DELAY] [--strategy {1,2,both}] [--crawl *true, T, false, F, ...*] [--breadth *integer from  0 to 50*] 
[--depth *integer from  0 to 100*] [--separate_store *true, T, false, F, ...*]
