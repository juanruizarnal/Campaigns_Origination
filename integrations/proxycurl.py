"""Proxycurl API integration for LinkedIn data.

This module provides access to LinkedIn company and person data
via the Proxycurl API, which allows safe access without violating
LinkedIn's Terms of Service.

Proxycurl API documentation: https://nubela.co/proxycurl/docs
"""

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import get_settings
from core.models import LinkedInCompanyData, LinkedInPersonData

logger = structlog.get_logger(__name__)


class ProxycurlClient:
    """Client for Proxycurl API to fetch LinkedIn data.
    
    Features:
    - Company profile data (employees, industry, description)
    - Person profile data (experience, headline)
    - Company posts for personalization
    - Retry logic with exponential backoff
    """
    
    BASE_URL = "https://nubela.co/proxycurl/api"
    
    def __init__(self, api_key: str | None = None):
        """Initialize Proxycurl client.
        
        Args:
            api_key: Proxycurl API key (defaults to settings)
        """
        settings = get_settings()
        self._api_key = api_key or settings.PROXYCURL_API_KEY
        
        if not self._api_key:
            logger.warning("proxycurl_no_api_key", message="Proxycurl API key not configured")
        
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=30.0,
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.aclose()
    
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return bool(self._api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def get_company_profile(
        self,
        linkedin_url: str,
    ) -> LinkedInCompanyData | None:
        """Get company profile data from LinkedIn.
        
        Args:
            linkedin_url: LinkedIn company URL
            
        Returns:
            LinkedInCompanyData or None if not found/error
            
        Raises:
            httpx.HTTPStatusError: On API error (after retries)
        """
        if not self.is_configured():
            logger.warning("proxycurl_not_configured")
            return None
        
        # Normalize URL
        linkedin_url = self._normalize_linkedin_url(linkedin_url, "company")
        
        logger.info("proxycurl_get_company", url=linkedin_url)
        
        try:
            response = await self._client.get(
                f"{self.BASE_URL}/linkedin/company",
                params={
                    "url": linkedin_url,
                    "resolve_numeric_id": "true",
                    "categories": "include",
                },
            )
            response.raise_for_status()
            data = response.json()
            
            # Get recent posts if available
            recent_posts = await self._get_company_posts(linkedin_url)
            
            return LinkedInCompanyData(
                linkedin_url=linkedin_url,
                name=data.get("name"),
                description=data.get("description"),
                industry=data.get("industry"),
                employee_count=self._parse_employee_count(data.get("company_size_on_linkedin")),
                employee_range=data.get("company_size"),
                founded_year=data.get("founded_year"),
                specialties=data.get("specialities") or [],
                website=data.get("website"),
                headquarters=self._format_headquarters(data.get("hq")),
                recent_posts=recent_posts,
            )
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("proxycurl_company_not_found", url=linkedin_url)
                return None
            elif e.response.status_code == 429:
                logger.error("proxycurl_rate_limited")
                raise
            else:
                logger.error("proxycurl_error", status=e.response.status_code, url=linkedin_url)
                raise
        except Exception as e:
            logger.error("proxycurl_unexpected_error", error=str(e), url=linkedin_url)
            return None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def get_person_profile(
        self,
        linkedin_url: str,
    ) -> LinkedInPersonData | None:
        """Get person profile data from LinkedIn.
        
        Args:
            linkedin_url: LinkedIn person URL
            
        Returns:
            LinkedInPersonData or None if not found/error
        """
        if not self.is_configured():
            logger.warning("proxycurl_not_configured")
            return None
        
        # Normalize URL
        linkedin_url = self._normalize_linkedin_url(linkedin_url, "person")
        
        logger.info("proxycurl_get_person", url=linkedin_url)
        
        try:
            response = await self._client.get(
                f"{self.BASE_URL}/linkedin/person",
                params={
                    "url": linkedin_url,
                    "fallback_to_cache": "on-error",
                    "use_cache": "if-present",
                },
            )
            response.raise_for_status()
            data = response.json()
            
            # Get recent posts if available
            recent_posts = await self._get_person_posts(linkedin_url)
            
            # Extract current position
            current_company = None
            current_role = None
            experiences = data.get("experiences") or []
            if experiences:
                current_exp = experiences[0]
                current_company = current_exp.get("company")
                current_role = current_exp.get("title")
            
            return LinkedInPersonData(
                linkedin_url=linkedin_url,
                full_name=data.get("full_name"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                headline=data.get("headline"),
                summary=data.get("summary"),
                location=self._format_location(data.get("country"), data.get("city")),
                current_company=current_company,
                current_role=current_role,
                experiences=experiences[:5],  # Limit to recent 5
                recent_posts=recent_posts,
            )
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("proxycurl_person_not_found", url=linkedin_url)
                return None
            elif e.response.status_code == 429:
                logger.error("proxycurl_rate_limited")
                raise
            else:
                logger.error("proxycurl_error", status=e.response.status_code, url=linkedin_url)
                raise
        except Exception as e:
            logger.error("proxycurl_unexpected_error", error=str(e), url=linkedin_url)
            return None
    
    async def _get_company_posts(
        self,
        linkedin_url: str,
        limit: int = 3,
    ) -> list[str]:
        """Get recent company posts for personalization.
        
        Note: This is a separate API call with additional cost.
        """
        try:
            response = await self._client.get(
                f"{self.BASE_URL}/linkedin/company/post",
                params={
                    "url": linkedin_url,
                    "max_results": str(limit),
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts") or []
                return [
                    post.get("text", "")[:500]  # Truncate
                    for post in posts
                    if post.get("text")
                ]
            return []
        except Exception:
            return []
    
    async def _get_person_posts(
        self,
        linkedin_url: str,
        limit: int = 3,
    ) -> list[str]:
        """Get recent person posts for personalization."""
        try:
            response = await self._client.get(
                f"{self.BASE_URL}/linkedin/person/profile/post",
                params={
                    "url": linkedin_url,
                    "max_results": str(limit),
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                posts = data.get("posts") or []
                return [
                    post.get("text", "")[:500]
                    for post in posts
                    if post.get("text")
                ]
            return []
        except Exception:
            return []
    
    async def search_company(
        self,
        company_name: str,
        country: str | None = None,
    ) -> str | None:
        """Search for a company's LinkedIn URL by name.
        
        Args:
            company_name: Company name to search
            country: Optional country filter
            
        Returns:
            LinkedIn URL or None if not found
        """
        if not self.is_configured():
            return None
        
        try:
            params = {
                "company_name": company_name,
                "enrich_profiles": "skip",
            }
            if country:
                params["country"] = country
            
            response = await self._client.get(
                f"{self.BASE_URL}/search/company",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results") or []
            if results:
                return results[0].get("linkedin_profile_url")
            
            return None
            
        except Exception as e:
            logger.error("proxycurl_search_error", error=str(e), company=company_name)
            return None
    
    async def search_person(
        self,
        first_name: str,
        last_name: str,
        company_name: str | None = None,
    ) -> str | None:
        """Search for a person's LinkedIn URL.
        
        Args:
            first_name: Person's first name
            last_name: Person's last name
            company_name: Optional current company
            
        Returns:
            LinkedIn URL or None if not found
        """
        if not self.is_configured():
            return None
        
        try:
            params = {
                "first_name": first_name,
                "last_name": last_name,
                "enrich_profiles": "skip",
            }
            if company_name:
                params["current_company_name"] = company_name
            
            response = await self._client.get(
                f"{self.BASE_URL}/search/person",
                params=params,
            )
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results") or []
            if results:
                return results[0].get("linkedin_profile_url")
            
            return None
            
        except Exception as e:
            logger.error("proxycurl_search_error", error=str(e), name=f"{first_name} {last_name}")
            return None
    
    def _normalize_linkedin_url(self, url: str, url_type: str) -> str:
        """Normalize LinkedIn URL format."""
        if not url.startswith("http"):
            if url_type == "company":
                return f"https://www.linkedin.com/company/{url.strip('/')}"
            else:
                return f"https://www.linkedin.com/in/{url.strip('/')}"
        return url
    
    def _parse_employee_count(self, size_str: str | None) -> int | None:
        """Parse employee count from size string."""
        if not size_str:
            return None
        try:
            # Handle ranges like "51-200"
            if "-" in str(size_str):
                parts = str(size_str).split("-")
                return int(parts[1].replace(",", "").replace("+", ""))
            return int(str(size_str).replace(",", "").replace("+", ""))
        except (ValueError, TypeError):
            return None
    
    def _format_headquarters(self, hq: dict | None) -> str | None:
        """Format headquarters location."""
        if not hq:
            return None
        parts = []
        if hq.get("city"):
            parts.append(hq["city"])
        if hq.get("country"):
            parts.append(hq["country"])
        return ", ".join(parts) if parts else None
    
    def _format_location(self, country: str | None, city: str | None) -> str | None:
        """Format person location."""
        parts = []
        if city:
            parts.append(city)
        if country:
            parts.append(country)
        return ", ".join(parts) if parts else None


# ==============================================================================
# CONVENIENCE FUNCTIONS
# ==============================================================================

async def get_company_linkedin_data(linkedin_url: str) -> LinkedInCompanyData | None:
    """Convenience function to get company LinkedIn data.
    
    Args:
        linkedin_url: LinkedIn company URL
        
    Returns:
        LinkedInCompanyData or None
    """
    async with ProxycurlClient() as client:
        return await client.get_company_profile(linkedin_url)


async def get_person_linkedin_data(linkedin_url: str) -> LinkedInPersonData | None:
    """Convenience function to get person LinkedIn data.
    
    Args:
        linkedin_url: LinkedIn profile URL
        
    Returns:
        LinkedInPersonData or None
    """
    async with ProxycurlClient() as client:
        return await client.get_person_profile(linkedin_url)


async def find_company_linkedin(company_name: str, country: str | None = None) -> str | None:
    """Find a company's LinkedIn URL by name.
    
    Args:
        company_name: Company name to search
        country: Optional country filter
        
    Returns:
        LinkedIn URL or None if not found
    """
    async with ProxycurlClient() as client:
        return await client.search_company(company_name, country)


async def find_person_linkedin(
    first_name: str,
    last_name: str,
    company: str | None = None,
) -> str | None:
    """Find a person's LinkedIn URL.
    
    Args:
        first_name: Person's first name
        last_name: Person's last name
        company: Optional current company
        
    Returns:
        LinkedIn URL or None if not found
    """
    async with ProxycurlClient() as client:
        return await client.search_person(first_name, last_name, company)
