import traceback
# import requests
import sys
import json
from pathlib import Path
import time
import random
import urllib.parse
#captcha process


import traceback

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select

PAGE_LOAD_TIMEOUT = 50
# BASE_DIR = "KnowYourPropaty"
# CONFIGURATION_FILE = BASE_DIR / 'settings.config'
DATA_DIR = "data"
CHROME_DIR = r"D:\Code\Python\KnowYourPropaty\chrome\chromedriver-win64\chromedriver.exe"
USER_DATA_DIR = r"D:\Code\Python\KnowYourPropaty\chrome\user-data"

retry = 0
max_retries = 5
# DATA_DIR.mkdir(exist_ok=True)
# CHROME_DIR.mkdir(exist_ok=True)
# USER_DATA_DIR.mkdir(exist_ok=True)
max_plot_no = 1201
plot_no = 1200
TARGET_NAME = "Enter Target name"


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.5735.90",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36", 
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
]

    

def closeBrowser(browser):
    if browser is not None:
                print("Closing the browser instance...")
                try:
                    # First try with close which sends termination signal to the chrome driver
                    browser.close()
                except:
                    pass
                try:
                    # Try quiting the chrome driver
                    browser.quit()
                except:
                    pass
        

def is_head_ready(browser):
        """
        Check if head tag is available
        """
        try:
            WebDriverWait(browser, 40).until(EC.presence_of_element_located((By.TAG_NAME, "head")))
            return True
        except Exception as e:
            print("DaisyPoolCoversScraper.is_head_ready Error: ", e, traceback.format_exc())
            return False


def scroll(browser):
    """
    Scroll the page down to bottom
    So that everything is loaded properly which are dynamically rendered by javascript of the page
    """
    try:
        scroll_height = browser.execute_script("return document.body.scrollHeight;")
        while True:
            i = 10
            while i>0:
                browser.execute_script(f"window.scrollTo(0, {scroll_height/i});")
                time.sleep(random.randrange(1, 3)/100)
                i -= 1
            time.sleep(random.randrange(1, 5)/100)
            new_scroll_height = browser.execute_script("return document.body.scrollHeight;")
            if new_scroll_height==scroll_height:
                break
    finally:
        browser.execute_script("window.scrollTo(0, 0);")

def is_dom_ready(browser):
    """
    Check if body is available in the HTML page
    """
    try:
        time.sleep(0.5)
        WebDriverWait(browser, 40).until(EC.presence_of_element_located((By.TAG_NAME, "body")))                
        try:
            # Scroll the page so that everything is loaded properly which are dynamically rendered by javascript of the page
            scroll(browser)
        except:
            pass
        return True
    except Exception as e:
        print("DaisyPoolCoversScraper.is_dom_ready Error: ", e, traceback.format_exc())
        return False        

def is_title_valid(browser, title=""):
    """
    Validate page title
    """
    try:
        if title is None or title=="": return True # handle None or empty title (precaution)
        return browser.title==title or browser.title.strip()==title.strip() # check given title is matching with the browser title 
    except Exception as e:
        print("DaisyPoolCoversScraper.is_title_valid Error: ", e, traceback.format_exc())
        return False


def is_page_ready(browser, title):
    """
    Check if the page is ready
    """
    ready = False
    time.sleep(2)
    # Retry checking 3 times in case the page is not ready yet
    for _ in range(0, 3):
        try:
            # Wait for 1 sec
            time.sleep(1)
            # Wait for the page to be ready for scrapping
            ready = is_head_ready(browser=browser) and is_dom_ready(browser=browser) and is_title_valid(browser=browser,title=title)
            if ready:
                break
        except:
            ready = False
    return ready

