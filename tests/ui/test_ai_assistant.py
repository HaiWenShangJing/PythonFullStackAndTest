import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from tests.ui.pages.ai_assistant_page import AIAssistantPage


def test_ai_assistant_page_loads(driver: WebDriver, streamlit_url: str):
    """Test that the AI Assistant page loads correctly"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # Verify page elements
    assert page.is_page_loaded()
    
    # Check that input field and buttons are present
    driver.find_element(*page.MESSAGE_INPUT)
    driver.find_element(*page.SEND_BUTTON)
    driver.find_element(*page.CLEAR_BUTTON)


def test_send_message_to_ai(driver: WebDriver, streamlit_url: str):
    """Test sending a message to the AI and getting a response"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # Send a test message
    test_message = "Hello, AI assistant!"
    page.input_message(test_message).send_message()
    
    # Verify the message appears in the chat history
    user_messages = page.get_user_messages()
    assert test_message in user_messages
    
    # Verify AI responded (note: in a real test, we'd need to mock the AI response)
    assert page.has_ai_response()
    assert len(page.get_ai_messages()) > 0


def test_clear_chat_functionality(driver: WebDriver, streamlit_url: str):
    """Test that the clear chat button works"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # Send a message to generate chat history
    page.input_message("Test message for clearing").send_message()
    
    # Verify we have messages
    assert len(page.get_user_messages()) > 0
    assert len(page.get_ai_messages()) > 0
    
    # Clear the chat
    page.clear_chat()
    
    # Verify chat is cleared
    # Note: Need to refresh page object references after page reloads
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    assert len(page.get_user_messages()) == 0
    assert len(page.get_ai_messages()) == 0