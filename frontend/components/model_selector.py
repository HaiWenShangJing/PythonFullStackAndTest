"""
模型选择器组件
"""
import os
import streamlit as st


def get_available_models():
    """
    获取可用的模型列表 (从环境变量读取)
    
    Returns:
        元组: (可用模型列表, 默认模型名称)
    """
    # 从环境变量获取默认模型，提供一个硬编码的回退值
    default_model = os.environ.get("DEFAULT_MODEL", "qwen/qwen2.5-vl-32b-instruct")
    
    # 从环境变量获取支持的模型列表字符串
    models_str = os.environ.get("SUPPORTED_MODELS", default_model)
    
    # 解析逗号分隔的字符串为列表，并去除首尾空格
    available_models = [model.strip() for model in models_str.split(',') if model.strip()]
    
    # 确保默认模型在列表中，如果不在则添加
    if default_model not in available_models:
        # 尝试添加到列表开头
        available_models.insert(0, default_model)
        # 如果解析出的列表为空（例如环境变量未设置或为空），则至少包含默认模型
        if not available_models:
             available_models = [default_model]

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
    
    # 确定默认模型的索引
    try:
        default_index = models.index(default_model)
    except ValueError:
        default_index = 0 # 如果默认模型不在列表中，则选择第一个
    
    st.markdown("### 模型选择")
    
    selected_model = st.selectbox(
        "选择AI模型:",
        options=models,
        index=default_index, # 设置默认选项
        key=key,
        help="选择要用于AI助手的模型。确保所选模型在您的OpenRouter账户中可用。"
    )
    
    # 显示当前模型信息 (可以保留或移除)
    # st.info(f"当前使用模型: {selected_model}") 
    
    return selected_model 