import unittest
import time
import tkinter as tk
import environ

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException,  NoSuchElementException
from PIL import Image, ImageFont, ImageDraw 

env = environ.Env()
environ.Env.read_env()

CHECKOUT_URL=env('CHECKOUT_URL')
ADMIN_URL=env('ADMIN_URL')
ADMIN_USERNAME=env('ADMIN_USERNAME')
ADMIN_PASSWORD=env('ADMIN_PASSWORD')

class Utils(object):
    
    driver = None

    @staticmethod
    def get_clipboard():
        root = tk.Tk()
        root.withdraw()
        
        return root.clipboard_get()

    @staticmethod
    def get_amount_from_input(driver):
        element = driver.find_element(By.ID, "bnomics-amount-input")
        return element.get_attribute('value')

    @staticmethod
    def get_address_from_input(driver):
        element = driver.find_element(By.ID, "bnomics-address-input")
        return element.get_attribute('value')

    @staticmethod
    def is_crypto_enabled(driver, crypto):
        
        Utils.login_to_admin(driver, currencies=True)

        checkbox_name = "blockonomics_%s" % crypto
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.NAME, checkbox_name)
                )
            )
            return driver.find_element(By.NAME, checkbox_name).is_selected()
        except TimeoutException:
            return False
    
    @staticmethod
    def set_to_lite_mode(driver, enable=True):
        
        Utils.login_to_admin(driver)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.ID, "advanced_title")
            )
        )
        driver.find_element(By.CSS_SELECTOR, "#advanced_title a").click()
        
        check = driver.find_element(By.CSS_SELECTOR, "input[name=blockonomics_lite]")
        is_checked = check.is_selected()

        if is_checked == enable:
            print("Lite Mode is already %s" % enable)
            return
        
        check.click()
        driver.find_element(By.CSS_SELECTOR, "form .submit input[type=submit]").click()
        print("Lite Mode is set to %s" % enable)

    @staticmethod
    def set_js_mode(driver, enable=True):
        
        Utils.login_to_admin(driver)

        driver.find_element(By.CSS_SELECTOR, "#advanced_title a").click()
        
        check = driver.find_element(By.CSS_SELECTOR, "input[name=blockonomics_nojs]")
        is_checked = check.is_selected()

        if enable and not is_checked:
            print("JS mode is already enabled")
            return
        
        if not enable and is_checked:
            print("JS mode is already disabled")
            return
        
        check.click()
        driver.find_element(By.CSS_SELECTOR, "form .submit input[type=submit]").click()


    @staticmethod
    def login_to_admin(driver, currencies=False):
        url = ADMIN_URL
        if currencies:
            url += "&tab=currencies"
        
        driver.get(url)

        if "wp-login.php" not in driver.current_url:
            print("No Auth Needed")
            return
        
        u = driver.find_element(By.ID, 'user_login')
        u.clear()
        u.send_keys(ADMIN_USERNAME)

        u = driver.find_element(By.ID, 'user_pass')
        u.clear()
        u.send_keys(ADMIN_PASSWORD)

        driver.find_element(By.ID, "wp-submit").click()

        time.sleep(5)