def get_page( url, browser, title=None, ignore_load_timeout=False):
        """
        Invoke the url and get the page ready for scrapping
        """
        
        try:
            # Invoke
            browser.get(url)
            
            # time.sleep(2)
            # Check readiness of the page
            return is_page_ready(browser=browser,title=title)
        except TimeoutException as e:
            # In case page load timeout occurs, and if this flag is set then ignore retrying as the target element is available on page
            if ignore_load_timeout:
                return is_page_ready(title)
            print(f"{title}.get_page Error1: ", e, traceback.format_exc())
            if retry<=max_retries: #
                retry += 1
                return get_page(url, title)
            return False
        except Exception as e:
            print(f"{title}.get_page Error2: ", e, traceback.format_exc())
            return False

def getReadyDriver(user_agent):
    print("Configuring browser...")

        # Auto downloading the chrome driver and get the absolute path in return
    chrome_driver_path = CHROME_DIR
    

    # Creating Chrome Options
    options = Options()

    # Run chrome driver in headless mode i.e without a GUI or without a visible browser
    # options.add_argument("--headless")

    # Setting the logging level to 3 (FATAL) to log the fatal messages for troubleshooting and avoid getting unnecessary ingo/warning messages
    options.add_argument("--log-level=3")

    # Bypassing OS security model to run chrome driver in an environment where sanbox is not supported
    options.add_argument("--no-sandbox")

    # Disabling GPU acceleration to troubleshoot graphics issues
    options.add_argument("--disable-gpu")

    # Disbaling WebGL to troubleshoot graphics issues or improve performance on systems with limited graphics support
    options.add_argument("--disable-webgl")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--kiosk-printing")
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-notifications")
    # Create the chrome driver service
    service = Service(executable_path=chrome_driver_path)

    # Create a new instance of the Chrome driver with specified options
    browser = webdriver.Chrome(service=service, options=options) 

    # Set the maximum waiting time for page load
    browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    print("browserVersion: ", browser.capabilities["browserVersion"])
    print("chromedriverVersion: ", browser.capabilities["chrome"]["chromedriverVersion"].split(" ")[0])
    return browser

def click_element(browser, by, value):
    try:
        # Wait until the element is present
        element = WebDriverWait(browser, 40).until(
            EC.presence_of_element_located((by, value))
        )
        
        # Ensure the element is visible
        WebDriverWait(browser, 40).until(EC.visibility_of(element))
        
        # Scroll into view
        browser.execute_script("arguments[0].scrollIntoView(true);", element)
        
        # Wait until the element is clickable
        # WebDriverWait(browser, 10).until(EC.element_to_be_clickable((by, value)))
        attempts = 3
        for attempt in range(attempts):
            try:
                # Ensure the element is clickable
                WebDriverWait(browser, 40).until(EC.element_to_be_clickable((by, value)))
                
                # Try clicking the element
                element.click()
                return  # Exit the function if click is successful
            except Exception as e:
                print(f"Attempt {attempt + 1} failed, retrying...")
                print(traceback.format_exc())
                time.sleep(1)  # Wait before retrying

        # If standard click fails after retries, try JavaScript click
        print("Standard click failed, trying JavaScript click")
        browser.execute_script("arguments[0].click();", element)
        
        # Try clicking the element
        element.click()
    except Exception as e:
        print("Standard click failed, trying JavaScript click")
        print(traceback.format_exc())
        try:
            # Fallback to JavaScript click
            element = browser.find_element(by, value)
            browser.execute_script("arguments[0].click();", element)
        except Exception as js_e:
            print("JavaScript click also failed")
            print(traceback.format_exc())

def Select_option(browser,id,idx):
    option1 = WebDriverWait(browser, 40).until(EC.presence_of_element_located((By.ID, id)))
    option = Select(option1)
    all_options = option.options
    option_values = [option.get_attribute('value') for option in all_options]
    print(option_values)
    if(len(option_values)>1):

        option.select_by_value(value=idx)
        return True
    elif (len(option_values)==1):
        time.sleep(6)
        option.select_by_value(value=idx)
        return True
    else:
        return False

def after_refersh(browser):
    if Mouza_Identification(browser=browser):
        if Plot_no_by(browser=browser):
            # data_collection(browser=browser,khatian=khatian)
            return


