# Real-World QA Test Report

## Overview

This test suite uses **realistic IDs and scenarios** to test the agent with queries that mirror actual user interactions. The tests use either:
1. Real data fetched from Everflow API (if available)
2. Realistic sample data (fallback)

## Test Data

### Sample IDs Used
- **Affiliates/Partners:** 12345, 23456, 34567, 45678, 56789
- **Offers:** 1001, 1002, 1003, 1004, 1005
- **Landing Pages:** 5001, 5002, 5003, 5004
- **Countries:** US, DE, GB, FR, CA, AU, NL, ES, IT, PL

## Test Categories

### 1. WF2 - Top Landing Pages
- ✅ Real Offer ID queries
- ✅ Real Offer + Country combinations
- ✅ Complex multi-parameter queries

### 2. WF1 - Tracking Links
- ✅ Real Partner + Offer combinations
- ✅ Different ID combinations
- ✅ Various phrasings

### 3. WF3 - Export Reports
- ✅ Date range queries
- ✅ Real Offer ID exports
- ✅ Different report types

### 4. WF6 - Weekly Summary
- ✅ Standard summary queries
- ✅ Geo-specific queries
- ✅ Country filtering

### 5. Edge Cases
- ⚠️ Incomplete queries with real IDs
- ⚠️ Ambiguous requests

## Quality Metrics

### Expected Results
- **Pass Rate:** >70%
- **Table Formatting:** >60%
- **Number Formatting:** >80%
- **Workflow Routing:** >85%

### Quality Score Breakdown
Each test is scored on:
1. Response length (>50 chars) - 1 point
2. Table formatting - 2 points
3. Formatted numbers - 1 point
4. Structure/markdown - 1 point
5. Correct workflow routing - 1 point

**Total:** 6 points per test
**Pass Threshold:** 4/6 points

## Example Test Queries

### Real Offer ID
```
Query: "Which landing page is best for Offer 1001?"
Expected: Table with formatted numbers, correct workflow
```

### Real Partner + Offer
```
Query: "Generate a tracking link for Partner 12345 on Offer 1001"
Expected: Tracking link response, correct workflow
```

### Complex Query
```
Query: "Which landing pages work best in US for Offer 1001?"
Expected: Table filtered by country, formatted numbers
```

## Running the Tests

```bash
source venv/bin/activate
python -m backend.sql_agent.real_world_qa_tests
```

## Notes

- Tests use realistic IDs that mirror production scenarios
- If Everflow API is available, real data is fetched
- Fallback to sample data ensures tests always run
- Tests validate both functionality and output quality