class WooCommerceTest(unittest.TestCase):
    
    class Crypto:
        BTC = {'uri': 'bitcoin', 'url_code': 'btc'}
        BCH = {'uri': 'bitcoincash', 'url_code': 'bch'}

    class TestType:
        Lite = 'l'
        Normal = 'n'
    
    test_mode = Crypto.BTC
    test_type = TestType.Normal
    js_enabled = True

    @classmethod
    def setUpClass(cls):
        
        edgeOption = webdriver.EdgeOptions()
        edgeOption.add_experimental_option('excludeSwitches', ['enable-logging'])
        edgeOption.add_argument("start-maximized")

        service = Service("./msedgedriver.exe")

        cls.driver = webdriver.Edge(service=service, options=edgeOption)

        if cls.test_type == cls.TestType.Lite:
            Utils.set_to_lite_mode(cls.driver, True)
        elif cls.test_type == cls.TestType.Normal:
            Utils.set_to_lite_mode(cls.driver, False)

        Utils.set_js_mode(cls.driver, cls.js_enabled)
        
    @classmethod
    def tearDownClass(cls):
        screenshot_name = 'screenshot-%s-%s-%s.png' % (cls.test_type, 'js' if cls.js_enabled else 'nojs', cls.test_mode['url_code'])
        cls.driver.save_screenshot(screenshot_name)
        cls.add_url_to_screenshot(screenshot_name)

        cls.driver.quit()
    
    @classmethod
    def add_url_to_screenshot(cls, name):
        image = Image.open(name)
        ImageDraw.Draw(image).text((0,0), cls.driver.current_url, (0,0,0))
        image.save(name)

    def test_00_checkout_display(self):
        """Check is requested crypto is enabled"""
        self.assertTrue(Utils.is_crypto_enabled(self.driver, self.test_mode['url_code']))

    def test_01_checkout_display(self):
        """Check is the Order Panel is Displayed"""
        self.driver.get(CHECKOUT_URL % self.test_mode['url_code'])

        is_displayed = False

        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "bnomics-order-panel")
                )
            )
            element = self.driver.find_element(By.CLASS_NAME, "bnomics-order-panel")
            is_displayed = element.is_displayed()
        except TimeoutException:
            is_displayed = False
        
        self.assertTrue(is_displayed)

    def test_02_address_generation(self):
        """Test if Address is generated"""
        element = self.driver.find_element(By.ID, "bnomics-address-input")
        generated_address = element.get_attribute('value')

        self.assertTrue(len(str(generated_address).strip()) > 26)
    
    def test_03_address_regeneration(self):
        """Test if Address is regenerated"""

        generated_address = Utils.get_address_from_input(self.driver)

        self.driver.refresh()
        time.sleep(5)

        regenerated_address = Utils.get_address_from_input(self.driver)

        self.assertEqual(generated_address, regenerated_address)

    def test_04_copy_to_clipboard_address(self):
        """Test the Copy to Clipboard for Address"""

        if not self.js_enabled: return

        generated_address = Utils.get_address_from_input(self.driver)

        element = self.driver.find_element(By.ID, "bnomics-address-copy")
        element.click()
        copied_address = Utils.get_clipboard()

        print("=> Copied: %s, Generated %s" % (copied_address, generated_address))
        self.assertEqual(generated_address, copied_address)

    def test_05_copy_to_clipboard_amount(self):
        """Test the Copy to Clipboard for Amount"""

        if not self.js_enabled: return

        generated_amount = Utils.get_amount_from_input(self.driver)

        element = self.driver.find_element(By.ID, "bnomics-amount-copy")
        element.click()
        copied_amount = Utils.get_clipboard()

        print("=> Copied: %s, Generated %s" % (copied_amount, generated_amount))
        self.assertEqual(generated_amount, copied_amount)
 
    def test_06_qr_code(self):
        """Check is QR is Displayed and Links are valid"""

        if self.js_enabled:
            qr_btn = self.driver.find_element(By.ID, 'bnomics-show-qr')
            qr_btn.click()

        element = self.driver.find_element(By.CLASS_NAME, "bnomics-qr-code")
        self.assertTrue(element.is_displayed())

        element = self.driver.find_elements(By.CLASS_NAME, 'bnomics-qr-link')
        qr_link = '%s:%s?amount=%s' % (
            self.test_mode['uri'],
            Utils.get_address_from_input(self.driver),
            Utils.get_amount_from_input(self.driver)
        )

        for e in element:
            self.assertEqual(e.get_attribute('href'), qr_link)
    
    def test_06_refresh_btn(self):
        """Check if Refresh Button Works"""
        
        if not self.js_enabled: return

        btn = self.driver.find_element(By.ID, 'bnomics-refresh')
        btn.click()

        is_refresh_success = False
        try:
            # Check for animation rectangle to come up
            # if there is error or fallback code is executed, it'll raise exception
            WebDriverWait(self.driver, 2).until(
                EC.visibility_of_element_located(
                    (By.CLASS_NAME, 'bnomics-copy-container-animation-rectangle')
                )
            )

            # When detected, check if it's visible or not
            element = self.driver.find_element(By.CLASS_NAME, "bnomics-copy-container-animation-rectangle")
            self.assertTrue(element.is_displayed())

            # Wait for upto 10 seconds for it to hide i.e. requets completed
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element(element)
            )

            # Check for Animation Container is Gone
            try:
                is_refresh_success = not element.is_displayed()
            except StaleElementReferenceException:
                is_refresh_success = True
            
        except TimeoutException:
            is_refresh_success = False

        self.assertTrue(is_refresh_success)

    def test_07_conversion_rate(self):
        """Check if Conversion Rate is Correct"""

        amount = float(Utils.get_amount_from_input(self.driver))
        fiat_amount = float(self.driver.find_element(By.XPATH, '//*[contains(@class, "bnomics-header")]/div').text.split(" ")[0])

        crypto_rate = float(self.driver.find_element(By.ID, "bnomics-crypto-rate").text)

        self.assertAlmostEqual(round(fiat_amount/amount, 2), crypto_rate)
        
class BTCNormalJSWooCommerceTest(WooCommerceTest):
    test_mode = WooCommerceTest.Crypto.BTC
    test_type = WooCommerceTest.TestType.Normal
    js_enabled = True

class BTCLiteJSWooCommerceTest(WooCommerceTest):
    test_mode = WooCommerceTest.Crypto.BTC
    test_type = WooCommerceTest.TestType.Lite
    js_enabled = True

class BTCNormalNoJSWooCommerceTest(WooCommerceTest):
    test_mode = WooCommerceTest.Crypto.BTC
    test_type = WooCommerceTest.TestType.Normal
    js_enabled = False

class BTCLiteNoJSWooCommerceTest(WooCommerceTest):
    test_mode = WooCommerceTest.Crypto.BTC
    test_type = WooCommerceTest.TestType.Lite
    js_enabled = False

class BCHNormalJSWooCommerceTest(WooCommerceTest):
    test_mode = WooCommerceTest.Crypto.BCH
    test_type = WooCommerceTest.TestType.Normal
    js_enabled = True

class BCHLiteJSWooCommerceTest(WooCommerceTest):
    test_mode = WooCommerceTest.Crypto.BCH
    test_type = WooCommerceTest.TestType.Lite
    js_enabled = True

class BCHNormalNoJSWooCommerceTest(WooCommerceTest):
    test_mode = WooCommerceTest.Crypto.BCH
    test_type = WooCommerceTest.TestType.Normal
    js_enabled = False

class BCHLiteNoJSWooCommerceTest(WooCommerceTest):
    test_mode = WooCommerceTest.Crypto.BCH
    test_type = WooCommerceTest.TestType.Lite
    js_enabled = False
