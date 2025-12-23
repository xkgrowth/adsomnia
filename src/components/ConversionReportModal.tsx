"use client";

import { useState, useMemo } from "react";
import { X, Download, CheckCircle, XCircle, AlertCircle, Search, Filter } from "lucide-react";

export interface ConversionRecord {
  conversion_id?: string;
  click_id?: string;
  status?: string;
  date?: string;
  click_date?: string;
  sub1?: string;
  offer?: string;
  partner?: string;
  delta?: string;
  payout?: number | string;
  revenue?: number | string;
  conversion_ip?: string;
  transaction_id?: string;
  offer_events?: string;
  adv1?: string;
  adv2?: string;
  event_name?: string;
  is_fraud?: boolean;
  fraud_reason?: string;
  [key: string]: any; // Allow additional fields
}

export interface ConversionSummary {
  total: number;
  approved: number;
  invalid: number;
  pending: number;
  rejected_manual: number;
  rejected_throttle: number;
  payout: number;
  revenue: number;
  gross_sales: number;
}

export interface ConversionReportData {
  report_type: string;
  date_range: string;
  summary: ConversionSummary;
  conversions: ConversionRecord[];
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
  };
  filters?: Record<string, any>;
}

interface ConversionReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: ConversionReportData;
  onApprove?: (conversionIds: string[]) => Promise<void>;
  onReject?: (conversionIds: string[]) => Promise<void>;
  onExport?: () => void;
}

type SortConfig = {
  column: string;
  direction: "asc" | "desc";
};

const STATUS_COLORS: Record<string, string> = {
  approved: "text-success",
  invalid: "text-error",
  pending: "text-warning",
  rejected_manual: "text-error",
  rejected_throttle: "text-error",
};

const STATUS_ICONS: Record<string, any> = {
  approved: CheckCircle,
  invalid: XCircle,
  pending: AlertCircle,
  rejected_manual: XCircle,
  rejected_throttle: XCircle,
};

