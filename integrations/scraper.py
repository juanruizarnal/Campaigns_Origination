"""Web scraping integration using Playwright.

This module provides web scraping capabilities for extracting company data
from websites, including certifications, contacts, news, and other relevant
information for FEI evaluation and campaign personalization.
"""

import asyncio
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import get_settings
from core.models import (
    ScrapedCompanyData,
    ScrapedContact,
    ScrapedNewsItem,
)

logger = structlog.get_logger(__name__)


# ==============================================================================
# CONSTANTS
# ==============================================================================

# Certification patterns for FEI eligibility
CERTIFICATION_PATTERNS = [
    # Environmental Management
    (r"ISO\s*14001", "ISO 14001"),
    (r"ISO\s*50001", "ISO 50001"),
    (r"ISO\s*14064", "ISO 14064"),
    (r"EMAS", "EMAS"),
    
    # Sustainability
    (r"B\s*Corp", "B Corp"),
    (r"B[\s-]?Corporation", "B Corp"),
    (r"FSC", "FSC"),
    (r"PEFC", "PEFC"),
    
    # Building/Real Estate
    (r"LEED", "LEED"),
    (r"BREEAM", "BREEAM"),
    
    # Energy
    (r"ISO\s*9001", "ISO 9001"),
    (r"Energy\s*Star", "Energy Star"),
    
    # Other green
    (r"Eco[\s-]?Label", "Eco-Label"),
    (r"EU\s*Ecolabel", "EU Ecolabel"),
    (r"Green\s*Globe", "Green Globe"),
]

# Green/sustainability keywords
GREEN_KEYWORDS = [
    "sostenible", "sostenibilidad", "sustainable", "sustainability",
    "renovable", "renewable", "green", "verde",
    "carbono neutral", "carbon neutral", "net zero",
    "energía limpia", "clean energy",
    "economía circular", "circular economy",
    "biodiversidad", "biodiversity",
    "cambio climático", "climate change",
    "huella de carbono", "carbon footprint",
    "eficiencia energética", "energy efficiency",
    "reciclaje", "recycling", "reciclado",
]

# Role patterns for contact extraction
ROLE_PATTERNS = [
    r"CEO", r"CFO", r"COO", r"CTO", r"CMO",
    r"Director[a]?\s+(?:General|Financier[oa]|Ejecutiv[oa])",
    r"Chief\s+(?:Executive|Financial|Operating|Technology)",
    r"Gerente\s+General",
    r"Presidente",
    r"Consejero\s+Delegado",
    r"Managing\s+Director",
    r"Partner",
    r"Socio\s+Director",
]


# ==============================================================================
# SCRAPER CLASS
# ==============================================================================

