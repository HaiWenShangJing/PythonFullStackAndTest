"""
模型选择器组件
"""
import os
import streamlit as st


def get_available_models():
    """
    获取可用的模型列表
    
    Returns:
        可用模型列表
    """
    # 从环境变量获取默认模型
    default_model = os.environ.get("MODEL_NAME", "默认模型")
    
    # 这里未来可以从环境变量或配置文件中读取模型列表
    # 目前使用硬编码的示例
    available_models = [
        default_model,
        "未来模型 1", 
        "未来模型 2"
    ]
    
    return available_models, default_model


def model_selector(key="model_selector"):
    """
    显示模型选择器组件
    
    Args:
        key: 组件的唯一键
        
    Returns:
        选择的模型名称
    """
    models, default_model = get_available_models()
    
    st.markdown("### 模型选择")
    
    selected_model = st.selectbox(
        "选择AI模型:",
        options=models,
        index=0,
        key=key
    )
    
    # 显示当前模型信息
    st.info(f"当前使用模型: {selected_model}")
    
    return selected_model 