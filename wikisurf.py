import requests
import sys
import os
from termcolor import colored
from bs4 import BeautifulSoup

from rw_table import write_ref_file

init_url = '/wiki/Main_Page'
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
    soup = BeautifulSoup(resp.content, 'html.parser')

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
    # make sure that there is an input string
    if len(sys.argv) != 3:
        print(usage_txt)
        sys.exit(-1)
    else :
        if str(sys.argv[1]).find(host_url) != -1 :
            print(colored("slug_permalink invalid", 'red'), end='')
            print(usage_txt)
            sys.exit(-1)
        try:
            int(sys.argv[2])
        except:
            print(colored("max_depth invalid", 'red'), end='')
            print(usage_txt)
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
    while cur_depth != max_depth :
        # tell console progress at depth
        print(f'beginning at depth {cur_depth}')

        # make a new queue and go through until old queue is empty
        new_queue = list()
        max_queue_len = int(len(queue))
        while len(queue) != 0 :
            # pop the first element of the queue
            popped_slug_permalink = queue.pop(0)

            # retrieve list of references to that url and then write to a file the output
            list_of_refs = find_ref_in_url(host_url + popped_slug_permalink)
            if write_ref_file(output_folder + '\\' + popped_slug_permalink.replace('/', '(~)') + '.txt', list_of_refs) != 0 :
                # if there was things written then add it to the new queue
                for ref in list_of_refs :
                    new_queue.append(ref)

            # tell console progress of queue
            print(f'{(((max_queue_len - len(queue)) / max_queue_len) * 100):5.4}%')
        queue = new_queue
        cur_depth += 1
