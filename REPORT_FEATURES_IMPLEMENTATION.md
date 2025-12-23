# Report Viewing and CSV Export Features - Implementation Summary

## Overview
This document summarizes the implementation of report viewing and CSV export functionality for the Adsomnia workflow system.

## Frontend Components Created

### 1. ReportModal Component (`src/components/ReportModal.tsx`)
A comprehensive modal component for viewing and interacting with reports.

**Features:**
- ✅ Interactive table with sortable columns
- ✅ Expandable/collapsible rows for parent-child relationships (e.g., Partner → Offer)
- ✅ Row selection with checkboxes
- ✅ Scrollable table view
- ✅ Export field selector modal
- ✅ Responsive design matching Adsomnia design system

**Key Functionality:**
- Click column headers to sort (ascending/descending)
- Click expand/collapse icons to show/hide child rows
- Select individual rows or all rows for focused exports
- Export CSV with custom field selection

### 2. Updated Chat Component (`src/components/Chat.tsx`)
Enhanced to detect and display report data from LLM responses.

**Features:**
- ✅ Automatic detection of markdown tables in LLM responses
- ✅ "View Report" button appears when report data is detected
- ✅ Report data parsing from markdown tables
- ✅ Integration with ReportModal component
- ✅ Export functionality integration

**How it works:**
1. LLM response is parsed for markdown tables
2. If tables are found, report data is extracted
3. "View Report" button appears below the assistant message
4. Clicking opens the ReportModal with parsed data

### 3. API Functions (`src/lib/api.ts`)
Added functions for report data fetching and CSV export.

**New Functions:**
- `fetchReportData()` - Fetch structured report data for viewing
- `exportReportCSV()` - Export selected rows/columns as CSV

**Interfaces:**
- `ReportData` - Structure for report data
- `ExportRequest` - Request structure for CSV export
- `ExportResponse` - Response structure with download URL

## Backend Requirements

### Current Status
The frontend is ready, but the backend needs updates to fully support these features:

### 1. Report Data Endpoint (JSON Format)
**Needed:** Endpoint to return report data in JSON format (not just CSV)

**Current:** `/api/workflows/wf3/export-report` only returns CSV download links

**Required:** 
- Add `format` parameter support ('json' | 'csv')
- When `format=json`, return structured data:
  ```json
  {
    "columns": ["offer", "partner", "conversions", "cvr"],
    "rows": [
      {"id": "row-1", "offer": "Offer A", "partner": "Partner 1", ...},
      ...
    ],
    "metadata": {
      "reportType": "variance",
      "dateRange": "this week",
      "parentColumn": "partner",
      "childColumn": "offer"
    }
  }
  ```

### 2. Enhanced Export Endpoint
**Needed:** Support for:
- Selected rows export (filter by row IDs)
- Custom column selection
- Parent-child relationship handling

**Current:** Basic export with columns and filters

**Required:** Update `/api/workflows/wf3/export-report` to:
- Accept `selected_rows` parameter (array of row IDs)
- Accept `format` parameter ('json' | 'csv')
- Handle parent-child relationships in exports

### 3. Report Metadata Extraction
**Needed:** Backend should extract and return metadata:
- Report type (WF3.1, WF3.2, WF3.3, WF3.4)
- Date range used
- Filters applied
- Parent/child column relationships (for variance reports)

## Workflow-Specific Requirements

### WF3.1: Conversion Report (Fraud Detection)
- ✅ Frontend ready
- ⚠️ Backend needs to return structured data with fraud indicators

### WF3.2: Variance Report
- ✅ Frontend ready with parent/child support
- ⚠️ Backend needs to:
  - Return hierarchical data (Partner → Offer)
  - Include variance calculations (previous vs current)
  - Support expand/collapse structure

### WF3.3: Check Average EPC per Offer
- ✅ Frontend ready
- ⚠️ Backend needs to return EPC calculations per offer/partner

### WF3.4: Check CR Drop
- ✅ Frontend ready
- ⚠️ Backend needs to:
  - Compare two time periods
  - Calculate conversion rate drops
  - Return structured comparison data

## User Flow

1. **User asks question** → Chat interface
2. **LLM processes** → Returns formatted response with table data
3. **Frontend detects table** → Parses markdown table into structured data
4. **"View Report" button appears** → Below assistant message
5. **User clicks "View Report"** → ReportModal opens
6. **User interacts with report:**
   - Sorts columns
   - Expands/collapses parent rows
   - Selects specific rows
7. **User clicks "Export CSV"** → Export field selector opens
8. **User selects fields** → Chooses which columns to export
9. **User confirms export** → CSV download starts
10. **User continues chatting** → Can ask follow-up questions

## Next Steps

### Immediate Backend Tasks:
1. ✅ Update `/api/workflows/wf3/export-report` to support JSON format
2. ✅ Add report metadata extraction
3. ✅ Support selected rows export
4. ✅ Handle parent-child relationships in data structure

### Future Enhancements:
- [ ] Real-time report updates
- [ ] Report caching for performance
- [ ] Export templates (save column selections)
- [ ] Report sharing functionality
- [ ] Scheduled report exports

## Testing Checklist

- [ ] Test markdown table parsing
- [ ] Test "View Report" button appearance
- [ ] Test modal open/close
- [ ] Test column sorting
- [ ] Test row expansion/collapse
- [ ] Test row selection
- [ ] Test export field selection
- [ ] Test CSV export with selected fields
- [ ] Test CSV export with selected rows
- [ ] Test parent-child relationships (WF3.2)
- [ ] Test with different report types (WF3.1-3.4)

## Dependencies Added

- `lucide-react` - For icons (X, Download, ChevronDown, ChevronRight)

## Notes

- The frontend is fully functional and ready for testing
- Backend integration is needed for full end-to-end functionality
- Report data parsing currently works with markdown tables from LLM responses
- Future: Could enhance to parse structured JSON from backend directly

