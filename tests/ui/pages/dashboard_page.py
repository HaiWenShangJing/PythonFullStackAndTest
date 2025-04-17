from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage

class DashboardPage(BasePage):
    """Dashboard页面对象"""
    
    # 定位器
    PAGE_TITLE = (By.XPATH, "//h1[text()='Dashboard']")
    METRIC_CARDS = (By.CSS_SELECTOR, "div[data-testid='stMetric']")
    RECENT_ITEMS = (By.XPATH, "//h3[contains(text(), 'Recent Items')]")
    RECENT_CONVERSATIONS = (By.XPATH, "//h3[contains(text(), 'Recent AI Conversations')]")
    
    def navigate(self):
        """导航到Dashboard页面"""
        super().navigate_to("Dashboard")
        self.wait.until(EC.presence_of_element_located(self.PAGE_TITLE))
        return self
    
    def is_page_loaded(self) -> bool:
        """检查页面是否加载完成"""
        try:
            return self.driver.find_element(*self.PAGE_TITLE).is_displayed()
        except:
            return False
    
    def get_metrics(self):
        """获取所有指标卡的值"""
        metrics = {}
        metric_elements = self.driver.find_elements(*self.METRIC_CARDS)
        for metric in metric_elements:
            label = metric.find_element(By.CSS_SELECTOR, "label").text
            value = metric.find_element(By.CSS_SELECTOR, "div[data-testid='stMetricValue']").text
            metrics[label] = value
        return metrics
