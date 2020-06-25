#-*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
#       Veterans
#
#       FIRST VERSION  February 21, 2015
#       THIS VERSION   April    20, 2015
#       LAST RUN       April    20, 2015
#
#       LAST REVISOR   BC
#
#       This creates a list of registration boards, with number of people registered for *ALL* boards
#               - it is a preliminary sanity check to make sure that the scraping of people goes well
#               - note that the number of people recovered will be an upper bound.
#                 this is because I look for people that had "any event" in the 10% counties.
#                 Hence, people registered in other registration boards may be associated to these counties for other reasons.
#                 These people will not be scraped in the next procedures.
#                 
#       The procedure is based on procedure 9a_
# ---------------------------------------------------------------------------

###############################################################################################
####                                 PLAN OF THE PROCEDURE                                 ####
####                                                                                       ####
####        1. Import libraries                                                            ####
####        2. Initialize the procedure: create a dictionary for US states & open files    ####
####        3. Initialize Selenium webdriver                                               ####
####        4. Loop over all boards and extract necessary information                      ####
####        5. Set search parameters                                                       ####
####              a. Handle bad result matches                                             ####
####                   i. Non-cities: add "county" to the name                             ####
####                  ii. Cities: try "0" + board number                                   ####
####              b. Handle good results                                                   ####
####        6. Get the info about how many people there are and export it                  ####
###############################################################################################



###############################################################################################
####        1. Import libraries                                                            ####
###############################################################################################
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui  import Select
from selenium.webdriver.chrome.options import Options
from unidecode import unidecode
from bs4 import BeautifulSoup
from msilib import AMD64

###############################################################################################
####        2. Initialize the procedure: create a dictionary for US states & open files    ####
###############################################################################################
states_dictionary = dict(AL = 'Alabama',             \
                         AR = 'Arkansas',            \
                         AZ = 'Arizona',             \
                         CA = 'California',          \
                         CO = 'Colorado',            \
                         CT = 'Connecticut',         \
                         DC = 'District of Columbia',\
                         DE = 'Delaware',            \
                         FL = 'Florida',             \
                         GA = 'Georgia',             \
                         IA = 'Iowa',                \
                         ID = 'Idaho',               \
                         IL = 'Illinois',            \
                         IN = 'Indiana',             \
                         KS = 'Kansas',              \
                         KY = 'Kentucky',            \
                         LA = 'Louisiana',           \
                         MA = 'Massachusetts',       \
                         MD = 'Maryland',            \
                         ME = 'Maine',               \
                         MI = 'Michigan',            \
                         MN = 'Minnesota',           \
                         MO = 'Missouri',            \
                         MS = 'Mississippi',         \
                         MT = 'Montana',             \
                         NC = 'North Carolina',      \
                         ND = 'North Dakota',        \
                         NE = 'Nebraska',            \
                         NH = 'New Hampshire',       \
                         NJ = 'New Jersey',          \
                         NM = 'New Mexico',          \
                         NV = 'Nevada',              \
                         NY = 'New York',            \
                         OH = 'Ohio',                \
                         OK = 'Oklahoma',            \
                         OR = 'Oregon',              \
                         PA = 'Pennsylvania',        \
                         RI = 'Rhode Island',        \
                         SC = 'South Carolina',      \
                         SD = 'South Dakota',        \
                         TN = 'Tennessee',           \
                         TX = 'Texas',               \
                         UT = 'Utah',                \
                         VA = 'Virginia',            \
                         VT = 'Vermont',             \
                         WA = 'Washington',          \
                         WI = 'Wisconsin',           \
                         WV = 'West Virginia',       \
                         WY = 'Wyoming')

boards      = open(r"D:\Dropbox\Veterans\rawdata\Registration1917\Boards.txt")
boards_list = open(r"D:\Dropbox\Veterans\rawdata\Registration1917\Boards-cleaned.txt","a")

###############################################################################################
####        3. Initialize Selenium webdriver                                               ####
###############################################################################################
options = webdriver.ChromeOptions() 
#options.add_argument("user-data-dir=C:\\Users\\Bruno\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument("user-data-dir=D:\\ChromeSettings\\User Data")

driver   = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver',chrome_options=options)
driver.implicitly_wait(10)

