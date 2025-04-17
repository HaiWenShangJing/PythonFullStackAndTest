import os
import uuid
from typing import List, Optional, Tuple
from pathlib import Path

import httpx
import streamlit as st
from dotenv import load_dotenv
from streamlit.delta_generator import DeltaGenerator

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

# 使用绝对路径加载.env文件
print(f"Loading .env from: {ENV_FILE}")
load_dotenv(dotenv_path=ENV_FILE)

# API Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")


def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'items' not in st.session_state:
        st.session_state['items'] = []


async def fetch_items() -> Tuple[List[dict], int]:
    """Fetch items from the API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/items")
        if response.status_code == 200:
            data = response.json()
            return data["items"], data["total"]
        else:
            st.error(f"Error fetching items: {response.text}")
            return [], 0


async def create_item(name: str, description: Optional[str] = None) -> Optional[dict]:
    """Create a new item via API"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/items",
            json={"name": name, "description": description},
        )
        if response.status_code == 201:
            return response.json()
        else:
            st.error(f"Error creating item: {response.text}")
            return None


async def update_item(item_id: str, name: Optional[str] = None, description: Optional[str] = None) -> Optional[dict]:
    """Update an item via API"""
    data = {}
    if name:
        data["name"] = name
    if description:
        data["description"] = description
    
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{API_BASE_URL}/items/{item_id}",
            json=data,
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error updating item: {response.text}")
            return None


async def delete_item(item_id: str) -> bool:
    """Delete an item via API"""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{API_BASE_URL}/items/{item_id}")
        if response.status_code == 200:
            return True
        else:
            st.error(f"Error deleting item: {response.text}")
            return False


async def send_message_to_ai(message: str) -> dict:
    """Send a message to the AI and get a response"""
    # Format context for the AI
    context = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]
    
    # Add chat history as context (last 5 messages)
    for msg in st.session_state.chat_history[-5:]:
        # Add safety check to handle different message formats
        if isinstance(msg, dict):
            # If message has 'is_user' key, use it; otherwise try to determine from content or default to 'user'
            if "is_user" in msg:
                role = "user" if msg["is_user"] else "assistant" 
            elif "role" in msg:
                role = msg["role"]
            else:
                role = "user"  # Default role
            
            content = msg.get("content", "")
            context.append({"role": role, "content": content})
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/ai/chat",
                json={
                    "message": message,
                    "session_id": st.session_state.session_id,
                    "context": context,
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "message": data["message"],
                    "session_id": st.session_state.session_id
                }
            else:
                return {
                    "message": f"Error: {response.text}",
                    "session_id": st.session_state.session_id
                }
        
        except Exception as e:
            return {
                "message": f"Error communicating with AI service: {str(e)}",
                "session_id": st.session_state.session_id
            }


def display_dashboard():
    """Display the dashboard page"""
    st.title("Dashboard")
    st.write("Welcome to the Full-Stack AI CRUD Application!")
    
    # Create a completely local copy - avoid the method reference problem
    try:
        # Access through dictionary notation instead of attribute notation
        local_items = st.session_state["items"]
        # Check if it's callable (a method)
        if callable(local_items):
            local_items = []
        # Ensure it's a list
        if not isinstance(local_items, list):
            local_items = []
    except:
        local_items = []
    
    # Store back the fixed value
    st.session_state["items"] = local_items
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    total_items = len(local_items)  # Use local variable instead
    
    try:
        total_chats = len([msg for msg in st.session_state.chat_history if isinstance(msg, dict) and msg.get("is_user", False)])
    except:
        total_chats = 0
    
    with col1:
        st.metric(label="Total Items", value=total_items)
    
    with col2:
        st.metric(label="AI Chat Interactions", value=total_chats)
    
    with col3:
        st.metric(label="Active Session", value="Yes" if st.session_state.session_id else "No")
    
    # Use the local variable throughout the function
    st.subheader("Recent Items")
    if not local_items:
        st.info("No items found. Go to the Data Management page to create some!")
    else:
        for item in local_items[:5]:
            with st.expander(f"{item['name']}"):
                st.write(f"**Description:** {item['description'] or 'No description'}")
                st.write(f"**Created:** {item['created_at']}")
    
    # Recent AI conversations
    st.subheader("Recent AI Conversations")
    if not st.session_state.chat_history:
        st.info("No chat history found. Go to the AI Assistant page to start a conversation!")
    else:
        for msg in st.session_state.chat_history[-4:]:
            # 添加安全检查，确保存在is_user键
            if isinstance(msg, dict):
                if msg.get("is_user", False):
                    st.write(f"🧑 **You:** {msg.get('content', '')}")
                else:
                    st.write(f"🤖 **AI:** {msg.get('content', '')}")
            else:
                # 处理不是字典的情况
                st.write(f"🤖 **Message:** {str(msg)}")


