# Adsomnia Workflow Agent - Development Roadmap

> **Status:** Foundation Complete | **Current Phase:** API Integration & Name Resolution  
> **Last Updated:** 2025-12-16

## Executive Summary

**Current State:**
- ✅ Agent framework complete (LangChain + Google Gemini)
- ✅ Workflow tools structure in place (WF1-WF6)
- ✅ Test suite with realistic data (IDs + names)
- ✅ Formatting improvements (tables, numbers)
- ⚠️ **41.2% pass rate** - Core functionality works, but needs API integration

**Critical Gaps:**
1. **Everflow API Integration** - Tools return placeholder data
2. **Name-to-ID Resolution** - Name-based queries fail
3. **Date Parsing** - Natural language dates need conversion
4. **Response Formatting** - Some workflows need better formatting
5. **Error Handling** - API errors and edge cases

---

## Phase 1: Core API Integration (Priority: CRITICAL)

### Status: ⏳ Not Started
### Estimated Time: 2-3 days

### 1.1 Everflow API Client Enhancement
**Current:** Basic client exists but API calls fail  
**Needed:** Working API integration

**Tasks:**
- [ ] Fix API request format (columns structure, date format)
- [ ] Implement proper error handling and retries
- [ ] Add request/response logging
- [ ] Test with real Everflow API credentials
- [ ] Handle API rate limits

**Files to Modify:**
- `backend/sql_agent/everflow_client.py`
- `backend/sql_agent/config.py`

**Acceptance Criteria:**
- Can successfully fetch affiliates, offers, landing pages, countries
- Handles API errors gracefully
- Returns real data (not placeholders)

---

### 1.2 Workflow Tool Implementation - WF2 (Top Landing Pages)
**Current:** Returns placeholder JSON  
**Needed:** Real Everflow API calls

**Tasks:**
- [ ] Implement `POST /v1/networks/reporting/entity` call
- [ ] Parse response and calculate conversion rates
- [ ] Filter by min_leads threshold
- [ ] Sort by conversion rate
- [ ] Return top N results
- [ ] Handle country filtering

**API Endpoint:**
```
POST /v1/networks/reporting/entity
```

**Payload Example:**
```json
{
  "columns": [{"column": "offer_url"}, {"column": "offer"}],
  "query": {
    "filters": [
      {"resource_type": "offer", "filter_id_value": "1001"}
    ]
  },
  "from": "2024-11-16",
  "to": "2024-12-16",
  "timezone_id": 67
}
```

**Files to Modify:**
- `backend/sql_agent/workflow_tools.py` - `wf2_identify_top_lps()`

**Acceptance Criteria:**
- Returns real landing page data from Everflow
- Calculates conversion rates correctly
- Filters and sorts properly
- Handles country filters

---

### 1.3 Workflow Tool Implementation - WF3 (Export Reports)
**Current:** Returns placeholder download URL  
**Needed:** Real export generation

**Tasks:**
- [ ] Implement `POST /v1/networks/reporting/entity/table/export`
- [ ] Implement `POST /v1/networks/reporting/conversions/export`
- [ ] Parse natural language dates to YYYY-MM-DD
- [ ] Handle different report types (fraud, conversions, stats, scrub, variance)
- [ ] Return actual download URLs
- [ ] Format response as table

**API Endpoints:**
- `/v1/networks/reporting/entity/table/export` (General stats)
- `/v1/networks/reporting/conversions/export` (Conversions, fraud)

**Files to Modify:**
- `backend/sql_agent/workflow_tools.py` - `wf3_export_report()`
- Create `backend/sql_agent/date_parser.py` for date parsing

**Acceptance Criteria:**
- Generates real CSV exports
- Returns working download URLs
- Handles all report types
- Parses natural language dates correctly

---

### 1.4 Workflow Tool Implementation - WF1 (Tracking Links)
**Current:** Returns placeholder tracking URL  
**Needed:** Real approval check and link generation

**Tasks:**
- [ ] Implement `GET /v1/networks/affiliates/{id}/offers/{id}` (check approval)
- [ ] Implement `POST /v1/networks/affiliates/{id}/offers/{id}/visibility` (approve)
- [ ] Implement `POST /v1/networks/tracking/offers/clicks` (generate link)
- [ ] Handle approval workflow (check → confirm → approve → generate)
- [ ] Return formatted response with tracking URL
- [ ] Format as table for better UX

**API Endpoints:**
- `GET /v1/networks/affiliates/{affiliate_id}/offers/{offer_id}`
- `POST /v1/networks/affiliates/{affiliate_id}/offers/{offer_id}/visibility`
- `POST /v1/networks/tracking/offers/clicks`