###############################################################################################
####        4. Loop over the 10% sample boards and extract necessary information           ####
###############################################################################################
for num, board in enumerate(boards.readlines()):
    parse_board = board.split(";")
    
    active_state_abb  = parse_board[0]
    active_state      = states_dictionary.get(active_state_abb)
    active_board_id   = parse_board[2]
    active_board_raw  = parse_board[5]
    active_board_nr   = parse_board[6]
    active_board_city = parse_board[7]    # =1 it's a city
    active_board_nonr = parse_board[19]
    
    if os.path.isfile(r"D:\Dropbox\RegistrationCards\boards\\" + active_state_abb + "-" + str(active_board_id) + ".txt"):
        continue
    
    boards_list = open(r"D:\Dropbox\RegistrationCards\boards\\" + active_state_abb + "-" + str(active_board_id) + ".txt","a")

    if active_state_abb == "IN" and active_board_raw == "Wayne" and active_board_nr != "":
        boards_list.write(active_state + ";" + active_board_id  + ";;;.\n")
        boards_list.close()
        continue

    if   active_state_abb == "AR" and active_board_raw == "Little Rock":
        active_board = "Little Rock, Pulaski"
    elif active_state_abb == "CA" and active_board_raw == "San Francisco":
        active_board = "San Francisco, San Francisco"         # Otherwise it gets San Francisco county
    elif active_state_abb == "CO" and active_board_raw == "Denver":
        active_board = "Denver, Denver"
    elif active_state_abb == "DC":
        active_board = "Washington, District of Columbia"
    elif active_state_abb == "GA" and active_board_raw == "Macon" and active_board_nr != "":
        active_board = "Macon, Bibb"
    elif active_state_abb == "IA" and active_board_raw == "Sioux City":
        active_board = "Sioux City, Woodbury"
    elif active_state_abb == "IL" and active_board_raw == "Chicago":
        active_board = "Chicago, Cook"
    elif active_state_abb == "LA" and active_board_raw == "New Orleans":
        active_board = "New Orleans, Orleans"
    elif active_state_abb == "LA" and active_board_raw == "West Baton Rouge":
        active_board = "West Baton Rouge Parish"
    elif active_state_abb == "LA" and active_board_raw == "East Baton Rouge":
        active_board = "East Baton Rouge Parish"
    elif active_state_abb == "LA" and active_board_raw == "St Martin":
        active_board = "St Martin Parish"
    elif active_state_abb == "MD" and active_board_raw == "Baltimore" and str(active_board_city) == "1":
        active_board = "Baltimore, Independent Cities"
    elif active_state_abb == "MD" and active_board_raw == "Baltimore" and str(active_board_city) == "":
        active_board = "Baltimore county"
    elif active_state_abb == "MN" and active_board_raw  == "St Paul":
        active_board = "St Paul, Ramsey"
    elif active_state_abb == "MN" and active_board_raw  == "Minneapolis":
        active_board = "Minneapolis, Hennepin"
    elif active_state_abb == "NE" and active_board_raw  == "Omaha":
        active_board = "Omaha, Douglas"
    elif active_state_abb == "NE" and active_board_raw  == "Lincoln" and str(active_board_city) == "1":
        active_board = "Lincoln, Lancaster"
    elif active_state_abb == "NE" and active_board_raw  == "Lincoln" and str(active_board_city) == "":
        active_board = "Lincoln County"
    elif active_state_abb == "NJ" and active_board_raw  == "Atlantic City":
        active_board = "Atlantic City, Atlantic"
    elif active_state_abb == "NY" and active_board_raw  == "New York":
        active_board = "New York City (All Boroughs)"
    elif active_state_abb == "NY" and active_board_raw  == "Watertown":
        active_board = "Watertown, Jefferson"
    elif active_state_abb == "NY" and active_board_raw  == "Rensselaer":
        active_board = "Rensselaer county"
    elif active_state_abb == "NY" and active_board_raw  == "Rochester":
        active_board = "Rochester, Monroe"
    elif active_state_abb == "OH" and active_board_raw  == "Cincinnati":
        active_board = "Cincinnati, Hamilton"
    elif active_state_abb == "OH" and active_board_raw  == "Columbus":
        active_board = "Columbus, Franklin"
    elif active_state_abb == "OH" and active_board_raw  == "Lima":
        active_board = "Lima, Allen"
    elif active_state_abb == "OH" and active_board_raw  == "Springfield":
        active_board = "Springfield, Clark"
    elif active_state_abb == "OK" and active_board_raw  == "Oklahoma City":
        active_board = "Oklahoma City, Oklahoma"
    elif active_state_abb == "PA" and active_board_raw  == "Philadelphia":
        active_board = "Philadelphia, Philadelphia"
    elif active_state_abb == "RI" and active_board_raw  == "Cranston":
        active_board = "Cranston, Providence"
    elif active_state_abb == "RI" and active_board_raw  == "Lonsdale":
        active_board = "Lonsdale, Providence"
    elif active_state_abb == "RI" and active_board_raw  == "Saunderstown":
        active_board = "Saunderstown, Washington"
    elif active_state_abb == "RI" and active_board_raw  == "Bristol" and str(active_board_city) == "1":
        active_board = "Bristol, Bristol"
    elif active_state_abb == "RI" and active_board_raw  == "Bristol" and str(active_board_city) == "":
        active_board = "Bristol County"
    elif active_state_abb == "RI" and active_board_raw  == "Central Falls":
        active_board = "Central Falls, Providence"
    elif active_state_abb == "TX" and active_board_raw  == "Dallas" and str(active_board_city) == "1":
        active_board = "Dallas, Dallas"
    elif active_state_abb == "TX" and active_board_raw  == "Dallas" and str(active_board_city) == "":
        active_board = "Dallas County"
    elif active_state_abb == "TX" and active_board_raw  == "San Antonio":
        active_board = "San Antonio, Bexar"
    elif active_state_abb == "TX" and active_board_raw  == "Houston" and str(active_board_city) == "1":
        active_board = "Houston, Harris"
    elif active_state_abb == "TX" and active_board_raw  == "Houston" and str(active_board_city) == "":
        active_board = "Houston County"
    elif active_state_abb == "TX" and active_board_raw  == "Fort Worth":
        active_board = "Fort Worth, Tarrant"
    elif active_state_abb == "VA" and active_board_raw  == "Roanoke" and str(active_board_city) == "1":
        active_board = "Roanoke, Roanoke (Independent City)"
    elif active_state_abb == "VA" and active_board_raw  == "Roanoke" and str(active_board_city) == "":
        active_board = "Roanoke County"
    elif active_state_abb == "VA" and active_board_raw  == "Richmond" and str(active_board_city) == "1":
        active_board = "Richmond, Independent Cities"
    elif active_state_abb == "VA" and active_board_raw  == "Richmond" and str(active_board_city) == "":
        active_board = "Richmond County"
    elif active_state_abb == "WI" and active_board_raw  == "Milwaukee":
        active_board = "Milwaukee, Milwaukee"
    elif active_state_abb == "WV" and active_board_raw  == "Wheeling":
        active_board = "Wheeling, Ohio"
        active_board_nr = ""
    else:
        active_board = active_board_raw

    if   active_state_abb == "AR" and active_board_raw == "St Francis":
        active_state = "Arkansas, USA"
    elif active_state_abb == "LA" and (active_board_raw == "West Baton Rouge" or active_board_raw == "East Baton Rouge" or active_board_raw == "St Martin"):
        active_state = "Louisiana, USA"
    elif active_state_abb == "NM" and  active_board_raw == "Guadalupe":
        active_state = "New Mexico, USA"
    elif active_state_abb == "NY" and  active_board_raw == "St Lawrence":
        active_state = "New York, USA"
    
    if int(active_board_nonr) == 1:
        active_board_nr = ""

    if parse_board[6] != "":
        print "I'm looking for records from the board " + active_board + " Nr. " + str(active_board_nr) + " in " + active_state
    else:
        print "I'm looking for records from the board " + active_board + " in " + active_state
    
        
