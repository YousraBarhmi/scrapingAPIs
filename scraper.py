import os
import random
import time
import re
import json
from datetime import datetime
from typing import List, Dict, Type
from urllib.parse import urlparse, urljoin

import pandas as pd
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, create_model
import html2text

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from openai import OpenAI
import google.generativeai as genai
from groq import Groq
from webdriver_manager.chrome import ChromeDriverManager


from api_management import get_api_key
from assets import USER_AGENTS,HEADLESS_OPTIONS,SYSTEM_MESSAGE,evaluation_message,USER_MESSAGE,LLAMA_MODEL_FULLNAME,GROQ_LLAMA_MODEL_FULLNAME,HEADLESS_OPTIONS_DOCKER, LINKS_MESSAGE
load_dotenv()


# Set up the Chrome WebDriver options
import shutil



def is_running_in_docker():
    return os.path.exists("/.dockerenv") or os.getenv("DOCKER") == "true"

def setup_selenium(attended_mode=False):

    options = Options()
    for opt in HEADLESS_OPTIONS_DOCKER:
        options.add_argument(opt)

    # Optional: detect if in Docker
    if is_running_in_docker():
        options.binary_location = "/usr/bin/chromium"

    # 💡 Use webdriver-manager to auto-resolve correct driver version
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    return driver

def fetch_html_selenium(url, attended_mode=False, driver=None):
    if driver is None:
        driver = setup_selenium(attended_mode)
        should_quit = True
        if not attended_mode:
            driver.get(url)
    else:
        should_quit = False
        # Do not navigate to the URL if in attended mode and driver is already initialized
        if not attended_mode:
            driver.get(url)

    try:
        if not attended_mode:
            # Add more realistic actions like scrolling
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(1.1, 1.8))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.3);")
            time.sleep(random.uniform(1.1, 1.8))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1);")
            time.sleep(random.uniform(1.1, 1.8))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/0.8);")
            time.sleep(random.uniform(1.1, 1.8))
        # Get the page source from the current page
        html = driver.page_source
        return html
    finally:
        if should_quit:
            driver.quit()

def extract_links(data, selected_model):
    user_prompt = f"{USER_MESSAGE} {data}"
    
    # API configuration and call based on selected model
    if selected_model in ["gpt-4o-mini", "gpt-4o-2024-08-06"]:
        client = OpenAI(api_key=get_api_key("OPENAI_API_KEY"))
        response_content = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "system", "content": LINKS_MESSAGE}, {"role": "user", "content": user_prompt}]
        ).choices[0].message.content
        try:
            return json.loads(response_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse OpenAI response as JSON: {e}")

    elif selected_model == "gemini-1.5-flash":
        genai.configure(api_key=get_api_key("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        )
        response_content = model.generate_content(f"{LINKS_MESSAGE}\n{USER_MESSAGE} {data}").candidates[0].content.parts[0].text

        return response_content

    elif selected_model == "Groq Llama3.1 70b":
        client = Groq(api_key=get_api_key("GROQ_API_KEY"))
        response_content = client.chat.completions.create(
            model=GROQ_LLAMA_MODEL_FULLNAME,
            messages=[{"role": "system", "content": LINKS_MESSAGE}, {"role": "user", "content": user_prompt}]
        ).choices[0].message.content
        return response_content

    else:
        raise ValueError(f"Unsupported model: {selected_model}")
    
def extract_data(html_content, url):
    soup = BeautifulSoup(html_content, "lxml")

    # Basic metadata
    title = soup.title.string if soup.title else None
    description = (soup.find("meta", attrs={"name": "description"}) or {}).get("content")

    # Navigation menu
    nav = soup.find("nav")
    menu_items = [{"text": a.get_text(strip=True), "href": a["href"]} for a in nav.find_all("a", href=True)] if nav else []

    # Headings (h1-h6)
    headings = {f'h{i}': [h.get_text(strip=True) for h in soup.find_all(f'h{i}')] for i in range(1, 7)}

    # Links
    base_domain = urlparse(url).netloc
    links = soup.find_all('a', href=True)
    internal_links = {urljoin(url, a['href']) for a in links if urlparse(urljoin(url, a['href'])).netloc == base_domain}
    external_links = {urljoin(url, a['href']) for a in links if urlparse(urljoin(url, a['href'])).netloc != base_domain}

    # Images
    images = [{"src": img.get("src"), "alt": img.get("alt")} for img in soup.find_all("img")]

    # Structured data
    structured_data = [json.loads(script.string) for script in soup.find_all("script", type="application/ld+json") if script.string]

    # Word count
    text = soup.get_text(separator=' ', strip=True)
    word_count = len(text.split())

    # Other metadata
    robots_content = (soup.find("meta", attrs={"name": "robots"}) or {}).get("content")
    canonical_url = (soup.find("link", rel="canonical") or {}).get("href")

    return {
        "title": title,
        "description": description,
        "headings": headings,
        "internal_links": internal_links,
        "external_links": external_links,
        "images": images,
        "structured_data": structured_data,
        "word_count": word_count,
        "robots": robots_content,
        "canonical_url": canonical_url,
        "navigation": menu_items
    }

def evaluate(data):
    print('Selected model: gemini-1.5-flash >>>')

    # Configure the Google Gemini API
    GEMINI_API_KEY = 'AIzaSyA2WbooEs3dMYVOy2PDEe27QstNsPwE62s'

    # Configurer le client Gemini
    genai.configure(api_key=GEMINI_API_KEY)
    # genai.configure(api_key=get_api_key("GOOGLE_API_KEY"))
    print('API Key:', GEMINI_API_KEY)
    # Initialize the model
    model = genai.GenerativeModel("gemini-1.5-flash")
    print('Model:', model)
    # Construct the prompt
    prompt = evaluation_message + "\n" + USER_MESSAGE + data

    # Generate and parse the response
    try:
        print('Prompt:')
        completion = model.generate_content(prompt)
        print(f"Generated Response: {completion}")
        response_text = completion.candidates[0].content.parts[0].text
        print("Response Text:", response_text)  # Log the response text before parsing
        return response_text  # Return parsed JSON response
    except Exception as e:
        print(f"Error: {e}")  # More detailed error logging
        raise ValueError("Error processing Gemini response")