**Files to Modify:**
- `backend/sql_agent/workflow_tools.py` - `wf1_generate_tracking_link()`

**Acceptance Criteria:**
- Checks approval status correctly
- Generates real tracking links
- Handles approval workflow
- Returns formatted response

---

### 1.5 Workflow Tool Implementation - WF6 (Weekly Summary)
**Current:** Returns placeholder summary  
**Needed:** Real aggregated data

**Tasks:**
- [ ] Implement `POST /v1/networks/reporting/entity` with Advertiser_Internal label
- [ ] Aggregate by country or offer
- [ ] Calculate totals (revenue, conversions, clicks)
- [ ] Generate text summary
- [ ] Format as table

**API Endpoint:**
```
POST /v1/networks/reporting/entity
```

**Required Filter:**
```json
{
  "resource_type": "label",
  "filter_id_value": "Advertiser_Internal"
}
```

**Files to Modify:**
- `backend/sql_agent/workflow_tools.py` - `wf6_generate_weekly_summary()`

**Acceptance Criteria:**
- Returns real aggregated data
- Filters by Advertiser_Internal label
- Generates readable summary
- Formats as table

---

## Phase 2: Entity Resolution & Name Lookup (Priority: HIGH)

### Status: ⏳ Not Started
### Estimated Time: 1-2 days

### 2.1 Name-to-ID Lookup System
**Current:** Name-based queries fail (41.2% pass rate)  
**Needed:** Resolve names to IDs

**Tasks:**
- [ ] Create entity lookup functions (affiliate, offer, country)
- [ ] Implement fuzzy matching for names
- [ ] Cache lookups for performance
- [ ] Handle partial matches
- [ ] Return helpful errors if not found

**Implementation:**
```python
def lookup_offer_by_name(name: str) -> Optional[int]:
    """Lookup offer ID by name."""
    # Search Everflow API or use cached data
    pass

def lookup_affiliate_by_name(name: str) -> Optional[int]:
    """Lookup affiliate ID by name."""
    pass
```

**Files to Create:**
- `backend/sql_agent/entity_resolver.py`

**Files to Modify:**
- `backend/sql_agent/workflow_tools.py` - Add name resolution to all tools
- `backend/sql_agent/everflow_client.py` - Add search/lookup methods

**Acceptance Criteria:**
- Can resolve "Summer Promo 2024" → 1001
- Can resolve "Premium Traffic Partners" → 12345
- Handles variations and partial matches
- Caches results for performance

---

### 2.2 Enhanced Entity Extraction
**Current:** Agent sometimes misses names  
**Needed:** Better name recognition

**Tasks:**
- [ ] Update system prompt with entity examples
- [ ] Add entity extraction examples
- [ ] Handle variations (e.g., "Summer Promo" vs "Summer Promo 2024")
- [ ] Support both IDs and names in same query

**Files to Modify:**
- `backend/sql_agent/workflow_agent.py` - System prompt

**Acceptance Criteria:**
- Extracts names correctly from queries
- Handles name variations
- Works with mixed ID + name queries

---

## Phase 3: Date Parsing & Natural Language (Priority: HIGH)

### Status: ⏳ Not Started
### Estimated Time: 1 day

### 3.1 Natural Language Date Parser
**Current:** Date parsing not implemented  
**Needed:** Convert "last week" → "2024-12-09" to "2024-12-16"

**Tasks:**
- [ ] Create date parser module
- [ ] Handle common phrases: "last week", "yesterday", "December 2024"
- [ ] Support relative dates: "last 30 days", "past week"
- [ ] Support absolute dates: "November 1st to 15th"
- [ ] Handle timezone conversions
- [ ] Return YYYY-MM-DD format

**Implementation:**
```python
def parse_date_range(natural_language: str) -> tuple[str, str]:
    """
    Examples:
    "last week" → ("2024-12-09", "2024-12-16")
    "December 2024" → ("2024-12-01", "2024-12-31")
    "last 30 days" → (30_days_ago, today)
    """
    pass
```

**Files to Create:**
- `backend/sql_agent/date_parser.py`

**Files to Modify:**
- `backend/sql_agent/workflow_tools.py` - Use date parser in WF3

**Acceptance Criteria:**
- Parses all common date phrases
- Returns correct YYYY-MM-DD format
- Handles edge cases (month boundaries, year boundaries)

---

## Phase 4: Response Formatting & UX (Priority: MEDIUM)

### Status: ⏳ Partially Complete
### Estimated Time: 1 day

### 4.1 WF1 Response Formatting
**Current:** Plain text responses  
**Needed:** Formatted tables

