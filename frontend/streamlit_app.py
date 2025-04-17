import os
import uuid
from typing import List, Optional, Tuple

import httpx
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

# API Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")


def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "items" not in st.session_state:
        st.session_state.items = []


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


async def send_message_to_ai(message: str) -> str:
    """Send a message to the AI and get a response"""
    # Format context for the AI
    context = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]
    
    # Add chat history as context (last 5 messages)
    for msg in st.session_state.chat_history[-5:]:
        role = "user" if msg["is_user"] else "assistant"
        context.append({"role": role, "content": msg["content"]})
    
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
                return data["message"]
            else:
                return f"Error: {response.text}"
        
        except Exception as e:
            return f"Error communicating with AI service: {str(e)}"


def display_dashboard():
    """Display the dashboard page"""
    st.title("Dashboard")
    st.write("Welcome to the Full-Stack AI CRUD Application!")
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    total_items = len(st.session_state.items)
    total_chats = len([msg for msg in st.session_state.chat_history if msg["is_user"]])
    
    with col1:
        st.metric(label="Total Items", value=total_items)
    
    with col2:
        st.metric(label="AI Chat Interactions", value=total_chats)
    
    with col3:
        st.metric(label="Active Session", value="Yes" if st.session_state.session_id else "No")
    
    # Recent items
    st.subheader("Recent Items")
    if not st.session_state.items:
        st.info("No items found. Go to the Data Management page to create some!")
    else:
        for item in st.session_state.items[:5]:
            with st.expander(f"{item['name']}"):
                st.write(f"**Description:** {item['description'] or 'No description'}")
                st.write(f"**Created:** {item['created_at']}")
    
    # Recent AI conversations
    st.subheader("Recent AI Conversations")
    if not st.session_state.chat_history:
        st.info("No chat history found. Go to the AI Assistant page to start a conversation!")
    else:
        for msg in st.session_state.chat_history[-4:]:
            if msg["is_user"]:
                st.write(f"🧑 **You:** {msg['content']}")
            else:
                st.write(f"🤖 **AI:** {msg['content']}")


def display_data_management():
    """Display the data management page"""
    st.title("Data Management")
    
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
            result = create_item(
                st.session_state.form_data["name"],
                st.session_state.form_data["description"]
            )
            if result:
                st.success("Item created successfully!")
                # Refresh items list
                items, _ = fetch_items()
                st.session_state.items = items
        
        # Reset form state
        del st.session_state.form_submitted
        del st.session_state.form_data
    
    # Display items table
    st.subheader("Items List")
    
    if not st.session_state.items:
        st.info("No items found.")
    else:
        # Create a dataframe for display
        df_data = []
        for item in st.session_state.items:
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
        item_names = [f"{item['name']} ({item['id'][:8]}...)" for item in st.session_state.items]
        selected_item_idx = st.selectbox("Select an item", range(len(item_names)), format_func=lambda i: item_names[i])
        selected_item = st.session_state.items[selected_item_idx]
        
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
                st.session_state.items = items
        
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
                st.session_state.items = items
        
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
            ai_response = send_message_to_ai(user_input)
            
            # Add AI response to history
            st.session_state.chat_history.append({
                "is_user": False,
                "content": ai_response
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
    
    # Fetch items on startup
    if not st.session_state.items:
        items, _ = fetch_items()
        st.session_state.items = items
    
    # Sidebar for navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.radio(
            "Go to",
            ["Dashboard", "Data Management", "AI Assistant"],
        )
        
        st.divider()
        st.write("Session ID:", st.session_state.session_id)
        
        # Refresh data button
        if st.button("Refresh Data"):
            with st.spinner("Refreshing data..."):
                items, _ = fetch_items()
                st.session_state.items = items
            st.success("Data refreshed!")
    
    # Display the selected page
    if page == "Dashboard":
        display_dashboard()
    elif page == "Data Management":
        display_data_management()
    elif page == "AI Assistant":
        display_ai_assistant()


if __name__ == "__main__":
    main()