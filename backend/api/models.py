"""Request and Response models for API endpoints."""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# WF1 - Generate Tracking Link
# ============================================================================

class TrackingLinkRequest(BaseModel):
    """Request model for generating a tracking link."""
    affiliate_id: int = Field(..., description="The affiliate/partner ID")
    offer_id: int = Field(..., description="The offer ID")


class TrackingLinkResponse(BaseModel):
    """Response model for tracking link generation."""
    status: str
    tracking_link: Optional[str] = None
    message: str
    requires_approval: Optional[bool] = False


# ============================================================================
# WF2 - Top Performing Landing Pages
# ============================================================================

class TopLPsRequest(BaseModel):
    """Request model for identifying top landing pages."""
    offer_id: int = Field(..., description="The offer ID")
    country_code: Optional[str] = Field(None, description="ISO country code (e.g., US, DE, FR)")
    days: int = Field(30, ge=1, le=365, description="Number of days to analyze")
    min_leads: int = Field(20, ge=1, description="Minimum conversions for significance")
    top_n: int = Field(3, ge=1, le=50, description="Number of results to return")


class LandingPageResult(BaseModel):
    """Single landing page result."""
    offer_url_name: str
    conversion_rate: float
    clicks: int
    conversions: int


class TopLPsResponse(BaseModel):
    """Response model for top landing pages."""
    status: str
    offer_id: int
    country_code: Optional[str] = None
    period_days: int
    top_lps: List[LandingPageResult]


# ============================================================================
# WF3 - Export Report
# ============================================================================

class ExportReportRequest(BaseModel):
    """Request model for exporting reports."""
    report_type: Literal["fraud", "conversions", "stats", "scrub", "variance"] = Field(
        ..., description="Type of report to export"
    )
    date_range: str = Field(..., description="Natural language date range (e.g., 'last week', 'December 2024')")
    columns: Optional[List[str]] = Field(None, description="Specific columns to include")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters (offer_id, affiliate_id, etc.)")


class ExportReportResponse(BaseModel):
    """Response model for report export."""
    status: str
    report_type: str
    date_range: str
    download_url: Optional[str] = None
    expires_in: Optional[str] = None
    message: Optional[str] = None


# ============================================================================
# WF3.1 - Fetch Conversions (Viewing)
# ============================================================================

class FetchConversionsRequest(BaseModel):
    """Request model for fetching conversion data."""
    report_type: Literal["fraud", "conversions"] = Field(
        ..., description="Type of conversion report"
    )
    date_range: str = Field(..., description="Natural language date range")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filters (offer_id, affiliate_id, source_id, etc.)")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Results per page")


class ConversionSummary(BaseModel):
    """Summary statistics for conversions."""
    total: int
    approved: int
    invalid: int
    pending: int
    rejected_manual: int
    rejected_throttle: int
    payout: float
    revenue: float
    gross_sales: float


class ConversionRecord(BaseModel):
    """Single conversion record."""
    conversion_id: Optional[str] = None
    click_id: Optional[str] = None
    status: Optional[str] = None
    date: Optional[str] = None
    click_date: Optional[str] = None
    sub1: Optional[str] = None
    offer: Optional[str] = None
    partner: Optional[str] = None
    delta: Optional[str] = None
    payout: Optional[float] = None
    revenue: Optional[float] = None
    conversion_ip: Optional[str] = None
    transaction_id: Optional[str] = None
    offer_events: Optional[str] = None
    adv1: Optional[str] = None
    adv2: Optional[str] = None
    event_name: Optional[str] = None
    is_fraud: Optional[bool] = None
    fraud_reason: Optional[str] = None
    # Allow additional fields
    class Config:
        extra = "allow"


class PaginationInfo(BaseModel):
    """Pagination information."""
    page: int
    page_size: int
    total_count: int
    total_pages: int


class FetchConversionsResponse(BaseModel):
    """Response model for fetching conversions."""
    status: str
    report_type: str
    date_range: str
    summary: ConversionSummary
    conversions: List[ConversionRecord]
    pagination: PaginationInfo
    filters: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class UpdateConversionStatusRequest(BaseModel):
    """Request model for updating conversion status."""
    conversion_id: str = Field(..., description="Conversion ID")
    status: Literal["approved", "rejected", "invalid"] = Field(..., description="New status")


class BulkUpdateConversionStatusRequest(BaseModel):
    """Request model for bulk updating conversion statuses."""
    conversion_ids: List[str] = Field(..., description="List of conversion IDs")
    status: Literal["approved", "rejected", "invalid"] = Field(..., description="New status")


class UpdateConversionStatusResponse(BaseModel):
    """Response model for updating conversion status."""
    status: str
    message: str
    conversion_id: Optional[str] = None
    updated_count: Optional[int] = None


# ============================================================================
# WF4 - Default LP Alert
# ============================================================================

class DefaultLPAlertRequest(BaseModel):
    """Request model for checking default LP alerts."""
    date: Optional[str] = Field(None, description="Specific date to check (YYYY-MM-DD, default: yesterday)")
    click_threshold: int = Field(50, ge=1, description="Minimum clicks to alert")


class DefaultLPAlert(BaseModel):
    """Single default LP alert."""
    offer_id: int
    offer_name: str
    clicks: int
    date: str


class DefaultLPAlertResponse(BaseModel):
    """Response model for default LP alerts."""
    status: str
    alerts: List[DefaultLPAlert]
    message: str


# ============================================================================
# WF5 - Paused Partner Check
# ============================================================================

class PausedPartnerRequest(BaseModel):
    """Request model for checking paused partners."""
    analysis_days: int = Field(3, ge=1, le=30, description="Number of days to compare")
    drop_threshold: float = Field(-50.0, description="Percentage drop to alert")


class PausedPartnerAlert(BaseModel):
    """Single paused partner alert."""
    affiliate_id: int
    affiliate_name: str
    current_period_clicks: int
    previous_period_clicks: int
    drop_percentage: float


class PausedPartnerResponse(BaseModel):
    """Response model for paused partner alerts."""
    status: str
    alerts: List[PausedPartnerAlert]
    message: str


# ============================================================================
# WF6 - Weekly Summary
# ============================================================================

class WeeklySummaryRequest(BaseModel):
    """Request model for weekly performance summary."""
    days: int = Field(7, ge=1, le=30, description="Number of days to analyze")
    group_by: Literal["country", "offer"] = Field("country", description="Group by country or offer")


class SummaryDataPoint(BaseModel):
    """Single data point in summary."""
    name: str
    revenue: float
    conversions: int
    clicks: int


class WeeklySummaryResponse(BaseModel):
    """Response model for weekly summary."""
    status: str
    period_days: int
    group_by: str
    total_revenue: float
    total_conversions: int
    data: List[SummaryDataPoint]
    summary_text: Optional[str] = None


# ============================================================================
# Common Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = "error"
    message: str
    error_code: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    timestamp: datetime
    version: str = "1.0.0"

