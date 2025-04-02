from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, create_model

from typing import List, Dict, Optional
import os
import re
import time
import random
import json
from datetime import datetime
from urllib.parse import urlparse, urljoin

import pandas as pd
from bs4 import BeautifulSoup
import html2text
import tiktoken
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as genai
from groq import Groq
from scraper import (
    fetch_html_selenium,
    extract_links,
    extract_data,
    evaluate,
    setup_selenium,
)

load_dotenv()

app = FastAPI()

# ---------------------- Pydantic Models ----------------------

class ScrapeRequest(BaseModel):
    url: str
    selected_model: str
    fields: Optional[List[str]] = None
    attended_mode: Optional[bool] = True
# ---------------------- API Endpoints ----------------------
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Scraper API!"}

@app.post("/scrapeSearch/")
def scrape_googleSearch(request: ScrapeRequest):
    try:
        raw_html = fetch_html_selenium(request.url)
        soup = BeautifulSoup(raw_html, "html.parser")

        seen = set()
        results = [
            {"title": title.get_text(), "url": (url_text := url.get_text())}
            for div in soup.find_all("div", class_="CA5RN")
            if (title := div.find("span", class_="VuuXrf")) and
               (url := div.find("cite", class_="tjvcx")) and
               url_text not in seen and not seen.add(url_text)
        ]

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  

@app.post("/scrapeLinks/")
def scrape_links(request: ScrapeRequest):
    """Scrape a URL and return structured data."""
    try:
        # with open('./rules.json', 'r') as file:
        #     rules = json.load(file)
        # print("Rules:", rules)
        # Step 1: Fetch the page content
        url = request.url
        print("URL:", url)
        raw_html = fetch_html_selenium(url)
        print("raw_html:", raw_html)
        soup = BeautifulSoup(raw_html, "html.parser")
        # Step 2: Extract links from the page
        base_domain = urlparse(url).netloc
        links = soup.find_all('a', href=True)
        print("links:", links)
        internal_links = {urljoin(url, a['href']) for a in links if urlparse(urljoin(url, a['href'])).netloc == base_domain}
        internal_links = {urljoin(url, a['href']) for a in links if urlparse(urljoin(url, a['href'])).netloc == base_domain}
    
        print("links :", internal_links )
        data = extract_links(internal_links, request.selected_model)
        print("Data:", data)
        # result = evaluate(data)
        # print("Result:", result)
        return data
        

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrapeData/")
def scrape_data(request: ScrapeRequest):
    """Scrape a URL and return structured data."""
    try:
        # with open('./rules.json', 'r') as file:
        #     rules = json.load(file)
        # print("Rules:", rules)
        url = request.url
        raw_html = fetch_html_selenium(url)
        data = extract_data(raw_html, url)
        print("Data:", data)
        return {
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

