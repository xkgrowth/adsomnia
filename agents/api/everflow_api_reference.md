# Everflow API Reference

> Quick reference for Everflow API endpoints used in this project.

## Authentication

All requests require the `X-Eflow-API-Key` header:

```
X-Eflow-API-Key: YOUR_API_KEY
Content-Type: application/json
```

## Base URL

```
https://api.eflow.team
```

> **Note:** The API uses `api.eflow.team` not `api.everflow.io`

## Endpoints Used

### 1. Entity Reporting (Read)

**Used by:** WF2, WF4, WF5, WF6

```
POST /v1/networks/reporting/entity
```

**Purpose:** Flexible reporting with grouping and filtering by various dimensions.

**Request Body:**
```json
{
  "columns": [
    {"column": "offer"},
    {"column": "affiliate"},
    {"column": "country"},
    {"column": "offer_url"}
  ],
  "query": {
    "filters": [
      {
        "resource_type": "offer",
        "filter_id_value": "123"
      }
    ]
  },
  "from": "2024-12-01",
  "to": "2024-12-16",
  "timezone_id": 67,
  "currency_id": "EUR"
}
```

> **Important:** Columns must be objects with a `column` key, not plain strings.

**Available Columns:**
| Column | Description |
|--------|-------------|
| `offer` | Offer ID and name |
| `affiliate` | Affiliate/Partner ID and name |
| `country` | Country code and name |
| `offer_url` | Landing page ID and name |
| `source` | Traffic source |
| `sub1` - `sub5` | Sub-tracking parameters |

**Response Metrics (always included):**
- `clicks` - Total clicks
- `conversions` - Total conversions (leads)
- `event_conversion` - Event conversions
- `revenue` - Total revenue
- `payout` - Total payout
- `profit` - Revenue minus payout

**Filter Types:**
| resource_type | Description | Example filter_id_value |
|--------------|-------------|------------------------|
| `offer` | Filter by offer | "123" (offer ID) |
| `affiliate` | Filter by affiliate | "456" (affiliate ID) |
| `country` | Filter by country | "US", "DE", "GB" |
| `label` | Filter by label | "Advertiser_Internal" |
| `offer_url` | Filter by landing page | "789" (offer_url ID) |

---

### 2. Entity Table Export (Read)

**Used by:** WF3

```
POST /v1/networks/reporting/entity/table/export
```

**Purpose:** Export entity reports to CSV file.

**Request Body:**
```json
{
  "columns": ["offer", "affiliate", "country"],
  "query": {
    "filters": []
  },
  "from": "2024-12-01",
  "to": "2024-12-16",
  "format": "csv",
  "timezone_id": 67
}
```

**Response:**
```json
{
  "download_url": "https://api.everflow.io/exports/abc123.csv"
}
```

---

### 3. Conversions Export (Read)

**Used by:** WF3 (Fraud, Scrub reports)

```
POST /v1/networks/reporting/conversions/export
```

**Purpose:** Export individual conversion records to CSV.

**Request Body:**
```json
{
  "columns": ["conversion_id", "affiliate", "offer", "sub1", "sub2", "payout"],
  "query": {
    "filters": [
      {
        "filter_type": "is_fraud",
        "filter_value": true
      }
    ]
  },
  "from": "2024-12-01",
  "to": "2024-12-16",
  "format": "csv",
  "timezone_id": 67
}
```

**Available Columns:**
- `conversion_id`, `click_id`
- `affiliate_id`, `affiliate_name`
- `offer_id`, `offer_name`
- `sub1`, `sub2`, `sub3`, `sub4`, `sub5`
- `click_ip`, `conversion_ip`
- `user_agent`
- `payout`, `revenue`
- `status`
- `is_fraud`, `fraud_reason`
- `created_at`

**Response:**
```json
{
  "download_url": "https://api.everflow.io/exports/xyz789.csv"
}
```

---

### 4. Offer Visibility (Write)

**Used by:** WF1

```
POST /v1/networks/affiliates/{affiliate_id}/offers/{offer_id}/visibility
```

**Purpose:** Approve or revoke an affiliate's access to an offer.

**Path Parameters:**
- `affiliate_id` - The affiliate/partner ID
- `offer_id` - The offer ID

**Request Body:**
```json
{
  "status": "approved"
}
```

**Status Values:**
- `approved` - Grant access to the offer
- `pending` - Request pending approval
- `rejected` - Access denied

**Response:**
```json
{
  "success": true,
  "message": "Visibility updated"
}
```

---

### 5. Generate Tracking Link (Write)

**Used by:** WF1

```
POST /v1/networks/tracking/offers/clicks
```

