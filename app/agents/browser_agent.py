"""
Browser Agent - AI-Controlled Web Browsing
Like Perplexity/Gemini browser capabilities
Zero-cost using Playwright (FREE)
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Check if playwright is available
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not installed. Run: pip install playwright && playwright install")


class BrowserAgent:
    """
    AI-controlled browser automation
    
    Features (all FREE):
    - Web scraping and content extraction
    - Screenshot capture
    - Form filling
    - Click automation
    - JavaScript execution
    - PDF generation
    
    Like Perplexity's browse feature but local!
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.browser: Optional[Browser] = None
        self.is_available = PLAYWRIGHT_AVAILABLE
    
    async def _get_browser(self) -> Browser:
        """Get or create browser instance"""
        if not self.is_available:
            raise RuntimeError("Playwright not installed. Run: pip install playwright && playwright install chromium")
        
        if self.browser is None:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,  # Run without GUI
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
        
        return self.browser
    
    async def browse_and_extract(
        self,
        url: str,
        extract_type: str = "text",  # text, html, screenshot, pdf
        selector: Optional[str] = None,
        wait_for: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Browse URL and extract content
        
        Args:
            url: Website to visit
            extract_type: What to extract (text, html, screenshot, pdf)
            selector: CSS selector to target specific element
            wait_for: Wait for specific element before extracting
            
        Returns:
            Extracted content with metadata
        """
        
        if not self.is_available:
            return {
                "error": "Playwright not installed. Run: pip install playwright && playwright install chromium",
                "content": None
            }
        
        try:
            browser = await self._get_browser()
            page = await browser.new_page()
            
            # Navigate to URL
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait for specific element if requested
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=10000)
            
            result = {
                "url": url,
                "title": await page.title(),
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            # Extract based on type
            if extract_type == "text":
                if selector:
                    element = await page.query_selector(selector)
                    content = await element.text_content() if element else ""
                else:
                    content = await page.text_content("body")
                result["content"] = content
                result["type"] = "text"
                
            elif extract_type == "html":
                if selector:
                    element = await page.query_selector(selector)
                    content = await element.inner_html() if element else ""
                else:
                    content = await page.content()
                result["content"] = content
                result["type"] = "html"
                
            elif extract_type == "screenshot":
                screenshot = await page.screenshot(full_page=True)
                result["content"] = screenshot  # bytes
                result["type"] = "screenshot"
                
            elif extract_type == "pdf":
                pdf = await page.pdf(format="A4")
                result["content"] = pdf  # bytes
                result["type"] = "pdf"
            
            await page.close()
            return result
            
        except Exception as e:
            self.logger.error(f"Browser error: {str(e)}")
            return {
                "error": str(e),
                "url": url,
                "success": False
            }
    
    async def search_and_summarize(
        self,
        query: str,
        num_results: int = 3
    ) -> Dict[str, Any]:
        """
        Search web and summarize results (like Perplexity)
        Uses DuckDuckGo (free, no API key needed)
        """
        
        if not self.is_available:
            return {"error": "Playwright not installed"}
        
        try:
            browser = await self._get_browser()
            page = await browser.new_page()
            
            # Use DuckDuckGo (free, no tracking)
            search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            await page.goto(search_url, wait_until="domcontentloaded")
            
            # Wait for results
            await page.wait_for_selector('[data-testid="result"]', timeout=10000)
            
            # Extract search results
            results = await page.query_selector_all('[data-testid="result"]')
            
            extracted = []
            for i, result in enumerate(results[:num_results]):
                try:
                    title_el = await result.query_selector('h2')
                    link_el = await result.query_selector('a')
                    snippet_el = await result.query_selector('[data-result="snippet"]')
                    
                    title = await title_el.text_content() if title_el else ""
                    link = await link_el.get_attribute('href') if link_el else ""
                    snippet = await snippet_el.text_content() if snippet_el else ""
                    
                    extracted.append({
                        "title": title.strip(),
                        "url": link,
                        "snippet": snippet.strip()
                    })
                except:
                    continue
            
            await page.close()
            
            return {
                "query": query,
                "results": extracted,
                "num_results": len(extracted),
                "source": "DuckDuckGo",
                "cost": 0.0  # Free!
            }
            
        except Exception as e:
            self.logger.error(f"Search error: {str(e)}")
            return {"error": str(e), "query": query}
    
    async def fill_form(
        self,
        url: str,
        form_data: Dict[str, str],
        submit_selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AI-controlled form filling
        
        Args:
            url: Page with form
            form_data: {selector: value} mapping
            submit_selector: Button to click for submission
        """
        
        if not self.is_available:
            return {"error": "Playwright not installed"}
        
        try:
            browser = await self._get_browser()
            page = await browser.new_page()
            
            await page.goto(url, wait_until="domcontentloaded")
            
            # Fill each form field
            for selector, value in form_data.items():
                await page.fill(selector, value)
            
            # Submit if requested
            if submit_selector:
                await page.click(submit_selector)
                await page.wait_for_load_state("networkidle")
            
            result_url = page.url
            result_title = await page.title()
            
            await page.close()
            
            return {
                "success": True,
                "original_url": url,
                "result_url": result_url,
                "result_title": result_title,
                "fields_filled": len(form_data)
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def execute_javascript(
        self,
        url: str,
        script: str
    ) -> Dict[str, Any]:
        """
        Execute JavaScript on a page
        Useful for dynamic content extraction
        """
        
        if not self.is_available:
            return {"error": "Playwright not installed"}
        
        try:
            browser = await self._get_browser()
            page = await browser.new_page()
            
            await page.goto(url, wait_until="domcontentloaded")
            
            # Execute script
            result = await page.evaluate(script)
            
            await page.close()
            
            return {
                "success": True,
                "url": url,
                "result": result
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def close(self):
        """Close browser instance"""
        if self.browser:
            await self.browser.close()
            self.browser = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get browser agent status"""
        return {
            "playwright_available": self.is_available,
            "browser_running": self.browser is not None,
            "features": [
                "Web scraping",
                "Screenshot capture",
                "Form automation",
                "JavaScript execution",
                "PDF generation",
                "Search (DuckDuckGo)"
            ],
            "cost": "$0 (local execution)"
        }


# Singleton instance
browser_agent = BrowserAgent()
