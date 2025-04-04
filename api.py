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
    selected_model: str
    fields: Optional[List[str]] = None
    attended_mode: Optional[bool] = True
# ---------------------- API Endpoints ----------------------
@app.on_event("startup")
def check_env():
    import os
    print("🚀 DOCKER ENV:", os.getenv("DOCKER"))

@app.get("/")
async def root():
    return {"message": "Welcome to the AI Scraper API!"}


@app.post("/scrapeSearch/")
def scrape_googleSearch(request: ScrapeRequest):
    try:
        raw_html = fetch_html_selenium(request.url)
        soup = BeautifulSoup(raw_html, "html.parser")

        seen = set()
        results = []

        for div in soup.find_all("div", class_="CA5RN"):
            title_elem = div.find("span", class_="VuuXrf")
            cite_elem = div.find("cite")

            if not title_elem or not cite_elem:
                continue

            # Clean up the cite URL (strip child spans and whitespace)
            cite_span = cite_elem.find("span")
            if cite_span:
                cite_span.extract()  # remove span from cite

            url_text = cite_elem.get_text(strip=True)

            if url_text not in seen:
                seen.add(url_text)
                results.append({
                    "title": title_elem.get_text(strip=True),
                    "url": url_text
                })

        return results

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

