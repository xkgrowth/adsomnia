"""
Everflow API Validator using Context7 for dynamic endpoint discovery and validation.
Provides runtime validation, parameter checking, and field mapping based on current API docs.
"""
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Context7 library ID for Everflow API
EVERFLOW_LIBRARY_ID = "/websites/developers_everflow_io"
EVERFLOW_LIBRARY_NAME = "everflow"


@dataclass
class EndpointSpec:
    """Specification for an API endpoint."""
    path: str
    method: str
    description: str
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)
    param_types: Dict[str, str] = field(default_factory=dict)
    response_fields: List[str] = field(default_factory=list)
    deprecated: bool = False
    alternative: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of API validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class Context7Client:
    """Client for interacting with Context7 MCP."""
    
    def __init__(self):
        self.library_id = EVERFLOW_LIBRARY_ID
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(hours=24)  # Cache for 24 hours
        self.last_fetch: Optional[datetime] = None
    
    def _call_mcp(self, function_name: str, **kwargs) -> Any:
        """
        Call Context7 MCP function.
        This assumes MCP tools are available in the environment.
        """
        try:
            # In a real implementation, this would call the MCP server
            # For now, we'll use a placeholder that can be replaced with actual MCP calls
            # The actual implementation would use the MCP client library
            import subprocess
            import sys
            
            # This is a placeholder - actual implementation would use MCP client
            # For now, we'll return None and fall back to cached/local data
            logger.warning(f"MCP call {function_name} not implemented - using fallback")
            return None
        except Exception as e:
            logger.error(f"Error calling MCP function {function_name}: {e}")
            return None
    
    def get_library_docs(self, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get Everflow API documentation from Context7.
        
        Args:
            force_refresh: Force refresh even if cache is valid
        
        Returns:
            Documentation dictionary or None if unavailable
        """
        cache_key = "library_docs"
        
        # Check cache
        if not force_refresh and cache_key in self.cache:
            if self.last_fetch and datetime.now() - self.last_fetch < self.cache_ttl:
                logger.debug("Using cached Context7 documentation")
                return self.cache[cache_key]
        
        # Try to fetch from Context7
        # In production, this would use: mcp_context7_get-library-docs
        docs = self._call_mcp("mcp_context7_get-library-docs", library_id=self.library_id)
        
        if docs:
            self.cache[cache_key] = docs
            self.last_fetch = datetime.now()
            return docs
        
        # Fallback to local documentation
        logger.warning("Context7 unavailable, using local documentation fallback")
        return self._load_local_docs()
    
    def _load_local_docs(self) -> Optional[Dict[str, Any]]:
        """Load local documentation as fallback."""
        docs_path = Path(__file__).parent.parent.parent / "docs" / "api" / "everflow_api_reference.md"
        if docs_path.exists():
            # Parse markdown documentation (simplified)
            return {"source": "local", "path": str(docs_path)}
        return None
    
    def resolve_library_id(self, library_name: str = EVERFLOW_LIBRARY_NAME) -> Optional[str]:
        """
        Resolve library name to ID.
        
        Args:
            library_name: Name of the library (default: "everflow")
        
        Returns:
            Library ID or None
        """
        # In production: mcp_context7_resolve-library-id
        return self._call_mcp("mcp_context7_resolve-library-id", library_name=library_name) or EVERFLOW_LIBRARY_ID


class EverflowAPIValidator:
    """
    Validates Everflow API calls against current documentation from Context7.
    """
    
    def __init__(self):
        self.context7 = Context7Client()
        self.endpoint_specs: Dict[str, EndpointSpec] = {}
        self.field_mappings: Dict[str, Dict[str, str]] = {}
        self._initialized = False
    
    def initialize(self, force_refresh: bool = False) -> bool:
        """
        Initialize validator by loading API documentation.
        
        Args:
            force_refresh: Force refresh from Context7
        
        Returns:
            True if initialization successful
        """
        try:
            docs = self.context7.get_library_docs(force_refresh=force_refresh)
            if docs:
                self._parse_documentation(docs)
                self._initialized = True
                logger.info("Everflow API Validator initialized successfully")
                return True
            else:
                logger.warning("Could not load API documentation - validation will be limited")
                self._load_default_specs()
                self._initialized = True
                return True
        except Exception as e:
            logger.error(f"Error initializing validator: {e}")
            self._load_default_specs()
            self._initialized = True
            return False
    
    def _load_default_specs(self):
        """Load default endpoint specifications from known endpoints."""
        self.endpoint_specs = {
            "/v1/networks/reporting/entity": EndpointSpec(
                path="/v1/networks/reporting/entity",
                method="POST",
                description="Entity reporting with grouping and filtering",
                required_params=["columns", "from", "to", "timezone_id"],
                optional_params=["query", "currency_id", "page", "page_size"],
                param_types={
                    "columns": "array",
                    "from": "string",
                    "to": "string",
                    "timezone_id": "integer",
                    "currency_id": "string",
                    "page": "integer",
                    "page_size": "integer"
                },
                response_fields=["table", "paging", "summary"]
            ),
            "/v1/networks/reporting/entity/table/export": EndpointSpec(
                path="/v1/networks/reporting/entity/table/export",
                method="POST",
                description="Export entity reports to CSV",
                required_params=["columns", "from", "to", "timezone_id"],
                optional_params=["query", "currency_id", "format"],
                param_types={
                    "columns": "array",
                    "from": "string",
                    "to": "string",
                    "timezone_id": "integer",
                    "format": "string"
                },
                response_fields=["export_id", "download_url"]
            ),
            "/v1/networks/reporting/conversions": EndpointSpec(
                path="/v1/networks/reporting/conversions",
                method="POST",
                description="Fetch conversion data",
                required_params=["from", "to", "timezone_id", "show_conversions"],
                optional_params=["show_events", "query", "page", "page_size"],
                param_types={
                    "from": "string",
                    "to": "string",
                    "timezone_id": "integer",
                    "show_conversions": "boolean",
                    "show_events": "boolean",
                    "page": "integer",
                    "page_size": "integer"
                },
                response_fields=["conversions", "paging", "summary"]
            ),
            "/v1/networks/affiliates": EndpointSpec(
                path="/v1/networks/affiliates",
                method="GET",
                description="Get list of affiliates",
                required_params=[],
                optional_params=["page", "limit"],
                param_types={
                    "page": "integer",
                    "limit": "integer"
                },
                response_fields=["affiliates", "paging"]
            ),
            "/v1/networks/offers": EndpointSpec(
                path="/v1/networks/offers",
                method="GET",
                description="Get list of offers",
                required_params=[],
                optional_params=["page", "limit"],
                param_types={
                    "page": "integer",
                    "limit": "integer"
                },
                response_fields=["offers", "paging"]
            ),
            "/v1/networks/reporting/conversions/export": EndpointSpec(
                path="/v1/networks/reporting/conversions/export",
                method="POST",
                description="Export conversion reports to CSV",
                required_params=["from", "to", "timezone_id"],
                optional_params=["query", "format", "show_conversions", "show_events"],
                param_types={
                    "from": "string",
                    "to": "string",
                    "timezone_id": "integer",
                    "format": "string",
                    "show_conversions": "boolean",
                    "show_events": "boolean"
                },
                response_fields=["export_id", "download_url"]
            ),
        }
    
    def _parse_documentation(self, docs: Dict[str, Any]):
        """
        Parse Context7 documentation to extract endpoint specifications.
        This is a simplified parser - in production, you'd parse the full documentation structure.
        """
        # In a full implementation, this would parse the Context7 documentation format
        # For now, we'll enhance the default specs with any new information
        logger.info("Parsing Context7 documentation...")
        # Placeholder for actual parsing logic
    
    def validate_endpoint(self, endpoint: str, method: str = "POST") -> ValidationResult:
        """
        Validate that an endpoint exists and is correct.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
        
        Returns:
            ValidationResult
        """
        if not self._initialized:
            self.initialize()
        
        errors = []
        warnings = []
        suggestions = []
        
        # Check if endpoint exists
        if endpoint not in self.endpoint_specs:
            errors.append(f"Unknown endpoint: {endpoint}")
            
            # Suggest similar endpoints
            similar = self._find_similar_endpoints(endpoint)
            if similar:
                suggestions.append(f"Did you mean: {', '.join(similar[:3])}?")
        else:
            spec = self.endpoint_specs[endpoint]
            
            # Check method
            if spec.method != method:
                errors.append(f"Method mismatch: endpoint expects {spec.method}, got {method}")
            
            # Check if deprecated
            if spec.deprecated:
                warnings.append(f"Endpoint {endpoint} is deprecated")
                if spec.alternative:
                    suggestions.append(f"Use alternative endpoint: {spec.alternative}")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def validate_payload(self, endpoint: str, payload: Dict[str, Any]) -> ValidationResult:
        """
        Validate request payload against endpoint specification.
        
        Args:
            endpoint: API endpoint path
            payload: Request payload
        
        Returns:
            ValidationResult
        """
        if not self._initialized:
            self.initialize()
        
        errors = []
        warnings = []
        suggestions = []
        
        if endpoint not in self.endpoint_specs:
            errors.append(f"Cannot validate payload for unknown endpoint: {endpoint}")
            return ValidationResult(valid=False, errors=errors)
        
        spec = self.endpoint_specs[endpoint]
        
        # Check required parameters
        for param in spec.required_params:
            if param not in payload:
                errors.append(f"Missing required parameter: {param}")
        
        # Check parameter types
        for param, expected_type in spec.param_types.items():
            if param in payload:
                value = payload[param]
                if not self._check_type(value, expected_type):
                    errors.append(
                        f"Parameter '{param}' has wrong type: expected {expected_type}, "
                        f"got {type(value).__name__}"
                    )
        
        # Warn about unknown parameters
        known_params = set(spec.required_params + spec.optional_params)
        for param in payload.keys():
            if param not in known_params:
                warnings.append(f"Unknown parameter: {param} (may be ignored by API)")
        
        # Special validation for columns format
        if "columns" in payload:
            if not isinstance(payload["columns"], list):
                errors.append("'columns' must be an array")
            else:
                for i, col in enumerate(payload["columns"]):
                    if not isinstance(col, dict) or "column" not in col:
                        errors.append(
                            f"Column {i} must be an object with 'column' key, "
                            f"not a plain string"
                        )
                        suggestions.append(
                            "Use format: [{\"column\": \"offer\"}, {\"column\": \"affiliate\"}]"
                        )
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "string": str,
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "number": (int, float)
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return True
    
    def _find_similar_endpoints(self, endpoint: str) -> List[str]:
        """Find similar endpoints for suggestions."""
        similar = []
        endpoint_parts = endpoint.split("/")
        
        for known_endpoint in self.endpoint_specs.keys():
            known_parts = known_endpoint.split("/")
            # Simple similarity: check if last parts match
            if endpoint_parts[-1] in known_parts or known_parts[-1] in endpoint_parts:
                similar.append(known_endpoint)
        
        return similar
    
    def get_authoritative_field_names(self, entity_type: str) -> Dict[str, str]:
        """
        Get authoritative field names for an entity type from API documentation.
        
        Args:
            entity_type: Type of entity (e.g., "offer", "affiliate", "country")
        
        Returns:
            Dictionary mapping field aliases to authoritative names
        """
        if not self._initialized:
            self.initialize()
        
        # Default field mappings based on known API structure
        field_maps = {
            "offer": {
                "offer_name": "offer_name",
                "advertiser_name": "offer_name",  # Map to primary field
                "advertiser": "offer_name",
                "offer": "offer_name",
            },
            "affiliate": {
                "affiliate_name": "affiliate_name",
                "affiliate": "affiliate_name",
            },
            "country": {
                "country_name": "country_name",
                "country": "country_name",
                "name": "country_name",
            },
            "landing_page": {
                "offer_url_name": "offer_url_name",
                "offer_url": "offer_url_name",
            }
        }
        
        return field_maps.get(entity_type, {})
    
    def extract_field(self, data: Dict[str, Any], entity_type: str, field_name: str) -> Optional[Any]:
        """
        Extract field value using authoritative field mapping.
        
        Args:
            data: Data dictionary
            entity_type: Type of entity
            field_name: Desired field name
        
        Returns:
            Field value or None
        """
        field_map = self.get_authoritative_field_names(entity_type)
        
        # Try authoritative name first
        if field_name in data:
            return data[field_name]
        
        # Try mapped aliases
        authoritative_name = field_map.get(field_name)
        if authoritative_name and authoritative_name in data:
            return data[authoritative_name]
        
        # Try common variations
        variations = [
            field_name,
            f"{entity_type}_{field_name}",
            field_name.replace("_", ""),
        ]
        
        for variation in variations:
            if variation in data:
                return data[variation]
        
        return None
    
    def get_endpoint_suggestion(self, operation: str) -> Optional[str]:
        """
        Get suggested endpoint for an operation.
        
        Args:
            operation: Description of operation (e.g., "get affiliates", "export report")
        
        Returns:
            Suggested endpoint path or None
        """
        if not self._initialized:
            self.initialize()
        
        operation_lower = operation.lower()
        
        # Simple keyword matching
        if "affiliate" in operation_lower and "list" in operation_lower:
            return "/v1/networks/affiliates"
        elif "offer" in operation_lower and "list" in operation_lower:
            return "/v1/networks/offers"
        elif "export" in operation_lower or "csv" in operation_lower:
            return "/v1/networks/reporting/entity/table/export"
        elif "conversion" in operation_lower and "view" in operation_lower:
            return "/v1/networks/reporting/conversions"
        elif "report" in operation_lower or "entity" in operation_lower:
            return "/v1/networks/reporting/entity"
        
        return None
    
    def validate_all_endpoints(self) -> Dict[str, ValidationResult]:
        """
        Validate all known endpoints on startup.
        
        Returns:
            Dictionary mapping endpoints to validation results
        """
        if not self._initialized:
            self.initialize()
        
        results = {}
        for endpoint, spec in self.endpoint_specs.items():
            results[endpoint] = self.validate_endpoint(endpoint, spec.method)
        
        return results


# Global validator instance
_validator_instance: Optional[EverflowAPIValidator] = None


def get_validator() -> EverflowAPIValidator:
    """Get or create global validator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = EverflowAPIValidator()
        _validator_instance.initialize()
    return _validator_instance

