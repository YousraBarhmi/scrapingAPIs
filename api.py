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

from dotenv import load_dotenv
from openai import OpenAI
import google.generativeai as gena
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
    selected_model: Optional[str]
    fields: Optional[List[str]] = None
    attended_mode: Optional[bool] = True
class MultiScrapeRequest(BaseModel):
    urls: List[str]

# ---------------------- API Endpoints ----------------------

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Scraper API!"}


@app.post("/scrapeSearch/")
def scrape_googleSearch(request: ScrapeRequest):
    try:
        raw_html = fetch_html_selenium(request.url)
        print("raw_html", raw_html)
        soup = BeautifulSoup(raw_html, 'html.parser')

        # Set to avoid duplicates
        seen = set()
        results_list = []

        # Find all result blocks
        results = soup.find_all('div', class_='CA5RN')
        print("results", results)

        for item in results:
            title_tag = item.find('span', class_='VuuXrf')
            cite_tag = item.find('cite')

            if title_tag and cite_tag:
                title = title_tag.text.strip()
                link = cite_tag.get_text(strip=True)

                # Use a tuple to check for duplicates
                if (title, link) not in seen:
                    seen.add((title, link))
                    results_list.append({
                        "title": title,
                        "link": link
                    })

        # Output JSON
        json_output = json.dumps(results_list, indent=2, ensure_ascii=False)
        print(json_output)

    except Exception as e:
        return {"detail": str(e)}


@app.post("/scrapeLinks/")
def scrape_links(request: ScrapeRequest):
    """Scrape a URL and return structured data."""
    try:
        url = request.url
        raw_html = fetch_html_selenium(url)
        soup = BeautifulSoup(raw_html, "html.parser")

        base_domain = urlparse(url).netloc
        links = soup.find_all('a', href=True)
        internal_links = {urljoin(url, a['href']) for a in links if urlparse(urljoin(url, a['href'])).netloc == base_domain}
        internal_links = {urljoin(url, a['href']) for a in links if urlparse(urljoin(url, a['href'])).netloc == base_domain}
    
        data = extract_links(internal_links, request.selected_model)
        
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrapeData/")
def scrape_data(request: ScrapeRequest):
    """Scrape a URL and return structured data."""
    try:
        url = request.url
        raw_html = fetch_html_selenium(url)
        data = extract_data(raw_html, url)
        return {
            "data": data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from concurrent.futures import ThreadPoolExecutor, as_completed
from scraper import fetch_html_selenium, extract_data

from concurrent.futures import ThreadPoolExecutor, as_completed
from scraper import fetch_html_selenium, extract_data

@app.post("/scrapeMultiple/")
def scrape_multiple_data(request: MultiScrapeRequest):
    """Scrape multiple URLs concurrently using headless Selenium."""
    results = []

    urls = request.urls
    def scrape_url(url):
        try:
            html = fetch_html_selenium(url)
            data = extract_data(html, url)
            return {"url": url, "data": data}
        except Exception as e:
            return {"url": url, "error": str(e)}

    for url in urls:
        results.append(scrape_url(url))

    return {"results": results}
