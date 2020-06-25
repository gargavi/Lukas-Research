

###############################################
####  THIS PROGRAMS LOOKS FOR THE INDIVIDUAL ID
####  OF ALL MARRIAGE RECORDS FOR A GIVEN STATE
####  B. 1840 and 1855
####  and saves the marriage ID (the info about
####  the marriage will then be downloaded 
####  though another program)
###############################################


# THIS PROGRAM REQUIRES "TOR" TO BE RUNNING AS WELL
# AS A FAKE DISPLAY TO BE CREATED (IF RUNNING ON A SERVER)
# RUN THE CODE IN THE TERMINAL TO DO JUST THAT

	# nohup sudo killall tor
	# nohup sudo tor &
	# nohup sudo Xvfb :10 -ac &
	# export DISPLAY=:10

# Type here the state and the collectionid 
# for the marriage record database to scrape 
# on family search

col_id = '1681052'
state = 'texas'

###############################################
#### SET DIRECTORY BASED ON WHERE THE PROGRAM 
### RUN
###############################################

import sys
if sys.platform=='darwin' :
	workfolder = '/Users/Fred/Dropbox/Peters/marriage_records'
elif sys.platform=='linux2' :
	workfolder = '/home/dulbea/Dropbox/Peters/marriage_records'
sleeptime = 1

###############################################
#### Preparatory work
###############################################

# Load packages

import os
import re
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from time import sleep
import csv
import string

# Move to folder

os.chdir(workfolder)
os.getcwd()

# REcord output

import sys
log = state + '_' + col_id + '.txt'
# sys.stdout = open('log', 'w')

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

sys.stdout = Logger(log)

# Create file for records

