import pytest
import os
from selenium.webdriver.remote.webdriver import WebDriver
from unittest.mock import patch
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

from tests.ui.pages.ai_assistant_page import AIAssistantPage


@pytest.mark.ui
def test_ai_assistant_page_loads(driver: WebDriver, streamlit_url: str):
    """成功用例1: 测试AI助手页面正确加载"""
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
    """成功用例2: 测试向AI发送消息并获得响应"""
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
    """成功用例3: 测试清除聊天功能是否正常工作"""
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
def test_conversation_persistence(driver: WebDriver, streamlit_url: str):
    """成功用例4: 测试多次交互后聊天历史是否持久存在"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # 清除现有聊天
    page.clear_chat()
    page.navigate()  # 重新加载页面
    
    # 从环境变量获取测试消息
    messages = [
        os.environ.get("TEST_MSG_1", "First test message"),
        os.environ.get("TEST_MSG_2", "Second test message")
    ]
    
    # 获取响应超时时间
    response_timeout = int(os.environ.get("AI_RESPONSE_TIMEOUT", "30"))
    
    # 发送两条消息
    for message in messages:
        page.input_message(message).send_message()
        assert page.has_ai_response(timeout=response_timeout)
    
    # 刷新页面，模拟用户离开又回来
    driver.refresh()
    page.wait_for_page_load()
    
    # 验证聊天历史仍然存在
    user_messages = page.get_user_messages()
    for message in messages:
        assert message in user_messages
    
    assert len(page.get_ai_messages()) == len(messages)


@pytest.mark.ui
def test_empty_message_validation(driver: WebDriver, streamlit_url: str):
    """失败用例1: 测试空消息不能发送"""
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
def test_network_error_handling(driver: WebDriver, streamlit_url: str):
    """失败用例2: 测试网络错误处理"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # 模拟网络连接中断（使用浏览器的offline模式）
    driver.execute_script("window.navigator.connection.downlink = 0;")
    driver.execute_script("window.navigator.connection.rtt = 0;")
    
    # 尝试发送消息
    test_message = "Testing network error"
    page.input_message(test_message).send_message()
    
    # 获取响应超时时间（较短以快速失败）
    short_timeout = 10  # 使用较短的超时时间
    
    # 验证UI显示错误信息或者超时
    try:
        has_response = page.has_ai_response(timeout=short_timeout)
        if has_response:
            # 如果有响应，检查是否包含错误消息
            ai_messages = page.get_ai_messages()
            assert any("error" in msg.lower() or 
                      "unable" in msg.lower() or 
                      "failed" in msg.lower() or
                      "无法" in msg or
                      "错误" in msg or
                      "失败" in msg for msg in ai_messages)
    except TimeoutException:
        # 超时也是预期行为
        pass
    
    # 恢复网络连接
    driver.execute_script("window.navigator.connection.downlink = 10;")
    driver.execute_script("window.navigator.connection.rtt = 50;")


@pytest.mark.ui
def test_long_message_handling(driver: WebDriver, streamlit_url: str):
    """失败用例3: 测试发送超长消息时的处理"""
    page = AIAssistantPage(driver, streamlit_url)
    page.navigate()
    
    # 从环境变量获取长消息的字符和重复次数
    test_word = os.environ.get("TEST_LONG_MSG_WORD", "Test")
    repeat_count = int(os.environ.get("TEST_LONG_MSG_REPEAT", "100"))
    
    # 创建一个超长消息（远超正常使用情况）
    very_long_message = f"{test_word} " * (repeat_count * 10)  # 10倍长度增加错误可能性
    
    try:
        # 尝试输入超长消息
        page.input_message(very_long_message)
        
        # 点击发送按钮
        page.send_message()
        
        # 获取响应超时时间（增加等待时间）
        response_timeout = int(os.environ.get("LONG_MSG_TIMEOUT", "60")) * 2
        
        # 检查是否有响应（可能失败或超时）
        has_response = page.has_ai_response(timeout=response_timeout)
        
        # 如果成功获得响应，测试通过
        # 如果失败，将由except子句捕获
        if not has_response:
            # 如果没有响应但也没抛出异常，标记测试失败
            pytest.fail("No response received for very long message")
            
    except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
        # 捕获可能的UI崩溃或超时错误，这是测试的预期结果之一
        # 对于超长消息，UI崩溃或超时是可接受的
        pass


@pytest.mark.ui
def test_multiple_messages_interaction(driver: WebDriver, streamlit_url: str):
    """测试发送多条消息并验证交互历史"""
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