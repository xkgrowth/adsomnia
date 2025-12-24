"""API routes for fetching entities (affiliates, offers, etc.)."""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.api.deps import verify_api_key
from backend.sql_agent.everflow_client import EverflowClient

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.get("/affiliates")
async def get_affiliates(
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Get list of affiliates/partners from Everflow API.
    
    Returns real affiliate IDs and names for use in example questions.
    """
    try:
        client = EverflowClient()
        affiliates = client.get_affiliates(limit=limit)
        
        return {
            "status": "success",
            "affiliates": affiliates,
            "count": len(affiliates)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch affiliates: {str(e)}"
        )


@router.get("/offers")
async def get_offers(
    limit: int = 10,
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Get list of offers from Everflow API.
    
    Returns real offer IDs and names for use in example questions.
    """
    try:
        client = EverflowClient()
        offers = client.get_offers(limit=limit)
        
        return {
            "status": "success",
            "offers": offers,
            "count": len(offers)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch offers: {str(e)}"
        )


@router.get("/all")
async def get_all_entities(
    limit: int = 5,
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Get affiliates and offers in a single request.
    
    Useful for frontend to fetch example question data.
    """
    try:
        client = EverflowClient()
        affiliates = client.get_affiliates(limit=limit)
        offers = client.get_offers(limit=limit)
        
        return {
            "status": "success",
            "affiliates": affiliates,
            "offers": offers,
            "affiliate_count": len(affiliates),
            "offer_count": len(offers)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch entities: {str(e)}"
        )



