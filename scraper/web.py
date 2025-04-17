import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class UNCTADScraper:
    def __init__(self, headless=False):
        """Initialize the UNCTAD Trains Online scraper."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        self.url = "https://trainsonline.unctad.org/detailedSearch?imposingCountries=1,4,8,10,16,11,12,9,13,14,15,17,34,18,59,21,23,25,30,31,242,33,38,35,36,37,42,43,44,48,49,51,54,55,56,57,58,110,52,60,61,63,234,64,68,215,66,279,72,73,75,80,82,81,84,85,88,90,93,94,95,99,100,101,102,103,104,107,108,109,111,112,114,113,115,118,119,120,123,121,122,124,127,128,131,132,134,135,137,138,139,145,146,32,148,150,151,158,159,160,164,147,170,83,171,172,173,174,175,177,178,182,184,185,186,197,198,200,202,203,205,28,207,117,209,41,213,216,217,219,239,220,221,224,226,227,231,225,240,243,157,245,204,249&imposingCountriesGroupSelection=&imposingCountriesAll=true&internationalStandardsImposing=false&imposingCountriesGroup=0&affectedCountries=1,2,4,5,6,7,190,3,8,10,16,153,11,12,9,13,14,15,17,34,18,26,59,19,20,21,155,22,23,24,25,273,27,29,30,31,242,33,38,35,36,37,39,40,42,43,44,46,47,48,49,51,53,54,55,56,152,57,58,250,110,52,60,79,61,62,63,234,64,65,67,68,215,66,279,69,70,72,73,75,77,78,80,82,81,84,85,86,88,89,90,92,93,236,94,179,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,111,112,237,274,114,113,115,87,277,118,119,120,123,121,122,124,125,127,128,129,130,131,132,133,134,135,168,137,138,139,167,275,142,141,143,144,145,146,32,148,149,150,151,254,256,156,158,159,160,161,162,163,116,233,165,164,147,257,170,169,83,171,259,172,173,174,175,176,177,178,182,184,185,186,187,188,189,191,192,193,194,247,195,196,278,197,198,199,272,200,201,202,154,203,205,28,206,207,71,117,210,209,41,211,264,213,214,216,217,218,45,219,239,220,180,221,222,223,224,226,228,229,230,227,265,231,232,225,235,240,166,269,243,244,157,245,204,276,246,212,248,263,271,249,208,74&affectedCountriesGroupSelection=&affectedCountriesAll=true&affectedCountriesGroup=0&products=&productsAll=true&productsGroup=1&ntmTypes=A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P&allNtmTypes=true&fromDate=2020-1-1&toDate=&import=true&export=true&multilateral=true&unilateral=true&pageNumber=1&columnsVisibility=%7B%22countryImposingNTMsVisible%22:true,%22affectedCountriesNamesVisible%22:true,%22ntmCodeVisible%22:true,%22ntmDescriptionVisible%22:true,%22measureDescriptionVisible%22:true,%22productDescriptionVisible%22:false,%22hsCodeVisible%22:true,%22issuingAgencyVisible%22:false,%22regulationTitleVisible%22:true,%22regulationSymbolVisible%22:false,%22implementationDateVisible%22:true,%22regulationFileVisible%22:true,%22regulationOfficialTitleOriginalVisible%22:false,%22measureDescriptionOriginalVisible%22:false,%22measureProductDescriptionOriginalVisible%22:false,%22supportingRegulationsVisible%22:false,%22measureObjectivesOriginalVisible%22:false,%22yearsOfDataCollectionVisible%22:false,%22repealDateVisible%22:false,%22objectiveCodesVisible%22:true%7D"

    def wait_for_page_load(self, timeout=30):
        """Wait for the page to fully load."""
        time.sleep(2)
        try:
            # Wait for the document to be in a ready state
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )

            # Wait for Angular to finish rendering (since this appears to be an Angular app)
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(
                    "return (window.angular !== undefined) ? "
                    "window.angular.element(document).injector().get('$http').pendingRequests.length === 0 : true"
                )
            )

            # Additional wait for any AJAX requests to complete
            time.sleep(2)

            print("Page fully loaded")
            return True
        except Exception as e:
            print(f"Error waiting for page to load: {e}")
            return False

    def navigate_to_site(self):
        """Navigate to the UNCTAD Trains Online detailed search page."""
        self.driver.get(self.url)
        self.wait_for_page_load()

        # Also wait for the specific form element we're interested in
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "app-country-groups-selection")
            )
        )

        print("Successfully navigated to the UNCTAD Trains Online search page")

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            print("Browser closed")


def main():
    # Initialize scraper
    scraper = UNCTADScraper(headless=False)

    try:
        # Navigate to the site
        scraper.navigate_to_site()

        # Keep the browser open until manually closed
        input("Press Enter to close the browser...")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        scraper.close()


if __name__ == "__main__":
    main()
