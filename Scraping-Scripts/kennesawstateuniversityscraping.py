from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
import time
# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument('--window-size=1920,1080') 
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-web-security")
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')

# Create a WebDriver instance with the specified service and options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
# Load the desired URL
url = 'https://d2l.kennesaw.edu/'
driver.get(url)

# Getting through the login stages
try:
    # Remove the cookie notification div
    driver.execute_script("document.getElementById('cookie-notification').remove()")
    login_button = driver.find_element(By.XPATH, '//a[text()="Log in to KSU D2L Brightspace"]')
    login_button.click()

    title_textblock_map = {}
    USERNAME = os.environ.get("USERNAME_KSU")
    PASSWORD = os.environ.get("PASSWORD_KSU")

    WebDriverWait(driver, 10).until(lambda x: len(driver.window_handles) > 1)
    driver.switch_to.window(driver.window_handles[1])  # Switch to the new window
    # Find the element with the ID "userNameInput"
    user_name_input = driver.find_element(By.ID, 'userNameInput')
    # Perform actions on the found element
    user_name_input.send_keys(USERNAME) 

    # Find the element with the ID "passwordInput"
    password_input = driver.find_element(By.ID, 'passwordInput')
    # Perform actions on the found element
    password_input.send_keys(PASSWORD)  
    submit_button = driver.find_element(By.ID, 'submitButton')
    submit_button.click()
    # Prefoorm necessary actions to make it through 2FA screens
    try:
        duo =  WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'trust-browser-button'))
        )
        initial_url = driver.current_url
        duo.click()
        # Check if the URL has changed loop for flow control
        while True:
            if driver.current_url != initial_url:
                print("Webpage changed.")
                break
    except Exception:
        print(f"No button")
    try:
        # XPath of the container element (d2l-my-courses-container)
        container_xpath = "/html/body/div[2]/div[2]/div[2]/div/div[1]/div[3]/d2l-expand-collapse-content/div/d2l-my-courses"
        # Wait for the container element to be present
        container = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, container_xpath)))
        # Use JavaScript to open the shadow root of the container element (d2l-my-courses-container)
        shadow_root_script = "return arguments[0].shadowRoot"
        container_shadow_root = driver.execute_script(shadow_root_script, container)
        # Within the container element, find the d2l-tab-panel
        d2l_my_courses_container_selector = "d2l-my-courses-container"
        d2l_my_courses_container = container_shadow_root.find_element(By.CSS_SELECTOR, d2l_my_courses_container_selector)
        d2l_my_courses_container_shadow_root = driver.execute_script(shadow_root_script, d2l_my_courses_container)
        # Within the shadow root of d2l-my-courses-container, find the d2l-my-courses-content element
        time.sleep(3)
        d2l_courses_content_selector = "#panel-3098087 > d2l-my-courses-content"
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME,"d2l-widget-content")))
        d2l_courses_content = d2l_my_courses_container_shadow_root.find_element(By.CSS_SELECTOR, d2l_courses_content_selector)
        d2l_courses_content_shadow_root = driver.execute_script(shadow_root_script, d2l_courses_content)
        # Within the shadow root of d2l-my-courses-container, find the d2l-my-courses-content element
        d2l_my_courses_card_grid_selector = "d2l-my-courses-card-grid"
        d2l_my_courses_card_grid = d2l_courses_content_shadow_root.find_element(By.CSS_SELECTOR, d2l_my_courses_card_grid_selector)
        d2l_my_courses_card_grid_shadow_root = driver.execute_script(shadow_root_script, d2l_my_courses_card_grid)
        # Within the shadow root of d2l-my-courses-container, find the d2l-my-courses-content element
        d2l_dual_enrollement_card_selector = "d2l-enrollment-card"
        d2l_dual_enrollement_cards = d2l_my_courses_card_grid_shadow_root.find_elements(By.CSS_SELECTOR, d2l_dual_enrollement_card_selector)
        # Iterate through each d2l-enrollment-card and find the href of its corresponding d2l-card
        for d2l_dual_enrollment_card in d2l_dual_enrollement_cards:
            # Within the shadow root of d2l-enrollment-card, find the d2l-card element
            d2l_dual_enrollement_card_shadow_root = driver.execute_script(shadow_root_script, d2l_dual_enrollment_card)
            d2l_card_selector = "d2l-card"
            d2l_card = d2l_dual_enrollement_card_shadow_root.find_element(By.CSS_SELECTOR, d2l_card_selector)

            # Get the href attribute
            href_value = d2l_card.get_attribute("href")
            
            # Open a new tab using JavaScript
            driver.execute_script("window.open('', '_blank');")

            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[-1])

            # Open a URL in the new tab
            driver.get("https://kennesaw.view.usg.edu" + href_value)
            # Locate the expand_calendar element
            expand_calendar_locator = (By.CLASS_NAME, 'd2l-collapsible-panel')

            # Use WebDriverWait with the custom condition to ensure visibility and clickability
            expand_calendar = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(expand_calendar_locator)
            )

            # If the element is not visible, perform a scroll action
            driver.execute_script("arguments[0].scrollIntoView(true);", expand_calendar)

            expand_calendar.click()
            element_today = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[contains(@class, "d2l-calendar-mini-today")]'))
            )
            tomorrow_day = int(element_today.text)
            # Search for the <td> element with data-date equal to (today_value + 1)
            td_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f'//td[@data-date="{tomorrow_day + 1}"]'))
            )
            try:
                span_has_events = td_element.find_element(By.XPATH, './/span[@class="d2l-offscreen" and text()="Has Events"]')
                print(f'The <td> element for {tomorrow_day + 1} has events')
                td_element.click()
                time.sleep(1)
                events = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".d2l-datalist-item.d2l-datalist-item-actionable.d2l-datalist-simpleitem"))
                )
                title = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "d2l-navigation-s-link"))
                )
                title_text = title.text
                for event in events:
                    textblock_elements = event.find_elements(By.CLASS_NAME, "d2l-textblock")

                    textblock_texts = [textblock.text for textblock in textblock_elements]
                    
                    title_textblock_map.setdefault(title_text, []).extend(textblock_texts)
                    
            except NoSuchElementException:
                print(f'The <td> element for {tomorrow_day + 1} does not have events')
            # Print or use the href value
            driver.switch_to.window(driver.window_handles[1])
    except Exception as e:
        print(f"Error: {e}")
    # URL of the Flask route for receiving logs within the Kubernetes cluster
    flask_url = 'http://flask-webapp-service/receive-logs' 

    # Send the log data to the Flask backend
    response = requests.post(flask_url, json=title_textblock_map)
    if response.status_code == 200:
        print('Logs sent successfully')
    else:
        print('Failed to send logs')
except Exception as e:
    print(f"Error: {e}")
