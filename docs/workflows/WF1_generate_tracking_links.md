# WF1: Generate Tracking Links

> **Phase:** 2 - The Watchdog (Monitoring & Create)  
> **Type:** Write Operation (Safety-Critical)  
> **Week:** 2

## Objective

Approve an offer for a partner and generate the tracking link in one go, with mandatory user confirmation for any approval actions.

## User Intent Examples

- "Get tracking link for Partner 123, Offer 456"
- "Generate a link for affiliate ABC on the summer promo offer"
- "I need a tracking URL for partner ID 789, offer ID 101"
- "Create tracking link for John's affiliate account on Offer X"

## Required Entities

| Entity | Required | Example | Extraction Notes |
|--------|----------|---------|------------------|
| `affiliate_id` | ✅ | 123, "Partner ABC" | May need lookup if name provided |
| `offer_id` | ✅ | 456, "Summer Promo" | May need lookup if name provided |

## API Endpoints

### 1. Check Approval Status (Optional Pre-check)
```
GET /v1/networks/affiliates/{affiliate_id}/offers/{offer_id}
```

### 2. Approve Offer for Affiliate
```
POST /v1/networks/affiliates/{affiliate_id}/offers/{offer_id}/visibility
```

**Payload:**
```json
{
  "status": "approved"
}
```

### 3. Generate Tracking Link
```
POST /v1/networks/tracking/offers/clicks
```

**Payload:**
```json
{
  "network_affiliate_id": 123,
  "network_offer_id": 456
}
```

## Workflow Logic

```python
async def generate_tracking_link(affiliate_id: int, offer_id: int) -> str:
    """
    Generate tracking link with safety checks.
    
    Flow:
    1. Check if affiliate is approved for offer
    2. If not approved, ASK USER for confirmation
    3. If confirmed, approve the affiliate
    4. Generate and return tracking link
    """
    
    # Step 1: Check current approval status
    is_approved = await check_offer_visibility(affiliate_id, offer_id)
    
    if not is_approved:
        # Step 2: SAFETY CHECK - Must get user confirmation
        # Return a confirmation request to the UI
        return {
            "status": "confirmation_required",
            "message": f"Partner {affiliate_id} is not approved for Offer {offer_id}. "
                      f"Do you want me to auto-approve them?",
            "action": "approve_and_generate",
            "params": {"affiliate_id": affiliate_id, "offer_id": offer_id}
        }
    
    # Step 3: Generate tracking link
    tracking_link = await create_tracking_link(affiliate_id, offer_id)
    
    return {
        "status": "success",
        "tracking_link": tracking_link,
        "message": f"Here's your tracking link: {tracking_link}"
    }


async def confirm_and_generate(affiliate_id: int, offer_id: int) -> str:
    """Called after user confirms approval."""
    
    # Approve the affiliate for this offer
    await set_offer_visibility(affiliate_id, offer_id, status="approved")
    
    # Generate tracking link
    tracking_link = await create_tracking_link(affiliate_id, offer_id)
    
    return {
        "status": "success",
        "tracking_link": tracking_link,
        "message": f"Partner {affiliate_id} has been approved and here's your tracking link: {tracking_link}"
    }
```

## Safety Requirements

### ⚠️ CRITICAL: User Confirmation Required

This workflow involves a **write operation** that modifies partner access. The following safety measures are MANDATORY:

1. **Never auto-approve without explicit user confirmation**
2. **Display clear confirmation dialog** showing:
   - Partner ID/Name
   - Offer ID/Name
   - What action will be taken
3. **Log all approval actions** with timestamp and user who confirmed
4. **Provide undo information** (manual steps to revoke if needed)

### Confirmation UI Pattern

```
┌─────────────────────────────────────────────────────────┐
│  ⚠️ Confirmation Required                               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Partner 123 is not currently approved for Offer 456.   │
│                                                         │
│  Do you want me to:                                     │
│  • Approve Partner 123 for Offer 456                    │
│  • Generate the tracking link                           │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                  │
│  │   Confirm    │    │    Cancel    │                  │
│  └──────────────┘    └──────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

## Response Templates

### Success (Already Approved)
```
Here's your tracking link for Partner 123 on Offer 456:

🔗 https://tracking.domain.com/aff_c?offer_id=456&aff_id=123

The partner was already approved for this offer.
```

### Success (After Approval)
```
Done! I've approved Partner 123 for Offer 456 and generated the tracking link:

🔗 https://tracking.domain.com/aff_c?offer_id=456&aff_id=123

Note: Partner 123 now has access to promote Offer 456.
```

### Error: Partner Not Found
```
I couldn't find Partner 123 in the system. Could you double-check the partner ID?

Tip: You can search for partners by name if you're unsure of the ID.
```

### Error: Offer Not Found
```
I couldn't find Offer 456. This offer might be archived or the ID might be incorrect.

Would you like me to search for active offers instead?
```

## Edge Cases

| Scenario | Handling |
|----------|----------|
| Partner already approved | Skip approval, generate link directly |
| Offer is paused/archived | Return error, suggest checking offer status |
| Partner is blocked | Return error, explain partner status |
| Invalid IDs provided | Validate before API call, return friendly error |
| Network timeout on approval | Retry once, then report error |

## Testing Checklist

- [ ] Link generation for already-approved partner
- [ ] Full flow: check → confirm → approve → generate
- [ ] User cancels confirmation
- [ ] Invalid partner ID handling
- [ ] Invalid offer ID handling
- [ ] Network error recovery
- [ ] Audit log verification

## Audit Logging

Every execution should log:
```json
{
  "workflow": "WF1",
  "timestamp": "2025-01-15T10:30:00Z",
  "user": "user@adsomnia.com",
  "action": "generate_tracking_link",
  "affiliate_id": 123,
  "offer_id": 456,
  "approval_required": true,
  "approval_confirmed": true,
  "result": "success"
}
```

**Note:** Do NOT log the actual tracking link URL in production.






