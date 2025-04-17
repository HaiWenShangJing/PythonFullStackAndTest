import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from tests.ui.pages.dashboard_page import DashboardPage

def test_dashboard_page_loads(driver: WebDriver, streamlit_url: str):
    """测试Dashboard页面加载"""
    page = DashboardPage(driver, streamlit_url)
    page.navigate()
    
    assert page.is_page_loaded()
    metrics = page.get_metrics()
    assert "Total Items" in metrics
    assert "AI Chat Interactions" in metrics
