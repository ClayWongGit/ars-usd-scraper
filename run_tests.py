#!/usr/bin/env python3
"""
测试运行脚本
"""

import subprocess
import sys

def run_tests():
    """运行所有测试"""
    print("🧪 开始运行测试...")
    
    try:
        # 运行 pytest
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        print("测试输出:")
        print(result.stdout)
        
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ 所有测试通过!")
        else:
            print(f"❌ 测试失败，退出码: {result.returncode}")
            sys.exit(result.returncode)
            
    except Exception as e:
        print(f"❌ 运行测试时发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
