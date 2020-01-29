
import csv
import requests
import urllib.request
import re
import json
import time

from lxml import html
from bs4 import BeautifulSoup
desired_keys = ["title", "common_name", "cas", "pubchem_id", "mechanism_of_toxicity", "uniprot_id",
                "moldb_smiles", "pdb_id", "chemspider_id", "target_uniprot_ids", "target_names", "target_pdb_ids"]
desired_types = {'Bacterial Toxin', 'Drug', 'Food Toxin', 'Fungal Toxin',
                 'Natural Toxin', 'Pesticide', 'Plant Toxin', 'Protein', 'Synthetic Toxin'}
# this is a list of all the elements, each element is a temp_entry which is also a list.
desired_elements = []


def parsejson(file):
    with open(file, 'r') as f:
        toxdb = json.load(f)
    for toxin in toxdb:
        # print(type(toxin)) ## should be a dictionary
        desired = False
        for key in toxin:
            # print(key)
            if key == "types":
                # print(toxin[key])
                # print(type(toxin[key])) ### each toxin type as a whole has a list of dictionaries
                # for each dictionary in the list
                for entry in toxin[key]:
                    # for each key in the dictionary
                    for attribute in entry:
                        if attribute == "type_name":
                            # # the types have more attributes so make sure each of them
                            if (entry[attribute]) in desired_types:
                                # print(entry[attribute])
                                desired = True
                            # print('target type found')
                                break
        if desired:
            temp_elem = ["", "", "", "", "", "", "", "", "", "", "", ""]
            for key in toxin:
                # do we want to scrape this attribute?
                if key in desired_keys:
                    # build an element with this new attribute
                    index = desired_keys.index(key)
                    temp_elem[index] = toxin[key]
                    # print(key, " : ", temp_elem[index])
            desired_elements.append(temp_elem)


parsejson('t3.json')
# then from all the elements, scrape the pdb id and uniprot id

for element in desired_elements:
    # print("New elem")
    uniprot = []
    if "T3" in element[0]:
        # Start target queries
        # print("searching..")
        # make a request to t3db
        time_elapsed = time.time()
        url = "http://www.t3db.ca/toxins/" + element[0] + "#targets"
        print('url : ', url)
        response = requests.get(url)
        tree = html.fromstring(response.content)
        uniprots = tree.xpath(
            '//a[contains(@href, "uniprot") and @target="_blank" and @class="wishart-link-out"]/@href')
        names = tree.xpath('//strong/a[contains(@href, "biodb")]/text()')
        element[10] = names
        # if len(names) == len(uniprots):
        del tree
        for code in uniprots:
            code = code.replace('http://www.uniprot.org/uniprot/', "")
            uniprot.append(code)
            #print('code in uniprot: ', code)
        element[9] = uniprot
        
    #for value in element:
        #print(value)

with open('toxinparsedee.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(desired_keys)
    for element in desired_elements:
        writer.writerow(element)
        # print(element)
