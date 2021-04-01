import csv
import io
from selenium import webdriver
from selenium.common import exceptions
import sys
import time

def linkurl():
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver=webdriver.Chrome(options=options, executable_path=r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')

    driver.get("https://www.youtube.com/feed/explore")
    driver.maximize_window()
    time.sleep(10)

    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print("Scraping progress")
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    try : 
        elemen = driver.find_element_by_xpath("//ytd-thumbnail[@class='style-scope ytd-video-renderer']/a").get_attribute('href')

        print(elemen)
    except exceptions.NoSuchElementException:
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)
    
    for link in zip(elemen):
        print(link.text)

    driver.close()

if __name__ == "__main__":
    linkurl()