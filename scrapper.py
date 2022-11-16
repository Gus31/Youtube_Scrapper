import os
import sys
from time import sleep
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from parsel import Selector

def get_title(selector, output):
    output["outputs"][-1]["title"] = selector.css(".title .ytd-video-primary-info-renderer::text").get()
    return output

def get_channel(selector, output):
    output["outputs"][-1]["channel"] = selector.css("#channel-name a::text").get()
    return output

def get_description(selector, output):
    output["outputs"][-1]["description"] = selector.css(".ytd-expandable-video-description-body-renderer span:nth-child(1)::text").get()
    return output

def get_links(selector, output):
    pass 

def get_video_id(soup, output):
    output["outputs"][-1]["video_id"] = soup.find("ytd-watch-flexy", class_="style-scope ytd-page-manager hide-skeleton")['video-id']
    return output

def get_comments(soup, output):
    N = 15
    comments = []
    comments_soup = soup.find_all("ytd-comment-thread-renderer", {"class": "style-scope ytd-item-section-renderer"}, limit = N)
    for comment in comments_soup:
        comments.append(comment.find("yt-formatted-string", {"id": "content-text"}).text)
    output["outputs"][-1]["comments"] = comments
    
    return output

def open_driver_and_soup(youtube_url):
    s = FirefoxService(GeckoDriverManager().install())
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(service=s, options=options)
    driver.get(youtube_url)
    # we let the driver load the page
    sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    return driver, soup

def close_driver(driver):
    driver.quit()

def scroll(youtube_url):
    driver, soup = open_driver_and_soup(youtube_url)
    element = driver.find_element(By.XPATH, "//*[@id=\"comments\"]")
    driver.execute_script("arguments[0].scrollIntoView();", element)
    sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    selector = Selector(driver.page_source)
    close_driver(driver)

    return selector, soup

def scrape_data(selector, soup, output):
    output = get_title(selector, output)
    output = get_channel(selector, output)
    output = get_description(selector, output)
    output = get_video_id(soup, output)
    output = get_comments(soup, output)

    return output

def main():
    if sys.argv.__len__() != 5:
        sys.exit("Nombre d'arguments incorrects, essayez sous la forme \"python scrapper.py --input input.json --output output.json\"")

    json_input = sys.argv[2]
    if not os.path.isfile(json_input):
        sys.exit("Fichier d'entrée json introuvable")       

    with open(json_input) as f:
        inputs = json.load(f)["video_id"]
    

    output = {}
    output["outputs"] = []
    with open("output.json", "w") as f:
        for input in inputs:
            output["outputs"].append({})
            youtube_url = f"https://www.youtube.com/watch?v={input}"
            selector, soup = scroll(youtube_url)
            output = scrape_data(selector, soup, output)
        json.dump(output, f, ensure_ascii=False)

if __name__ == "__main__":
    main()