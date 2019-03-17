from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import random
import re
import string

### SAMPLE DATA ###
DATE = "03/14/2019"
TIME_S = "08:00 AM"
TIME_E = "10:00 AM"
CAPACITY = "3"

month_trans = {
        "Jan": '1',
        "Feb": '2',
        "Mar": '3',
        "Apr": '4',
        "May": '5',
        "Jun": '6',
        "Jul": '7',
        "Aug": '8',
        "Sep": '9',
        "Oct": '10',
        "Nov": '11',
        "Dec": '12',

        }

def verify_info(date, start, end, min_capacity):
    verified = True
    date_parsed = date.split("/")
    tmp = (len(date_parsed) == 3) and \
            (len(date_parsed[0]) == 2) and \
            date_parsed[0].isdigit() and \
            (len(date_parsed[1]) == 2) and \
            date_parsed[1].isdigit() and \
            (len(date_parsed[2]) == 4) and \
            date_parsed[2].isdigit() 
    verified = verified and tmp

    start_parsed = re.split(' |:', start)
    tmp = (len(start_parsed) == 3) and \
            (len(start_parsed[0]) == 2) and \
            start_parsed[0].isdigit() and \
            (len(start_parsed[1]) == 2) and \
            start_parsed[1].isdigit() and \
            (
                    (start_parsed[2] == 'AM') or \
                        (start_parsed[2] == 'PM')
            )
    verified = verified and tmp

    end_parsed = re.split(' |:', end)
    tmp = (len(end_parsed) == 3) and \
            (len(end_parsed[0]) == 2) and \
            end_parsed[0].isdigit()   and \
            (len(end_parsed[1]) == 2) and \
            end_parsed[1].isdigit()   and \
            (
                    (end_parsed[2] == 'AM') or \
                        (end_parsed[2] == 'PM')
            )
    verified = verified and tmp

    verified = verified and min_capacity.isdigit()

    

    return True

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


def input_time(wait, date, start, end):
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

def list_rooms(wait, browser):
    button = wait.until(EC.element_to_be_clickable((By.XPATH,'//div[@id="location-filter-container"]/div[2]/button')))
    button.click()

    sleep(2)
    button = wait.until(EC.element_to_be_clickable((By.XPATH,'//ul[@id="result-tabs"]/li[1]/a')))
    button.click()

    sleep(2)
    entries = browser.find_elements_by_xpath('//table[@id="available-list"]/tbody/tr')
    if len(entries):
        return entries
    
    return False

def finalize_reservation(wait):
    button = wait.until(EC.element_to_be_clickable((By.XPATH,'//button[@id="next-step-btn"]')))
    button.click()

    info = wait.until(EC.element_to_be_clickable((By.XPATH,'//input[@id="event-name"]')))
    info.send_keys("private")
    info = wait.until(EC.element_to_be_clickable((By.XPATH,'//input[@id="1stContactPhone1"]')))
    info.send_keys("1")

    sleep(2)
    button = wait.until(EC.element_to_be_clickable((By.XPATH,'//button[text()="Create Reservation"]')))
    button.click()

def get_rooms(date, start, end, min_capacity):
    result = get_available_rooms(date,start,end,min_capacity)
    if not result: return []

    browser, wait, rooms, entries = result
    browser.quit()
    return [room for room in rooms if room[1] >= 0]

def get_available_rooms(date, start, end, min_capacity):

    # Preprocess and check inputs
    if not verify_info(date, start, end, min_capacity):
        return False

    min_capacity = int(min_capacity)
    date = re.split(" |,",date)
    date = [el for el in date if el != ""]
    date[0] = month_trans[date[0]]
    date = '/'.join(date)

    browser = initialize_browser()
    wait = WebDriverWait(browser, 10)
    input_time(wait, date, start, end)
    
    entries = list_rooms(wait, browser)
    if not entries:
        return False

    #entries = browser.find_elements_by_xpath('//table[@id="available-list"]/tbody/tr')
    rooms = []
    for i in range(1, len(entries)):
        room_name     = entries[i].find_element_by_xpath('.//td[3]/a').text 
        room_capacity = entries[i].find_element_by_xpath('.//td[8]')  
        room_capacity = int(room_capacity.text)
        if room_capacity >= min_capacity:
            rooms.append((room_name, room_capacity))
        else:
            rooms.append((room_name, -1))
    
    return (browser, wait, rooms, entries)

def create_reservation(date, start, end, min_capacity):

    result = get_available_rooms(date,start,end,min_capacity)
    if not result: return False

    min_capacity = int(min_capacity)
    browser, wait, rooms, entries = result

    maximum = min_capacity - 1; max_index = -1
    for i, room in enumerate(rooms):
        if room[1] > maximum:
            maximum = room[1]
            max_index = i

    if max_index >= 0:
        entries[max_index].find_element_by_xpath('.//td[1]/a').click()
        finalize_reservation(wait)
        token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) \
            + rooms[max_index][0]
    else:
        token = False
    
    browser.quit()
    return False

#token = create_reservation(DATE, TIME_S, TIME_E, CAPACITY)
#print(token)
