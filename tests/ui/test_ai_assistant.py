import pytest
import os
from selenium.webdriver.remote.webdriver import WebDriver
from unittest.mock import patch
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tests.ui.pages.ai_assistant_page import AIAssistantPage


@pytest.mark.ui
def test_ai_assistant_page_loads(driver: WebDriver, streamlit_url: str):
    """Test that the AI Assistant page loads correctly"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # 获取页面加载超时时间
    page_load_timeout = int(os.environ.get("PAGE_LOAD_TIMEOUT", "30"))
    
    # Verify page elements with configurable timeout
    assert page.is_page_loaded(timeout=page_load_timeout)
    
    # Check that input field and buttons are present
    driver.find_element(*page.MESSAGE_INPUT)
    driver.find_element(*page.SEND_BUTTON)
    driver.find_element(*page.CLEAR_BUTTON)


@pytest.mark.ui
def test_send_message_to_ai(driver: WebDriver, streamlit_url: str):
    """Test sending a message to the AI and getting a response"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # 从环境变量获取测试消息
    test_message = os.environ.get("TEST_AI_MESSAGE", "Hello, AI assistant!")
    page.input_message(test_message).send_message()
    
    # 获取响应超时时间
    response_timeout = int(os.environ.get("AI_RESPONSE_TIMEOUT", "30"))
    
    # Verify the message appears in the chat history
    user_messages = page.get_user_messages()
    assert test_message in user_messages
    
    # Verify AI responded (note: in a real test, we'd need to mock the AI response)
    assert page.has_ai_response(timeout=response_timeout)
    assert len(page.get_ai_messages()) > 0


@pytest.mark.ui
def test_clear_chat_functionality(driver: WebDriver, streamlit_url: str):
    """Test that the clear chat button works"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # 从环境变量获取测试消息
    test_message = os.environ.get("TEST_CLEAR_MESSAGE", "Test message for clearing")
    
    # Send a message to generate chat history
    page.input_message(test_message).send_message()
    
    # 获取响应超时时间
    response_timeout = int(os.environ.get("AI_RESPONSE_TIMEOUT", "30"))
    
    # Wait for AI response
    page.has_ai_response(timeout=response_timeout)
    
    # Verify we have messages
    assert len(page.get_user_messages()) > 0
    assert len(page.get_ai_messages()) > 0
    
    # Clear the chat
    page.clear_chat()
    
    # 获取页面重新加载超时时间
    reload_timeout = int(os.environ.get("PAGE_RELOAD_TIMEOUT", "10"))
    
    # Verify chat is cleared
    # Note: Need to refresh page object references after page reloads
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    page.wait_for_page_load(timeout=reload_timeout)
    assert len(page.get_user_messages()) == 0
    assert len(page.get_ai_messages()) == 0


@pytest.mark.ui
def test_empty_message_validation(driver: WebDriver, streamlit_url: str):
    """Test that empty messages cannot be sent"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # Get initial message count
    initial_user_messages = len(page.get_user_messages())
    
    # Try to send an empty message
    page.input_message("").send_message()
    
    # 获取验证延迟时间
    validation_timeout = int(os.environ.get("VALIDATION_TIMEOUT", "3"))
    
    # Wait a moment for potential changes
    import time
    time.sleep(validation_timeout)
    
    # Verify no new message was sent
    assert len(page.get_user_messages()) == initial_user_messages


@pytest.mark.ui
def test_long_message_handling(driver: WebDriver, streamlit_url: str):
    """Test sending a very long message to check handling"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # 从环境变量获取长消息的字符和重复次数
    test_word = os.environ.get("TEST_LONG_MSG_WORD", "Test")
    repeat_count = int(os.environ.get("TEST_LONG_MSG_REPEAT", "100"))
    
    # Create a long message
    long_message = f"{test_word} " * repeat_count
    
    # Send the long message
    page.input_message(long_message).send_message()
    
    # 获取响应超时时间
    response_timeout = int(os.environ.get("LONG_MSG_TIMEOUT", "60"))
    
    # Verify the message was sent
    user_messages = page.get_user_messages()
    assert long_message in user_messages
    
    # Verify AI responded
    assert page.has_ai_response(timeout=response_timeout)


@pytest.mark.ui
def test_multiple_messages_interaction(driver: WebDriver, streamlit_url: str):
    """Test sending multiple messages in sequence"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # Clear any existing chat
    page.clear_chat()
    
    # 获取页面重新加载超时时间
    reload_timeout = int(os.environ.get("PAGE_RELOAD_TIMEOUT", "10"))
    
    # 重新加载页面
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    page.wait_for_page_load(timeout=reload_timeout)
    
    # 从环境变量获取测试消息
    messages = [
        os.environ.get("TEST_MSG_1", "First test message"),
        os.environ.get("TEST_MSG_2", "Second test message"),
        os.environ.get("TEST_MSG_3", "Third test message")
    ]
    
    # 获取响应超时时间
    response_timeout = int(os.environ.get("AI_RESPONSE_TIMEOUT", "30"))
    
    # Send three messages in sequence
    for message in messages:
        page.input_message(message).send_message()
        # 等待AI响应
        assert page.has_ai_response(timeout=response_timeout)
    
    # Verify all messages were sent
    user_messages = page.get_user_messages()
    for message in messages:
        assert message in user_messages
    
    # Verify AI responded to each message
    ai_messages = page.get_ai_messages()
    assert len(ai_messages) == len(messages)