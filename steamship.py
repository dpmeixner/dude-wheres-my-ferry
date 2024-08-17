# TODO: Error Handling

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pushbullet import Pushbullet
import datetime
import logging
logging.basicConfig(
    filename='log.txt', 
    filemode='w',
    format='%(asctime)s %(message)s', 
    level=logging.INFO)

DEPART_MONTH = "Aug"
DEPART_DAY = 10
DEPART_AFTER = "9:14 am"
DEPART_BEFORE = "5:31 pm"

RETURN_MONTH = "Aug"
RETURN_DAY = 15
RETURN_AFTER = "12:00 am"
RETURN_BEFORE = "11:59 pm"

times = {
    "departures": {
        "after": DEPART_AFTER,
        "before": DEPART_BEFORE
    },
    "returns": {
        "after": RETURN_AFTER,
        "before": RETURN_BEFORE
    },
}

logging.info("Starting program")

url = "https://www.steamshipauthority.com/schedules/availability" 
user_agent = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
pb_key = "o.WsFOYRwuiBUF0VZwSiD1LZmcAM4PbEMw"
pb = Pushbullet(pb_key)
delay = 10

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument(f"--user-agent={user_agent}")
driver = webdriver.Chrome(options=chrome_options)

# Load the page
logging.debug(f"Loading {url}")
driver.get(url)
WebDriverWait(driver, delay).until(EC.title_is("Car Reservation Availability to Nantucket & Martha’s Vineyard | The Steamship Authority"))

# Route
logging.debug("Selecting route")
select = Select(driver.find_element_by_class_name('route'))
select.select_by_visible_text('Hyannis to Nantucket')

# Departure Date
logging.debug(f"Selecting date {DEPART_MONTH} {DEPART_DAY}")
driver.find_element_by_name('depart_date').click()
select = Select(driver.find_element_by_class_name('ui-datepicker-month'))
select.select_by_visible_text(DEPART_MONTH)
driver.find_element_by_xpath(f"//*[@id='ui-datepicker-div']/table/tbody/tr/td[contains(., {DEPART_DAY})]").click()

# Return Date
logging.debug(f"Selecting date {RETURN_MONTH} {RETURN_DAY}")
driver.find_element_by_name('return_date').click()
select = Select(driver.find_element_by_class_name('ui-datepicker-month'))
select.select_by_visible_text(RETURN_MONTH)
driver.find_element_by_xpath(f"//*[@id='ui-datepicker-div']/table/tbody/tr/td[contains(., {RETURN_DAY})]").click()

# Get Results
logging.debug("Showing results")
driver.find_element_by_class_name('submit_button').click()
WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.CLASS_NAME, "returned_trips")))

for class_val in ("departures", "returns"):
    rows = driver.find_elements_by_xpath(f"//*[@class='{class_val}']/table/tbody/tr")
    logging.debug(f"Found {len(rows)} trips for {class_val}")
    for row in rows:
        # '6:30 am Hyannis 8:45 am Nantucket M/V WOODS HOLE Full'
        trs = row.find_elements_by_xpath('td')
        depart_text = trs[0].text
        availability = trs[5].text

        logging.debug("Checking availability for {depart_text} between {times[class_val]['after']} and {times[class_val]['before']}")
        if (datetime.datetime.strptime(depart_text, '%I:%M %p') >= 
            datetime.datetime.strptime(times[class_val]['after'], '%I:%M %p') and 
            datetime.datetime.strptime(depart_text, '%I:%M %p') <= 
            datetime.datetime.strptime(times[class_val]['before'], '%I:%M %p') and 
            availability != 'Full' and 
            availability != 'Unavailable'):
            logging.info(f"Found Trip: {class_val} at {depart_text}")
            push = pb.push_note(f"{class_val} Ferry found!", depart_text)
        else:
            logging.info(f"No {class_val} trip found at {depart_text}")

# Close the driver
driver.quit()
