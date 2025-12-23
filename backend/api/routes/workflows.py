"""API routes for Everflow workflows (WF1-WF6)."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.api.models import (
    TrackingLinkRequest, TrackingLinkResponse,
    TopLPsRequest, TopLPsResponse, LandingPageResult,
    ExportReportRequest, ExportReportResponse,
    FetchConversionsRequest, FetchConversionsResponse, ConversionRecord, ConversionSummary, PaginationInfo,
    UpdateConversionStatusRequest, BulkUpdateConversionStatusRequest, UpdateConversionStatusResponse,
    DefaultLPAlertRequest, DefaultLPAlertResponse, DefaultLPAlert,
    PausedPartnerRequest, PausedPartnerResponse, PausedPartnerAlert,
    WeeklySummaryRequest, WeeklySummaryResponse, SummaryDataPoint,
    ErrorResponse
)
from backend.api.deps import verify_api_key
from backend.sql_agent.workflow_tools import (
    wf1_generate_tracking_link,
    wf2_identify_top_lps,
    wf3_export_report,
    wf3_fetch_conversions,
    wf4_check_default_lp_alert,
    wf5_check_paused_partners,
    wf6_generate_weekly_summary
)
import json

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


def parse_json_string(value: str) -> Any:
    """Parse JSON string safely."""
    if not value:
        return None
    try:
        return json.loads(value)
    except:
        return value


@router.post("/wf1/tracking-link", response_model=TrackingLinkResponse)
async def generate_tracking_link(
    request: TrackingLinkRequest,
    api_key: str = Depends(verify_api_key)
) -> TrackingLinkResponse:
    """
    Generate a tracking link for an affiliate on an offer (WF1).
    
    May require approval if affiliate is not already approved for the offer.
    """
    try:
        # Call the tool using invoke method for LangChain tools
        result = wf1_generate_tracking_link.invoke({
            "affiliate_id": request.affiliate_id,
            "offer_id": request.offer_id
        })
        
        data = json.loads(result) if isinstance(result, str) else result
        
        return TrackingLinkResponse(
            status=data.get("status", "success"),
            tracking_link=data.get("tracking_link"),
            message=data.get("message", ""),
            requires_approval=data.get("requires_approval", False)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate tracking link: {str(e)}"
        )


@router.post("/wf2/top-landing-pages", response_model=TopLPsResponse)
async def get_top_landing_pages(
    request: TopLPsRequest,
    api_key: str = Depends(verify_api_key)
) -> TopLPsResponse:
    """
    Find top performing landing pages for an offer (WF2).
    """
    try:
        # Call the tool using invoke method for LangChain tools
        result = wf2_identify_top_lps.invoke({
            "offer_id": request.offer_id,
            "country_code": request.country_code,
            "days": request.days,
            "min_leads": request.min_leads,
            "top_n": request.top_n
        })
        
        data = json.loads(result) if isinstance(result, str) else result
        
        # Convert landing pages to models
        landing_pages = [
            LandingPageResult(**lp) for lp in data.get("top_lps", [])
        ]
        
        return TopLPsResponse(
            status=data.get("status", "success"),
            offer_id=data.get("offer_id", request.offer_id),
            country_code=data.get("country_code"),
            period_days=data.get("period_days", request.days),
            top_lps=landing_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top landing pages: {str(e)}"
        )


@router.post("/wf3/export-report", response_model=ExportReportResponse)
async def export_report(
    request: ExportReportRequest,
    api_key: str = Depends(verify_api_key)
) -> ExportReportResponse:
    """
    Export a CSV report (fraud, conversions, stats, scrub, variance) (WF3).
    """
    try:
        # Convert columns and filters to JSON strings if needed
        columns_str = json.dumps(request.columns) if request.columns else None
        filters_str = json.dumps(request.filters) if request.filters else None
        
        result = wf3_export_report.invoke({
            "report_type": request.report_type,
            "date_range": request.date_range,
            "columns": columns_str,
            "filters": filters_str
        })
        
        data = json.loads(result) if isinstance(result, str) else result
        
        return ExportReportResponse(
            status=data.get("status", "success"),
            report_type=data.get("report_type", request.report_type),
            date_range=data.get("date_range", request.date_range),
            download_url=data.get("download_url"),
            expires_in=data.get("expires_in"),
            message=data.get("message")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export report: {str(e)}"
        )


@router.post("/wf3/fetch-conversions", response_model=FetchConversionsResponse)
async def fetch_conversions(
    request: FetchConversionsRequest,
    api_key: str = Depends(verify_api_key)
) -> FetchConversionsResponse:
    """
    Fetch conversion data for viewing (WF3.1 - Conversion Report for Fraud Detection).
    """
    try:
        # Convert filters to JSON string if provided
        filters_str = json.dumps(request.filters) if request.filters else None
        
        result = wf3_fetch_conversions.invoke({
            "report_type": request.report_type,
            "date_range": request.date_range,
            "filters": filters_str,
            "page": request.page,
            "page_size": request.page_size
        })
        
        data = json.loads(result) if isinstance(result, str) else result
        
        if data.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=data.get("message", "Failed to fetch conversions")
            )
        
        # Parse conversions
        conversions_data = data.get("conversions", [])
        conversions = [ConversionRecord(**conv) for conv in conversions_data]
        
        # Parse summary
        summary_data = data.get("summary", {})
        summary = ConversionSummary(**summary_data)
        
        # Parse pagination
        pagination_data = data.get("pagination", {})
        pagination = PaginationInfo(**pagination_data)
        
        return FetchConversionsResponse(
            status=data.get("status", "success"),
            report_type=data.get("report_type", request.report_type),
            date_range=data.get("date_range", request.date_range),
            summary=summary,
            conversions=conversions,
            pagination=pagination,
            filters=data.get("filters"),
            message=data.get("message")
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = str(e)
        traceback_str = traceback.format_exc()
        print(f"❌ Error in fetch_conversions endpoint: {error_details}")
        print(f"❌ Traceback: {traceback_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch conversions: {error_details}"
        )


@router.put("/wf3/conversions/{conversion_id}/status", response_model=UpdateConversionStatusResponse)
async def update_conversion_status(
    conversion_id: str,
    request: UpdateConversionStatusRequest,
    api_key: str = Depends(verify_api_key)
) -> UpdateConversionStatusResponse:
    """
    Update the status of a single conversion (approve/reject).
    """
    try:
        from backend.sql_agent.everflow_client import EverflowClient
        client = EverflowClient()
        
        result = client.update_conversion_status(conversion_id, request.status)
        
        return UpdateConversionStatusResponse(
            status="success",
            message=f"Conversion {conversion_id} status updated to {request.status}",
            conversion_id=conversion_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update conversion status: {str(e)}"
        )


@router.post("/wf3/conversions/bulk-status", response_model=UpdateConversionStatusResponse)
async def bulk_update_conversion_status(
    request: BulkUpdateConversionStatusRequest,
    api_key: str = Depends(verify_api_key)
) -> UpdateConversionStatusResponse:
    """
    Bulk update conversion statuses (approve/reject multiple).
    """
    try:
        from backend.sql_agent.everflow_client import EverflowClient
        client = EverflowClient()
        
        result = client.bulk_update_conversion_status(request.conversion_ids, request.status)
        
        return UpdateConversionStatusResponse(
            status="success",
            message=f"Updated {len(request.conversion_ids)} conversions to {request.status}",
            updated_count=len(request.conversion_ids)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bulk update conversion statuses: {str(e)}"
        )


@router.post("/wf4/default-lp-alert", response_model=DefaultLPAlertResponse)
async def check_default_lp_alert(
    request: DefaultLPAlertRequest,
    api_key: str = Depends(verify_api_key)
) -> DefaultLPAlertResponse:
    """
    Check for traffic to default landing pages (WF4).
    """
    try:
        result = wf4_check_default_lp_alert.invoke({
            "date": request.date,
            "click_threshold": request.click_threshold
        })
        
        data = json.loads(result) if isinstance(result, str) else result
        
        # Convert alerts to models
        alerts = [
            DefaultLPAlert(**alert) for alert in data.get("alerts", [])
        ]
        
        return DefaultLPAlertResponse(
            status=data.get("status", "success"),
            alerts=alerts,
            message=data.get("message", "")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check default LP alerts: {str(e)}"
        )


@router.post("/wf5/paused-partners", response_model=PausedPartnerResponse)
async def check_paused_partners(
    request: PausedPartnerRequest,
    api_key: str = Depends(verify_api_key)
) -> PausedPartnerResponse:
    """
    Identify partners with significant volume drops (WF5).
    """
    try:
        result = wf5_check_paused_partners.invoke({
            "analysis_days": request.analysis_days,
            "drop_threshold": request.drop_threshold
        })
        
        data = json.loads(result) if isinstance(result, str) else result
        
        # Convert alerts to models
        alerts = [
            PausedPartnerAlert(**alert) for alert in data.get("alerts", [])
        ]
        
        return PausedPartnerResponse(
            status=data.get("status", "success"),
            alerts=alerts,
            message=data.get("message", "")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check paused partners: {str(e)}"
        )


@router.post("/wf6/weekly-summary", response_model=WeeklySummaryResponse)
async def get_weekly_summary(
    request: WeeklySummaryRequest,
    api_key: str = Depends(verify_api_key)
) -> WeeklySummaryResponse:
    """
    Generate weekly performance summary by country or offer (WF6).
    """
    try:
        result = wf6_generate_weekly_summary.invoke({
            "days": request.days,
            "group_by": request.group_by
        })
        
        data = json.loads(result) if isinstance(result, str) else result
        
        # Convert data points to models
        data_points = [
            SummaryDataPoint(**point) for point in data.get("data", [])
        ]
        
        return WeeklySummaryResponse(
            status=data.get("status", "success"),
            period_days=data.get("period_days", request.days),
            group_by=data.get("group_by", request.group_by),
            total_revenue=data.get("total_revenue", 0.0),
            total_conversions=data.get("total_conversions", 0),
            data=data_points,
            summary_text=data.get("summary_text")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate weekly summary: {str(e)}"
        )