def display_data_management():
    """Display the data management page"""
    st.title("Data Management")
    
    # 在顶部添加这段代码来修复items问题
    temp_items = st.session_state.get("items")
    if callable(temp_items) or not isinstance(temp_items, list):
        temp_items = []
        st.session_state["items"] = temp_items
    
    # Add new item form
    with st.expander("Add New Item", expanded=False):
        with st.form("new_item_form"):
            name = st.text_input("Name")
            description = st.text_area("Description")
            submit_button = st.form_submit_button("Create Item")
            
            if submit_button and name:
                st.session_state.form_submitted = True
                st.session_state.form_data = {"name": name, "description": description}
                st.rerun()
    
    # Handle form submission (after rerun to avoid streamlit form issues)
    if hasattr(st.session_state, "form_submitted") and st.session_state.form_submitted:
        with st.spinner("Creating item..."):
            result = asyncio.run(create_item(
                st.session_state.form_data["name"],
                st.session_state.form_data["description"]
            ))
            if result:
                st.success("Item created successfully!")
                # Refresh items list
                items, _ = asyncio.run(fetch_items())
                st.session_state.items = items if isinstance(items, list) else []
        
        # Reset form state
        del st.session_state.form_submitted
        del st.session_state.form_data
    
    # Display items table
    st.subheader("Items List")
    
    if not temp_items:  # 使用temp_items代替st.session_state.items
        st.info("No items found.")
    else:
        # Create a dataframe for display
        df_data = []
        for item in temp_items:  # 使用temp_items代替st.session_state.items
            df_data.append({
                "ID": item["id"],
                "Name": item["name"],
                "Description": item["description"] or "",
                "Created At": item["created_at"].split("T")[0],  # Just the date part
            })
        
        # Display as a dataframe
        st.dataframe(df_data, use_container_width=True)
        
        # Item actions
        st.subheader("Item Actions")
        
        # Select an item
        item_names = [f"{item['name']} ({item['id'][:8]}...)" for item in temp_items]
        selected_item_idx = st.selectbox("Select an item", range(len(item_names)), format_func=lambda i: item_names[i])
        selected_item = temp_items[selected_item_idx]
        
        # Action tabs
        tab1, tab2 = st.tabs(["Edit", "Delete"])
        
        with tab1:
            with st.form("edit_item_form"):
                edit_name = st.text_input("Name", value=selected_item["name"])
                edit_description = st.text_area("Description", value=selected_item["description"] or "")
                update_button = st.form_submit_button("Update Item")
                
                if update_button:
                    st.session_state.update_submitted = True
                    st.session_state.update_data = {
                        "id": selected_item["id"],
                        "name": edit_name,
                        "description": edit_description
                    }
                    st.rerun()
        
        with tab2:
            st.write("Are you sure you want to delete this item?")
            if st.button(f"Delete {selected_item['name']}", type="primary"):
                st.session_state.delete_id = selected_item["id"]
                st.rerun()
    
    # Handle update submission
    if hasattr(st.session_state, "update_submitted") and st.session_state.update_submitted:
        with st.spinner("Updating item..."):
            result = update_item(
                st.session_state.update_data["id"], 
                st.session_state.update_data["name"],
                st.session_state.update_data["description"]
            )
            if result:
                st.success("Item updated successfully!")
                # Refresh items list
                items, _ = fetch_items()
                st.session_state.items = items if isinstance(items, list) else []
        
        # Reset update state
        del st.session_state.update_submitted
        del st.session_state.update_data
    
    # Handle delete submission
    if hasattr(st.session_state, "delete_id"):
        with st.spinner("Deleting item..."):
            result = delete_item(st.session_state.delete_id)
            if result:
                st.success("Item deleted successfully!")
                # Refresh items list
                items, _ = fetch_items()
                st.session_state.items = items if isinstance(items, list) else []
        
        # Reset delete state
        del st.session_state.delete_id


