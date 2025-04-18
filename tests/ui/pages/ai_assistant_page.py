from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os

from .base_page import BasePage


class AIAssistantPage(BasePage):
    """Page Object Model for the AI Assistant page"""
    
    # Locators
    PAGE_TITLE = (By.XPATH, "//h1[contains(text(), 'AI Assistant')]")
    MESSAGE_INPUT = (By.CSS_SELECTOR, "textarea[aria-label='Your message:']")
    SEND_BUTTON = (By.XPATH, "//button[contains(text(), 'Send Message')]")
    CLEAR_BUTTON = (By.XPATH, "//button[contains(text(), 'Clear Chat')]")
    USER_MESSAGES = (By.XPATH, "//div[contains(text(), 'You:')]")
    AI_MESSAGES = (By.XPATH, "//div[contains(text(), 'AI:')]")
    LOADING_SPINNER = (By.CSS_SELECTOR, "div[data-testid='stSpinner']")
    
    def navigate(self):
        """Navigate to the AI Assistant page"""
        super().navigate_to("AI Assistant")
        # 使用环境变量配置的页面加载超时时间
        timeout = int(os.environ.get("PAGE_LOAD_TIMEOUT", "30"))
        self.wait_for_page_load(timeout)
        return self
    
    def wait_for_page_load(self, timeout=None):
        """等待页面加载完成"""
        if timeout is None:
            timeout = int(os.environ.get("PAGE_LOAD_TIMEOUT", "30"))
        wait = WebDriverWait(self.driver, timeout)
        wait.until(EC.presence_of_element_located(self.PAGE_TITLE))
        return self
    
    def is_page_loaded(self, timeout=None) -> bool:
        """Check if the AI Assistant page is loaded"""
        try:
            if timeout is not None:
                wait = WebDriverWait(self.driver, timeout)
                return wait.until(EC.visibility_of_element_located(self.PAGE_TITLE)) is not None
            return self.driver.find_element(*self.PAGE_TITLE).is_displayed()
        except:
            return False
    
    def input_message(self, message: str):
        """Enter a message in the input field"""
        # 使用环境变量配置的输入超时时间
        timeout = int(os.environ.get("INPUT_TIMEOUT", "10"))
        wait = WebDriverWait(self.driver, timeout)
        input_field = wait.until(EC.element_to_be_clickable(self.MESSAGE_INPUT))
        input_field.clear()
        input_field.send_keys(message)
        return self
    
    def send_message(self):
        """Click the send message button"""
        # 使用环境变量配置的按钮点击超时时间
        timeout = int(os.environ.get("BUTTON_CLICK_TIMEOUT", "10"))
        wait = WebDriverWait(self.driver, timeout)
        send_button = wait.until(EC.element_to_be_clickable(self.SEND_BUTTON))
        send_button.click()
        # Wait for loading spinner to appear and disappear (AI response)
        try:
            self.wait.until(EC.presence_of_element_located(self.LOADING_SPINNER))
            self.wait.until(EC.invisibility_of_element_located(self.LOADING_SPINNER))
        except:
            # If spinner doesn't appear or disappear, continue anyway
            pass
        return self
    
    def clear_chat(self):
        """Click the clear chat button"""
        # 使用环境变量配置的按钮点击超时时间
        timeout = int(os.environ.get("BUTTON_CLICK_TIMEOUT", "10"))
        wait = WebDriverWait(self.driver, timeout)
        clear_button = wait.until(EC.element_to_be_clickable(self.CLEAR_BUTTON))
        clear_button.click()
        return self
    
    def get_user_messages(self):
        """Get all user messages in the chat"""
        elements = self.driver.find_elements(*self.USER_MESSAGES)
        return [element.text.replace('🧑 You:', '').strip() for element in elements]
    
    def get_ai_messages(self):
        """Get all AI messages in the chat"""
        elements = self.driver.find_elements(*self.AI_MESSAGES)
        return [element.text.replace('🤖 AI:', '').strip() for element in elements]
    
    def has_ai_response(self, timeout=None) -> bool:
        """Check if there is an AI response in the chat with configurable timeout"""
        if timeout is None:
            timeout = int(os.environ.get("AI_RESPONSE_TIMEOUT", "30"))
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda d: len(d.find_elements(*self.AI_MESSAGES)) > 0)
            return True
        except:
            return False