from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

### SAMPLE DATA ###
DATE = "02/13/2019"
TIME_S = "7:00 PM"
TIME_E = "8:00 PM"
CAPACITY = 4


def initialize_browser():
    browser = webdriver.Chrome('chromedriver/chromedriver')

    browser.get('https://ems.haas.berkeley.edu/')

    wait = WebDriverWait(browser, 10)
    signin_tab = wait.until(EC.element_to_be_clickable((By.ID, 'my-home-tab')))
    signin_tab.click()

    user_id = wait.until(EC.element_to_be_clickable((By.ID, 'userID_input')))
    user_id.clear()
    user_id.send_keys("sujaksh")

    user_id = wait.until(EC.element_to_be_clickable((By.ID, 'password_input')))
    user_id.clear()
    user_id.send_keys("Thirteen-1=99" + Keys.RETURN)

    return browser


def create_reservation(browser, date, start, end, min_capacity):
    wait = WebDriverWait(browser, 10)
    button = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@title="Create A Reservation"]')))
    button.click()
    button = wait.until(EC.element_to_be_clickable((By.XPATH,'//button[text()="book now"]')))
    button.click()

    info = wait.until(EC.element_to_be_clickable((By.ID, 'booking-date-input')))
    info.clear()
    info.send_keys(date)

    info = wait.until(EC.element_to_be_clickable((By.XPATH,'//div[@id="booking-start"]/input')))
    info.clear()
    info.send_keys(start)
    info = wait.until(EC.element_to_be_clickable((By.XPATH,'//div[@id="booking-end"]/input')))
    info.clear()
    info.send_keys(end)

    button = wait.until(EC.element_to_be_clickable((By.XPATH,'//div[@id="location-filter-container"]/div[2]/button')))
    button.click()

    sleep(2)
    button = wait.until(EC.element_to_be_clickable((By.XPATH,'//ul[@id="result-tabs"]/li[1]/a')))
    button.click()

    try:
        wait.until(EC.element_to_be_clickable((By.XPATH,'//table[@id="available-list"]')))
    except:
        print("No rooms available")

    entries = browser.find_elements_by_xpath('//table[@id="available-list"]/tbody/tr')
    best_room   = None
    max_cap = 0
    for i in range(1, len(entries)):
        room_name     = entries[i].find_element_by_xpath('.//td[3]/a') 
        room_capacity = entries[i].find_element_by_xpath('.//td[8]')  
        room_capacity = int(room_capacity.text)
        if room_capacity > max_cap and room_capacity >= min_capacity and "Room" in room_name.text:
            max_cap = room_capacity
            best_room = i
            best_room_name = room_name.text
    if best_room:
        selected = entries[best_room]
        print(best_room)
        print(best_room_name)
        selected.find_element_by_xpath('//td/a').click()
    else:
        print("No room found")
    
    button = wait.until(EC.element_to_be_clickable((By.XPATH,'//button[@id="next-step-btn"]')))
    button.click()

    info = wait.until(EC.element_to_be_clickable((By.XPATH,'//input[@id="event-name"]')))
    info.send_keys("private")
    info = wait.until(EC.element_to_be_clickable((By.XPATH,'//input[@id="1stContactPhone1"]')))
    info.send_keys("1")

    button = wait.until(EC.element_to_be_clickable((By.XPATH,'//button[text()="Create Reservation"]')))
    button.click()

session = initialize_browser()
create_reservation(session, DATE, TIME_S, TIME_E, CAPACITY)
session.quit()
