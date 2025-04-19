"""
提供应用程序所需的CSS样式
"""

def get_chat_css():
    """
    获取聊天界面的CSS样式 (Updated for st.chat_input)
    """
    return """
    <style>
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        /* Keep footer hidden if desired */
        footer {visibility: hidden;}
        /* Hide status widget */
        div[data-testid="stStatusWidget"] {display: none !important;}

        /* Ensure main chat area stretches and scrolls */
        /* Target the block container likely holding the chat messages */
        div[data-testid="stBlockContainer"]:has(div[data-testid="stVerticalBlock"]) {
             /* This might need adjustment based on exact structure */
             /* flex-grow: 1; Seems unnecessary with chat_input */
             /* No padding-bottom needed here, st.chat_input handles spacing */
        }

        /* Style the chat messages within st.chat_message */
        [data-testid="stChatMessage"] {
            /* Example: Add gap between messages */
             margin-bottom: 10px; 
        }

        /* --- Remove Old/Redundant Styles --- */
        /* Remove custom chat container height/margin/padding */
        /* .chat-container { ... } */

        /* Remove specific input-container styling (handled by st.chat_input) */
        /* .input-container { ... } */

        /* Remove padding-bottom hack */
        /* div[data-testid="stVerticalBlock"] > ... { padding-bottom: 120px; } */

        /* Keep other styles like message bubbles if needed for custom markdown rendering */
        /* (Though st.chat_message often handles this better) */
         .message-bubble {
             padding: 10px 15px;
             border-radius: 18px;
             display: inline-block;
             margin-bottom: 5px;
             max-width: 80%; /* Limit bubble width */
             word-wrap: break-word; /* Wrap long words */
         }
         .user-bubble {
             background-color: #f0f0f0;
             /* align-self: flex-end; Handled by st.chat_message */
         }
         .ai-bubble {
             background-color: #e6f7ff;
             color: black;
             /* align-self: flex-start; Handled by st.chat_message */
         }

        /* Custom styling for code blocks inside markdown */
        pre {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: monospace; /* Ensure monospace font */
            font-size: 0.9em;
        }
        code {
            font-family: monospace; /* Ensure monospace font */
            background-color: #f0f0f0; /* Slight background for inline code */
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
        }

        /* Retain other styles if necessary */
        .model-selector {
            max-width: 250px;
            margin-bottom: 20px;
        }
        h1 {
            font-size: 24px !important;
            color: #333;
            margin-bottom: 20px !important;
        }
        .stTextArea textarea {
            border-radius: 20px !important;
            padding: 12px !important;
        }
        .stButton button {
            border-radius: 20px !important;
            background-color: #4169E1 !important;
            color: white !important;
            padding: 5px 20px !important;
        }
    </style>
    """ 