filename = 'search_' + state
act_keys = ['year','letter','counter','count','uniqueid','totres']
# act_keys = ['count','uniqueid','name','colname','date','place']
if not os.path.exists(filename) :
	act_records_doc = open(filename, 'w')
	act_records = csv.DictWriter(act_records_doc,fieldnames=act_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')
	act_records.writeheader()
	act_records_doc.close()
act_records_doc = open(filename, 'a')
act_records = csv.DictWriter(act_records_doc,fieldnames=act_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')

# Create file for problems in scraping

prob_filename = 'search_problems'
prob_keys = ['state','year','letter','counter','prob','expected','found']
# act_keys = ['count','uniqueid','name','colname','date','place']
if not os.path.exists(prob_filename) :
	prob_records_doc = open(prob_filename, 'w')
	prob_records = csv.DictWriter(prob_records_doc,fieldnames=prob_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')
	prob_records.writeheader()
	prob_records_doc.close()
prob_records_doc = open(prob_filename, 'a')
prob_records = csv.DictWriter(act_records_doc,fieldnames=prob_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')


# Create file for no results for a given letter/year

nores_filename = 'search_nores'
nores_keys = ['state','year','letter']
# act_keys = ['count','uniqueid','name','colname','date','place']
if not os.path.exists(nores_filename) :
	nores_records_doc = open(nores_filename, 'w')
	nores_records = csv.DictWriter(nores_records_doc,fieldnames=nores_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')
	nores_records.writeheader()
	nores_records_doc.close()
nores_records_doc = open(nores_filename, 'a')
nores_records = csv.DictWriter(act_records_doc,fieldnames=nores_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')


# Create file for done results

done_filename = 'search_done_' + state
done_keys = ['state','year','letter','counter','totres']
# act_keys = ['count','uniqueid','name','colname','date','place']
if not os.path.exists(done_filename) :
	done_records_doc = open(done_filename, 'w')
	done_records = csv.DictWriter(done_records_doc,fieldnames=done_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')
	done_records.writeheader()
	done_records_doc.close()
done_records_doc = open(done_filename, 'a')
done_records = csv.DictWriter(act_records_doc,fieldnames=done_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')

###############################################
# Define program to scrape results from a page
###############################################

def scrape_res(soup):
	Records = []

	# DOING EVEN ROW
	list = soup.findAll(attrs={'class' : 'row-template even'})

	for n,l in enumerate(list) :
		rec = {}
		temp = l.find(attrs={"class" : "person-name"})
		rec['uniqueid'] = temp['href']
		# rec['name'] = temp.find(text=True).encode('ascii','ignore')
		# temp = l.find(attrs={"class" : "collection-name"})
		# rec['colname'] = temp.find(text=True).encode('ascii','ignore')
		# temp = l.find(attrs={"class" : "event-date"})
		# rec['date'] = temp.find(text=True).encode('ascii','ignore')
		# temp = l.find(attrs={"class" : "event-place"})
		# rec['place'] = temp.find(text=True).encode('ascii','ignore')
		Records.append(rec)
	list = soup.findAll(attrs={'class' : 'row-template odd'})
	for n,l in enumerate(list) :
		rec = {}
		temp = l.find(attrs={"class" : "person-name"})
		rec['uniqueid'] = temp['href']
		# rec['name'] = temp.find(text=True).encode('ascii','ignore')
		# temp = l.find(attrs={"class" : "collection-name"})
		# rec['colname'] = temp.find(text=True).encode('ascii','ignore')
		# temp = l.find(attrs={"class" : "event-date"})
		# rec['date'] = temp.find(text=True).encode('ascii','ignore')
		# temp = l.find(attrs={"class" : "event-place"})
		# rec['place'] = temp.find(text=True).encode('ascii','ignore')
		Records.append(rec)

	return Records

##########################################################
# Input the different parts of the adress on family search
##########################################################

adres_p1 = 'https://familysearch.org/search/collection/results?count=100&query=%2Bsurname%3A'
adres_p2 = '*%20%2Bmarriage_year%3A'
adres_p3 = '~&collection_id='

##########################################################
# OPEN BROWSER (use tor proxy)
# TOR NEED TO BE RUNNING WHEN DOING THIS
##########################################################

profile=webdriver.FirefoxProfile()
profile.set_preference('network.proxy.type', 1)
profile.set_preference('network.proxy.socks', '127.0.0.1')
profile.set_preference('network.proxy.socks_port', 9050)
browser=webdriver.Firefox(profile)
browser.implicitly_wait(10) 

##########################################################
# LOOP OVER ALL YEARS AND LETTERS OF THE ALPHABET
##########################################################

# YEARS
for y in range(1840,1851) :

	print 'DOING YEAR ' + str(y)

	# LETTERS
	for letter in list(string.ascii_uppercase) :

		print ' DOING LETTER ' + letter

		###############################################
		# Skip if done
		###############################################	

		done_records_doc = open(done_filename, 'r')
		done_records = csv.DictReader(done_records_doc,delimiter='\t', restval='',lineterminator='\n')
		if any(item['state']== state and  item['year'] == str(y) and item['letter'] == letter and item['counter'] == '' for item in done_records): 
			print '  ALREADY DONE ' + letter + ' FOR STATE' + state + ' IN YEAR ' + str(y)
			continue

		###############################################
		# Starting adress
		###############################################	

		adres = adres_p1 + letter + adres_p2 + str(y) + '-' + str(y) + adres_p3 + str(col_id)

		###############################################
		# Go faster : do 100 records at a time by changing adress bar
		###############################################	

		adres = re.sub('count=[0-9]*','count=100', adres, count=1)

		###############################################
		# LOAD FIRST PAGE OF RESULTS 
		###############################################

		browser.get(adres)

		###############################################
		# Wait for # of results to be loaded
		# and robustly relaunch if connections drops
		# or page does not load
		###############################################

		nores = 0 
		attemps = 1
		while True :

			# Check if found results
			soup = BeautifulSoup(browser.page_source)
			if soup.findAll(attrs={'data-test' : 'totalResults'}) != [] :
				# print soup.findAll(attrs={'data-test' : 'totalResults'})
				print '  FOUND RESULTS FOR THIS LETTER AND YEAR'
				break

			# Check if no found results

			if re.search('No records found for >',str(soup)) is not None :
				nores = 1
				print "  FOUND NO RESULTS FOR THIS LETTER AND YEAR"
				break

			# Reload if waited for 60 seconds

			if attemps % 60 == 0 and attemps !=0 :
				print '  WAITED FOR 60 SECONDS, reloading '
				browser.quit()
				profile=webdriver.FirefoxProfile()
				profile.set_preference('network.proxy.type', 1)
				profile.set_preference('network.proxy.socks', '127.0.0.1')
				profile.set_preference('network.proxy.socks_port', 9050)
				browser=webdriver.Firefox(profile)
				browser.get(adres)

			# Wait 1 seconds and update counter if page still no loaded

			sleep(1)
			print '  STILL NOT LOADED : WAITING'
			attemps = attemps + 1


		###############################################
		# Skip if no results and record it
		###############################################

		if nores == 1 :
			print ' RECORDING AND CONTINUING'
			nores_records_doc = open(nores_filename, 'a')
			nores_records = csv.DictWriter(nores_records_doc,fieldnames=nores_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')
			rec = {}
			rec['state'] = state
			rec['year'] = y
			rec['letter'] = letter
			nores_records.writerow(rec)
			nores_records_doc.close()
			continue

		###############################################
		# Get # of results
		###############################################

		# Get number of results

		totres = str(soup.findAll(attrs={'data-test' : 'totalResults'})[0])
		totres = int(re.search('sults">([,0-9]*)</span>',totres).group(1).replace(',',''))
		print '  NUMBER OF RESULTS FOUND : ' + str(totres)



		###############################################
		# Now loop through all results
		###############################################

		# Initiate counter

		maderecords = 0
		counter = maderecords
		maxcounter = 0


		# loop as long as total # of records not scraped
		# We are scraping the max # of records allowed by the website (100)

		while maxcounter < totres:

			maxcounter = counter + 100
			print '    Doing records ' + str(counter) + ' to ' + str(maxcounter) + ' out of ' + str(totres)
			
			# Skip if already done (as recorded in done_filename file)

			done_records_doc = open(done_filename, 'r')
			done_records = csv.DictReader(done_records_doc,delimiter='\t', restval='',lineterminator='\n')
			if any(item['state']== state and  item['year'] == str(y) and item['letter'] == letter and item['counter'] == str(counter) for item in done_records): 
				print '     ALREADY DONE COUNTERS ' + str(counter) + ' FOR THIS STATE'
				maderecords = counter + 100
				counter = maderecords
				continue

			# Modify URL to get the good results (offset by the # of already done records)

			offset = '&offset=' + str(counter)
			adres2 = adres + offset

			# Open email adres

			browser.get('')
			browser.get(adres2)
			print '     page loaded'
			

			# Wait for results to be loaded
			# and robustly reload or restart the browser
			# if connection drops

			attemps = 0

			while True :

				
				# Parse records

				soup = BeautifulSoup(browser.page_source)
				records = scrape_res(soup)

				# Check if found results

				if len(records)==0 :
					print "     No record found : waiting"
				if len(records)>0 :
					print '     ' + str(len(records)) + ' records found'
					break

				# Reload if waited for 60 seconds without success

				if attemps % 30 == 0 and attemps!=0 :
					print '   WAITED FOR 30 SECONDS, reloading '
					browser.quit()
					profile=webdriver.FirefoxProfile()
					profile.set_preference('network.proxy.type', 1)
					profile.set_preference('network.proxy.socks', '127.0.0.1')
					profile.set_preference('network.proxy.socks_port', 9050)
					browser=webdriver.Firefox(profile)
					browser.get(adres)

				# Wait 1 seconds and update counter if 
				# records are still not loaded

				sleep(1)
				attemps = attemps + 1

			 # Record problem in file prob_filename 
			 # if less than 100 or remaining # of records

			remaining = min(100,totres-counter)
			if len(records)!=remaining :
				print ' NOT EXPECTED # OF RECORDS, expected ' + str(remaining) + ' and found ' + str(len(records))
				prob_records_doc = open(prob_filename, 'a')
				prob_records = csv.DictWriter(prob_records_doc,fieldnames=prob_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')
				rec = {}
				rec['state'] = state
				rec['year'] = y
				rec['letter'] = letter
				rec['counter'] = counter
				rec['prob'] = 'NO GOOD NUMBER OF RESULTS'
				rec['expected'] = str(remaining)
				rec['found'] = str(len(records))
				prob_records.writerow(rec)
				prob_records_doc.close()

			# OLD CODE TO BE DISCARDED IN LAST VERSION
			# 	print 'PROBLEM LESS THAN 100 RECORDS'
			# 	inp = raw_input('PRESS C TO CONTINUE, R to restart, B to BREAK')
			# 	while True :
			# 		if inp == 'C' :
			# 			break
			# 		elif inp == 'B' :
			# 			breakos = 'B'
			# 			break
			# 		elif inp == 'R' :
			# 			continuos = 'C'
			# 			continue
			# 		else :
			# 			print 'TYPE C OR B, try again'
			# 			inp = raw_input('PRESS C TO CONTINUE, R to restart, B to BREAK')
			# if continuos == 'C' :
			# 	print 'RESTARTING'
			# 	continue 
			# if breakos == 'B':
			# 	print 'BREAKING LOOP'
			# 	break

			# Save records in "filename" document

			act_records_doc = open(filename, 'a')
			act_records = csv.DictWriter(act_records_doc,fieldnames=act_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')
			for n,rec in enumerate(records) :
				rec['count'] = n + counter
				rec['state'] = state
				rec['year'] = y
				rec['letter'] = letter
				rec['counter'] = counter
				rec['totres'] = totres
				act_records.writerow(rec)
			act_records_doc.close()
			print '     Appended ' + str(n+1) + ' records'

			
			# Record letter and counter as done in "done_filename" document

			done_records_doc = open(done_filename, 'a')
			done_records = csv.DictWriter(done_records_doc,fieldnames=done_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')
			rec = {}
			rec['state'] = state
			rec['year'] = y
			rec['letter'] = letter
			rec['counter'] = counter
			rec['totres'] = totres
			done_records.writerow(rec)
			done_records_doc.close()

			# Go to next records (update the counters)	

			maderecords = counter + n + 1
			counter = maderecords

		# Record letter as all done in "done_filename" document

		done_records_doc = open(done_filename, 'a')
		done_records = csv.DictWriter(done_records_doc,fieldnames=done_keys,restval='',extrasaction='ignore',delimiter='\t',lineterminator='\n')
		rec = {}
		rec['state'] = state
		rec['year'] = y
		rec['letter'] = letter
		done_records.writerow(rec)
		done_records_doc.close()			

		# LOOP IS GOING TO NEXT LETTER/STATE HERE

