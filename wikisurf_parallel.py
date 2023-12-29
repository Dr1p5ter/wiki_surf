# imports
import concurrent.futures
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

# global variables
host_url = 'https://en.wikipedia.org'
output_folder = 'out'
max_depth = 5
min_depth = 1
max_thread_count = 10
min_thread_count = 2

# usage string
usage_txt = """
Usage: "wikisurf.py <str : slug_permalink> <int : depth> <int : number_of_threads_in_pool>"

slug_permalink :
    wikisurf expects "/[slug]/[Article Permalink]"
        EX : "/wiki/Main_Page"

depth :
    min : 1
    max : 5

number_of_threads_in_pool :
    min : 2
    max : 10
"""

def find_ref_in_url(url : str) -> list[str]:
    print(colored(f'thread {threading.get_ident()} ', 'light_magenta'), colored(f'starting', 'red'))
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
    print(colored(f'thread {threading.get_ident()} ', 'light_magenta'), colored(f'ending', 'red'))
    return ref_list_for_url

# main program
if __name__ == "__main__":
    # config logger
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    def log_invalid_arg_statement(err_msg : str) :
        logging.info(colored(err_msg, 'red'))
        print(colored(usage_txt, 'light_green'))
        sys.exit(-1)

    # make sure inputs are valid
    stat = 0
    if len(sys.argv) != 4:
        log_invalid_arg_statement('arguments must match usage')
    else :
        # check if the slug is valid
        if str(sys.argv[1]).find(host_url) != -1 :
            log_invalid_arg_statement("slug_permalink invalid input")

        # check if the depth is valid
        try:
            stat = 0
            if int(sys.argv[2]) < min_depth or int(sys.argv[2]) > max_depth :
                stat = 1
                log_invalid_arg_statement("depth : threshold not within valid range")
        except:
            if stat :
                sys.exit(-1)
            else :
                log_invalid_arg_statement('depth : invalid input')

        # check if the number of threads is valid
        try:
            stat = 0
            if int(sys.argv[3]) < min_thread_count or int(sys.argv[3]) > max_thread_count :
                stat = 1
                log_invalid_arg_statement("number_of_threads_in_pool threshold not within valid range")
        except:
            if stat :
                sys.exit(-1)
            else :
                log_invalid_arg_statement("number_of_threads_in_pool invalid input")

    # clear the output folder
    if os.path.exists(output_folder) : 
        for file in os.listdir(output_folder) :
            os.remove(output_folder + '\\' + file)
    else :
        os.mkdir(output_folder)

    # collect valid arguments from command line
    queue = [str(sys.argv[1])]
    depth = int(sys.argv[2])
    thread_count = int(sys.argv[3])

    # make a pool of threads and begin moving through the queue
    

    sys.exit(0)