**Purpose:** Generate a tracking link for an affiliate/offer combination.

**Request Body:**
```json
{
  "network_affiliate_id": 123,
  "network_offer_id": 456
}
```

**Optional Parameters:**
```json
{
  "network_affiliate_id": 123,
  "network_offer_id": 456,
  "sub1": "campaign_name",
  "sub2": "ad_group",
  "offer_url_id": 789
}
```

**Response:**
```json
{
  "tracking_url": "https://tracking.domain.com/aff_c?offer_id=456&aff_id=123"
}
```

---

### 6. Check Offer Approval Status (Read)

**Used by:** WF1 (pre-check)

```
GET /v1/networks/affiliates/{affiliate_id}/offers/{offer_id}
```

**Purpose:** Check if an affiliate is approved for a specific offer.

**Response:**
```json
{
  "affiliate_id": 123,
  "offer_id": 456,
  "status": "approved",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Common Parameters

### Timezone IDs

| ID | Timezone |
|----|----------|
| 67 | UTC |
| 1 | America/New_York |
| 2 | America/Chicago |
| 3 | America/Denver |
| 4 | America/Los_Angeles |
| 26 | Europe/Amsterdam |
| 27 | Europe/London |

### Date Format

All dates use `YYYY-MM-DD` format:
- `"from": "2024-12-01"`
- `"to": "2024-12-16"`

### Pagination (Entity Reports)

```json
{
  "page": 1,
  "page_size": 100
}
```

Default page_size is typically 50. Maximum varies by endpoint.

---

## Error Responses

### 401 Unauthorized
```json
{
  "error": "Invalid API key",
  "code": 401
}
```

### 400 Bad Request
```json
{
  "error": "Invalid filter parameter",
  "code": 400,
  "details": "resource_type 'invalid' not recognized"
}
```

### 404 Not Found
```json
{
  "error": "Offer not found",
  "code": 404
}
```

### 429 Rate Limited
```json
{
  "error": "Rate limit exceeded",
  "code": 429,
  "retry_after": 60
}
```

---

## Rate Limits

- **Standard:** 100 requests/minute
- **Export endpoints:** 10 requests/minute
- **Write endpoints:** 30 requests/minute

Implement exponential backoff on 429 responses.

---

## API Wrapper Interface

The project should implement a standardized API client:

```python
class EverflowClient:
    """Standardized Everflow API client."""
    
    async def get_entity_report(
        self,
        columns: list[str],
        filters: list[dict],
        from_date: str,
        to_date: str
    ) -> dict:
        """Fetch entity report data."""
        pass
    
    async def export_entity_report(
        self,
        columns: list[str],
        filters: list[dict],
        from_date: str,
        to_date: str,
        format: str = "csv"
    ) -> str:
        """Export entity report, return download URL."""
        pass
    
    async def export_conversions(
        self,
        columns: list[str],
        filters: list[dict],
        from_date: str,
        to_date: str,
        format: str = "csv"
    ) -> str:
        """Export conversions report, return download URL."""
        pass
    
    async def set_offer_visibility(
        self,
        affiliate_id: int,
        offer_id: int,
        status: str
    ) -> bool:
        """Set affiliate's visibility for an offer."""
        pass
    
    async def generate_tracking_link(
        self,
        affiliate_id: int,
        offer_id: int,
        **kwargs
    ) -> str:
        """Generate tracking link for affiliate/offer."""
        pass
    
    async def check_offer_approval(
        self,
        affiliate_id: int,
        offer_id: int
    ) -> dict:
        """Check affiliate's approval status for offer."""
        pass
```

---

## Testing the API

### cURL Example (Entity Report)

```bash
curl -X POST "https://api.everflow.io/v1/networks/reporting/entity" \
  -H "X-Eflow-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["offer", "affiliate"],
    "query": {"filters": []},
    "from": "2024-12-01",
    "to": "2024-12-16",
    "timezone_id": 67
  }'
```

### Python Example

```python
import httpx

async def test_api():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.everflow.io/v1/networks/reporting/entity",
            headers={
                "X-Eflow-API-Key": "YOUR_API_KEY",
                "Content-Type": "application/json"
            },
            json={
                "columns": ["offer", "affiliate"],
                "query": {"filters": []},
                "from": "2024-12-01",
                "to": "2024-12-16",
                "timezone_id": 67
            }
        )
        return response.json()
```

---

## Additional Resources

- [Everflow API Documentation](https://developers.everflow.io/)
- [Authentication Guide](https://developers.everflow.io/docs/authentication)
- [Reporting Endpoints](https://developers.everflow.io/docs/reporting)

