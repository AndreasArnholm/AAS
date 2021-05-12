from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from webdriver_manager import firefox, chrome
from tqdm import tqdm

from time import sleep

class Scraper:
    def __init__(self, browser, dir, tag, gecko):
        self.BROWSER = browser
        self.DOWNLOAD_DIRECTORY = dir
        self.TEST_TAG = tag

        self.run(gecko)

    def id_click(self, driver, id):
        button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, id)))
        button.click()

    def enter_text_name(self, driver, name, keys):
        field = driver.find_element_by_name(name)
        field.send_keys(keys)

    def enter_text_id(self, driver, id, keys, submit=False, bounce=False):
        field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, id)))
        driver.execute_script("arguments[0].value = ''", field)
        field.send_keys(keys)
        if submit:
            field.send_keys(Keys.ENTER)
            sleep(3)
        if bounce:
            return field

    def link_text_click(self, driver, text, partial=False):
        by = By.PARTIAL_LINK_TEXT if partial else By.LINK_TEXT
        button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((by, text)))
        button.click()

    def test_details_value(self, driver, col):
        val = driver.find_element_by_id('resultdetails-details-tab').find_elements_by_tag_name('table')[1].find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')[col].find_elements_by_tag_name('td')[1]
        return val.text

    def find_rows(self, driver, table, last=None):
        while True:
            rows = driver.find_element_by_id(table).find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
            if len(rows) > 1:
                break
        if last:
            while True:
                if rows[0].find_elements_by_tag_name('td')[6].text == last:
                    break
                driver.refresh()
                rows = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, table))).find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        return rows

    def run(self, gecko):
        if self.BROWSER == 'chrome':
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            #options.add_argument("--headless")
            options.add_argument('disable-infobars')
            prefs = {"profile.default_content_settings.popups": 0,
                    "download.default_directory": self.DOWNLOAD_DIRECTORY,
                    "directory_upgrade": True}
            options.add_experimental_option("prefs", prefs)
            driver = webdriver.Chrome(chrome.ChromeDriverManager().install(), chrome_options=options)
        elif self.BROWSER == 'firefox':
            profile = webdriver.FirefoxProfile()
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference("browser.download.manager.showWhenStarting", False)
            profile.set_preference("browser.download.dir", self.DOWNLOAD_DIRECTORY)
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                        "text/plain, application/octet-stream, application/binary, text/csv, application/csv, application/excel, text/comma-separated-values, text/xml, application/xml")
            options = Options()
            options.headless = True
            driver = webdriver.Firefox(executable_path=gecko, firefox_profile=profile, firefox_options=options)

        driver.get("http://20.20.20.232/login")

        # Enter username
        self.enter_text_name(driver, 'login', '5gvinni-viewer')

        # Enter password
        self.enter_text_name(driver, 'password', 'testing')

        # Log in
        self.id_click(driver, 'loginExec')

        # For results
        self.id_click(driver, "sidemenu-results")

        # Filter for correct test tag
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ranges')))
        filter = driver.find_element_by_id('results-filter-count')
        filter.find_element_by_xpath('..').click()
        driver.find_element_by_xpath('//button[contains(text(), "+ Filter")]').click()
        self.id_click(driver, 'testTag')
        self.enter_text_id(driver, 'results-filter-field-testTag', self.TEST_TAG, submit=True)

        # Select time frame 
        time_frame = 'Past Week'
        self.id_click(driver, 'results-time-filter')
        WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,"//div[@class='daterangepicker dropdown-menu ltr opensright']//ul/li[text()='" + time_frame + "']"))).click()

        # Iterate over table rows and create reports
        rows = self.find_rows(driver, 'results-table')
        print(len(rows))
        i = 0
        for row in tqdm(rows, desc="Processing results"):
            col = row.find_elements_by_tag_name('td')[2]
            col.click()
            while(True):
                try:     
                    self.link_text_click(driver, 'Detailed')
                    #source = self.test_details_value(driver, 3)
                    #dest = self.test_details_value(driver, 8)
                    last_report = "system_test_" + str(i)
                    report_name_field = self.enter_text_id(driver, 'test-result-report-name', last_report, bounce=True)
                    report_name_field.find_element_by_xpath('..').find_element_by_tag_name('div').find_element_by_tag_name('button').click()
                    driver.find_element_by_link_text('CSV').click()
                    WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH,'//button[contains(text(), "OK")]'))).click()
                    self.id_click(driver, 'resultsModal-times')
                    break
                except: 
                    continue
            i += 1
            sleep(0.3)

        # Go to reports
        #sleep(5)
        self.id_click(driver, "sidemenu-reports")

        # Filter by report name
        driver.find_element_by_id('reportsfiles-filter-count').find_element_by_xpath('..').click()
        cb = '5gvinni-viewer'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "+ Filter")]'))).click()
        self.id_click(driver, 'ReportName')
        self.enter_text_id(driver, 'reportsfiles-filter-field-ReportName', 'system_test_', submit=True)

        # Iterate over reports and download
        report_rows = self.find_rows(driver, 'reportsfiles-table', last_report)
        for row in tqdm(report_rows, desc="Processing reports"):
            sleep(0.05)
            col = row.find_elements_by_tag_name('td')[3]
            col.click()

BROWSER = 'firefox'
DOWNLOAD_DIRECTORY = r"C:\Users\Mathias Henriksen\Desktop\hawkeye-downloads\\" # IMPORTANT - ENDING SLASH V IMPORTANT
TEST_TAG = 'test_aas_no_commands_10min'
GECKO_PATH = r"C:\Users\Mathias Henriksen\Desktop\geckodriver.exe"

Scraper(BROWSER, DOWNLOAD_DIRECTORY, TEST_TAG, GECKO_PATH)