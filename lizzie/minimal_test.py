#!/usr/bin/env python3
"""
МИНИМАЛЬНЫЙ ТЕСТ - проверяем OpenAI без всякой фигни
"""

import os
import sys

print("🔥 MINIMAL TEST START")
print(f"🔥 Python version: {sys.version}")
print(f"🔥 Working dir: {os.getcwd()}")

# Проверяем переменные
lizzie_token = os.getenv("LIZZIE_TOKEN")
openai_token = os.getenv("OPENAILIZZIE_TOKEN")

print(f"🔥 LIZZIE_TOKEN: {'SET' if lizzie_token else 'NOT SET'}")
print(f"🔥 OPENAILIZZIE_TOKEN: {'SET' if openai_token else 'NOT SET'}")

if lizzie_token:
    print(f"🔥 LIZZIE_TOKEN ends with: ...{lizzie_token[-4:]}")
if openai_token:
    print(f"🔥 OPENAILIZZIE_TOKEN ends with: ...{openai_token[-4:]}")

# Тестируем OpenAI
try:
    print("🔥 Importing openai...")
    import openai
    print(f"🔥 OpenAI version: {openai.__version__}")
    
    print("🔥 Creating client...")
    client = openai.OpenAI(api_key=openai_token)
    print("🔥 CLIENT CREATED SUCCESSFULLY!")
    
except Exception as e:
    print(f"🔥 OPENAI ERROR: {type(e).__name__}: {str(e)}")
    
    # ОБХОДНОЙ ПУТЬ - прямые HTTP запросы
    print("🔥 TRYING HTTP WORKAROUND...")
    try:
        import requests
        headers = {"Authorization": f"Bearer {openai_token}"}
        response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
        print(f"🔥 HTTP TEST: {response.status_code}")
        if response.status_code == 200:
            print("🔥 OPENAI API WORKS VIA HTTP!")
        else:
            print(f"🔥 HTTP ERROR: {response.text}")
    except Exception as http_e:
        print(f"🔥 HTTP ALSO FAILED: {http_e}")

print("🔥 MINIMAL TEST END")
