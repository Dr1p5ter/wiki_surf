# Wikipedia Surf Tool

## Table of Contents

* [Description](https://github.com/Dr1p5ter/wiki_surf#Description)
* [Usage](https://github.com/Dr1p5ter/wiki_surf#Usage)

## Description

> This tool is a web crawler that begins at a Wikipedia link and captures all of the out going links from that page. It will then keep track of each link and traverse in order to create an outgoing tree. This is computationally heavy and respect the ammount of wait requests the website gives. Be curtious as to not attempt disrupt normal traffic to a single page. For more information check out the [usage](https://github.com/Dr1p5ter/wiki_surf#Usage) tab below.

## Usage

> Clone the entire directory and open inside of a terminal. Then use the -h flag before running either wikisurf.py or wikisurf_parallel.py files. They have their own arguments. Since the wikisurf.py file runs each link one at a time, use wikisurf_parallel.py for running on a gpu for faster computation. All records will be recorded within a folder that will begin populating during and after execution. If a branch can't be connected to, it will simply be skipped/ignored.
