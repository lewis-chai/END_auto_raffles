import re
import time
import requests
import random
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def select_product():
    # Make a GET request to the Launches page
    launches_url = 'https://launches.endclothing.com/'
    launches_page = requests.get(launches_url)

    # Parse the HTML content of the Launches page
    launches_soup = BeautifulSoup(launches_page.text, 'html.parser')

    # Select only the upcoming launches
    upcoming_launches = launches_soup.find('div', {'class': re.compile('.*ProductListNew*.')})
    
    # Store the products in a dictionary where each index maps to a tuple containing the link and the name of the product
    product_list = {}
    idx = 1
    for launch in upcoming_launches.find_all('div',id=re.compile('^plp-item-')):
        product_list[idx]=(launch.find('div', {'class': re.compile('.*ProductName*.')}).text, launch.a['href'],)
        idx+=1

    # Prompt the user to enter the product they would like to draw for
    for product in product_list:
        print(f'{product}. {product_list[product][0]}')
    while True:
        try:
            n = int(input('Select a product: ' ))
        except ValueError:
            print('Please enter a valid number.')
            continue
        if 0 < n < idx:
            break
        else: 
            print('Please enter a valid number.')

    # Return the selected product
    product = product_list[n]
    return product

def select_size(html_content):
    # Parse the HTML content of the forms page
    sizes_soup = BeautifulSoup(html_content, 'html.parser')
    try:
        # Select only the available sizes
        sizes_container  = sizes_soup.find('div', {'class': re.compile('.*styles__SizesGridSC*.')})
        if sizes_container:
            # Store the sizes in a dictionary where each index maps to the size
            size_dictionary = {}
            idx = 1
            for size in sizes_container.find_all('button', {'class': re.compile('styles__SizeButtonSC')}):
                size_dictionary[idx]=size.find('span').text
                idx += 1

            # Prompt the user to enter the size they would like
            for index in size_dictionary:
                print(f'{index}. {size_dictionary[index]}')

            print("If you want to select only one size, enter the same minumum and maximum value.")
            while True:
                try:
                    min_size = int(input("Select a minimum size: "))
                    max_size = int(input("Select a maximum size: "))
                except ValueError:
                    print('Please enter a valid number.')
                    continue
                if max_size<min_size:
                    print('Please enter a valid range. The maximum size must be less than or equal to the minimum size.')
                else:
                    return list(size_dictionary.values())[min_size-1:max_size]
        else:
            return None
    except Exception as e:
        print(f"ERROR: {e}")

def add_address(wait, contact_number, address, city, postcode):
    # Enter contact number 
    contact_number_field = wait.until(EC.presence_of_element_located((By.NAME, "telephone")))
    contact_number_field.send_keys(contact_number)
    wait.until(EC.element_to_be_clickable((By.XPATH,'//button[div[text()="Continue"]]'))).click()
    # Enter shipping address
    address_field = wait.until(EC.presence_of_element_located((By.NAME, "addressLine1")))
    address_field.send_keys(address)
    city_field = wait.until(EC.presence_of_element_located((By.NAME, "city")))
    city_field.send_keys(city)
    postcode_field = wait.until(EC.presence_of_element_located((By.NAME, "postcode")))
    postcode_field.send_keys(postcode)

def enter_raffle(product, profile):
    # Make a GET request to the product page
    product_url = 'https://launches.endclothing.com' + product[1]
    options = webdriver.ChromeOptions() 
    #options.add_argument('--headless=new')
    options.add_argument("--start-maximized")
    driver = uc.Chrome(options=options)
    driver.get(product_url)

    # Set a wait time 
    wait = WebDriverWait(driver, 20); 

    # Login to END account
    try:
        # Click the Enter Draw button
        wait.until(EC.element_to_be_clickable((By.XPATH,'//button[text()="Enter Draw"]'))).click()
        # Enter email address
        email_input_field = wait.until(EC.element_to_be_clickable((By.ID, "email")))
        email_input_field.send_keys(profile[1])
        email_input_field.send_keys(Keys.RETURN)
        # Check if account already exists
        try:
            # Enter first name
            first_name_input_field =  WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "first_name")))
            first_name_input_field.click()
            first_name_input_field.send_keys(profile[2])
            # Enter last name
            last_name_input_field =  WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "last_name")))
            last_name_input_field.click()
            last_name_input_field.send_keys(profile[3])
        except:
            pass
        # Enter password
        password_input_field = wait.until(EC.element_to_be_clickable((By.ID, "password")))
        password_input_field.send_keys(profile[4])
        password_input_field.send_keys(Keys.RETURN)
        # Select size
        wait.until(EC.presence_of_element_located((By.XPATH,'//button[div/h5[text()="Size"]]'))).click()
        global size_list
        try: 
            print(size_list)
        except:
            size_list = select_size(driver.page_source)
        size = random.choice(size_list)
        print("Selected Size: ", size)
        size = size.replace(" ","__")
        
        driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH,'//button[contains(@data-test-id, "{}")]'.format(size)))))
        driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH,'//button[div[text()="Continue"]]'))))
        # Check if contact details and address exits
        driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH,'//button[div/h5[text()="Ship To"]]'))))
        try:
            # Select the first address
            driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH, './/div[contains(@class, "RadioAddressSC")]'))))
        except: 
            add_address(wait, profile[5], profile[6], profile[7], profile[8]) 
        driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH,'//button[div[text()="Done"]]'))))
        # Select billing address
        driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH,'//button[div/h5[text()="Billing"]]'))))
        driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH, './/div[contains(@class, "RadioAddressSC")]'))))
        driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH,'//button[div[text()="Done"]]'))))
        # Tick checkbox
        driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH,'.//div[contains(@class, "CheckboxIconSC")]'))))
        # Select payment method 
        driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH,'//button[div[text()="Select Payment Method"]]'))))
        # driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH,'//li[contains(@iframe, "payment-method--card")]'))))
        # print("I am here") # The line above breaks the code
        # Enter card details
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,'//iframe[@title= "Iframe for card number"]')))
        card_number_field = wait.until(EC.element_to_be_clickable((By.XPATH,'//input[contains(@id, "encryptedCardNumber")]')))
        card_number_field.send_keys(profile[9])
        driver.switch_to.parent_frame()   
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,'//iframe[@title= "Iframe for expiry date"]')))
        expiry_field = wait.until(EC.element_to_be_clickable((By.XPATH,'//input[contains(@id, "encryptedExpiryDate")]')))
        expiry_field.send_keys(profile[10])
        driver.switch_to.parent_frame()   
        
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,'//iframe[@title= "Iframe for security code"]')))
        security_code_field = wait.until(EC.element_to_be_clickable((By.XPATH,'//input[contains(@id, "encryptedSecurityCode")]')))
        security_code_field.send_keys(profile[11])
        driver.switch_to.parent_frame()        
        holder_name_field = wait.until(EC.element_to_be_clickable((By.XPATH,'//input[contains(@id, "holderName")]')))
        holder_name_field.send_keys(profile[12])
        driver.switch_to.parent_frame() 
        # Enter the draw
        driver.execute_script("arguments[0].click();", wait.until(EC.presence_of_element_located((By.XPATH,'//button[span[span[text()="Enter Draw"]]]'))))
        print("I am complete")
        time.sleep(10)
    except Exception as e:
        print(f"ERROR: {e}")

    driver.quit()

if __name__ == '__main__':
    product = select_product()
    df = pd.read_csv('profiles.csv') 
    for profile in df.itertuples():
        print(profile)
        enter_raffle(product, profile)