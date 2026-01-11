"""
Browser Agent API Routes - Phase 3
AI-controlled web browsing endpoints
Like Perplexity's browse feature (Zero cost via Playwright)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.agents.browser_agent import browser_agent

router = APIRouter(tags=["Browser Agent"])


class BrowseRequest(BaseModel):
    """Request for browsing a URL"""
    url: str
    extract_type: str = "text"  # text, html, screenshot, pdf
    selector: Optional[str] = None  # CSS selector for specific element
    wait_for: Optional[str] = None  # Wait for element before extraction


class SearchRequest(BaseModel):
    """Request for web search"""
    query: str
    num_results: int = 3


class FormFillRequest(BaseModel):
    """Request for form filling"""
    url: str
    form_data: Dict[str, str]  # {selector: value}
    submit_selector: Optional[str] = None


@router.post("/browse")
async def browse_url(request: BrowseRequest) -> Dict[str, Any]:
    """
    Browse a URL and extract content
    
    Extract types:
    - **text**: Plain text content
    - **html**: Raw HTML
    - **screenshot**: Full page screenshot (binary)
    - **pdf**: PDF export (binary)
    
    Zero cost - runs locally via Playwright
    """
    
    result = await browser_agent.browse_and_extract(
        url=request.url,
        extract_type=request.extract_type,
        selector=request.selector,
        wait_for=request.wait_for
    )
    
    # Handle binary content
    if request.extract_type in ["screenshot", "pdf"]:
        if result.get("success") and result.get("content"):
            # Return metadata only for binary (content too large for JSON)
            return {
                "url": result.get("url"),
                "title": result.get("title"),
                "type": result.get("type"),
                "success": True,
                "note": "Binary content generated. Use dedicated endpoint to download."
            }
    
    return result


@router.post("/search")
async def search_web(request: SearchRequest) -> Dict[str, Any]:
    """
    Search the web using DuckDuckGo (FREE, no API key)
    
    Returns top results with titles, URLs, and snippets.
    Like Perplexity's web search feature.
    """
    
    return await browser_agent.search_and_summarize(
        query=request.query,
        num_results=request.num_results
    )


@router.post("/fill-form")
async def fill_form(request: FormFillRequest) -> Dict[str, Any]:
    """
    AI-controlled form filling
    
    Provide form data as {selector: value} mapping.
    Optionally specify submit button selector.
    """
    
    return await browser_agent.fill_form(
        url=request.url,
        form_data=request.form_data,
        submit_selector=request.submit_selector
    )


@router.post("/execute-js")
async def execute_javascript(url: str, script: str) -> Dict[str, Any]:
    """
    Execute JavaScript on a page
    
    Useful for:
    - Extracting dynamic content
    - Triggering interactions
    - Getting computed values
    """
    
    return await browser_agent.execute_javascript(url, script)


@router.get("/status")
async def browser_status() -> Dict[str, Any]:
    """
    Check browser agent status
    """
    
    return browser_agent.get_status()
