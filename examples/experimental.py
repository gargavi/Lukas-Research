from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd
import glob
import json
import os
import re
import time
import csv


chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : "C:\\Users\\aviga\\Documents\\Code\\Research\\Lukas_L\\downloads\\",  "directory_upgrade": True}
chromeOptions.add_experimental_option("prefs",prefs)
chromedriver = "/Users/aviga/Documents/Code/Drivers/chromedriver.exe"
driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)


## have to log in before doing anything else


def get_content(offset, link):
    link += str(offset)
    driver.get(link)
    driver.find_element_by_id("userName").send_keys("avigarg")
    driver.find_element_by_id("password").send_keys("TestPwd123")
    driver.find_element_by_id("login").click()
    time.sleep(6)
    content = driver.page_source
    soup = BeautifulSoup(content)
    return soup



direct_link =  "https://www.familysearch.org/search/record/results?q.birthLikePlace=New%20York&f.collectionId=1529100&m.defaultFacets=on&m.queryRequireDefault=on&m.facetNestCollectionInCategory=on&count=100&offset="


#soup0 = get_content(0, direct_link)
#print(soup0.find('sr-table', attrs= {'class': "desktop"}))


#Trying to navigate the search page, not working th
#time.sleep(8)
#driver.find_element_by_xpath('/html/body/div[2]/main/div/article/div[2]/section/fs-search-form//form/sf-search-field-group[2]/sf-search-field-group[1]/sf-search-field[1]//span/span/span/input').send_keys(" New York")
#print(BeautifulSoup(driver.page_source).prettify())

#driver.get("https://www.familysearch.org/search/collection/2381996")

def login():
    driver.find_element_by_id("userName").clear()
    driver.find_element_by_id("userName").send_keys("avigarg")
    driver.find_element_by_id("password").send_keys("TestPwd123")
    driver.find_element_by_id("login").click()
    time.sleep(3)

values = ["", "Name", "District", "Gender", "Age", "Age 2", "Citizenship Status",
          "Citizenship Status 2", "Citizenship Status 3", "Race", "Institution", "Birth Year",
          "Birth Year Est", "Birthplace", "Birthplace 2", "Relationship to HoH", "Page NUmber",
          "Record Number", "Digital Folder Number", "Record Number", "Record NUmber 2", "Record NUmber 3" ]


def get_elements(driver, j):
    rows = driver.find_elements_by_xpath('//*[@id="image-index"]/div[3]/div[2]/table/tbody/tr')
    cells = rows[j].find_elements_by_tag_name("td")
    if cells:
        return cells
    else:
        return False


driver.get('https://www.familysearch.org/search/image/index?owc=https://www.familysearch.org/service/cds/recapi/collections/1529100/waypoints')
login()
lst = driver.find_element_by_xpath('//*[@id="ImageViewer"]/div[1]/div/fs-waypoints/fs-waypoint-browse-pane/ul')
items = lst.find_elements_by_tag_name("li")
counties = []
for item in items:
    counties.append(item.find_element_by_tag_name("a").text)

all_data = {}
overall_num = 0

for county in counties:
    time.sleep(3)
    driver.find_element_by_xpath("//a[contains(text(), '" + county + "')]").click()
    districts = []
    lst = driver.find_element_by_xpath('//*[@id="ImageViewer"]/div[1]/div/fs-waypoints/fs-waypoint-browse-pane/ul')
    items = lst.find_elements_by_tag_name("li")
    for item in items:
        districts.append(item.find_element_by_tag_name("a").text)
    driver.find_element_by_xpath("//a[contains(text(), '" + county + "')]").click()
    for district in districts:
        if district != "":
            # try:
            time.sleep(2)
            range_name = driver.find_element_by_xpath('//*[@id="ImageViewer"]/div[1]/div/fs-waypoints/fs-waypoint-crumbs/nav/ul/li[3]/a')
            range_name.click()
            time.sleep(1)
            driver.find_element_by_xpath("//a[contains(text(), '" + district + "')]").click()
            time.sleep(3)
            num = re.sub("\D", "", driver.find_element_by_xpath('//*[@id="openSDPagerInputContainer2"]/label[2]').text)
            if num != "":
                num = int(num)
            else:
                num = 0
            print(num, district)
            i = 1
            driver.implicitly_wait(2)
            while i <= num:
                # save and download if the image contains indexes
                #if len(driver.find_elements_by_xpath("//*[@title='Name']")) != 0:
                num_rows = len(driver.find_elements_by_xpath('//*[@id="image-index"]/div[3]/div[2]/table/tbody/tr'))
                download = driver.find_element_by_xpath("//*[@id='saveLi']/a")
                download.click()
                time.sleep(2)
                list_of_files = glob.glob('/Users/aviga/Documents/Code/Research/Lukas_L/downloads/*')
                latest_file = max(list_of_files, key=os.path.getctime)
                j = 0
                print(num_rows)
                while num_rows > j:
                    all_data[overall_num] = {}
                    all_data[overall_num]["district"] = district
                    all_data[overall_num]["county"] = county
                    k = 0
                    while k < len(values):
                        try:
                            cell = driver.find_element_by_xpath('//*[@id="image-index"]/div[3]/div[2]/table/tbody/tr[{0}]/td[{1}]'.format(j + 1, k + 1))
                            if values[k] != "":
                                all_data[overall_num][values[k]] = cell.text
                            k += 1
                        except:
                            print("Failed element at row {} cell {} of district {} of county {}".format(j+ 1, k + 1, district, county))
                            break
                            k += 1

                    all_data[overall_num]["picture_name"] = latest_file
                    overall_num += 1
                    j += 1


                # click toward next picture
                next_button = driver.find_element_by_xpath("//*[@id='ImageViewer']/div[2]/div[3]/div[1]/span[3]")
                next_button.click()
                i += 1
                time.sleep(2)
    driver.find_element_by_xpath('//*[@id="ImageViewer"]/div[1]/div/fs-waypoints/fs-waypoint-crumbs/nav/ul/li[2]/a').click()

with open("pension_record.csv", "w", newline='') as f:
    w = csv.DictWriter(f, values)
    w.writeheader()
    for k in all_data:
        w.writerow({field: all_data[k].get(field) or k for field in values})
