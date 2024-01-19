import re
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
import time

# In case you forgot how the plugin works check out this video :)

# https://www.youtube.com/watch?v=IgoIQutaVvg

# Make sure to have the following done:
# Python Installed
# Selenium Installed
# Chrome Driver Working
# Input your local user in the user_data_dir
# Login to apollo on the user instance (run it one time to see if your logged in or not and if not just log in)

# And then enjoy :)

chrome_options = Options()
user_data_dir = r'/Users/kentluckybuhawe/Library/Application Support/Google/Chrome/Default'
chrome_options.add_argument(f"user-data-dir={user_data_dir}")
chrome_driver_path = './chromedriver'
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Link and name of CSV
driver.get("https://app.apollo.io/#/people?finderViewId=5b6dfc5a73f47568b2e5f11c&page=1&contactEmailStatus[]=verified")
csv_file_name = 'salesforce.csv'

time.sleep(2)

def find_email_address(page_source):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, page_source)

def filter_emails(emails, excluded_domain):
    filtered = [email for email in emails if not email.endswith(excluded_domain)]
    return filtered[:2]

def split_name(name):
    parts = name.split()
    first_name = parts[0] if parts else ''
    last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
    return first_name, last_name

while True:
    try:
        wait = WebDriverWait(driver, 10)  # wait for a maximum of 10 seconds
        element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-cy-loaded='true']")))
        loaded_section_selector = "[data-cy-loaded='true']"
        loaded_section = driver.find_element(By.CSS_SELECTOR, loaded_section_selector)

        tbodies = loaded_section.find_elements(By.TAG_NAME, 'tbody')
        if not tbodies:
            break

        for tbody in tbodies:
 
            # button_classes = ["zp-button", "zp_zUY3r", "zp_hLUWg", "zp_n9QPr", "zp_B5hnZ", "zp_MCSwB", "zp_IYteB"]
            button_classes = ["zp-button", "zp_zUY3r", "zp_jSaSY", "zp_MCSwB", "zp_IYteB"]
            
            try:
                print('button: ', By.CSS_SELECTOR, "." + ".".join(button_classes))
                button = tbody.find_element(By.CSS_SELECTOR, "." + ".".join(button_classes))

                # button = WebDriverWait(driver, 10).until(
                #     EC.element_to_be_clickable((By.XPATH, "//button[.//div[text()='Access email']]"))
                # )

                
                if button:
                    button.click()
                    email_address = find_email_address(driver.page_source)

                     # Wait for the email element to become visible
                    # email_element = WebDriverWait(driver, 10).until(
                    #     EC.visibility_of_element_located((By.CSS_SELECTOR, "div.zp-contact-email-envelope-container a.zp-link.zp_OotKe.zp_Iu6Pf"))
                    # )
                    # email_address = email_element.text.strip()
                    print("Email: ", email_address)
                    
                    
                    tbody_height = driver.execute_script("return arguments[0].offsetHeight;", tbody)
                    driver.execute_script("arguments[0].scrollBy(0, arguments[1]);", loaded_section, tbody_height)
                else:
                    print('no button')
            except NoSuchElementException:
                print('no button!')
                continue

        # Pagination Logic
        next_button_selector = ".zp-button.zp_zUY3r.zp_MCSwB.zp_xCVC8[aria-label='right-arrow']"
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
            next_button.click()
            time.sleep(1)
            # break
        except NoSuchElementException:
            print("No more pages to navigate.")
            break

    except Exception as e:
        error_message = str(e)
        if "element click intercepted" in error_message:
            # print(error_message)
            print("Your leads are ready!")
            break
        else:
            print(f"An error occurred: {error_message}")
            break

driver.quit()