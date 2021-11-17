#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import json
import pdb
from tqdm import tqdm
import click
import random

## FUNS

class WikiPage(object):
    def __init__(self, url, verbose = False):
        self.url_or = url
        page = requests.get(url)
        ## this is for the Basque wiki only I think, it has this
        ## weird thing
        if "Txikipedia" in page.url:
            url = page.url.replace("Txikipedia:", "")
            page = requests.get(url)
        self.url = page.url
        if verbose:
            print(page)
            print(self.url)
        soup = BeautifulSoup(page.content, "html.parser")
        self.soup = soup


class CatalanWikiPage(WikiPage):
    def __init__(self, url, verbose = False, mode = "ca"):
        super().__init__(url, verbose)
        self.mode = mode
    def get_locations(self, singleLoc=True, verbose = False):
        geo_info = self.soup.find_all("span", class_="geo-dms")
        geo_info_set = set(geo_info)
        if verbose:
            print(len(geo_info_set))
            print(len(geo_info))
        geo_info_unset = list(geo_info_set)
        locations = [parse_locations(i.text, verbose=verbose, mode=self.mode) for i in geo_info_unset]
        if singleLoc and len(locations) > 0:
            locations = random.choice(locations)
        if verbose:
            print(locations)
        return locations

class BasqueWikiPage(WikiPage):
    def get_locations(self, singleLoc=True, verbose = False):
        geo_info = self.soup.find_all("a", class_="mw-kartographer-maplink")
        geo_info_set = set(geo_info)
        if verbose:
            print(len(geo_info_set))
            print(len(geo_info))
        geo_info_unset = list(geo_info_set)
        locations = [parse_locations_eu(i, verbose=verbose) for i in geo_info_unset]
        if singleLoc and len(locations) > 0:
            locations = random.choice(locations)    
        return locations

class GermanWikiPage(WikiPage):
    def get_locations(self, singleLoc = True, verbose = False):
        long_arr = self.soup.find_all("span",attrs={"title":"Breitengrad"})
        lat_arr = self.soup.find_all("span",attrs={"title":"Längengrad"})
        if len(lat_arr) != len(long_arr):
            raise ValueError("Number of lat and long coordinates do not match")
        geo_info = []
        for i in range(len(lat_arr)):
            txt_loc_arr = "{}, {}".format(long_arr[i].text, lat_arr[i].text)
            geo_info.append(txt_loc_arr)
        geo_info_set = set(geo_info)
        if verbose:
            print(len(geo_info_set))
            print(len(geo_info))
        geo_info_unset = list(geo_info_set)
        locations = [parse_locations(i, verbose=verbose, mode="de") for i in geo_info_unset]
        if singleLoc and len(locations) > 0:
            locations = random.choice(locations)
        if verbose:
            print(locations)
        return locations

#example for : 0°25'30"S, 91°7'W
# from here https://stackoverflow.com/questions/17193351
def dms_to_loc(str, mode = "ca"):
    if mode == "ca":
        direction = {'N':1, 'S':-1, 'E': 1, 'O':-1}
        new = str.replace(u'°',' ').replace('′',' ').replace('″',' ')
    elif mode == "de":
        direction = {'N':1, 'S':-1, 'O': 1, 'W':-1}
        new = str.replace(u'°',' ').replace('′',' ').replace('″',' ')
    elif mode == "it":
        direction = {'N':1, 'S':-1, 'E': 1, 'W':-1}
        new = str.replace(u'°',' ').replace('′',' ').replace('″',' ')
    elif mode == "eo":
        direction = {'N':1, 'S':-1, 'O': 1, 'U':-1}
        new = str.replace(u'°',' ').replace('′',' ').replace('″',' ')
    elif mode == "gl":
        direction = {'N':1, 'S':-1, 'L': 1, 'O':-1}
        new = str.replace(u'°',' ').replace('′',' ').replace('″',' ')
    else:
        raise Exception("Not implemented yet")
    new = new.split()
    new_dir = new.pop()
    if mode == "de" and len(new) == 3:
        new[2] = new[2].replace(',','.')
    if mode == "de" and len(new) == 1:
        new[0] = new[0].replace(',','.')
    new.extend([0,0,0])
    try:
        return (float(new[0])+float(new[1])/60.0+float(new[2])/3600.0) * direction[new_dir]
    except ValueError:
        pdb.set_trace()

def dms_to_longlat(str, mode = "ca"):
    lat_raw, long = str.split()
    lat = lat_raw.rstrip(', ')
    lat_dec = dms_to_loc(lat, mode = mode)
    long_dec = dms_to_loc(long, mode = mode)
    ret_obj = {
        "lat" : round(lat_dec, 3),
        "long" : round(long_dec, 3)
    }
    return ret_obj

def parse_locations(str, mode = "ca", verbose = False):
    geo_info_str = str.replace(u'\xa0', u'')
    if verbose:
        print(geo_info_str)
    position = dms_to_longlat(geo_info_str, mode = mode)
    return position

def parse_locations_eu(obj, verbose = False):
    obj_ret = {
        "lat" : float(obj['data-lat']),
        "long" : float(obj['data-lon'])
    }
    return obj_ret

def build_url(language, verbose):
    url = "https://{}.wikipedia.org/wiki/Special:Random".format(language)
    ca_like_lan = ["ca", "es"]
    it_like_lan = ["it"]
    eu_like_lan = ["eu", "fr"]
    de_like_lan = ["de"]
    eo_like_lan = ["eo"]
    gl_like_lan = ["gl"]
    if (language in ca_like_lan):
        w_page = CatalanWikiPage(url, verbose)
    elif (language in eu_like_lan):
        w_page = BasqueWikiPage(url, verbose)
    elif (language in de_like_lan):
        w_page = GermanWikiPage(url, verbose)
    elif (language in it_like_lan):
        w_page = CatalanWikiPage(url, verbose, mode = "it")
    elif (language in eo_like_lan):
        w_page = CatalanWikiPage(url, verbose, mode = "eo")
    elif (language in gl_like_lan):
        w_page = CatalanWikiPage(url, verbose, mode = "gl")      
    else:
        raise Exception("Not implemented yet")
    return w_page


@click.command()
@click.option('-t','--target', default=10, help='Number of random locations to sample.')
@click.option('-l','--language', default="ca", help='Wikipedia s language')
@click.option('-o','--output', default="locations.json", help='Output file name')
@click.option('--verbose', is_flag=True)
def main_wrk(target, language, output, verbose):
    """
    The main function of the script, needed for click_
    """
    locations = []
    pbar = tqdm(total = target)
    # get_locations("https://ca.wikipedia.org/wiki/Barcelona", verbose=True)
    while len(locations) < target:
        w_page = build_url(language, verbose=verbose)
        tmp_loc = w_page.get_locations(verbose=verbose)
        pbar.update(len(tmp_loc))
        locations += tmp_loc
        time.sleep(.1)
    pbar.close()
    with open(output, 'w') as f:
        json.dump(locations, f)

if __name__ == "__main__":
    main_wrk()
