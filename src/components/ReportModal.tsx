"use client";

import { useState, useMemo, useRef, useEffect } from "react";
import { X, Download, ChevronDown, ChevronRight } from "lucide-react";
import { getAvailableExportFields, getFieldsByCategory, type ExportField } from "@/lib/everflowFields";

export interface ReportRow {
  id: string;
  [key: string]: any; // Dynamic columns
  children?: ReportRow[]; // For parent/child relationships
}

export interface ReportData {
  columns: string[];
  rows: ReportRow[];
  metadata?: {
    reportType?: string;
    dateRange?: string;
    parentColumn?: string;
    childColumn?: string;
    filters?: Record<string, any>;
    originalQuery?: string;
  };
}

interface ReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: ReportData;
  onExport?: (selectedRows: ReportRow[], selectedColumns: string[]) => void;
}

type SortConfig = {
  column: string;
  direction: "asc" | "desc";
};

export default function ReportModal({
  isOpen,
  onClose,
  data,
  onExport,
}: ReportModalProps) {
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set());
  const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set());
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(null);
  const [showExportSelector, setShowExportSelector] = useState(false);

  const toggleRow = (rowId: string) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(rowId)) {
      newExpanded.delete(rowId);
    } else {
      newExpanded.add(rowId);
    }
    setExpandedRows(newExpanded);
  };

  const toggleRowSelection = (rowId: string) => {
    const newSelected = new Set(selectedRows);
    if (newSelected.has(rowId)) {
      newSelected.delete(rowId);
    } else {
      newSelected.add(rowId);
    }
    setSelectedRows(newSelected);
  };

  const handleSort = (column: string) => {
    setSortConfig((current) => {
      if (current?.column === column) {
        return {
          column,
          direction: current.direction === "asc" ? "desc" : "asc",
        };
      }
      return { column, direction: "asc" };
    });
  };

  const sortedRows = useMemo(() => {
    if (!sortConfig) return data.rows;

    const sorted = [...data.rows].sort((a, b) => {
      let aVal = a[sortConfig.column];
      let bVal = b[sortConfig.column];

      // Parse numbers from strings (handles "4,255", "12.76%", etc.)
      const parseNumber = (val: any): number | null => {
        if (typeof val === "number") return val;
        if (typeof val === "string") {
          // Remove commas, percentage signs, and other formatting
          const cleaned = val.replace(/[,\s%$]/g, "");
          const parsed = parseFloat(cleaned);
          return isNaN(parsed) ? null : parsed;
        }
        return null;
      };

      const aNum = parseNumber(aVal);
      const bNum = parseNumber(bVal);

      // If both are numbers, sort numerically
      if (aNum !== null && bNum !== null) {
        return sortConfig.direction === "asc"
          ? aNum - bNum
          : bNum - aNum;
      }

      // If one is a number and one isn't, numbers come first
      if (aNum !== null && bNum === null) return -1;
      if (aNum === null && bNum !== null) return 1;

      // Both are strings, sort alphabetically
      const aStr = String(aVal || "").toLowerCase();
      const bStr = String(bVal || "").toLowerCase();

      if (sortConfig.direction === "asc") {
        return aStr.localeCompare(bStr);
      } else {
        return bStr.localeCompare(aStr);
      }
    });

    return sorted;
  }, [data.rows, sortConfig]);

  const selectAllCheckboxRef = useRef<HTMLInputElement>(null);
  
  // Calculate select all state after sortedRows is defined
  const allSelected = sortedRows.length > 0 && selectedRows.size === sortedRows.length;
  const someSelected = selectedRows.size > 0 && selectedRows.size < sortedRows.length;

  // Set indeterminate state for select all checkbox
  useEffect(() => {
    if (selectAllCheckboxRef.current) {
      selectAllCheckboxRef.current.indeterminate = someSelected;
    }
  }, [someSelected]);

  const toggleSelectAll = () => {
    if (selectedRows.size === sortedRows.length) {
      // Deselect all
      setSelectedRows(new Set());
    } else {
      // Select all
      setSelectedRows(new Set(sortedRows.map(row => row.id)));
    }
  };

  const renderRow = (row: ReportRow, level: number = 0): JSX.Element => {
    const hasChildren = row.children && row.children.length > 0;
    const isExpanded = expandedRows.has(row.id);
    const isSelected = selectedRows.has(row.id);

    return (
      <div key={row.id} className="w-full">
        <div
          className={`flex items-center gap-2 py-2 px-3 border-b border-border hover:bg-bg-secondary ${
            isSelected ? "bg-bg-tertiary" : ""
          }`}
          style={{ paddingLeft: `${level * 24 + 12}px` }}
        >
          {/* Expand/Collapse Button */}
          {hasChildren ? (
            <button
              onClick={() => toggleRow(row.id)}
              className="p-1 hover:bg-bg-tertiary rounded"
            >
              {isExpanded ? (
                <ChevronDown className="w-4 h-4 text-text-secondary" />
              ) : (
                <ChevronRight className="w-4 h-4 text-text-secondary" />
              )}
            </button>
          ) : (
            <div className="w-6" /> // Spacer for alignment
          )}

          {/* Checkbox for Selection */}
          <input
            type="checkbox"
            checked={isSelected}
            onChange={() => toggleRowSelection(row.id)}
            className="w-4 h-4 border-2 border-accent-yellow rounded bg-bg-primary cursor-pointer checked:bg-accent-yellow checked:border-accent-yellow focus:ring-2 focus:ring-accent-yellow focus:ring-offset-2 focus:ring-offset-bg-primary transition-colors"
          />

          {/* Row Data */}
          {data.columns.map((column) => (
            <div
              key={column}
              className="flex-1 text-sm text-text-primary min-w-[120px]"
            >
              {row[column] !== undefined && row[column] !== null
                ? String(row[column])
                : "-"}
            </div>
          ))}
        </div>

        {/* Children Rows */}
        {hasChildren && isExpanded && (
          <div className="w-full">
            {row.children!.map((child) => renderRow(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  if (!isOpen) return null;

  const selectedRowsData = sortedRows.filter((row) =>
    selectedRows.has(row.id)
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop with transparency */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />
      {/* Modal */}
      <div className="relative bg-bg-primary border border-border rounded-lg w-[90vw] h-[85vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div>
            <h2 className="text-lg font-semibold text-text-primary">
              Report View
            </h2>
            {data.metadata?.dateRange && (
              <p className="text-xs text-text-muted mt-1">
                {data.metadata.dateRange}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {selectedRowsData.length > 0 && (
              <span className="text-xs text-text-secondary">
                {selectedRowsData.length} selected
              </span>
            )}
            <button
              onClick={() => setShowExportSelector(true)}
              className="btn-primary px-4 py-2 flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-bg-secondary rounded"
            >
              <X className="w-5 h-5 text-text-secondary" />
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-auto">
          <div className="w-full">
            {/* Table Header */}
            <div className="sticky top-0 bg-bg-tertiary border-b border-border z-10">
              <div className="flex items-center gap-2 py-2 px-3">
                <div className="w-6" /> {/* Spacer for expand button */}
                {/* Select All Checkbox */}
                <input
                  ref={selectAllCheckboxRef}
                  type="checkbox"
                  checked={allSelected}
                  onChange={toggleSelectAll}
                  className="w-4 h-4 border-2 border-accent-yellow rounded bg-bg-primary cursor-pointer checked:bg-accent-yellow checked:border-accent-yellow focus:ring-2 focus:ring-accent-yellow focus:ring-offset-2 focus:ring-offset-bg-primary transition-colors"
                />
                {data.columns.map((column) => (
                  <button
                    key={column}
                    onClick={() => handleSort(column)}
                    className="flex-1 text-left text-xs font-semibold text-accent-yellow uppercase tracking-wide min-w-[120px] hover:text-accent-yellow/80"
                  >
                    <div className="flex items-center gap-1">
                      {column}
                      {sortConfig?.column === column && (
                        <span className="text-text-secondary">
                          {sortConfig.direction === "asc" ? "↑" : "↓"}
                        </span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Table Body */}
            <div className="w-full">
              {sortedRows.map((row) => renderRow(row))}
            </div>
          </div>
        </div>

        {/* Export Field Selector Modal */}
        {showExportSelector && (
          <ExportFieldSelector
            availableColumns={data.columns}
            selectedRows={selectedRowsData}
            reportType={data.metadata?.reportType}
            onExport={(selectedColumns) => {
              if (onExport) {
                onExport(selectedRowsData, selectedColumns);
              }
              setShowExportSelector(false);
            }}
            onClose={() => setShowExportSelector(false)}
          />
        )}
      </div>
    </div>
  );
}

interface ExportFieldSelectorProps {
  availableColumns: string[];
  selectedRows: ReportRow[];
  reportType?: string;
  onExport: (selectedColumns: string[]) => void;
  onClose: () => void;
}

function ExportFieldSelector({
  availableColumns,
  selectedRows,
  reportType,
  onExport,
  onClose,
}: ExportFieldSelectorProps) {
  // Get all available Everflow export fields
  const allExportFields = getAvailableExportFields(reportType);
  const fieldsByCategory = getFieldsByCategory(allExportFields);
  
  // Map table column names to export field IDs
  // Table shows: "Offer", "Offer URL", "CV", "CVR", "EPC", "RPC", "Payout"
  // Export fields use: "offer", "offer_url", "cv", "cvr", "epc", "rpc", "payout"
  const columnNameToFieldId: Record<string, string> = {
    "Offer": "offer_name",
    "Offer URL": "offer_url_name",
    "CV": "cv",
    "CVR": "cvr",
    "EPC": "epc",
    "RPC": "rpc",
    "Payout": "payout",
    "Revenue": "revenue",
    "Clicks": "clicks",
    "Profit": "profit",
    "Conversions": "cv",
    "Conversion Rate": "cvr",
    "Landing Page": "offer_url_name",
  };
  
  // Map available table columns to export field IDs
  // Try exact match first, then fallback to lowercase with underscores
  const defaultSelectedFieldIds = availableColumns
    .map(col => {
      // Try exact match
      if (columnNameToFieldId[col]) {
        return columnNameToFieldId[col];
      }
      // Try lowercase with underscores
      const normalized = col.toLowerCase().replace(/\s+/g, '_');
      // Check if this normalized ID exists in export fields
      if (allExportFields.some(field => field.id === normalized)) {
        return normalized;
      }
      // Return null if no match found
      return null;
    })
    .filter((id): id is string => id !== null && allExportFields.some(field => field.id === id));
  
  // Initialize with table columns selected by default (mapped to field IDs)
  // If no matches found, at least select the first few common fields
  const [selectedColumns, setSelectedColumns] = useState<Set<string>>(() => {
    if (defaultSelectedFieldIds.length > 0) {
      return new Set(defaultSelectedFieldIds);
    }
    // Fallback: select common fields if available
    const commonFields = ['offer_name', 'offer_url_name', 'cv', 'cvr', 'payout'];
    const availableCommonFields = commonFields.filter(id => 
      allExportFields.some(field => field.id === id)
    );
    return new Set(availableCommonFields);
  });

  const toggleColumn = (column: string) => {
    const newSelected = new Set(selectedColumns);
    if (newSelected.has(column)) {
      newSelected.delete(column);
    } else {
      newSelected.add(column);
    }
    setSelectedColumns(newSelected);
  };

  const handleExport = () => {
    if (selectedColumns.size > 0) {
      onExport(Array.from(selectedColumns));
    }
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50">
      <div className="bg-bg-primary border border-border rounded-lg w-[500px] max-h-[80vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h3 className="text-lg font-semibold text-text-primary">
            Select Export Fields
          </h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-bg-secondary rounded"
          >
            <X className="w-5 h-5 text-text-secondary" />
          </button>
        </div>

        <div className="flex-1 overflow-auto p-4">
          <p className="text-sm text-text-secondary mb-4">
            Select the fields to include in your CSV export. All available Everflow API export fields are shown below.
            {selectedRows.length > 0 && (
              <span className="block mt-1">
                Exporting {selectedRows.length} selected row
                {selectedRows.length !== 1 ? "s" : ""}.
              </span>
            )}
          </p>

          <div className="space-y-4">
            {Object.entries(fieldsByCategory).map(([category, fields]) => (
              <div key={category}>
                <h4 className="text-xs font-semibold text-accent-yellow uppercase tracking-wider mb-2">
                  {category}
                </h4>
                <div className="space-y-1">
                  {fields.map((field) => {
                    const isSelected = selectedColumns.has(field.id);
                    return (
                      <label
                        key={field.id}
                        className="flex items-center gap-2 p-2 hover:bg-bg-secondary rounded cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleColumn(field.id)}
                          className="w-4 h-4 border-2 border-accent-yellow rounded bg-bg-primary cursor-pointer checked:bg-accent-yellow checked:border-accent-yellow focus:ring-2 focus:ring-accent-yellow focus:ring-offset-2 focus:ring-offset-bg-primary transition-colors"
                        />
                        <div className="flex-1">
                          <span className={`text-sm ${isSelected ? 'text-accent-yellow font-medium' : 'text-text-primary'}`}>
                            {field.label}
                          </span>
                          {field.description && (
                            <span className="text-xs text-text-secondary block mt-0.5">
                              {field.description}
                            </span>
                          )}
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 p-4 border-t border-border">
          <button onClick={onClose} className="btn-secondary px-4 py-2">
            Cancel
          </button>
          <button
            onClick={handleExport}
            disabled={selectedColumns.size === 0}
            className="btn-primary px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Export CSV
          </button>
        </div>
      </div>
    </div>
  );
}

