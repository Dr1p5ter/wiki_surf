import logging
import os
import requests
import sys
import time

from bs4 import BeautifulSoup
from termcolor import colored

from rw_table import write_ref_file

host_url = 'https://en.wikipedia.org'
output_folder = 'out'

usage_txt = """
Usage: "wikisurf.py <str : slug_permalink> <int : max_depth>"
slug_permalink :
    wikisurf expects "/[slug]/[Article Permalink]"
        EX : "/wiki/Main_Page"
"""

def find_ref_in_url(url : str) -> list[str]:
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
    return ref_list_for_url

if __name__ == "__main__":
    # config logger
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    # make sure that there is an input string
    if len(sys.argv) != 3:
        logging.info(usage_txt)
        sys.exit(-1)
    else :
        if str(sys.argv[1]).find(host_url) != -1 :
            logging.info(colored("slug_permalink invalid", 'red'), end='')
            logging.info(usage_txt)
            sys.exit(-1)
        try:
            int(sys.argv[2])
        except:
            logging.info(colored("max_depth invalid", 'red'), end='')
            logging.info(usage_txt)
            sys.exit(-1)

    # clear the output folder
    if os.path.exists(output_folder) : 
        for file in os.listdir(output_folder) :
            os.remove(output_folder + '\\' + file)
    else :
        os.mkdir(output_folder)

    # begin collecting references on recieved link
    queue = [str(sys.argv[1])]
    max_depth = int(sys.argv[2])
    cur_depth = 0
    num_writes = 0
    num_files = 0
    while cur_depth != max_depth :
        # tell console progress at depth
        logging.info(f'beginning at depth {cur_depth}')

        # make a new queue and go through until old queue is empty
        new_queue = list()
        max_queue_len = int(len(queue))
        for i in range(max_queue_len) :
            # pop the first element of the queue
            slug_permalink = queue[i]

            # retrieve list of references to that url
            list_of_refs = find_ref_in_url(host_url + slug_permalink)
            if list_of_refs == None :
                continue
            list_of_refs = list(set(list_of_refs))
            list_of_refs.sort(reverse=False)

            # write to a file the output
            write_count = write_ref_file(output_folder + '\\' + slug_permalink.replace('/', '(~)') + '.txt', list_of_refs)
            if write_count != 0 :
                # add count to total
                num_writes += write_count
                num_files += 1

                # if there was things written then add it to the new queue
                for ref in set(list_of_refs) :
                    new_queue.append(ref)

            # tell console progress of queue
            logging.info(f'{(((i + 1) / max_queue_len) * 100):5.4}%')
        queue = new_queue
        cur_depth += 1

    # log total number of links wrote to the folder
    logging.info(colored(f'Total number of writes is {num_writes}', 'cyan'))
    logging.info(colored(f'Total number of files in folder is {num_files}', 'cyan'))

    # end program
    sys.exit(0)
