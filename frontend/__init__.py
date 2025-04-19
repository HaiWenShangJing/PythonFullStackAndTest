"""
前端模块初始化
"""

import sys
import os
from pathlib import Path

# 获取frontend目录的绝对路径
frontend_dir = Path(__file__).resolve().parent
project_root = frontend_dir.parent

# 将项目根目录添加到Python路径中
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 将frontend目录添加到Python路径中
if str(frontend_dir) not in sys.path:
    sys.path.insert(0, str(frontend_dir))
