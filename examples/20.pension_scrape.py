#!/usr/bin/env python
# coding: utf-8

# In[11]:


# load packages
import re
import csv
import time
import itertools
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# set dowload location [todo: clarify the path, download to dropbox]
#options = webdriver.ChromeOptions()
#options.add_argument("download.default_directory = /Users/xianghongwei/Desktop/Research/record_pictures")
#driver = webdriver.Chrome(options=options)


# In[67]:


# open web page
#river = webdriver.Chrome('/usr/local/bin/chromedriver')
driver = webdriver.Chrome("/Users/aviga/Documents/Code/Drivers/chromedriver.exe")
driver.get('https://www.familysearch.org/search/collection/1919699')
driver.implicitly_wait(10) 

# go to browse page
browse = driver.find_element_by_xpath("//*[@id='main']/article/section[1]/a")
browse.click()
driver.implicitly_wait(10) 

# sign in
username = driver.find_element_by_id("userName")
username.send_keys("vv1204@berkeley.edu")
password = driver.find_element_by_id("password")
password.send_keys("Xhwvv@1204")
driver.find_element_by_xpath("//*[@id='login']/span").click()
time.sleep(30)


# In[ ]:


# get list of surname ranges
lst = driver.find_element_by_xpath("//*[@class='film-viewer-header flex-container']/fs-waypoints/fs-waypoint-browse-pane/ul")
items = lst.find_elements_by_tag_name("li")
names = []
for item in items:
    names.append(item.find_element_by_tag_name("a").text)


# In[21]:


# create a nested_dict to save all infos
fields = ["name", "date", "place", "ben_name", "file_name"]
metadata = {}

# save info and image for each individual
def save(index):
    
    # save info in image index section
    metadata[index] = {}
    metadata[index]["name"] = driver.find_element_by_xpath("//*[@id='image-index']/div[3]/div[2]/table/tbody/tr/td[2]").text
    metadata[index]["date"] = driver.find_element_by_xpath("//*[@id='image-index']/div[3]/div[2]/table/tbody/tr/td[4]").text
    metadata[index]["place"] = driver.find_element_by_xpath("//*[@id='image-index']/div[3]/div[2]/table/tbody/tr/td[5]").text
    metadata[index]["ben_name"] = driver.find_element_by_xpath("//*[@id='image-index']/div[3]/div[2]/table/tbody/tr/td[6]").text
    print(metadata[index])
    # download image
    download = driver.find_element_by_xpath("//*[@id='saveLi']/a")
    download.click()
    time.sleep(10)
    
    ## TODO: record downloaded file name
    # switch to new tab
    driver.execute_script("window.open()")
    driver.switch_to.window(driver.window_handles[-1])
    # navigate to chrome downloads
    driver.get('chrome://downloads')
    time.sleep(5)
    # find the latest file name
    if len(driver.find_elements_by_id("file-link")) != 0:
        metadata[index]["file_name"] = driver.find_element_by_xpath("//*[@id='file-link']").text
    else:
        metadata[index]["file_name"] = "Download failed"
    ## TODO: how to switch back to previous window


# In[ ]:


# loop over all surname ranges
i = 1
for name in names:
    try:
        # get to the name page
        driver.find_element_by_xpath("//a[contains(text(), '" + name + "')]").click()
        driver.implicitly_wait(10)

        # get the total number of pictures in this name range
        num = driver.find_element_by_xpath("//*[@id='openSDPagerInputContainer2']/label[2]").text
        num = re.sub("\D", "", num)
        num = int(num)
        # loop through all pictures
        i = 1
        while i <= num:
            # save and download if the image contains indexes
            if len(driver.find_elements_by_xpath("//*[@title='Name']")) != 0:
                index = name + " " + str(i)
                save(index)
            # click toward next picture
            next_button = driver.find_element_by_xpath("//*[@id='ImageViewer']/div[2]/div[3]/div[1]/span[3]")
            next_button.click()
            i += 1

        # get back to the range page
    except Exception as e:
        print(e)
        print(name)

    time.sleep(5)
    range_name = driver.find_element_by_xpath(
        '//*[@id="ImageViewer"]/div[1]/div/fs-waypoints/fs-waypoint-crumbs/nav/ul/li[2]/a')
    range_name.click()


# In[70]:


# export metadata to csv
with open("pension_record.csv", "w", newline='') as f:
    w = csv.DictWriter(f, fields)
    w.writeheader()
    for k in metadata:
        w.writerow({field: metadata[k].get(field) or k for field in fields})


# In[ ]:


# close all browsers and end the driver
driver.quit()

