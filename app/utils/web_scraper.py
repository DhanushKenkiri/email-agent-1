"""
Web scraping utility - the art of politely stealing public information.

Look, if they put it on their website, they want people to see it.
We're just... automating the seeing part.
"""

import httpx
from bs4 import BeautifulSoup
from typing import Optional
import re


class WebScraper:
    """
    Fetches and cleans website content.
    
    Is it elegant? No.
    Does it work? Usually.
    Will it break on some weird website? Probably.
    """
    
    TIMEOUT = 15.0  # if your site takes longer than this, get better hosting
    MAX_CONTENT_LENGTH = 10000  # we don't need your entire blog history
    
    def __init__(self):
        # pretend to be a normal browser because some sites are paranoid
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Grab a webpage and extract the text.
        
        Args:
            url: The website to raid for information
            
        Returns:
            Clean text content, or None if the internet decided to be difficult
        """
        try:
            with httpx.Client(timeout=self.TIMEOUT, follow_redirects=True) as client:
                response = client.get(str(url), headers=self.headers)
                response.raise_for_status()
                return self._extract_text(response.text)
        except httpx.HTTPError as e:
            # network issues, 404s, the usual suspects
            raise ScraperError(f"Failed to fetch {url}: {str(e)}")
        except Exception as e:
            # something weird happened, log it and move on
            raise ScraperError(f"Unexpected error scraping {url}: {str(e)}")
    
    def _extract_text(self, html: str) -> str:
        """
        Turn messy HTML into clean text.
        
        Removes all the junk (scripts, nav bars, footers) and keeps
        the stuff that actually tells us about the company.
        
        Args:
            html: Raw HTML (brace yourself)
            
        Returns:
            Cleaned text that a human could actually read
        """
        soup = BeautifulSoup(html, "lxml")
        
        # yeet all the useless stuff
        # (sorry to any nav designers reading this, your work is beautiful but irrelevant)
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        
        # get the actual text
        text = soup.get_text(separator=" ", strip=True)
        
        # fix the nightmare of whitespace that HTML gives us
        text = re.sub(r'\s+', ' ', text)
        
        # don't return a novel
        if len(text) > self.MAX_CONTENT_LENGTH:
            text = text[:self.MAX_CONTENT_LENGTH] + "..."
        
        return text


class ScraperError(Exception):
    """
    When scraping goes wrong.
    
    Could be the site is down, blocked us, or maybe the internet 
    gremlins are just having a bad day.
    """
    pass