**Tasks:**
- [ ] Format tracking link responses as tables
- [ ] Include approval status
- [ ] Show affiliate and offer names
- [ ] Format tracking URL clearly

**Files to Modify:**
- `backend/sql_agent/workflow_tools.py` - `wf1_generate_tracking_link()`
- `backend/sql_agent/formatting_helpers.py` - Add tracking link formatter

**Acceptance Criteria:**
- Responses use markdown tables
- All information clearly formatted
- Tracking URL is prominent

---

### 4.2 WF3 Response Formatting
**Current:** Some exports lack formatting  
**Needed:** Consistent table formatting

**Tasks:**
- [ ] Format all export responses as tables
- [ ] Include report metadata (type, date range, columns)
- [ ] Format download links clearly
- [ ] Show expiration info

**Files to Modify:**
- `backend/sql_agent/workflow_tools.py` - `wf3_export_report()`
- `backend/sql_agent/formatting_helpers.py` - Use `format_report_info()`

**Acceptance Criteria:**
- All export responses use tables
- Metadata clearly displayed
- Download links formatted

---

### 4.3 Error Message Formatting
**Current:** Generic error messages  
**Needed:** User-friendly error responses

**Tasks:**
- [ ] Format API errors as user-friendly messages
- [ ] Provide helpful suggestions
- [ ] Include troubleshooting tips
- [ ] Format as structured responses

**Files to Create:**
- `backend/sql_agent/error_formatter.py`

**Files to Modify:**
- All workflow tools - Use error formatter

**Acceptance Criteria:**
- Errors are user-friendly
- Include actionable suggestions
- Formatted consistently

---

## Phase 5: Human-in-the-Loop & Safety (Priority: MEDIUM)

### Status: ⏳ Structure Complete
### Estimated Time: 1 day

### 5.1 WF1 Approval Workflow
**Current:** Structure exists, needs API integration  
**Needed:** Working approval confirmation

**Tasks:**
- [ ] Implement approval check before generating link
- [ ] Return confirmation request if approval needed
- [ ] Handle approval confirmation
- [ ] Log all approval actions
- [ ] Format confirmation messages clearly

**Files to Modify:**
- `backend/sql_agent/workflow_tools.py` - `wf1_generate_tracking_link()`
- `backend/sql_agent/agent_with_human_review.py`

**Acceptance Criteria:**
- Checks approval status before generating link
- Requests confirmation when needed
- Logs all approval actions
- Never auto-approves without confirmation

---

### 5.2 Safety Checks & Validation
**Current:** Basic validation  
**Needed:** Comprehensive safety checks

**Tasks:**
- [ ] Validate all IDs before API calls
- [ ] Check offer/affiliate existence
- [ ] Validate date ranges
- [ ] Prevent invalid operations
- [ ] Add rate limiting protection

**Files to Create:**
- `backend/sql_agent/validators.py`

**Files to Modify:**
- All workflow tools - Add validation

**Acceptance Criteria:**
- All inputs validated before API calls
- Helpful error messages for invalid inputs
- Prevents dangerous operations

---

## Phase 6: Testing & Quality Assurance (Priority: ONGOING)

### Status: ⏳ Test Suite Complete
### Estimated Time: Ongoing

### 6.1 Expand Test Coverage
**Current:** 17 test queries  
**Needed:** More edge cases

**Tasks:**
- [ ] Add tests for API error scenarios
- [ ] Add tests for invalid inputs
- [ ] Add tests for name resolution edge cases
- [ ] Add tests for date parsing edge cases
- [ ] Add integration tests with real API

**Files to Modify:**
- `backend/sql_agent/real_world_qa_tests.py`

**Acceptance Criteria:**
- 30+ test cases covering all scenarios
- >80% pass rate
- All edge cases covered

---

### 6.2 Performance Testing
**Current:** Not tested  
**Needed:** Performance benchmarks

**Tasks:**
- [ ] Measure response times
- [ ] Test with large datasets
- [ ] Optimize slow queries
- [ ] Add caching where appropriate

**Acceptance Criteria:**
- Average response time < 3 seconds
- Handles large result sets
- No memory leaks

---

## Phase 7: Documentation & Deployment (Priority: LOW)

### Status: ⏳ Partial
### Estimated Time: 1 day

### 7.1 API Documentation
**Tasks:**
- [ ] Document all API endpoints used
- [ ] Document error codes and handling
- [ ] Create API integration guide

### 7.2 User Documentation
**Tasks:**
- [ ] Create user guide
- [ ] Document all workflows
- [ ] Add examples for each workflow