###############################################################################################
####        6. Set search parameters                                                       ####
###############################################################################################
    cohort = 1885
    driver.get("http://search.ancestry.com/search/db.aspx?dbid=6482")
    
    id_any_event       = driver.find_elements_by_xpath("//*[contains(@id, 'sfs__SelfPlace_')]")[0].get_attribute('id')
    id_cohort          = driver.find_elements_by_xpath("//*[@id='sfs_SelfBirthYear']")[0].get_attribute('id')
    driver.find_element_by_id(id_any_event).send_keys(active_board + ", " + active_state)
    driver.find_element_by_id(id_cohort).send_keys(str(cohort))
        
    driver.find_element_by_xpath("//*[@id='sfs_ContentBased']/div[1]/div/fieldset[1]/div[10]/div/div/button").send_keys(" ")
    driver.find_element_by_xpath("//*[@id='sfs_ContentBased']/div[1]/div/fieldset[3]/div[11]/div/div/button[1]").send_keys(" ")
    
    if str(active_board_nr) != "":
        id_board_nr       = driver.find_elements_by_xpath("//*[contains(@id, 'sfs__F0006EAE')]")[0].get_attribute('id')
        id_board_nr_exact = driver.find_elements_by_xpath("//*[contains(@id, 'sfs_sfsFdidTextBoxCtrl-2')]")[0].get_attribute('id')
        
        driver.find_element_by_id(id_board_nr).send_keys(str(active_board_nr))
        driver.find_element_by_id(id_board_nr_exact).send_keys(" ")
    else:
        pass
    
    driver.find_element_by_xpath("//*[@id='sfs_ContentBased']/div[1]/div/div[1]/table/tbody/tr/td[1]/input").submit()
    