def display_ai_assistant():
    """Display the AI assistant page"""
    st.title("AI Assistant")
    st.write("Chat with our AI assistant for help and information.")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["is_user"]:
                st.write(f"🧑 **You:** {message['content']}")
            else:
                st.write(f"🤖 **AI:** {message['content']}")
    
    # Input for new message
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area("Your message:", height=100)
        cols = st.columns([4, 1])
        with cols[0]:
            submit_button = st.form_submit_button("Send Message")
        with cols[1]:
            clear_button = st.form_submit_button("Clear Chat")
    
    # Handle new message
    if submit_button and user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "is_user": True,
            "content": user_input
        })
        
        # Show a spinner while waiting for AI response
        with st.spinner("AI is thinking..."):
            response = send_message_to_ai(user_input)
            
            # Add AI response to history
            st.session_state.chat_history.append({
                "is_user": False,
                "content": response["message"]
            })
        
        # Rerun to update the UI
        st.rerun()
    
    # Clear chat history if requested
    if clear_button:
        st.session_state.chat_history = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()


def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Full-Stack AI CRUD App",
        page_icon="🤖",
        layout="wide",
    )
    
    # Initialize session state
    initialize_session_state()
    
    # 添加状态指示器，在侧边栏显示
    with st.sidebar:
        st.title("Navigation")
        status_container = st.empty()
        
        # 显示当前API连接状态
        api_status = check_api_connection()
        
        if api_status:
            status_container.success("✅ API Connected")
        else:
            status_container.error("❌ API Connection Failed")
            st.error(f"Cannot connect to API at {API_BASE_URL}")
            st.info("Make sure your backend server is running.")
            st.code("docker-compose up -d")
            
        page = st.radio(
            "Go to",
            ["Dashboard", "Data Management", "AI Assistant"],
        )
        
        st.divider()
        st.write("Session ID:", st.session_state.session_id)
        
        # Refresh data button
        if st.button("Refresh Data"):
            with st.spinner("Refreshing data..."):
                items, _ = asyncio.run(fetch_items())
                st.session_state.items = items if isinstance(items, list) else []
            st.success("Data refreshed!")
    
    # Fetch items on startup using asyncio.run
    import asyncio
    import sys
    from pathlib import Path

    # Add frontend directory to Python path
    frontend_dir = str(Path(__file__).parent.resolve())
    if frontend_dir not in sys.path:
        sys.path.append(frontend_dir)

    if not st.session_state.items:
        try:
            with st.spinner("Loading initial data..."):
                items, _ = asyncio.run(fetch_items())
                st.session_state.items = items if isinstance(items, list) else []
        except Exception as e:
            st.error(f"Failed to fetch initial items: {e}")
            st.session_state.items = [] # Ensure it's an empty list on error
    
    # Display the selected page
    if page == "Dashboard":
        display_dashboard()
    elif page == "Data Management":
        display_data_management()
    elif page == "AI Assistant":
        display_ai_assistant()


def check_api_connection():
    """检查API连接状态"""
    import asyncio
    
    async def _check_connection():
        try:
            async with httpx.AsyncClient() as client:
                # 使用API_BASE_URL的基础路径部分 + "/"
                base_url = API_BASE_URL.rstrip("/api/v1")
                if not base_url:
                    base_url = "http://localhost:8000"
                
                # 首先尝试API根路径
                response = await client.get(f"{API_BASE_URL}/", timeout=2.0)
                if response.status_code == 200:
                    return True
                    
                # 如果失败，尝试服务器根路径
                response = await client.get(f"{base_url}/", timeout=2.0)
                return response.status_code == 200
        except Exception as e:
            print(f"API连接错误: {str(e)}")
            return False
    
    try:
        return asyncio.run(_check_connection())
    except Exception as e:
        print(f"运行API检查时出错: {str(e)}")
        return False


if __name__ == "__main__":
    main()