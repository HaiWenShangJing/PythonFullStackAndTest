from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class BasePage:
    """Base class for all page objects"""
    
    # 共享定位器
    SIDEBAR_NAVIGATION = (By.XPATH, "//div[contains(@class, 'st-emotion-cache')]//div[contains(@role, 'radio')]")
    LOADING_SPINNER = (By.CSS_SELECTOR, "div[data-testid='stSpinner']")
    
    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, 10)
    
    def navigate_to(self, page_name: str):
        """导航到指定页面"""
        self.driver.get(self.base_url)
        
        # 点击侧边栏中的页面链接
        sidebar_items = self.driver.find_elements(*self.SIDEBAR_NAVIGATION)
        for item in sidebar_items:
            if page_name in item.text:
                item.click()
                break
        
        return self
    
    def wait_for_loading(self):
        """等待加载结束"""
        try:
            self.wait.until(EC.presence_of_element_located(self.LOADING_SPINNER))
            self.wait.until(EC.invisibility_of_element_located(self.LOADING_SPINNER))
        except:
            # 如果加载器没有出现或消失，继续
            pass
        return self
