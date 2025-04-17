import os
from typing import Generator

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.fixture(scope="function")
def driver() -> Generator[WebDriver, None, None]:
    """Setup a Selenium WebDriver for UI testing"""
    # Get environment variables
    selenium_hub_url = os.environ.get("SELENIUM_HUB_URL", "http://localhost:4444/wd/hub")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Create a remote WebDriver using Selenium Grid
    try:
        driver = webdriver.Remote(
            command_executor=selenium_hub_url,
            options=chrome_options
        )
        driver.implicitly_wait(10)
        
        yield driver
    finally:
        if driver:
            driver.quit()


@pytest.fixture(scope="session")
def streamlit_url() -> str:
    """Get the URL for the Streamlit app"""
    return os.environ.get("STREAMLIT_URL", "http://localhost:8501")