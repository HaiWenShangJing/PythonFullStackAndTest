from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage

class DataManagementPage(BasePage):
    """Data Management页面对象"""
    
    # 定位器
    PAGE_TITLE = (By.XPATH, "//h1[contains(text(), 'Data Management')]")
    ADD_ITEM_EXPANDER = (By.XPATH, "//button[contains(text(), 'Add New Item')]")
    NAME_INPUT = (By.CSS_SELECTOR, "input[aria-label='Name']")
    DESCRIPTION_INPUT = (By.CSS_SELECTOR, "textarea[aria-label='Description']")
    CREATE_BUTTON = (By.XPATH, "//button[contains(text(), 'Create Item')]")
    ITEMS_TABLE = (By.CSS_SELECTOR, "div[data-testid='stDataFrame']")
    
    def navigate(self):
        """导航到Data Management页面"""
        super().navigate_to("Data Management")
        self.wait.until(EC.presence_of_element_located(self.PAGE_TITLE))
        return self
    
    def is_page_loaded(self) -> bool:
        """检查页面是否加载完成"""
        try:
            return self.driver.find_element(*self.PAGE_TITLE).is_displayed()
        except:
            return False
    
    def add_new_item(self, name: str, description: str = ""):
        """添加新数据项"""
        # 展开添加项表单
        self.driver.find_element(*self.ADD_ITEM_EXPANDER).click()
        
        # 填写表单
        self.driver.find_element(*self.NAME_INPUT).send_keys(name)
        self.driver.find_element(*self.DESCRIPTION_INPUT).send_keys(description)
        
        # 提交表单
        self.driver.find_element(*self.CREATE_BUTTON).click()
        
        # 等待加载完成
        self.wait_for_loading()
        return self
    
    def get_items_count(self) -> int:
        """获取数据项数量"""
        try:
            table = self.driver.find_element(*self.ITEMS_TABLE)
            rows = table.find_elements(By.CSS_SELECTOR, "tr")
            # 减去1 (表头行)
            return len(rows) - 1
        except:
            return 0
