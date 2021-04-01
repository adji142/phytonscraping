"""
Main script to scrape the comments of any Youtube video.

Example:
    $ python main.py YOUTUBE_VIDEO_URL
"""

import csv
import io
from selenium import webdriver
from selenium.common import exceptions
import sys
import time
import mysql.connector
import re

def demoji(text):
	emoji_pattern = re.compile("["
		u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U00010000-\U0010ffff"
	                           "]+", flags=re.UNICODE)
	return(emoji_pattern.sub(r'', text))

def replacestring(text):
    my_new_string = re.sub('[^a-zA-Z0-9 \n\.]', '', text)
    return(my_new_string)

def scrape(url):
    """
    Extracts the comments from the Youtube video given by the URL.

    Args:
        url (str): The URL to the Youtube video

    Raises:
        selenium.common.exceptions.NoSuchElementException:
        When certain elements to look for cannot be found
    """
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="lagis3nt0s4",
        database="ytdata"
    )
    if db.is_connected():
        print("Berhasilkonek")
    # Note: Download and replace argument with path to the driver executable.
    # Simply download the executable and move it into the webdrivers folder.
    # driver = webdriver.Chrome('./webdrivers/chromedriver')
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver=webdriver.Chrome(options=options, executable_path=r'C:\Program Files\Google\Chrome\Application\chromedriver.exe')

    # Navigates to the URL, maximizes the current window, and
    # then suspends execution for (at least) 5 seconds (this
    # gives time for the page to load).
    driver.get(url)
    driver.maximize_window()
    time.sleep(10)

    try:
        # Extract the elements storing the video title and
        # comment section.
        title = driver.find_element_by_xpath('//*[@id="container"]/h1/yt-formatted-string').text
        comment_section = driver.find_element_by_xpath('//*[@id="comments"]')
        # print(comment_section)
    except exceptions.NoSuchElementException:
        # Note: Youtube may have changed their HTML layouts for
        # videos, so raise an error for sanity sake in case the
        # elements provided cannot be found anymore.
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)

    # Scroll into view the comment section, then allow some time
    # for everything to be loaded as necessary.
    driver.execute_script("arguments[0].scrollIntoView();", comment_section)
    time.sleep(7)

    # Scroll all the way down to the bottom in order to get all the
    # elements loaded (since Youtube dynamically loads them).
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    xindex = 0
    while True:
        # Scroll down 'til "next load".
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

        # Wait to load everything thus far.
        time.sleep(3)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print("Data progress -> " + str(xindex))

        xindex += 1
    # One last scroll just in case.
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    try:
        print("> VIDEO TITLE: " + title + "\n")

        # Extract the elements storing the usernames and comments.
        username_elems = driver.find_elements_by_xpath('//*[@id="author-text"]')
        comment_elems = driver.find_elements_by_xpath('//*[@id="content-text"]')
        # TimeComment = driver.find_element_by_class_name('yt-simple-endpoint.style-scope.yt-formatted-string')
        ChanelName = driver.find_element_by_xpath('//*[@class="yt-simple-endpoint style-scope yt-formatted-string"]')
        # TimeComment = driver.find_element_by_xpath('//*[contains(@class, "published-time-text above-comment style-scope ytd-comment-renderer")]//a[@class="yt-simple-endpoint style-scope yt-formatted-string"]')
        # TimeComment = driver.find_elements_by_xpath('//*[@id="published-time-text"]')

        totalcomments= len(driver.find_elements_by_xpath("""//*[@id="content-text"]"""))
        # print(TimeComment.text)
        youtube_xdata = []
        ccount = 0
        while ccount < totalcomments: 
            youtube_dict ={}
            comment = driver.find_elements_by_xpath('//*[@id="content-text"]')[ccount].text
            authors = driver.find_elements_by_xpath('//a[@id="author-text"]/span')[ccount].text
            comment_posted = driver.find_elements_by_xpath('//*[@class="published-time-text above-comment style-scope ytd-comment-renderer"]/a')[ccount].text
            try:
                replies = driver.find_elements_by_xpath('//*[@id="more-text"]')[ccount].text                    
                if replies =="View reply":
                    replies= 1
                else:
                    replies =replies.replace("View ","")
                    replies =replies.replace(" replies","")
            except:
                replies=""
            
            try:
                upvotes = driver.find_elements_by_xpath('//*[@id="vote-count-middle"]')[ccount].text
            except:
                upvotes = ""

            youtube_dict['comment'] = comment
            youtube_dict['author'] = authors
            youtube_dict['comment_posted'] = comment_posted
            youtube_dict['no_of_replies'] = replies
            youtube_dict['upvotes'] = upvotes
            
            # youtube_xdata.append(youtube_dict)
            # writer.writerow(youtube_dict.values())
            # Insert to databse
            print("Getting Data -> "+ str(ccount) +" / "+ str(totalcomments) +" : "+ authors +" ##> " + comment)
            cursor = db.cursor()

            sql = "INSERT INTO comment values(0,'YouTube','" + replacestring(ChanelName.text.replace("'","").replace("/","-")) + ",','"+ replacestring(title.replace("'","").replace("/","-")) +"',"+ str(ccount) +",'"+ replacestring(authors.replace("'","").replace("/","")) +"','"+ replacestring(comment.replace("'","").replace("/","")) +"','"+ comment_posted.replace("'","").replace("/","") +"','"+ replies.replace("'","").replace("/","") +"','"+ upvotes.replace("'","").replace("/","") +"',now());"
            cursor.execute(sql)
            db.commit()

            ccount = ccount +1

    except exceptions.NoSuchElementException:
        error = "Error: Double check selector OR "
        error += "element may not yet be on the screen at the time of the find operation"
        print(error)
    # line = 0
    # for username, comment in zip(username_elems, comment_elems):
    #     # print(xtime.text.rstrip("\n"))
    #     comentfix = comment.text.replace("'","").replace("/","")
    #     cursor = db.cursor()
    #     sql = "INSERT INTO comment values(0,'"+ replacestring(title.replace("'","").replace("/","-")) +"',"+ str(line) +",'"+ replacestring(username.text.replace("'","").replace("/","")) +"','"+ replacestring(comentfix) +"');"
    #     # print(sql)
    #     cursor.execute(sql)

    #     db.commit()
    #     line += 1

    # with io.open('results.csv', 'w', newline='', encoding="utf-16") as file:
    #     writer = csv.writer(file, delimiter =",", quoting=csv.QUOTE_ALL)
    #     writer.writerow(["Username", "Comment"])
    #     for username, comment in zip(username_elems, comment_elems):
    #         writer.writerow([username.text, comment.text])

    driver.close()

if __name__ == "__main__":
    print("test")
    scrape(sys.argv[1])
