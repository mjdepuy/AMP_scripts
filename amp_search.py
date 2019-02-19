#!/usr/bin/env python

'''
# Title: FireAMP IOC Query Script
# Author: Michael Depuy
# Original Date: 2/14/2019
#
# The purpose of this script is to query
# the FireAMP API for any information 
# related to the IOCs given to the script.
#
# Current version: 1.0.0
#
# Changelog: 
# 1.0.0 -- Created
'''

import requests
import json
import sys
import argparse
import re
import csv
from base64 import encodebytes
from time import sleep

AMP_URL = "https://api.amp.cisco.com/v1/computers/activity?q="

def get_ratelimit(res):
	if int(res.headers["X-RateLimit-Remaining"]) <= 10:
		#print("API query limit reached. Resuming in " + int(res.headers["X-RateLimit-Reset"]) + " seconds...")
		sleep(int(res.headers["X-RateLimit-Reset"]))
	return	

def out_txt(hits):
	for hit in hits:
		print(hit + ":")
		for host in hits[hit]:
			print("\t" + host)
		print("\n")
	return

def out_csv(hits):
	outfile = open("hits.csv","w+")

	outfile.write("HASH,HOSTNAME(S)\n")
	
	for hit in hits:
		outfile.write(hit + ",")
		for host in hits[hit]:
			outfile.write(host + " | ")
		outfile.write("\n")

	outfile.close()
	return

def out_json(hits):
	print(json.dumps(hits,indent=4,separators=(',',' ')))
	return

def query_fireamp(args,h):
	print("Querying FireAMP for hits...")

	f = open(args.file,"r")
	iocs = {}

	for line in f:
		l = str(line).rstrip()
		iocs[l] = []

	f.close()
	for i in iocs:
		res = requests.get(AMP_URL + i,headers=h)
		jres = res.json()
		if len(jres["data"]) == 0:
			continue
		else:
			for event in jres["data"]:
				iocs[i].append(str(event["hostname"].rstrip()))
		get_ratelimit(res)

	return iocs

def main():
	# Put AMP Client ID and API key in here.
	client_id = ""
	api_key = ""
	auth = encodestring(client_id + ":" + api_key).replace('\n','')

	# Uncomment this if you have already encoded your Cient ID and API key
	#AMP_API=''
	#auth = encodebytes(AMP_API.encode('utf-8')).decode('utf-8').replace('\n','')

	# User-Agent can be deleted if your certs are working correctly.
	# Must leave Authorization header in for authentication.
	amp_h = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0", "Authorization": "Basic %s" % auth}

	print("Usage: amp_search.py -f FILE -o OUTPUT_FORMAT\n")

	# Generate arguments/parser
	p = argparse.ArgumentParser()
	p.add_argument("-f", "--file", help="Input file containing list of IOCs")
	p.add_argument("-o", "--output", help="Format of output file: txt, csv, json")

	# Parse through arguments
	args = p.parse_args()
	
	# Send to FireAMP
	ioc_hits = query_fireamp(args,amp_h)
	
	# Output to CSV, text, or JSON. Default is text to STDOUT.
	if args.output == "csv":
		out_csv(ioc_hits)
	elif args.output == "txt":
		out_txt(ioc_hits)
	elif args.output == "json":
		out_json(ioc_hits)
	else:
		out_txt(ioc_hits)

	print("Fin.\n")

if __name__ == "__main__":
	main()