###############################################################################################
####        5. Get the info about how many people there are and export it                  ####
####              a. Handle bad result matches                                             ####
###############################################################################################
    try:
        no_results = driver.find_element_by_xpath("//*[@id='badResultMatch']/div/h3").get_attribute('innerHTML')
        driver.get("http://search.ancestry.com/search/db.aspx?dbid=6482")
        
        id_any_event       = driver.find_elements_by_xpath("//*[contains(@id, 'sfs__SelfPlace_')]")[0].get_attribute('id')
        id_cohort          = driver.find_elements_by_xpath("//*[@id='sfs_SelfBirthYear']")[0].get_attribute('id')
        driver.find_element_by_id(id_cohort).send_keys(str(cohort))    
        driver.find_element_by_xpath("//*[@id='sfs_ContentBased']/div[1]/div/fieldset[1]/div[10]/div/div/button").send_keys(" ")
            
###############################################################################################
####                   i. Non-cities: add "county" to the name                             ####
###############################################################################################
        if active_board_city != "1":
            active_board = active_board + " county"

###############################################################################################
####                  ii. Cities: try "0" + board number                                   ####
###############################################################################################
        else:
            active_board_nr = "0" + str(active_board_nr)
            id_board_nr       = driver.find_elements_by_xpath("//*[contains(@id, 'sfs__F0006EAE')]")[0].get_attribute('id')
            id_board_nr_exact = driver.find_elements_by_xpath("//*[contains(@id, 'sfs_sfsFdidTextBoxCtrl-2')]")[0].get_attribute('id')
            
            driver.find_element_by_id(id_board_nr).send_keys(str(active_board_nr))
            driver.find_element_by_id(id_board_nr_exact).send_keys(" ")
        
        driver.find_element_by_id(id_any_event).send_keys(active_board  + ", " + active_state)
        driver.find_element_by_xpath("//*[@id='sfs_ContentBased']/div[1]/div/fieldset[3]/div[11]/div/div/button[1]").send_keys(" ")
        
        driver.find_element_by_xpath("//*[@id='sfs_ContentBased']/div[1]/div/div[1]/table/tbody/tr/td[1]/input").submit()
        
        results = unidecode(driver.find_element_by_xpath("//*[@id='results-header']/h3").get_attribute('innerHTML'))
        if results == results.replace("Results 1-50 of ",""):
            results = results[len(results)-2:len(results)]
        else:
            results = results.replace("Results 1-50 of ","")

###############################################################################################
###              b. Handle good results                                                   ####
###############################################################################################
    except:
        results = unidecode(driver.find_element_by_xpath("//*[@id='results-header']/h3").get_attribute('innerHTML'))
        if results == results.replace("Results 1-50 of ",""):
            results = results[len(results)-2:len(results)]
        else:
            results = results.replace("Results 1-50 of ","")
        
    results = results.replace("\n","")       
    boards_list.write(active_state + ";" + active_board_id  + ";" + active_board + ";" + str(active_board_nr) + ";" + str(results) + "\n")
    boards_list.close()

driver.close()
print "I'm done! :) "
