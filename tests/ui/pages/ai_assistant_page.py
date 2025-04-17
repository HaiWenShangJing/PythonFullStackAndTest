from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
        self.wait.until(EC.presence_of_element_located(self.PAGE_TITLE))
        return self
    
    def is_page_loaded(self) -> bool:
        """Check if the AI Assistant page is loaded"""
        try:
            return self.driver.find_element(*self.PAGE_TITLE).is_displayed()
        except:
            return False
    
    def input_message(self, message: str):
        """Enter a message in the input field"""
        input_field = self.wait.until(EC.element_to_be_clickable(self.MESSAGE_INPUT))
        input_field.clear()
        input_field.send_keys(message)
        return self
    
    def send_message(self):
        """Click the send message button"""
        send_button = self.wait.until(EC.element_to_be_clickable(self.SEND_BUTTON))
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
        clear_button = self.wait.until(EC.element_to_be_clickable(self.CLEAR_BUTTON))
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
    
    def has_ai_response(self) -> bool:
        """Check if there is an AI response in the chat"""
        return len(self.get_ai_messages()) > 0