class PlaywrightScraper:
    """Web scraper using Playwright for JavaScript-rendered pages.
    
    Features:
    - Handles JavaScript-rendered content
    - Extracts certifications for FEI eligibility
    - Finds contact information
    - Detects green/sustainability indicators
    - Extracts news and press releases
    """
    
    def __init__(
        self,
        timeout: Optional[int] = None,
        user_agent: Optional[str] = None,
    ):
        """Initialize scraper.
        
        Args:
            timeout: Page load timeout in milliseconds (default from settings)
            user_agent: Custom user agent string
        """
        settings = get_settings()
        self._timeout = timeout or (settings.SCRAPING_TIMEOUT * 1000)
        self._user_agent = user_agent or settings.USER_AGENT
        self._browser = None
        self._playwright = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        try:
            from playwright.async_api import async_playwright
        except Exception as e:
            logger.warning("playwright_unavailable", error=str(e))
            self._playwright = None
            self._browser = None
            return self

        try:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"],
            )
        except Exception as e:
            logger.warning("playwright_launch_failed", error=str(e))
            if self._playwright:
                try:
                    await self._playwright.stop()
                except Exception:
                    pass
            self._playwright = None
            self._browser = None
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def scrape_company_website(
        self,
        url: str,
        follow_links: bool = True,
    ) -> ScrapedCompanyData:
        """Scrape a company website for relevant data.
        
        Args:
            url: Company website URL
            follow_links: Whether to follow internal links for more data
            
        Returns:
            ScrapedCompanyData with extracted information
        """
        logger.info("scraping_website", url=url)
        
        # Ensure URL has scheme
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        if not self._browser:
            return await self._scrape_with_httpx(url, follow_links=follow_links)
        
        try:
            # Create browser context with custom user agent
            context = await self._browser.new_context(
                user_agent=self._user_agent,
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()
            
            # Navigate to main page
            await page.goto(url, timeout=self._timeout, wait_until="networkidle")
            
            # Get main page content
            html = await page.content()
            
            # Extract text using trafilatura for clean text
            main_text = await self._extract_clean_text(html)
            
            # Initialize result
            result = ScrapedCompanyData(
                url=url,
                scraped_at=datetime.now(),
                success=True,
            )
            
            # Extract all data
            result.certifications = self._extract_certifications(html, main_text)
            result.green_indicators = self._extract_green_indicators(main_text)
            result.description = await self._extract_description(page)
            result.activities = self._extract_activities(main_text)
            result.linkedin_url = await self._extract_linkedin(page)
            result.twitter_url = await self._extract_twitter(page)
            result.employee_count, result.employee_range = self._extract_employee_info(main_text)
            result.revenue_mentions = self._extract_revenue_mentions(main_text)
            result.main_text = main_text[:10000] if main_text else None
            
            # Follow links for more data if enabled
            if follow_links:
                # Look for about, contact, news pages
                about_text = await self._scrape_subpage(page, url, ["about", "sobre", "nosotros", "quienes-somos", "empresa", "company"])
                if about_text:
                    result.certifications.extend(self._extract_certifications("", about_text))
                    result.green_indicators.extend(self._extract_green_indicators(about_text))
                
                # Extract contacts from contact page
                contacts_html = await self._scrape_subpage_html(page, url, ["contact", "contacto", "team", "equipo"])
                if contacts_html:
                    result.contacts = self._extract_contacts(contacts_html)
                
                # Extract news
                news_html = await self._scrape_subpage_html(page, url, ["news", "noticias", "press", "prensa", "blog", "actualidad"])
                if news_html:
                    result.news_items = self._extract_news_items(news_html, url)
            
            # Deduplicate lists
            result.certifications = list(set(result.certifications))
            result.green_indicators = list(set(result.green_indicators))
            
            await context.close()
            
            logger.info(
                "scraping_complete",
                url=url,
                certifications=len(result.certifications),
                contacts=len(result.contacts),
                news_items=len(result.news_items),
            )
            
            return result
            
        except Exception as e:
            logger.error("scraping_failed", url=url, error=str(e))
            return ScrapedCompanyData(
                url=url,
                scraped_at=datetime.now(),
                success=False,
                error_message=str(e),
            )

    async def _scrape_with_httpx(
        self,
        url: str,
        follow_links: bool = True,
    ) -> ScrapedCompanyData:
        """Fallback scraper using HTTP requests when Playwright is unavailable."""
        logger.info("scraping_fallback_httpx", url=url)
        try:
            timeout = max(5, self._timeout / 1000)
            async with httpx.AsyncClient(
                headers={"User-Agent": self._user_agent},
                timeout=timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text

            main_text = await self._extract_clean_text(html)

            result = ScrapedCompanyData(
                url=url,
                scraped_at=datetime.now(),
                success=True,
            )

            result.certifications = self._extract_certifications(html, main_text)
            result.green_indicators = self._extract_green_indicators(main_text)
            result.description = self._extract_meta_description(html)
            result.activities = self._extract_activities(main_text)
            result.linkedin_url = self._extract_linkedin_from_html(html)
            result.twitter_url = self._extract_twitter_from_html(html)
            result.employee_count, result.employee_range = self._extract_employee_info(main_text)
            result.revenue_mentions = self._extract_revenue_mentions(main_text)
            result.main_text = main_text[:10000] if main_text else None

            result.certifications = list(set(result.certifications))
            result.green_indicators = list(set(result.green_indicators))

            return result

        except Exception as e:
            logger.error("scraping_fallback_failed", url=url, error=str(e))
            return ScrapedCompanyData(
                url=url,
                scraped_at=datetime.now(),
                success=False,
                error_message=str(e),
            )
    
    async def _extract_clean_text(self, html: str) -> str:
        """Extract clean text from HTML using trafilatura."""
        try:
            import trafilatura
            text = trafilatura.extract(html, include_comments=False)
            return text or ""
        except Exception:
            # Fallback: basic text extraction
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            return soup.get_text(separator=" ", strip=True)
    
    async def _extract_description(self, page) -> Optional[str]:
        """Extract company description from meta tags or content."""
        try:
            # Try meta description first
            meta = await page.query_selector('meta[name="description"]')
            if meta:
                content = await meta.get_attribute("content")
                if content and len(content) > 50:
                    return content
            
            # Try Open Graph description
            og_meta = await page.query_selector('meta[property="og:description"]')
            if og_meta:
                content = await og_meta.get_attribute("content")
                if content:
                    return content
            
            return None
        except Exception:
            return None

    def _extract_meta_description(self, html: str) -> Optional[str]:
        """Extract description from meta tags in raw HTML."""
        try:
            from bs4 import BeautifulSoup
        except Exception:
            return None

        try:
            soup = BeautifulSoup(html, "lxml")
            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content"):
                return meta.get("content")
            og_meta = soup.find("meta", attrs={"property": "og:description"})
            if og_meta and og_meta.get("content"):
                return og_meta.get("content")
        except Exception:
            return None
        return None
    
    async def _extract_linkedin(self, page) -> Optional[str]:
        """Extract LinkedIn URL from page."""
        try:
            selectors = [
                'a[href*="linkedin.com/company"]',
                'a[href*="linkedin.com/in"]',
            ]
            for selector in selectors:
                link = await page.query_selector(selector)
                if link:
                    href = await link.get_attribute("href")
                    if href:
                        return href
            return None
        except Exception:
            return None
    
    async def _extract_twitter(self, page) -> Optional[str]:
        """Extract Twitter/X URL from page."""
        try:
            selectors = [
                'a[href*="twitter.com"]',
                'a[href*="x.com"]',
            ]
            for selector in selectors:
                link = await page.query_selector(selector)
                if link:
                    href = await link.get_attribute("href")
                    if href:
                        return href
            return None
        except Exception:
            return None

    def _extract_linkedin_from_html(self, html: str) -> Optional[str]:
        """Extract LinkedIn URL from raw HTML."""
        match = re.search(
            r"https?://(?:www\.)?linkedin\.com/(company|in)/[A-Za-z0-9\-_/]+",
            html,
        )
        return match.group(0) if match else None

    def _extract_twitter_from_html(self, html: str) -> Optional[str]:
        """Extract Twitter/X URL from raw HTML."""
        match = re.search(
            r"https?://(?:www\.)?(twitter|x)\.com/[A-Za-z0-9_]+",
            html,
        )
        return match.group(0) if match else None
    
    def _extract_certifications(self, html: str, text: str) -> list[str]:
        """Extract certifications from HTML and text."""
        certs = []
        combined = f"{html} {text}".lower()
        
        for pattern, cert_name in CERTIFICATION_PATTERNS:
            if re.search(pattern, combined, re.IGNORECASE):
                certs.append(cert_name)
        
        return certs
    
    def _extract_green_indicators(self, text: str) -> list[str]:
        """Extract green/sustainability indicators from text."""
        indicators = []
        text_lower = text.lower()
        
        for keyword in GREEN_KEYWORDS:
            if keyword.lower() in text_lower:
                indicators.append(keyword)
        
        return indicators
    
    def _extract_activities(self, text: str) -> list[str]:
        """Extract business activities from text."""
        # Simple extraction - look for common patterns
        activities = []
        
        # Look for "dedicados a", "especializados en", etc.
        patterns = [
            r"dedicad[oa]s?\s+a\s+(.+?)(?:\.|,|\n)",
            r"especializad[oa]s?\s+en\s+(.+?)(?:\.|,|\n)",
            r"líder(?:es)?\s+en\s+(.+?)(?:\.|,|\n)",
            r"somos\s+una\s+empresa\s+de\s+(.+?)(?:\.|,|\n)",
            r"we\s+specialize\s+in\s+(.+?)(?:\.|,|\n)",
            r"leading\s+(?:provider|company)\s+(?:of|in)\s+(.+?)(?:\.|,|\n)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) < 200:  # Reasonable length
                    activities.append(match.strip())
        
        return activities[:5]  # Limit to 5
    
    def _extract_employee_info(self, text: str) -> tuple[Optional[int], Optional[str]]:
        """Extract employee count from text."""
        patterns = [
            r"(\d{1,5})\s*(?:empleados|employees|trabajadores)",
            r"(?:más de|more than|over)\s*(\d{1,5})\s*(?:empleados|employees)",
            r"(\d{1,4})\s*-\s*(\d{1,4})\s*(?:empleados|employees)",
            r"plantilla de\s*(\d{1,5})",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2 and groups[1]:  # Range
                    return None, f"{groups[0]}-{groups[1]}"
                elif groups[0]:
                    try:
                        return int(groups[0]), None
                    except ValueError:
                        pass
        
        return None, None
    
    def _extract_revenue_mentions(self, text: str) -> list[str]:
        """Extract revenue/financial mentions from text."""
        mentions = []
        
        patterns = [
            r"facturación\s+(?:de\s+)?(\d+(?:\.\d+)?)\s*(?:M€|millones|M)",
            r"revenue\s+(?:of\s+)?(\$?\d+(?:\.\d+)?\s*(?:M|B|million|billion))",
            r"(\d+(?:\.\d+)?)\s*(?:M€|millones)\s+(?:de\s+)?(?:facturación|euros)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                mentions.append(match)
        
        return mentions[:3]
    
    def _extract_contacts(self, html: str) -> list[ScrapedContact]:
        """Extract contact information from HTML."""
        from bs4 import BeautifulSoup
        
        contacts = []
        soup = BeautifulSoup(html, "lxml")
        
        # Look for email patterns
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, html)
        
        # Look for role patterns with nearby names
        text = soup.get_text(separator=" ")
        
        for role_pattern in ROLE_PATTERNS:
            matches = re.finditer(role_pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end]
                
                # Try to find name near role
                name_match = re.search(
                    r"([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)",
                    context
                )
                
                contact = ScrapedContact(
                    role=match.group(),
                    name=name_match.group() if name_match else None,
                )
                
                # Try to find LinkedIn URL
                linkedin_match = re.search(
                    r'linkedin\.com/in/([a-zA-Z0-9-]+)',
                    context
                )
                if linkedin_match:
                    contact.linkedin_url = f"https://linkedin.com/in/{linkedin_match.group(1)}"
                
                contacts.append(contact)
        
        # Add emails as separate contacts if not already associated
        for email in emails[:5]:  # Limit
            if not any(c.email == email for c in contacts):
                contacts.append(ScrapedContact(email=email))
        
        return contacts[:10]  # Limit to 10
    
    def _extract_news_items(self, html: str, base_url: str) -> list[ScrapedNewsItem]:
        """Extract news/press items from HTML."""
        from bs4 import BeautifulSoup
        
        news_items = []
        soup = BeautifulSoup(html, "lxml")
        
        # Look for common news article patterns
        article_selectors = [
            "article",
            ".news-item",
            ".post",
            ".noticia",
            ".entry",
        ]
        
        for selector in article_selectors:
            articles = soup.select(selector)[:5]  # Limit per selector
            
            for article in articles:
                title_el = article.select_one("h2, h3, h4, .title, .titulo")
                if not title_el:
                    continue
                
                title = title_el.get_text(strip=True)
                if len(title) < 10:
                    continue
                
                # Get link
                link_el = article.select_one("a")
                url = None
                if link_el and link_el.get("href"):
                    url = urljoin(base_url, link_el.get("href"))
                
                # Get date
                date_el = article.select_one("time, .date, .fecha")
                pub_date = None
                if date_el:
                    date_str = date_el.get("datetime") or date_el.get_text(strip=True)
                    try:
                        from dateutil import parser
                        pub_date = parser.parse(date_str).date()
                    except Exception:
                        pass
                
                # Get summary
                summary_el = article.select_one("p, .summary, .resumen, .excerpt")
                summary = summary_el.get_text(strip=True)[:200] if summary_el else None
                
                news_items.append(ScrapedNewsItem(
                    title=title,
                    date=pub_date,
                    summary=summary,
                    url=url,
                ))
        
        return news_items[:10]  # Limit total
    
    async def _scrape_subpage(
        self,
        page,
        base_url: str,
        path_keywords: list[str],
    ) -> Optional[str]:
        """Try to find and scrape a subpage."""
        html = await self._scrape_subpage_html(page, base_url, path_keywords)
        if html:
            return await self._extract_clean_text(html)
        return None
    
    async def _scrape_subpage_html(
        self,
        page,
        base_url: str,
        path_keywords: list[str],
    ) -> Optional[str]:
        """Try to find and get HTML from a subpage."""
        try:
            # Find links containing keywords
            for keyword in path_keywords:
                link = await page.query_selector(f'a[href*="{keyword}"]')
                if link:
                    href = await link.get_attribute("href")
                    if href:
                        full_url = urljoin(base_url, href)
                        # Only follow internal links
                        if urlparse(full_url).netloc == urlparse(base_url).netloc:
                            await page.goto(full_url, timeout=self._timeout // 2)
                            html = await page.content()
                            await page.go_back()
                            return html
            return None
        except Exception:
            return None


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

async def scrape_company(url: str) -> ScrapedCompanyData:
    """Convenience function to scrape a single company.
    
    Args:
        url: Company website URL
        
    Returns:
        ScrapedCompanyData with extracted information
    """
    async with PlaywrightScraper() as scraper:
        return await scraper.scrape_company_website(url)


async def scrape_companies(urls: list[str], max_concurrent: int = 3) -> list[ScrapedCompanyData]:
    """Scrape multiple companies with concurrency control.
    
    Args:
        urls: List of company website URLs
        max_concurrent: Maximum concurrent scraping operations
        
    Returns:
        List of ScrapedCompanyData for each URL
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def scrape_with_semaphore(url: str) -> ScrapedCompanyData:
        async with semaphore:
            async with PlaywrightScraper() as scraper:
                return await scraper.scrape_company_website(url)
    
    tasks = [scrape_with_semaphore(url) for url in urls]
    return await asyncio.gather(*tasks)


def extract_certifications_from_text(text: str) -> list[str]:
    """Extract certifications from plain text (no scraping).
    
    Useful for analyzing text from other sources.
    """
    certs = []
    text_lower = text.lower()
    
    for pattern, cert_name in CERTIFICATION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            certs.append(cert_name)
    
    return list(set(certs))


def has_fei_certificate(scraped_data: ScrapedCompanyData) -> bool:
    """Check if scraped data contains FEI-eligible certificates.
    
    Returns True if any ISO 14001, ISO 50001, EMAS, B Corp, etc.
    """
    fei_certs = {"ISO 14001", "ISO 50001", "ISO 14064", "EMAS", "B Corp", "FSC", "PEFC"}
    return bool(set(scraped_data.certifications) & fei_certs)