### 7.3 Deployment Guide
**Tasks:**
- [ ] Create deployment instructions
- [ ] Document environment setup
- [ ] Add troubleshooting guide

---

## Implementation Priority

### 🔴 Critical (Week 1)
1. **Phase 1.1** - Fix Everflow API client
2. **Phase 1.2** - Implement WF2 (Top Landing Pages)
3. **Phase 1.3** - Implement WF3 (Export Reports)
4. **Phase 1.4** - Implement WF1 (Tracking Links)

### 🟡 High Priority (Week 2)
5. **Phase 2.1** - Name-to-ID lookup
6. **Phase 3.1** - Date parsing
7. **Phase 1.5** - Implement WF6 (Weekly Summary)

### 🟢 Medium Priority (Week 3)
8. **Phase 4.1-4.3** - Response formatting improvements
9. **Phase 5.1-5.2** - Human-in-the-loop & safety
10. **Phase 6.1** - Expand test coverage

### ⚪ Low Priority (Week 4)
11. **Phase 7** - Documentation & deployment

---

## Current Test Results Analysis

### Pass Rate: 41.2% (7/17 tests)

**Working Well:**
- ✅ WF2 with IDs (100% pass)
- ✅ WF6 Weekly Summary (100% pass)
- ✅ Complex queries with IDs

**Needs Work:**
- ❌ Name-based queries (0% pass) - **Requires Phase 2**
- ❌ WF1 tracking links (0% pass) - **Requires Phase 1.4**
- ❌ WF3 exports (33% pass) - **Requires Phase 1.3**
- ❌ Date parsing - **Requires Phase 3**

### Quality Metrics
- **Table Formatting:** 41% (needs improvement)
- **Number Formatting:** 65% (good)
- **Workflow Routing:** 90% (excellent)

---

## Dependencies

### External
- ✅ Everflow API (configured)
- ✅ Google Gemini API (configured)
- ⚠️ Everflow API format validation needed

### Internal
- ✅ LangChain framework
- ✅ Workflow tool structure
- ✅ Test data with names
- ⏳ API integration (needed)
- ⏳ Entity resolver (needed)
- ⏳ Date parser (needed)

---

## Success Criteria

### Phase 1 Complete When:
- [ ] All workflow tools make real API calls
- [ ] Can fetch real data from Everflow
- [ ] >70% test pass rate with real data

### Phase 2 Complete When:
- [ ] Name-based queries work
- [ ] >80% test pass rate
- [ ] Name resolution is fast (<500ms)

### Phase 3 Complete When:
- [ ] All date phrases parsed correctly
- [ ] Date parsing handles edge cases
- [ ] Natural language dates work in all workflows

### Overall Project Complete When:
- [ ] >90% test pass rate
- [ ] All 6 workflows fully functional
- [ ] Production-ready error handling
- [ ] Complete documentation

---

## Risk Assessment

### High Risk
- **Everflow API format issues** - API may have different format than documented
- **Rate limiting** - Need to handle API rate limits gracefully
- **Name resolution accuracy** - Fuzzy matching may return wrong results

### Medium Risk
- **Date parsing edge cases** - Complex date phrases may fail
- **Performance** - Large datasets may be slow
- **Error handling** - API errors need proper handling

### Low Risk
- **Formatting** - Mostly cosmetic, easy to fix
- **Documentation** - Can be done incrementally

---

## Estimated Timeline

| Phase | Duration | Dependencies |
|-------|---------|--------------|
| Phase 1 | 2-3 days | Everflow API access |
| Phase 2 | 1-2 days | Phase 1.1 complete |
| Phase 3 | 1 day | None |
| Phase 4 | 1 day | Phase 1 complete |
| Phase 5 | 1 day | Phase 1.4 complete |
| Phase 6 | Ongoing | All phases |
| Phase 7 | 1 day | Phase 1-5 complete |

**Total Estimated Time:** 7-10 days for core functionality

---

## Next Immediate Steps

1. **Fix Everflow API Client** (Phase 1.1)
   - Debug API request format
   - Test with real credentials
   - Get first successful API call

2. **Implement WF2** (Phase 1.2)
   - Start with simplest workflow
   - Validate API integration works
   - Test with real data

3. **Implement Name Lookup** (Phase 2.1)
   - Critical for name-based queries
   - Will improve pass rate significantly

---

## Notes

- All placeholder data should be replaced with real API calls
- Test suite is ready and comprehensive
- Formatting improvements are in place
- Foundation is solid, needs API integration

**Current Branch:** `feature/langchain-sql-agent`  
**Ready for:** Phase 1 implementation

