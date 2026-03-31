from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class Scraper:

    def __init__(self, url, headless=True):
        """
        Initialize the Scraper with the given URL and headless option.
        
        Attributes:
            __url (str): The URL of the site to scrape.
            __driver (webdriver.Chrome): The Chrome WebDriver instance.
            __urls_jobs_list (list): List of job offer URLs.
        """
        self.__driver = None
        self.__url = url
        self.__urls_jobs_list = []
        self.__init_driver(headless)
        self.__scrape_jobs()

    def __init_driver(self, headless):
        """
        Initialize the Chrome WebDriver with the specified options.
        
        Args:
            headless (bool): Whether to run the browser in headless mode.
        """
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        self.__driver = webdriver.Chrome(options=options)

        if not self.__driver:
            print("Failed to initialize the WebDriver.")

    def __scrape_jobs(self):
        """
        Scrape the job URLs from the given website.
        """
        self.__driver.get(self.__url)
        job_list = self.__driver.find_elements(By.CLASS_NAME, "job-list")
        for i, e in enumerate(job_list):
            tag_A = e.find_element(By.TAG_NAME, 'a')
            self.__urls_jobs_list.append(tag_A.get_attribute("href"))

    def get_job_description(self, url: str) -> str:
        """
        Extract the job description from the given URL by opening a new tab.
        
        Args:
            url (str): The URL of the job offer.
        
        Returns:
            str: The job description text.
        """
        # Open a new tab
        self.__driver.execute_script(f"window.open('{url}', '_blank');")
        self.__driver.switch_to.window(self.__driver.window_handles[-1])  # Switch to the newly opened tab

        try:
            # Wait for the description to load
            description = self.__driver.find_element(By.CLASS_NAME, "job-description").text
            self.__driver.close()
            self.__driver.switch_to.window(self.__driver.window_handles[0])
            return description
        except Exception as e:
            print(f"Error retrieving job description: {e}")
            self.__driver.close()
            self.__driver.switch_to.window(self.__driver.window_handles[0])
            return None

    def get_jobs(self) -> list:
        """
        Return the list of job URLs.
        
        Returns:
            list: List of job offer URLs.
        """
        return self.__urls_jobs_list

    def driver_quit(self):
        """
        Close the WebDriver.
        """
        if self.__driver:
            self.__driver.quit()