export default function ConversionReportModal({
  isOpen,
  onClose,
  data,
  onApprove,
  onReject,
  onExport,
}: ConversionReportModalProps) {
  const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set());
  const [sortConfig, setSortConfig] = useState<SortConfig | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [isProcessing, setIsProcessing] = useState(false);

  const toggleRowSelection = (conversionId: string) => {
    const newSelected = new Set(selectedRows);
    if (newSelected.has(conversionId)) {
      newSelected.delete(conversionId);
    } else {
      newSelected.add(conversionId);
    }
    setSelectedRows(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedRows.size === filteredConversions.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(filteredConversions.map(c => c.conversion_id || "").filter(Boolean)));
    }
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

  // Filter and search conversions
  const filteredConversions = useMemo(() => {
    let filtered = data.conversions;

    // Status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter(c => c.status?.toLowerCase() === statusFilter.toLowerCase());
    }

    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(c => {
        return (
          c.conversion_id?.toLowerCase().includes(query) ||
          c.transaction_id?.toLowerCase().includes(query) ||
          c.conversion_ip?.toLowerCase().includes(query) ||
          c.sub1?.toLowerCase().includes(query) ||
          c.offer?.toLowerCase().includes(query) ||
          c.partner?.toLowerCase().includes(query)
        );
      });
    }

    // Sort
    if (sortConfig) {
      filtered = [...filtered].sort((a, b) => {
        let aVal = a[sortConfig.column];
        let bVal = b[sortConfig.column];

        const parseNumber = (val: any): number | null => {
          if (typeof val === "number") return val;
          if (typeof val === "string") {
            const cleaned = val.replace(/[,\s%$€]/g, "");
            const parsed = parseFloat(cleaned);
            return isNaN(parsed) ? null : parsed;
          }
          return null;
        };

        const aNum = parseNumber(aVal);
        const bNum = parseNumber(bVal);

        if (aNum !== null && bNum !== null) {
          return sortConfig.direction === "asc" ? aNum - bNum : bNum - aNum;
        }

        const aStr = String(aVal || "").toLowerCase();
        const bStr = String(bVal || "").toLowerCase();
        return sortConfig.direction === "asc"
          ? aStr.localeCompare(bStr)
          : bStr.localeCompare(aStr);
      });
    }

    return filtered;
  }, [data.conversions, statusFilter, searchQuery, sortConfig]);

  const handleApprove = async (conversionIds: string[]) => {
    if (!onApprove) return;
    setIsProcessing(true);
    try {
      await onApprove(conversionIds);
      // Clear selection after successful approval
      setSelectedRows(new Set());
    } catch (error) {
      console.error("Failed to approve conversions:", error);
      alert("Failed to approve conversions. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReject = async (conversionIds: string[]) => {
    if (!onReject) return;
    setIsProcessing(true);
    try {
      await onReject(conversionIds);
      // Clear selection after successful rejection
      setSelectedRows(new Set());
    } catch (error) {
      console.error("Failed to reject conversions:", error);
      alert("Failed to reject conversions. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBulkApprove = () => {
    const ids = Array.from(selectedRows).filter(Boolean);
    if (ids.length === 0) {
      alert("Please select at least one conversion to approve.");
      return;
    }
    if (confirm(`Approve ${ids.length} conversion(s)?`)) {
      handleApprove(ids);
    }
  };

  const handleBulkReject = () => {
    const ids = Array.from(selectedRows).filter(Boolean);
    if (ids.length === 0) {
      alert("Please select at least one conversion to reject.");
      return;
    }
    if (confirm(`Reject ${ids.length} conversion(s)?`)) {
      handleReject(ids);
    }
  };

  if (!isOpen) return null;

  // Get all unique column names from conversions
  const allColumns = useMemo(() => {
    const columns = new Set<string>();
    data.conversions.forEach(conv => {
      Object.keys(conv).forEach(key => {
        if (key !== "children") columns.add(key);
      });
    });
    return Array.from(columns);
  }, [data.conversions]);

  // Priority columns matching Everflow default order for conversion reports
  // Status | Date | Click Date | Sub1 | Offer | Partner | Delta | Payout | Conversion IP | Transaction ID | Adv1 | Adv2 | Conversion ID | Event Name
  const priorityColumns = [
    "status", "date", "click_date", "sub1", "offer", "partner",
    "delta", "payout", "conversion_ip", "transaction_id",
    "adv1", "adv2", "conversion_id", "event_name"
  ];

  const orderedColumns = [
    ...priorityColumns.filter(col => allColumns.includes(col)),
    ...allColumns.filter(col => !priorityColumns.includes(col))
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-bg-secondary border border-border w-full max-w-[95vw] h-[90vh] flex flex-col shadow-xl">
        {/* Header */}
        <div className="border-b border-border px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="font-headline text-xl tracking-wider text-text-primary">
              CONVERSION REPORT
            </h2>
            <p className="text-xs text-text-muted font-mono mt-1">
              {data.report_type.toUpperCase()} • {data.date_range}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-text-muted hover:text-text-primary transition-colors p-1"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Summary Section */}
        <div className="border-b border-border px-6 py-4 bg-bg-tertiary">
          <div className="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-4">
            <div>
              <div className="text-xs text-text-muted font-mono uppercase">Total</div>
              <div className="text-lg font-semibold text-text-primary">{data.summary.total}</div>
            </div>
            <div>
              <div className="text-xs text-text-muted font-mono uppercase">Approved</div>
              <div className="text-lg font-semibold text-success">{data.summary.approved}</div>
            </div>
            <div>
              <div className="text-xs text-text-muted font-mono uppercase">Invalid</div>
              <div className="text-lg font-semibold text-error">{data.summary.invalid}</div>
            </div>
            <div>
              <div className="text-xs text-text-muted font-mono uppercase">Pending</div>
              <div className="text-lg font-semibold text-warning">{data.summary.pending}</div>
            </div>
            <div>
              <div className="text-xs text-text-muted font-mono uppercase">Rejected Manual</div>
              <div className="text-lg font-semibold text-error">{data.summary.rejected_manual}</div>
            </div>
            <div>
              <div className="text-xs text-text-muted font-mono uppercase">Rejected Throttle</div>
              <div className="text-lg font-semibold text-error">{data.summary.rejected_throttle}</div>
            </div>
            <div>
              <div className="text-xs text-text-muted font-mono uppercase">Payout</div>
              <div className="text-lg font-semibold text-text-primary">€{data.summary.payout.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-xs text-text-muted font-mono uppercase">Revenue</div>
              <div className="text-lg font-semibold text-text-primary">€{data.summary.revenue.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-xs text-text-muted font-mono uppercase">Gross Sales</div>
              <div className="text-lg font-semibold text-text-primary">€{data.summary.gross_sales.toFixed(2)}</div>
            </div>
          </div>
        </div>

        {/* Toolbar */}
        <div className="border-b border-border px-6 py-3 flex items-center gap-4 bg-bg-secondary">
          <div className="flex-1 flex items-center gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by Conversion IP, Transaction ID, Sub1..."
                className="w-full pl-9 pr-3 py-2 bg-bg-tertiary border border-border text-text-primary placeholder:text-text-muted text-sm focus:outline-none focus:border-accent-yellow transition-colors font-body"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 bg-bg-tertiary border border-border text-text-primary text-sm focus:outline-none focus:border-accent-yellow transition-colors font-body"
            >
              <option value="all">All Status</option>
              <option value="approved">Approved</option>
              <option value="invalid">Invalid</option>
              <option value="pending">Pending</option>
              <option value="rejected_manual">Rejected Manual</option>
              <option value="rejected_throttle">Rejected Throttle</option>
            </select>
          </div>
          <div className="flex items-center gap-2">
            {selectedRows.size > 0 && (
              <>
                <button
                  onClick={handleBulkApprove}
                  disabled={isProcessing}
                  className="btn-primary px-4 py-2 text-xs disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Approve ({selectedRows.size})
                </button>
                <button
                  onClick={handleBulkReject}
                  disabled={isProcessing}
                  className="px-4 py-2 text-xs border border-error text-error hover:bg-error/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <XCircle className="w-4 h-4" />
                  Reject ({selectedRows.size})
                </button>
              </>
            )}
            {onExport && (
              <button
                onClick={onExport}
                className="btn-primary px-4 py-2 text-xs flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
            )}
          </div>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-auto">
          <div className="overflow-x-auto min-w-full">
            <table className="w-full border-collapse" style={{ minWidth: 'max-content' }}>
            <thead className="bg-bg-tertiary sticky top-0">
              <tr>
                <th className="px-4 py-2 text-left border-b border-border">
                  <input
                    type="checkbox"
                    checked={selectedRows.size === filteredConversions.length && filteredConversions.length > 0}
                    onChange={toggleSelectAll}
                    className="cursor-pointer"
                  />
                </th>
                {orderedColumns.map((column) => (
                  <th
                    key={column}
                    onClick={() => handleSort(column)}
                    className="px-4 py-2 text-left text-xs font-semibold text-accent-yellow uppercase tracking-wide border-b border-border cursor-pointer hover:bg-bg-secondary transition-colors whitespace-nowrap"
                    style={{ minWidth: 'fit-content' }}
                  >
                    <div className="flex items-center gap-2">
                      {column.replace(/_/g, " ")}
                      {sortConfig?.column === column && (
                        <span className="text-text-muted">
                          {sortConfig.direction === "asc" ? "↑" : "↓"}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
                <th className="px-4 py-2 text-left border-b border-border">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredConversions.length === 0 ? (
                <tr>
                  <td colSpan={orderedColumns.length + 2} className="px-6 py-12 text-center text-text-muted">
                    No conversions found
                  </td>
                </tr>
              ) : (
                filteredConversions.map((conversion) => {
                  const conversionId = conversion.conversion_id || "";
                  const StatusIcon = conversion.status ? STATUS_ICONS[conversion.status.toLowerCase()] || AlertCircle : AlertCircle;
                  const statusColor = conversion.status ? STATUS_COLORS[conversion.status.toLowerCase()] || "text-text-muted" : "text-text-muted";

                  return (
                    <tr
                      key={conversionId}
                      className="border-b border-border hover:bg-bg-tertiary transition-colors"
                    >
                      <td className="px-4 py-2">
                        <input
                          type="checkbox"
                          checked={selectedRows.has(conversionId)}
                          onChange={() => toggleRowSelection(conversionId)}
                          className="cursor-pointer"
                        />
                      </td>
                      {orderedColumns.map((column) => {
                        const value = conversion[column];
                        const isNumber = typeof value === "number" || (typeof value === "string" && /^[\d,.\-€$]+$/.test(value));
                        
                        // Special handling for status column
                        if (column === "status" && conversion.status) {
                          return (
                            <td key={column} className="px-4 py-2 text-sm">
                              <div className="flex items-center gap-2">
                                <StatusIcon className={`w-4 h-4 ${statusColor}`} />
                                <span className={statusColor}>{conversion.status}</span>
                              </div>
                            </td>
                          );
                        }

                        return (
                          <td
                            key={column}
                            className={`px-4 py-2 text-sm text-text-primary whitespace-nowrap ${
                              isNumber ? "text-right font-mono" : "text-left"
                            }`}
                            style={{ minWidth: 'fit-content' }}
                          >
                            {value !== null && value !== undefined ? String(value) : "-"}
                          </td>
                        );
                      })}
                      <td className="px-4 py-2">
                        <div className="flex items-center gap-2">
                          {onApprove && (
                            <button
                              onClick={() => conversionId && handleApprove([conversionId])}
                              disabled={isProcessing || conversion.status === "approved"}
                              className="text-success hover:text-success/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              title="Approve"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                          )}
                          {onReject && (
                            <button
                              onClick={() => conversionId && handleReject([conversionId])}
                              disabled={isProcessing || conversion.status === "rejected_manual"}
                              className="text-error hover:text-error/80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              title="Reject"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-border px-6 py-3 flex items-center justify-between bg-bg-secondary">
          <div className="text-xs text-text-muted font-mono">
            Showing {filteredConversions.length} of {data.pagination.total_count} conversions
            {data.pagination.total_pages > 1 && ` (Page ${data.pagination.page} of ${data.pagination.total_pages})`}
          </div>
          <div className="text-xs text-text-muted font-mono">
            {selectedRows.size > 0 && `${selectedRows.size} selected`}
          </div>
        </div>
      </div>
    </div>
  );
}

