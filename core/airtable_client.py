"""Airtable client wrapper with retry logic and structured logging.

This module provides a robust wrapper around PyAirtable with:
- Automatic retries with exponential backoff
- Structured logging for all operations
- Centralized configuration from settings
- Type-safe operations with Pydantic models
"""

from typing import Any, Optional

import structlog
from pyairtable import Api, Table
from pyairtable.formulas import match
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.airtable_schema import TABLES
from config.settings import get_settings

logger = structlog.get_logger()


class AirtableError(Exception):
    """Base exception for Airtable operations."""
    pass


class AirtableClient:
    """Client for Airtable operations with retry and logging.
    
    Provides a robust interface to Airtable with:
    - Automatic retries on transient errors
    - Structured logging for debugging
    - Table name to ID mapping
    - Query building helpers
    
    Example:
        client = AirtableClient()
        companies = client.query_records("companies", formula="FEI_Status='Unknown'")
    """
    
    def __init__(self, pat: Optional[str] = None, base_id: Optional[str] = None):
        """Initialize Airtable client.
        
        Args:
            pat: Personal Access Token. If not provided, loads from settings.
            base_id: Airtable Base ID. If not provided, loads from settings.
        """
        settings = get_settings()
        self._pat = pat or settings.AIRTABLE_PAT
        self._base_id = base_id or settings.AIRTABLE_BASE_ID
        
        self._api = Api(self._pat)
        self._tables_cache: dict[str, Table] = {}
        
        logger.info("airtable_client_initialized", base_id=self._base_id)
    
    def _get_table_id(self, table_name: str) -> str:
        """Get table ID from name.
        
        Args:
            table_name: Friendly name of the table (e.g., "companies")
            
        Returns:
            Table ID (e.g., "tbl47AWmhYAXerbWz")
            
        Raises:
            AirtableError: If table name is not found
        """
        if table_name in TABLES:
            return TABLES[table_name]
        # If it looks like a table ID already, use it directly
        if table_name.startswith("tbl"):
            return table_name
        raise AirtableError(f"Unknown table name: {table_name}")
    
    def get_table(self, table_name: str) -> Table:
        """Get PyAirtable Table object.
        
        Uses caching to avoid recreating Table objects.
        
        Args:
            table_name: Friendly name or ID of the table
            
        Returns:
            PyAirtable Table object
        """
        if table_name not in self._tables_cache:
            table_id = self._get_table_id(table_name)
            self._tables_cache[table_name] = self._api.table(self._base_id, table_id)
        return self._tables_cache[table_name]
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def get_record(self, table_name: str, record_id: str) -> dict[str, Any]:
        """Get a single record by ID.
        
        Args:
            table_name: Name of the table
            record_id: Airtable record ID (e.g., "recXXX")
            
        Returns:
            Record as dict with 'id', 'createdTime', and 'fields' keys
            
        Raises:
            AirtableError: If record not found
        """
        logger.debug("getting_record", table=table_name, record_id=record_id)
        
        table = self.get_table(table_name)
        try:
            record = table.get(record_id)
            logger.info("record_retrieved", table=table_name, record_id=record_id)
            return record
        except Exception as e:
            logger.error("get_record_failed", table=table_name, record_id=record_id, error=str(e))
            raise AirtableError(f"Failed to get record {record_id}: {e}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def create_record(self, table_name: str, fields: dict[str, Any]) -> dict[str, Any]:
        """Create a new record.
        
        Args:
            table_name: Name of the table
            fields: Dict of field names/IDs to values
            
        Returns:
            Created record with 'id', 'createdTime', and 'fields'
        """
        logger.debug("creating_record", table=table_name, field_count=len(fields))
        
        table = self.get_table(table_name)
        try:
            record = table.create(fields)
            logger.info(
                "record_created",
                table=table_name,
                record_id=record["id"],
            )
            return record
        except Exception as e:
            logger.error("create_record_failed", table=table_name, error=str(e))
            raise AirtableError(f"Failed to create record: {e}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def update_record(
        self,
        table_name: str,
        record_id: str,
        fields: dict[str, Any],
        typecast: bool = False,
    ) -> dict[str, Any]:
        """Update an existing record.
        
        Args:
            table_name: Name of the table
            record_id: Airtable record ID
            fields: Dict of field names/IDs to new values
            typecast: If True, Airtable will try to cast string values
            
        Returns:
            Updated record
        """
        logger.debug(
            "updating_record",
            table=table_name,
            record_id=record_id,
            field_count=len(fields),
        )
        
        table = self.get_table(table_name)
        try:
            record = table.update(record_id, fields, typecast=typecast)
            logger.info(
                "record_updated",
                table=table_name,
                record_id=record_id,
            )
            return record
        except Exception as e:
            logger.error(
                "update_record_failed",
                table=table_name,
                record_id=record_id,
                error=str(e),
            )
            raise AirtableError(f"Failed to update record {record_id}: {e}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def delete_record(self, table_name: str, record_id: str) -> bool:
        """Delete a record.
        
        Args:
            table_name: Name of the table
            record_id: Airtable record ID
            
        Returns:
            True if deleted successfully
        """
        logger.debug("deleting_record", table=table_name, record_id=record_id)
        
        table = self.get_table(table_name)
        try:
            table.delete(record_id)
            logger.info("record_deleted", table=table_name, record_id=record_id)
            return True
        except Exception as e:
            logger.error(
                "delete_record_failed",
                table=table_name,
                record_id=record_id,
                error=str(e),
            )
            raise AirtableError(f"Failed to delete record {record_id}: {e}") from e
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )
    def query_records(
        self,
        table_name: str,
        formula: Optional[str] = None,
        fields: Optional[list[str]] = None,
        max_records: Optional[int] = None,
        sort: Optional[list[str]] = None,
        view: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Query records with optional filtering.
        
        Args:
            table_name: Name of the table
            formula: Airtable formula for filtering (e.g., "FEI_Status='Unknown'")
            fields: List of field names to return (None = all fields)
            max_records: Maximum number of records to return
            sort: List of field names to sort by (prefix with - for descending)
            view: View name or ID to use
            
        Returns:
            List of records matching the query
        """
        logger.debug(
            "querying_records",
            table=table_name,
            formula=formula,
            max_records=max_records,
        )
        
        table = self.get_table(table_name)
        
        kwargs: dict[str, Any] = {}
        if formula:
            kwargs["formula"] = formula
        if fields:
            kwargs["fields"] = fields
        if max_records:
            kwargs["max_records"] = max_records
        if sort:
            kwargs["sort"] = sort
        if view:
            kwargs["view"] = view
        
        try:
            records = table.all(**kwargs)
            logger.info(
                "records_queried",
                table=table_name,
                count=len(records),
                formula=formula,
            )
            return records
        except Exception as e:
            logger.error(
                "query_records_failed",
                table=table_name,
                formula=formula,
                error=str(e),
            )
            raise AirtableError(f"Failed to query records: {e}") from e
    
    def query_by_field(
        self,
        table_name: str,
        field_name: str,
        value: Any,
        max_records: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """Query records by a single field value.
        
        Convenience method that builds the formula automatically.
        
        Args:
            table_name: Name of the table
            field_name: Field to match
            value: Value to match
            max_records: Maximum records to return
            
        Returns:
            List of matching records
        """
        formula = match({field_name: value})
        return self.query_records(
            table_name,
            formula=formula,
            max_records=max_records,
        )
    
    def batch_create(
        self,
        table_name: str,
        records: list[dict[str, Any]],
        typecast: bool = False,
    ) -> list[dict[str, Any]]:
        """Create multiple records in batch.
        
        Args:
            table_name: Name of the table
            records: List of field dicts to create
            typecast: If True, Airtable will try to cast string values
            
        Returns:
            List of created records
        """
        logger.debug(
            "batch_creating_records",
            table=table_name,
            count=len(records),
        )
        
        table = self.get_table(table_name)
        try:
            created = table.batch_create(records, typecast=typecast)
            logger.info(
                "batch_records_created",
                table=table_name,
                count=len(created),
            )
            return created
        except Exception as e:
            logger.error(
                "batch_create_failed",
                table=table_name,
                count=len(records),
                error=str(e),
            )
            raise AirtableError(f"Failed to batch create records: {e}") from e
    
    def batch_update(
        self,
        table_name: str,
        records: list[dict[str, Any]],
        typecast: bool = False,
    ) -> list[dict[str, Any]]:
        """Update multiple records in batch.
        
        Args:
            table_name: Name of the table
            records: List of dicts with 'id' and 'fields' keys
            typecast: If True, Airtable will try to cast string values
            
        Returns:
            List of updated records
        """
        logger.debug(
            "batch_updating_records",
            table=table_name,
            count=len(records),
        )
        
        table = self.get_table(table_name)
        try:
            updated = table.batch_update(records, typecast=typecast)
            logger.info(
                "batch_records_updated",
                table=table_name,
                count=len(updated),
            )
            return updated
        except Exception as e:
            logger.error(
                "batch_update_failed",
                table=table_name,
                count=len(records),
                error=str(e),
            )
            raise AirtableError(f"Failed to batch update records: {e}") from e
    
    def count_records(
        self,
        table_name: str,
        formula: Optional[str] = None,
    ) -> int:
        """Count records matching a formula.
        
        Args:
            table_name: Name of the table
            formula: Optional filter formula
            
        Returns:
            Number of matching records
        """
        records = self.query_records(table_name, formula=formula, fields=["id"])
        return len(records)
    
    def record_exists(self, table_name: str, record_id: str) -> bool:
        """Check if a record exists.
        
        Args:
            table_name: Name of the table
            record_id: Record ID to check
            
        Returns:
            True if record exists
        """
        try:
            self.get_record(table_name, record_id)
            return True
        except AirtableError:
            return False


# Singleton instance for convenience
_client: Optional[AirtableClient] = None


def get_airtable_client() -> AirtableClient:
    """Get shared AirtableClient instance.
    
    Returns:
        Singleton AirtableClient instance
    """
    global _client
    if _client is None:
        _client = AirtableClient()
    return _client