def Mouza_Identification(browser):
    print("radioSelectionViewType1")
    click_element(browser=browser, by=By.CSS_SELECTOR,value='input[id="radioSelectionViewType1"][value="1"]' )
    #select dist
    time.sleep(2)
    print("lstDistrictCode1")
    if Select_option(browser=browser,id= "lstDistrictCode1", idx="05"):
        #select block
        time.sleep(2)
        print("lstBlockCode1")
        if Select_option(browser=browser,id= "lstBlockCode1", idx="12_NEW"):
            #select mouza
            time.sleep(2)
            print("lstMouzaList")
            if Select_option(browser=browser,id= "lstMouzaList", idx="090"):
                return True
    return False
            
def data_collection(browser, khatian=[]):
    print("table....")
    # try:
    #     if "Record Not Found !!!!" in browser.find_elements(By.ID, "plotdetails").text :
    #         print("not Found")
    #         return
    # except Exception as e:
    #     pass
    try:
        table = WebDriverWait(browser, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.tables-fixed")))
        print("table")
        if table.is_displayed():
            print("row")
        # Ini  tialize variables to store খতিয়ান নং
            khatian_number = -1
            
            # Find all rows in the table body (tbody)
            rows = table.find_elements(By.XPATH, ".//tbody/tr")
            desired_name = TARGET_NAME #"খোদাবক্স সেখ" #"প্রশান্ত মন্ডল"
        # Loop through each row and extract values
            rows = table.find_elements(By.XPATH, ".//tbody/tr")
        
        # Loop through each row and extract values
            for row in rows:
                # Extract "খতিয়ান নং"
                khatiyan_no = row.find_element(By.XPATH, ".//td[1]").text
                # Extract "রায়তের নাম"
                rayater_name = row.find_element(By.XPATH, ".//td[2]").text
                
                # Compare the extracted name with the target name
                if rayater_name == desired_name or 'খোদাবক্স' in rayater_name:
                    khatiyan_number = khatiyan_no
                    print(khatiyan_no)
                    khatian.append((khatiyan_no," ",plot_no))
                    print("khatian.append")
                    print(f"Match found! খতিয়ান নং: {khatiyan_number}, রায়তের নাম: {rayater_name}")
                    Write_in_file(khatian=khatian)
                    return
            else:
                print("No match found for the target name.")
                return
        
           
           
    except Exception as e:
        print("table not found",e)
        return

def Plot_no_by(browser):
    Plot = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'txtPlotNo')))
    Plot.clear()
    Plot.send_keys(plot_no)
    captcha_input = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'drawText1')))
    captcha_element = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'captchaText')))
    captcha_txt = captcha_element.get_attribute("value")
    words = captcha_txt.split()
    

# Join the words without spaces
    captcha_txt = ''.join(words)
    # captcha_txt = solveCaptcha(browser, captcha_image_selector, captcha_input_selector)
    print("captchaText:",captcha_txt)
    time.sleep(1)
    
    captcha_input.send_keys(captcha_txt)
    # # popup_title
    try:
        pop_up = WebDriverWait(browser, 2).until(EC.presence_of_element_located((By.ID, 'popup_ok')))
        if pop_up.is_displayed() :
            pop_up.click()
            
            Plot_no_by(browser=browser)
    except Exception as e:
        print("pop not displayed")
    #     captcha_element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'captchaText')))
    # captcha_txt = captcha_element.get_attribute("value")
    # captcha_txt = solveCaptcha(browser, captcha_image_selector, captcha_input_selector)

    captcha_input = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'drawText1')))
    captcha_input.send_keys(captcha_txt)
    # time.sleep(2)
    # scroll(browser=browser)
    print("push")
    
    # print("viieew")
    # # Print the outer HTML of the button for debugging
    # print(plbutton.get_attribute('outerHTML'))
    
    # # Call the JavaScript function loadPlot()
    # browser.execute_script("loadPlot();")
    click_element(browser=browser,by=By.ID,value="plbutton")
    # view =WebDriverWait(browser, 40).until(EC.presence_of_element_located((By.ID, 'plbutton')))
    # view.click()
    print("viewed")
    # time.sleep(2)
    load=0
    while WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'loading'))).is_displayed():
        print("loding..")
        time.sleep(1)
        load+=1
        if (load == 10):
            browser.navigate().refresh()
            after_refersh(browser=browser)
    if WebDriverWait(browser, 50).until(EC.presence_of_element_located((By.ID, 'plotdetails'))).is_displayed():
        return True
    else:
        return False


