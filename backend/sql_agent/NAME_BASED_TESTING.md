# Name-Based Testing Enhancement

## Overview

The test suite now supports **both IDs and names** for all entities, making tests more realistic and comprehensive.

## Test Data Structure

### Affiliates/Partners
| ID | Name |
|----|------|
| 12345 | Premium Traffic Partners |
| 23456 | Global Media Network |
| 34567 | Digital Marketing Pro |
| 45678 | Affiliate Masters |
| 56789 | Traffic Boosters Inc |

### Offers
| ID | Name |
|----|------|
| 1001 | Summer Promo 2024 |
| 1002 | Holiday Special |
| 1003 | Evergreen Offer A |
| 1004 | Winter Campaign |
| 1005 | New Year Deal |

### Landing Pages
| ID | Name | Offer ID | Offer Name |
|----|------|----------|------------|
| 5001 | Summer LP v2 | 1001 | Summer Promo 2024 |
| 5002 | Summer LP v1 | 1001 | Summer Promo 2024 |
| 5003 | Holiday Main Page | 1002 | Holiday Special |
| 5004 | Generic Offer Page | 1003 | Evergreen Offer A |

### Countries
| Code | Name |
|------|------|
| US | United States |
| DE | Germany |
| GB | United Kingdom |
| FR | France |
| CA | Canada |
| AU | Australia |
| NL | Netherlands |
| ES | Spain |
| IT | Italy |
| PL | Poland |

## Test Query Types

### 1. ID-Based Queries
- "Which landing page is best for Offer 1001?"
- "Generate a tracking link for Partner 12345 on Offer 1001"
- "Show me top 3 landing pages for Offer 1001 in US"

### 2. Name-Based Queries
- "Which landing page is best for Summer Promo 2024?"
- "Generate a tracking link for Premium Traffic Partners on Summer Promo 2024"
- "Show me top 3 landing pages for Summer Promo 2024 in United States"

### 3. Mixed Queries
- "Get tracking link for Global Media Network on offer 1001"
- "Which landing pages work best in United States for Offer 1001?"
- "Export conversion data for Summer Promo 2024 from last month"

## Test Coverage

The enhanced test suite now includes:

1. **WF2 - Top Landing Pages**
   - Real Offer ID
   - Real Offer Name
   - Real Offer ID + Country Code
   - Real Offer Name + Country Name
   - Complex queries with mixed formats

2. **WF1 - Tracking Links**
   - Real Partner ID + Offer ID
   - Real Partner Name + Offer Name
   - Mixed Names and IDs

3. **WF3 - Export Reports**
   - Real Offer ID Export
   - Real Offer Name Export

4. **WF6 - Weekly Summary**
   - Geo Summary with Country Code
   - Geo Summary with Country Name

5. **Edge Cases**
   - Incomplete Query with ID
   - Incomplete Query with Name

## Benefits

1. **More Realistic:** Tests mirror how users actually interact (often using names)
2. **Better Coverage:** Tests both ID and name extraction
3. **Entity Resolution:** Validates agent can handle different entity formats
4. **User Experience:** Ensures agent works with natural language names

## Usage

### View Test Data
```bash
python -m backend.sql_agent.test_data_reference
```

### Run Tests
```bash
python -m backend.sql_agent.real_world_qa_tests
```

## Example Queries Generated

### With IDs
- "Which landing page is best for Offer 1001?"
- "Generate a tracking link for Partner 12345 on Offer 1001"
- "Show me top 3 landing pages for Offer 1001 in US"

### With Names
- "Which landing page is best for Summer Promo 2024?"
- "Generate a tracking link for Premium Traffic Partners on Summer Promo 2024"
- "Show me top 3 landing pages for Summer Promo 2024 in United States"

### Mixed
- "Get tracking link for Global Media Network on offer 1001"
- "Which landing pages work best in United States for Offer 1001?"

## Agent Behavior

The agent should:
1. ✅ Extract both IDs and names from queries
2. ✅ Handle name-to-ID resolution (if needed by tools)
3. ✅ Work with mixed formats (name + ID combinations)
4. ✅ Provide clear responses regardless of input format

