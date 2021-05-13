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
    def __init__(self, browser, dir, tag, gecko, report_name):
        self.BROWSER = browser
        self.DOWNLOAD_DIRECTORY = dir
        self.TEST_TAG = tag
        self.report_name = report_name

        if self.BROWSER == 'chrome':
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            #options.add_argument("--headless")
            options.add_argument('disable-infobars')
            prefs = {"profile.default_content_settings.popups": 0,
                    "download.default_directory": self.DOWNLOAD_DIRECTORY,
                    "directory_upgrade": True}
            options.add_experimental_option("prefs", prefs)
            self.driver = webdriver.Chrome(chrome.ChromeDriverManager().install(), chrome_options=options)
        elif self.BROWSER == 'firefox':
            profile = webdriver.FirefoxProfile()
            profile.set_preference("browser.download.folderList", 2)
            profile.set_preference("browser.download.manager.showWhenStarting", False)
            profile.set_preference("browser.download.dir", self.DOWNLOAD_DIRECTORY)
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                        "text/plain, application/octet-stream, application/binary, text/csv, application/csv, application/excel, text/comma-separated-values, text/xml, application/xml")
            options = Options()
            #options.headless = True
            self.driver = webdriver.Firefox(executable_path=gecko, firefox_profile=profile, firefox_options=options)

        self.run()

    def id_click(self, id):
        button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, id)))
        button.click()

    def enter_text_name(self, name, keys):
        field = self.driver.find_element_by_name(name)
        field.send_keys(keys)

    def enter_text_id(self, id, keys, submit=False, bounce=False):
        field = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, id)))
        self.driver.execute_script("arguments[0].value = ''", field)
        field.send_keys(keys)
        if submit:
            field.send_keys(Keys.ENTER)
            sleep(3)
        if bounce:
            return field

    def link_text_click(self, text, partial=False):
        by = By.PARTIAL_LINK_TEXT if partial else By.LINK_TEXT
        button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((by, text)))
        button.click()

    def test_details_value(self, col):
        val = self.driver.find_element_by_id('resultdetails-details-tab').find_elements_by_tag_name('table')[1].find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')[col].find_elements_by_tag_name('td')[1]
        return val.text

    def find_rows(self, table, last=None):
        while True:
            print("searching for non empty table...")
            rows = self.driver.find_element_by_id(table).find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
            if not rows[0].find_elements_by_tag_name('td')[0].text == "No matching records found":
                break
        if last:
            while True:
                if rows[0].find_elements_by_tag_name('td')[6].text == last:
                    break
                self.driver.refresh()
                self.set_table_length('reportsfiles-table_length')
                self.filter_report_name()
                rows = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, table))).find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        return rows

    def filter_report_name(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'reportsfiles-filter-count'))).find_element_by_xpath('..').click()
        #cb = '5gvinni-viewer'
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "+ Filter")]'))).click()
        self.id_click('ReportName')
        self.enter_text_id('reportsfiles-filter-field-ReportName', self.report_name, submit=True)

    def set_table_length(self, name):
        select = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, name)))
        for option in select.find_elements_by_tag_name('option'):
            if option.text == '500':
                option.click() # select() in earlier versions of webdriver
                break

    def run(self):
        self.driver.get("http://20.20.20.232/login")

        # Enter username
        self.enter_text_name('login', '5gvinni-viewer')

        # Enter password
        self.enter_text_name('password', 'testing')

        # Log in
        self.id_click('loginExec')

        # For results
        self.id_click("sidemenu-results")

        # Set table length
        # select = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, 'results-table_length')))
        # for option in select.find_elements_by_tag_name('option'):
        #     if option.text == '500':
        #         option.click() # select() in earlier versions of webdriver
        #         break
        self.set_table_length('results-table_length')

        # Filter for correct test tag
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ranges')))
        filter = self.driver.find_element_by_id('results-filter-count')
        filter.find_element_by_xpath('..').click()
        self.driver.find_element_by_xpath('//button[contains(text(), "+ Filter")]').click()
        self.id_click('testTag')
        self.enter_text_id('results-filter-field-testTag', self.TEST_TAG, submit=True)

        # Select time frame 
        #time_frame = 'Past Day'
        #self.id_click('results-time-filter')
        #WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,"//div[@class='daterangepicker dropdown-menu ltr opensright']//ul/li[text()='" + time_frame + "']"))).click()

        # Iterate over table rows and create reports
        rows = self.find_rows('results-table')
        print(len(rows))
        i = 0
        for row in tqdm(rows, desc="Processing results"):
            #col = row.find_elements_by_tag_name('td')[2]
            col = WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.TAG_NAME,'td')))[2]
            col.click()
            while(True):
                try:     
                    self.link_text_click('Detailed')
                    #source = self.test_details_value(driver, 3)
                    #dest = self.test_details_value(driver, 8)
                    last_report = self.report_name + str(i)
                    report_name_field = self.enter_text_id('test-result-report-name', last_report, bounce=True)
                    report_name_field.find_element_by_xpath('..').find_element_by_tag_name('div').find_element_by_tag_name('button').click()
                    self.driver.find_element_by_link_text('CSV').click()
                    WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,'//button[contains(text(), "OK")]'))).click()
                    self.id_click('resultsModal-times')
                    break
                except: 
                    continue
            i += 1
            sleep(1.5)
    
        # try:
        #     results_next_button = self.driver.find_element_by_id('results-table_next')
        #     self.driver.execute_script("arguments[0].click();", results_next_button)
        #     sleep(1)
        # except:
        #     break
        #rows = self.find_rows('results-table')
        
        # Go to reports
        self.id_click("sidemenu-reports")

        # select = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.NAME, 'reportsfiles-table_length')))
        # for option in select.find_elements_by_tag_name('option'):
        #     if option.text == '500':
        #         option.click() # select() in earlier versions of webdriver
        #         break
        self.set_table_length('reportsfiles-table_length')

        #time_frame = 'Past Day'
        #self.id_click('reportsfiles-time-filter')
        #WebDriverWait(self.driver,10).until(EC.element_to_be_clickable((By.XPATH,"//div[@class='daterangepicker dropdown-menu ltr opensright']//ul/li[text()='" + time_frame + "']"))).click()

        # Filter by report name
        self.filter_report_name()
        #last_report = 'aas_no_commands_report_107'

        # Iterate over reports and download
        report_rows = self.find_rows('reportsfiles-table', last_report)
        for row in tqdm(report_rows, desc="Processing reports"):
            sleep(0.05)
            col = row.find_elements_by_tag_name('td')[3]
            col.click()
            # try:
            #     next_button = self.driver.find_element_by_id('reportsfiles-table_next')
            #     self.driver.execute_script("arguments[0].click();", next_button)
            #     sleep(1)
            # except:
            #     break
            # report_rows = self.find_rows('reportsfiles-table')
            
        print("Completed!")

BROWSER = 'firefox'
DOWNLOAD_DIRECTORY = r"C:\Users\Mathias Henriksen\Desktop\hawkeye-reports-no-commands\\" # IMPORTANT - ENDING SLASH V IMPORTANT
GECKO_PATH = r"C:\Users\Mathias Henriksen\Desktop\geckodriver.exe"
TEST_TAG = 'test_aas_no_commands_13may'
REPORT_NAME = 'aas_no_commands_report_'

Scraper(BROWSER, DOWNLOAD_DIRECTORY, TEST_TAG, GECKO_PATH, REPORT_NAME)