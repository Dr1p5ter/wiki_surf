# imports
import concurrent.futures
import itertools
import logging
import os
import requests
import sys
import threading
import time

# specified imports
from bs4 import BeautifulSoup
from termcolor import colored

# local imports
from rw_table import write_ref_file

wiki_page_urls = set([
    "/wiki/Cat",
    "/wiki/Haida",
    "/wiki/Belgium",
    "/wiki/Shark",
    "/wiki/Pampas_fox",
    "/wiki/Phoenicia",
    "/wiki/Cat_show",
    "/wiki/"
])

def find_ref_in_url(url : str) -> list[str]:
    print(colored(f'thread {threading.get_ident():5}','light_magenta'),
          colored(f' S ', 'green'))
    # send a request to get the packet and open it for html parsing
    resp = requests.get(url)
    soup = None
    if resp.status_code == 200 :
        soup = BeautifulSoup(resp.content, 'html.parser')
    elif resp.status_code == 429 :
        # handle instance of too many requests sent to avoid timeout
        logging.info(colored(f'[Error 429 occured : pausing for {int(resp.headers["Retry-After"])}]', 'yellow'))
        time.sleep(int(resp.headers['Retry-After']))
        logging.info(colored('Resuming...', 'yellow'))
        return find_ref_in_url(url)
    else :
        logging.info(colored(f'Error {resp.status_code} occured : unsupported handle [skipping]', 'red'))
        return None

    # go into the html file and find only the parser output associated with the content body
    ps = soup.find('div', attrs = {'id' : 'bodyContent'})
    ps = ps.find('div', attrs = {'id' : 'mw-content-text'})
    ps = ps.find('div', attrs = {'class' : 'mw-parser-output'}).findAll()

    # get every hyperlink associated with the packet retrieved
    ref_list_for_url = list()
    for tag in ps:
        if tag.name == 'a':
            ref = str(tag.get('href'))
            if ref.find('/wiki/') >= 0 and ref.find(':') == -1:
                ref_list_for_url.append(ref)

    print(colored(f'thread {threading.get_ident():5}','light_magenta'),
          colored(f' E ', 'red'))
    return ref_list_for_url

def union_all_results(corpus_of_results : list) -> set :
    union_set = set()
    for lst in corpus_of_results :
        union_set = union_set | set(lst)
    return union_set

host_url = 'https://en.wikipedia.org'

def execute_batch_of_threads(url_list : set[str]) -> set[str] :
    new_refs = list([])
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor :
        futures = [executor.submit(find_ref_in_url, host_url + url) for url in url_list]

        # save sets when future is done
        for future in concurrent.futures.as_completed(futures) :
            new_refs.append(future.result())
    ref_set = union_all_results(new_refs)
    return ref_set

wiki_page_urls = execute_batch_of_threads(wiki_page_urls)
print(len(wiki_page_urls))
