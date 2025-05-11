import re
import os
import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from email_fetch.check2fa import Check2fa

class LuckyBirdHandler:
    
    def run(self):

        username = '{username}'
        password = '{password}'
        
        cookie_path = os.path.join(os.path.dirname(__file__), 'cookie.json')

        mu_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
        chrome_options = Options()
        chrome_options.add_argument(f"--user-agent={mu_user_agent}")

        driver = webdriver.Chrome()

        driver.get('https://www.luckybird.io')
        sleep(1)
        
        should_login = True
        
        if os.path.exists(cookie_path):
            #Cookie injection is not working for this site, I suggest submiting 'n' to proceed if set up. I left this here for your learning.
            continue_login = input("Cookies found. Do you want to load them? (y/n): ").strip().lower()
            if continue_login == 'y':
                print("Loading cookies...")
                with open(cookie_path, 'r') as f:
                    cookie = json.load(f)
                    print(cookie)
                for c in cookie:
                    driver.add_cookie(c)
                    sleep(1)
                driver.refresh()
                sleep(1)
                input("Press Enter to continue...")
                should_login = False
                
        if should_login:
            print("No cookies found, logging in...")
            sleep(1)
            login_tab = driver.find_element(By.ID, 'tab-login')
            login_tab.click()
            sleep(1)

            username_input = driver.find_element(By.XPATH, "//div[.//input[@placeholder='Username']]")
            password_input = driver.find_element(By.XPATH, "//div[.//input[@placeholder='Password']]")
            login_button = driver.find_element(By.CLASS_NAME, 'logRegister_page')
            sleep(1)

            ActionChains(driver).move_to_element(username_input).send_keys(username, Keys.TAB).perform()
            sleep(1)
            ActionChains(driver).move_to_element(password_input).send_keys(password, Keys.TAB, Keys.ENTER).perform()
            sleep(1)

            sleep(5)
            checkup2fa = driver.find_elements(By.CLASS_NAME, 'loginTwoFactor_input')
            if len(checkup2fa) > 0:
                print("2FA code required. Processing...")
                checker = Check2fa()
                checker.check2fa()
                print(checker.verif_code)

                sleep(5)

                verification_input = driver.find_element(By.XPATH, "//div[@class='loginTwoFactor_input']//input")
                verification_submit = driver.find_element(By.CLASS_NAME, 'loginTwoFactor_button')
                ActionChains(driver).move_to_element(verification_input).click().send_keys(checker.verif_code, Keys.TAB).perform()
                sleep(1)
                verification_submit.send_keys(Keys.ENTER)
                sleep(3)
                
                cookies = driver.get_cookies()
                print(cookies)
                with open(cookie_path, 'w') as f:
                    json.dump(cookies, f)
                    
                input("Press Enter to continue...")
                    
            else:
                print("No 2FA code required.")
                cookies = driver.get_cookies()
                print(cookies)
                with open(cookie_path, 'w') as f:
                    json.dump(cookies, f)
                    
                input("Press Enter to continue...")

            input("Press Enter to continue...")
        
if __name__ == '__main__':
    LuckyBirdHandler().run()
