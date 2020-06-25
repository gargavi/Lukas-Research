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
import multiprocessing
from multiprocessing import Pool, cpu_count

## make a copy of this and run it somewhere else, it should still work no matter where you run it on your computer
## provided that the you make the adjustments below
## need to put own username and password.
## need to change the name of the download directory (line 18), chromedriver (line 20) and picture location (line 92)
## changing the directory should really only mean changing the "aviga" to your own computer's named user



chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : "C:\\Users\\aviga\\Dropbox\\SafetyNetsUS\\rawdata\\NY1892\\pictures\\",  "directory_upgrade": True}
chromeOptions.add_experimental_option("prefs",prefs)
chromedriver = "/Users/aviga/Dropbox/SafetyNetsUS/rawdata/NY1892/chromedriver.exe"
driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)




direct_link =  "https://www.familysearch.org/search/record/results?q.birthLikePlace=New%20York&f.collectionId=1529100&m.defaultFacets=on&m.queryRequireDefault=on&m.facetNestCollectionInCategory=on&count=100&offset="
files = os.listdir("./csv")
files = [file[:-4] for file in files]


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




def get_counties():
    if "counties" in files:
        with open('./csv/counties.csv', newline = "") as f:
            reader  = csv.reader(f)
            data = list(reader)
            print(data)
            return data[0]
    else:
        driver.get(
            'https://www.familysearch.org/search/image/index?owc=https://www.familysearch.org/service/cds/recapi/collections/1529100/waypoints')
        try:
            login()
        except:
            print("no need to log in")
        lst = driver.find_element_by_xpath('//*[@id="ImageViewer"]/div[1]/div/fs-waypoints/fs-waypoint-browse-pane/ul')
        items = lst.find_elements_by_tag_name("li")
        counties = []
        for item in items:
            counties.append(item.find_element_by_tag_name("a").text)
        with open("./csv/counties.csv", 'w') as countyfile:
            wr = csv.writer(countyfile)
            wr.writerow(counties)
        return counties





def run_total(counties):
    while True:
        try:
            driver.get('https://www.familysearch.org/search/image/index?owc=https://www.familysearch.org/service/cds/recapi/collections/1529100/waypoints')
            try:
                login()
            except:
                print("no need to log in")
            print(counties)
            for county in counties:
                time.sleep(3)
                driver.find_element_by_xpath("//a[contains(text(), '" + county + "')]").click()
                districts = []
                lst = driver.find_element_by_xpath('//*[@id="ImageViewer"]/div[1]/div/fs-waypoints/fs-waypoint-browse-pane/ul')
                items = lst.find_elements_by_tag_name("li")
                for item in items:
                    districts.append(item.find_element_by_tag_name("a").text)
                for district in districts:
                    all_data = {}
                    if district != "" and (county.replace(" ", "") + district.replace(" ", "") not in files):
                        # try:
                        overall_num = 0
                        time.sleep(2)
                        try:
                            range_name = driver.find_element_by_xpath('//*[@id="ImageViewer"]/div[1]/div/fs-waypoints/fs-waypoint-crumbs/nav/ul/li[3]/a')
                            range_name.click()
                        except:
                            print("No need to go back")
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
                            list_of_files = glob.glob('/Users/aviga/Dropbox/SafetyNetsUS/rawdata/NY1892/pictures/*')
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
                                        else:
                                            all_data[overall_num][values[k]] = overall_num
                                        k += 1
                                    except:
                                        print("Failed element at row {} cell {} of district {} of county {}".format(j+ 1, k + 1, district, county))
                                        break
                                        k += 1

                                all_data[overall_num]["picture_name"] = latest_file
                                overall_num += 1
                                j += 1

                            print("finished", i)
                            # click toward next picture
                            next_button = driver.find_element_by_xpath("//*[@id='ImageViewer']/div[2]/div[3]/div[1]/span[3]")
                            next_button.click()
                            i += 1
                            time.sleep(2)
                        with open("./csv/" + county.replace(" ", "") + district.replace(" ","") +  ".csv", "w", newline='') as f:
                            updated_values = values + ["district", "county", "picture_name"]
                            w = csv.DictWriter(f, updated_values )
                            w.writeheader()
                            for k in all_data.keys():
                                w.writerow({field: all_data[k].get(field) or " " for field in updated_values})

                driver.find_element_by_xpath('//*[@id="ImageViewer"]/div[1]/div/fs-waypoints/fs-waypoint-crumbs/nav/ul/li[2]/a').click()
        except Exception as e:
            print(e)

def run_parallel():

    all_counties = get_counties()
    cpus = cpu_count() - 1
    print(cpus)
    amount = int(len(all_counties) / cpus)
    jobs = []
    for i in range(cpus):
        rel_counties = all_counties[i * amount: min((i+1) *amount, len(all_counties) + 1)]
        pool = multiprocessing.Process(target=run_total, args=(rel_counties, ))
        jobs.append(pool)
        pool.start()


def run_parallel_2():
    pool = Pool()
    all_counties = get_counties()
    cpus = cpu_count() - 1
    amount = int(len(all_counties)/cpus)
    print(cpus, amount)
    for i in range(cpus):
        start = i * amount
        end = min((i+1)*amount, len(all_counties)+1)
        print(start, end)
        rel_counties = all_counties[start: end]
        print(rel_counties)
        pool.apply_async(func=run_total, args = (rel_counties, ))
    pool.close()
    pool.join()

def run_one():
    all_counties = get_counties()[1:]
    run_total(all_counties)

if __name__ == '__main__':
    run_one()