def Option_for_search(browser):
    click_element(browser=browser, by=By.CSS_SELECTOR,value='input[id="radioKhatianDtlType0"][value="0"]' )
    click_element(browser=browser, by=By.CSS_SELECTOR,value='input[id="r2"]' )
    time.sleep(4)
    return Plot_no_by(browser=browser)
    
   

def logout(browser):
    click_element(browser=browser, by=By.XPATH,value="//a[@title='Click to Logout']//i" )
    print("Logging out...")


def login(browser):
    click_element(browser=browser, by=By.XPATH,value="//a[@id='knowYourProperty']//span" )
    click_element(browser=browser, by=By.CSS_SELECTOR,value='input[id="userType"][value="2"]' )
    # WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[id="userType"][value="2"]'))).click()
    username_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'username')))
    password_field = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'password')))
    username_field.send_keys('aaaaa')  # replace with the actual username
    password_field.send_keys('abc@13')  # replace with the actual password


    captcha_element = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'txtCaptcha')))
    captcha_txt = captcha_element.get_attribute("value")
    # captcha_txt = solveCaptcha(browser, captcha_image_selector, captcha_input_selector)
    print("captchaText:",captcha_txt)
    # time.sleep(10)
    captcha_input = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.ID, 'txtInput')))
    captcha_input.send_keys(captcha_txt)
    # Wait for a moment to ensure the CAPTCHA text is entered
    time.sleep(1)

    # Click the submit button
    # click_element(browser=browser, by=By.ID,value='loginsubmit' )
    submit_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, 'loginsubmit')))
    # time.sleep(2)
    submit_button.click()
    time.sleep(2)
    welcome =  WebDriverWait(browser, 40).until(EC.presence_of_element_located((By.XPATH, "//div[@id='afterLoginLabel']//span")))
    if (welcome.text =="Welcome"):
        return True
    else:
        return False


def Write_in_file(khatian):
    print("saving data")
    with open('detail.txt', 'a', encoding='utf-8') as file:
        for item in khatian:
            file.write(str(item)+ ',\t')


if __name__ == "__main__":
    # plot_no =455
    khatian =[]
    try:
        user_agent = USER_AGENTS[random.randrange(0, len(USER_AGENTS)-1)]
        browser = getReadyDriver(user_agent)
        browser.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent":user_agent})
        if get_page(url="https://banglarbhumi.gov.in/BanglarBhumi/Home.action",browser=browser,  title="LAND AND LAND REFORMS AND REFUGEE RELIEF AND REHABILITATION DEPARTMENT",ignore_load_timeout=True):
            # time.sleep(10)
            if login(browser=browser):
                time.sleep(2)
                scroll(browser=browser)
                # time.sleep(5)
                if Mouza_Identification(browser=browser):
                    # while True:
                    if Option_for_search(browser=browser):
                        print("data_collect")
                        data_collection(browser=browser,khatian=khatian)
                        plot_no+=1
                        while plot_no <= max_plot_no:
                            Plot_no_by(browser=browser)
                            data_collection(browser=browser,khatian=khatian)
                            plot_no+=1

        print("completed.....")
        time.sleep(5)
    except Exception as e:
        print("error:",e)
    finally:
        Write_in_file(khatian=khatian)
        logout(browser=browser)
        closeBrowser(browser=browser)

