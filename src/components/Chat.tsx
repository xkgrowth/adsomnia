"use client";

import { useState, useRef, useEffect, useImperativeHandle, forwardRef } from "react";
import { sendChatMessage, fetchEntities, exportReportCSV, type Affiliate, type Offer, type ReportData, type ExportRequest, fetchConversions, updateConversionStatus, bulkUpdateConversionStatus, type FetchConversionsResponse } from "@/lib/api";
import ReportModal, { type ReportRow } from "./ReportModal";
import ConversionReportModal, { type ConversionRecord, type ConversionReportData } from "./ConversionReportModal";
import { getAvailableExportFields } from "@/lib/everflowFields";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  reportData?: ReportData; // Optional report data for this message
  conversionReportData?: ConversionReportData; // Optional conversion report data
  reportMetadata?: {
    reportType?: string;
    dateRange?: string;
    filters?: Record<string, any>;
    originalQuery?: string; // Store original user query for fetching full reports
  };
  suggestsFeatureRequest?: boolean; // Whether this message suggests requesting as feature
};

type ExampleQuery = {
  query: string;
  subheading?: string; // Optional subheading for the query
};

type ExampleQueryCategory = {
  category: string;
  queries: (string | ExampleQuery)[];
  highlightedIndex?: number; // Index of the query to highlight
};

// Get real IDs from environment variables if available, otherwise use test data
const getFallbackAffiliates = (): Affiliate[] => {
  // Check for environment variable override
  const envAffiliates = process.env.NEXT_PUBLIC_AFFILIATE_IDS;
  if (envAffiliates) {
    try {
      const ids = JSON.parse(envAffiliates);
      return ids.map((aff: any) => ({
        affiliate_id: typeof aff === 'number' ? aff : aff.id,
        affiliate_name: typeof aff === 'object' ? aff.name : `Partner ${aff}`
      }));
    } catch (e) {
      console.warn("Failed to parse NEXT_PUBLIC_AFFILIATE_IDS, using default");
    }
  }
  // Default test data
  return [
    { affiliate_id: 12345, affiliate_name: "Premium Traffic Partners" },
    { affiliate_id: 23456, affiliate_name: "Global Media Network" },
    { affiliate_id: 34567, affiliate_name: "Digital Marketing Pro" },
  ];
};

const getFallbackOffers = (): Offer[] => {
  // Check for environment variable override
  const envOffers = process.env.NEXT_PUBLIC_OFFER_IDS;
  if (envOffers) {
    try {
      const ids = JSON.parse(envOffers);
      return ids.map((offer: any) => ({
        offer_id: typeof offer === 'number' ? offer : offer.id,
        offer_name: typeof offer === 'object' ? offer.name : `Offer ${offer}`
      }));
    } catch (e) {
      console.warn("Failed to parse NEXT_PUBLIC_OFFER_IDS, using default");
    }
  }
  // Default test data
  return [
    { offer_id: 1001, offer_name: "Summer Promo 2024" },
    { offer_id: 1002, offer_name: "Holiday Special" },
    { offer_id: 1003, offer_name: "Evergreen Offer A" },
  ];
};

const FALLBACK_AFFILIATES = getFallbackAffiliates();
const FALLBACK_OFFERS = getFallbackOffers();

// Generate example queries using real IDs
const generateExampleQueries = (affiliates: Affiliate[], offers: Offer[]): ExampleQueryCategory[] => {
  const offer1 = offers[0];
  const offer2 = offers[1] || offers[0];
  const offer3 = offers[2] || offers[0];
  const offer4 = offers[3] || offers[0];
  const offer5 = offers[4] || offers[0];

  // Find Matchaora offer if available, otherwise use first offer
  const matchaoraOffer = offers.find(o => 
    o.offer_name.toLowerCase().includes('matchaora')
  ) || offer1;

  return [
    {
      category: "WF2: Identify Top-Performing Landing Pages",
      queries: [
        // Exact match to user's manual process - Matchaora offer
        `Show me top landing pages for Matchaora - IT - DOI - (Responsive) year to date with conversions greater than 50 and Advertiser_Internal label`,
      ],
    },
    {
      category: "WF3: Search, Compile, and Export Reports",
      queries: [
        // WF3.1: Conversion report (Fraud detection)
        {
          subheading: "WF3.1: Conversion Report (Fraud Detection) (SOON)",
          query: "Show me conversion report for fraud detection for Papoaolado - BR - DOI - (responsive) with partner iMonetizeIt and source ID 134505 for last month",
        },
        
        // WF3.2: Variance Report
        {
          subheading: "WF3.2: Variance Report (SOON)",
          query: "Show me variance report for this week with parent Partner and child Offer",
        },
        
        // WF3.3: Check Average EPC per offer
        {
          subheading: "WF3.3: Check Average EPC per Offer (SOON)",
          query: "Check average EPC per offer for Matchaora - IT - DOI - (Responsive) with Traffic_FB label and conversions greater than or equal to 50 for last week",
        },
        
        // WF3.4: Check CR Drop
        {
          subheading: "WF3.4: Check CR Drop (SOON)",
          query: "Check conversion rate drop comparing one week versus another week for offers with Advertiser_Internal and Partner_external labels",
        },
      ],
    },
  ];
};

export type ChatSession = {
  id: string;
  title: string;
  threadId: string | null;
  messages: Message[];
  timestamp: Date;
  lastUpdated: Date;
  isFeatureRequest?: boolean;
};

export type ChatHandle = {
  clearChat: () => void;
  loadChat: (session: ChatSession) => void;
  getCurrentSession: () => ChatSession | null;
};

const STORAGE_KEY = "adsomnia_recent_chats";

// Helper functions for localStorage
const saveChatToStorage = (session: ChatSession) => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    const chats: ChatSession[] = stored ? JSON.parse(stored) : [];
    
    // Remove existing chat with same ID if it exists
    const filtered = chats.filter(c => c.id !== session.id);
    
    // Add updated chat at the beginning (no limit - preserve all history)
    const updated = [session, ...filtered];
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (err) {
    console.error("Failed to save chat to storage:", err);
  }
};

export const getRecentChats = (): ChatSession[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    const chats: ChatSession[] = JSON.parse(stored);
    // Convert timestamp strings back to Date objects
    return chats.map(chat => ({
      ...chat,
      timestamp: new Date(chat.timestamp),
      lastUpdated: new Date(chat.lastUpdated),
      messages: chat.messages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      })),
    }));
  } catch (err) {
    console.error("Failed to load chats from storage:", err);
    return [];
  }
};

export const deleteChatFromStorage = (chatId: string) => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return;
    const chats: ChatSession[] = JSON.parse(stored);
    const filtered = chats.filter(c => c.id !== chatId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  } catch (err) {
    console.error("Failed to delete chat from storage:", err);
  }
};

const generateChatTitle = (firstMessage: string): string => {
  // Use the full first user message as the title
  // The UI will handle truncation with line-clamp
  const trimmed = firstMessage.trim();
  return trimmed || "New Chat";
};

const Chat = forwardRef<ChatHandle>((props, ref) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState<string>("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [affiliates, setAffiliates] = useState<Affiliate[]>(FALLBACK_AFFILIATES);
  const [offers, setOffers] = useState<Offer[]>(FALLBACK_OFFERS);
  const [entitiesLoading, setEntitiesLoading] = useState(true);
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [currentReportData, setCurrentReportData] = useState<ReportData | null>(null);
  const [isLoadingFullReport, setIsLoadingFullReport] = useState(false);
  const [conversionReportModalOpen, setConversionReportModalOpen] = useState(false);
  const [currentConversionReportData, setCurrentConversionReportData] = useState<ConversionReportData | null>(null);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [isFeatureRequest, setIsFeatureRequest] = useState<boolean>(false);
  const [showFeatureRequestModal, setShowFeatureRequestModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Fetch real entities on mount
  useEffect(() => {
    const loadEntities = async () => {
      try {
        setEntitiesLoading(true);
        const data = await fetchEntities();
        console.log("Fetched entities response:", JSON.stringify(data, null, 2));
        console.log(`Affiliate count: ${data.affiliate_count}, Offer count: ${data.offer_count}`);
        
        if (data.affiliates && data.affiliates.length > 0) {
          console.log(`✅ Loaded ${data.affiliates.length} real affiliates:`, data.affiliates);
          setAffiliates(data.affiliates);
        } else {
          console.warn("⚠️  No affiliates returned from API, using fallback data");
          console.warn("API returned:", data);
        }
        if (data.offers && data.offers.length > 0) {
          console.log(`✅ Loaded ${data.offers.length} real offers:`, data.offers);
          setOffers(data.offers);
        } else {
          console.warn("⚠️  No offers returned from API, using fallback data");
          console.warn("API returned:", data);
        }
      } catch (err) {
        console.error("❌ Failed to fetch real entities, using fallback data:", err);
        // Keep fallback data
      } finally {
        setEntitiesLoading(false);
      }
    };

    loadEntities();
  }, []);

  // Generate example queries with current entities
  const exampleQueries = generateExampleQueries(affiliates, offers);

  // Expose methods via ref
  useImperativeHandle(ref, () => ({
    clearChat: () => {
      setMessages([]);
      setInput("");
      setThreadId(null);
      setError(null);
      setCurrentChatId(null);
      setIsFeatureRequest(false);
      setReportModalOpen(false);
      setCurrentReportData(null);
    },
    loadChat: (session: ChatSession) => {
      setMessages(session.messages);
      setThreadId(session.threadId);
      setCurrentChatId(session.id);
      setIsFeatureRequest(session.isFeatureRequest || false);
      setInput("");
      setError(null);
    },
    getCurrentSession: (): ChatSession | null => {
      if (messages.length === 0) return null;
      const firstUserMessage = messages.find(m => m.role === "user");
      return {
        id: currentChatId || Date.now().toString(),
        title: firstUserMessage ? generateChatTitle(firstUserMessage.content) : "New Chat",
        threadId,
        messages,
        timestamp: messages[0]?.timestamp || new Date(),
        lastUpdated: new Date(),
        isFeatureRequest,
      };
    },
  }));

  // Save chat to localStorage when messages change
  useEffect(() => {
    if (messages.length > 0) {
      const firstUserMessage = messages.find(m => m.role === "user");
      if (firstUserMessage) {
        const chatId = currentChatId || Date.now().toString();
        setCurrentChatId(chatId);
        
        const session: ChatSession = {
          id: chatId,
          title: generateChatTitle(firstUserMessage.content),
          threadId,
          messages,
          timestamp: messages[0].timestamp,
          lastUpdated: new Date(),
          isFeatureRequest,
        };
        saveChatToStorage(session);
      }
    }
  }, [messages, threadId, currentChatId, isFeatureRequest]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Parse report data from LLM response (detect markdown tables)
  const parseReportData = (content: string, metadata?: { reportType?: string; dateRange?: string }): ReportData | null => {
    // Look for markdown tables in the response - more flexible regex
    // Matches: header row, separator row (with dashes), and data rows
    const tableRegex = /\|(.+)\|\s*\n\s*\|[-\s|:]+\|\s*\n((?:\|.+\|\s*\n?)+)/g;
    const matches = Array.from(content.matchAll(tableRegex));
    
    if (matches.length === 0) {
      // Try alternative format without separator row
      const altRegex = /\|(.+)\|\s*\n((?:\|.+\|\s*\n?)+)/g;
      const altMatches = Array.from(content.matchAll(altRegex));
      if (altMatches.length > 0) {
        // Use first alternative match
        const match = altMatches[0];
        const headerRow = match[1];
        const dataRows = match[2].trim().split('\n').filter(row => row.trim().startsWith('|'));
        
        if (dataRows.length > 0) {
          const columns = headerRow
            .split('|')
            .map((col) => col.trim())
            .filter((col) => col.length > 0);
          
          const rows: ReportRow[] = dataRows.map((row, index) => {
            const cells = row
              .split('|')
              .map((cell) => cell.trim())
              .filter((cell) => cell.length > 0);
            
            const rowData: ReportRow = {
              id: `row-${index}`,
            };
            
            columns.forEach((col, colIndex) => {
              rowData[col] = cells[colIndex] || '';
            });
            
            return rowData;
          });
          
          return {
            columns,
            rows,
            metadata: {
              reportType: 'stats',
            },
          };
        }
      }
      return null;
    }

    // Use the first table found
    const match = matches[0];
    const headerRow = match[1];
    const dataRows = match[2].trim().split('\n');

    // Parse columns from header
    const columns = headerRow
      .split('|')
      .map((col) => col.trim())
      .filter((col) => col.length > 0);

    // Parse data rows
    const rows: ReportRow[] = dataRows.map((row, index) => {
      const cells = row
        .split('|')
        .map((cell) => cell.trim())
        .filter((cell) => cell.length > 0);

      const rowData: ReportRow = {
        id: `row-${index}`,
      };

      columns.forEach((col, colIndex) => {
        rowData[col] = cells[colIndex] || '';
      });

      return rowData;
    });

    return {
      columns,
      rows,
      metadata: metadata || {
        reportType: 'stats',
      },
    };
  };

  // Detect if response contains report data
  const hasReportData = (content: string): boolean => {
    // Check for markdown tables or report indicators
    return /\|.+\|/.test(content) || 
           /report|table|data|export/i.test(content);
  };

  // Unified handler for viewing full reports - workflow agnostic
  const handleViewFullReport = async (message: Message) => {
    try {
      setIsLoadingFullReport(true);
      
      // Check if this is a conversion report (uses different modal)
      if (message.conversionReportData || 
          (message.reportMetadata && 
           (message.reportMetadata.reportType?.includes('conversion') || 
            message.reportMetadata.reportType?.includes('fraud')))) {
        await handleViewConversionReport(message);
        return;
      }
      
      // For all other workflows (WF2, WF4, WF5, WF6, etc.)
      // Re-fetch ALL records using the original query
      if (message.reportMetadata && message.reportMetadata.originalQuery) {
        // Modify query to request ALL records (no limits)
        const fullQuery = `${message.reportMetadata.originalQuery} - show all records, no limit`;
        const fullReportResponse = await sendChatMessage(
          fullQuery,
          threadId || undefined
        );
        
        // Parse the full report data
        const fullReportData = parseReportData(fullReportResponse.response, {
          reportType: message.reportMetadata.reportType,
          dateRange: message.reportMetadata.dateRange
        });
        
        if (fullReportData && fullReportData.rows.length > 0) {
          // Update metadata to preserve original query for future re-fetches
          fullReportData.metadata = {
            ...message.reportMetadata,
            ...fullReportData.metadata
          };
          
          setCurrentReportData(fullReportData);
          setReportModalOpen(true);
          setIsLoadingFullReport(false);
          return;
        }
      }
      
      // Fallback: use the existing report data (may be limited)
      if (message.reportData) {
        setCurrentReportData(message.reportData);
        setReportModalOpen(true);
      }
    } catch (error) {
      console.error('Error fetching full report:', error);
      alert('Failed to load full report. Please try again.');
    } finally {
      setIsLoadingFullReport(false);
    }
  };
  
  // Keep handleViewReport for backward compatibility
  const handleViewReport = handleViewFullReport;

  const handleViewConversionReport = async (message: Message) => {
    try {
      setIsLoadingFullReport(true);
      
      // Always fetch ALL records for the full report, not just the preview
      // Use the metadata to reconstruct the query with a large page_size
      if (message.reportMetadata && 
          (message.reportMetadata.reportType === 'wf3_fraud' || 
           message.reportMetadata.reportType === 'wf3_conversions' ||
           message.reportMetadata.reportType === 'fraud' || 
           message.reportMetadata.reportType === 'conversions')) {
        
        // Determine report type
        const reportType = message.reportMetadata.reportType.includes('fraud') ? 'fraud' : 'conversions';
        
        // Fetch ALL records with maximum page size
        // The API supports up to 2000 records per page according to Everflow docs
        const conversionData = await fetchConversions({
          report_type: reportType,
          date_range: message.reportMetadata.dateRange || "last 30 days",
          filters: message.reportMetadata.filters || message.conversionReportData?.filters,
          page: 1,
          page_size: 2000  // Fetch maximum records per page
        });
        
        // If there are more pages, fetch them all
        let allConversions = [...conversionData.conversions];
        let currentPage = 1;
        const totalPages = conversionData.pagination.total_pages;
        
        // Fetch remaining pages if needed
        while (currentPage < totalPages && currentPage < 10) { // Limit to 10 pages to prevent excessive requests
          currentPage++;
          const pageData = await fetchConversions({
            report_type: reportType,
            date_range: message.reportMetadata.dateRange || "last 30 days",
            filters: message.reportMetadata.filters || message.conversionReportData?.filters,
            page: currentPage,
            page_size: 2000
          });
          allConversions = [...allConversions, ...pageData.conversions];
        }
        
        // Update the conversion data with all records
        const fullConversionData: ConversionReportData = {
          ...conversionData,
          conversions: allConversions,
          pagination: {
            ...conversionData.pagination,
            page: 1,
            total_pages: 1  // We've combined all pages
          }
        };
        
        setCurrentConversionReportData(fullConversionData);
        setConversionReportModalOpen(true);
      } else if (message.conversionReportData) {
        // If we have conversion report data but need to fetch all records
        // Use the existing data to fetch all pages
        const reportType = message.conversionReportData.report_type === 'fraud' ? 'fraud' : 'conversions';
        
        // Fetch ALL records
        const conversionData = await fetchConversions({
          report_type: reportType,
          date_range: message.conversionReportData.date_range,
          filters: message.conversionReportData.filters,
          page: 1,
          page_size: 2000
        });
        
        // Fetch remaining pages if needed
        let allConversions = [...conversionData.conversions];
        let currentPage = 1;
        const totalPages = conversionData.pagination.total_pages;
        
        while (currentPage < totalPages && currentPage < 10) {
          currentPage++;
          const pageData = await fetchConversions({
            report_type: reportType,
            date_range: message.conversionReportData.date_range,
            filters: message.conversionReportData.filters,
            page: currentPage,
            page_size: 2000
          });
          allConversions = [...allConversions, ...pageData.conversions];
        }
        
        const fullConversionData: ConversionReportData = {
          ...conversionData,
          conversions: allConversions,
          pagination: {
            ...conversionData.pagination,
            page: 1,
            total_pages: 1
          }
        };
        
        setCurrentConversionReportData(fullConversionData);
        setConversionReportModalOpen(true);
      }
    } catch (error) {
      console.error('Error fetching full conversion report:', error);
      alert('Failed to load full conversion report. Please try again.');
    } finally {
      setIsLoadingFullReport(false);
    }
  };

  const handleApproveConversions = async (conversionIds: string[]) => {
    try {
      if (conversionIds.length === 1) {
        await updateConversionStatus({
          conversion_id: conversionIds[0],
          status: "approved"
        });
      } else {
        await bulkUpdateConversionStatus({
          conversion_ids: conversionIds,
          status: "approved"
        });
      }
      
      // Refresh the conversion report data
      if (currentConversionReportData) {
        const refreshed = await fetchConversions({
          report_type: currentConversionReportData.report_type as "fraud" | "conversions",
          date_range: currentConversionReportData.date_range,
          filters: currentConversionReportData.filters,
          page: currentConversionReportData.pagination.page,
          page_size: currentConversionReportData.pagination.page_size
        });
        setCurrentConversionReportData(refreshed);
      }
    } catch (error) {
      console.error('Error approving conversions:', error);
      throw error;
    }
  };

  const handleRejectConversions = async (conversionIds: string[]) => {
    try {
      if (conversionIds.length === 1) {
        await updateConversionStatus({
          conversion_id: conversionIds[0],
          status: "rejected"
        });
      } else {
        await bulkUpdateConversionStatus({
          conversion_ids: conversionIds,
          status: "rejected"
        });
      }
      
      // Refresh the conversion report data
      if (currentConversionReportData) {
        const refreshed = await fetchConversions({
          report_type: currentConversionReportData.report_type as "fraud" | "conversions",
          date_range: currentConversionReportData.date_range,
          filters: currentConversionReportData.filters,
          page: currentConversionReportData.pagination.page,
          page_size: currentConversionReportData.pagination.page_size
        });
        setCurrentConversionReportData(refreshed);
      }
    } catch (error) {
      console.error('Error rejecting conversions:', error);
      throw error;
    }
  };

  const handleExportReport = async (
    selectedRows: ReportRow[],
    selectedColumns: string[]
  ) => {
    if (!currentReportData || !currentReportData.metadata) return;

    try {
      // Map WF2 report type to 'stats' for export (WF2 uses entity reporting which is stats)
      let reportType = currentReportData.metadata.reportType || 'stats';
      if (reportType === 'wf2' || reportType === 'wf2_top_lps') {
        reportType = 'stats';
      } else if (reportType === 'wf3_fraud') {
        reportType = 'fraud';
      } else if (reportType === 'wf3_conversions') {
        reportType = 'conversions';
      } else if (reportType === 'wf3_variance') {
        reportType = 'variance';
      } else if (reportType === 'wf3_scrub') {
        reportType = 'scrub';
      } else if (reportType === 'wf3_stats') {
        reportType = 'stats';
      }

      const exportRequest: ExportRequest = {
        report_type: reportType as "fraud" | "conversions" | "stats" | "scrub" | "variance",
        date_range: currentReportData.metadata.dateRange || 'last 30 days',
        columns: selectedColumns,
        filters: currentReportData.metadata?.filters,
        selected_rows: selectedRows.map((row) => row.id),
      };

      // Generate CSV from current report data for immediate download
      // This works even if backend returns a mock URL
      if (currentReportData && currentReportData.rows.length > 0) {
        // Filter rows if specific rows are selected
        const rowsToExport = selectedRows.length > 0 
          ? currentReportData.rows.filter(row => selectedRows.some(selected => selected.id === row.id))
          : currentReportData.rows;
        
        // Map field IDs to actual column names in the data
        // The reverse mapping from export selector field IDs to display column names
        // Note: Some fields like "offer_id" might not exist as separate columns in the data
        // In that case, we'll try to extract the ID from the "Offer" column or leave it empty
        const fieldIdToColumnName: Record<string, string> = {
          "offer": "Offer",           // Maps to "Offer" column (contains name, might contain ID too)
          "offer_id": "Offer",        // Also maps to "Offer" - we'll extract ID if possible
          "offer_name": "Offer",      // Maps to "Offer" column
          "offer_url": "Offer URL",
          "offer_url_id": "Offer URL",
          "offer_url_name": "Offer URL",
          "affiliate": "Partner",
          "affiliate_id": "Partner",
          "affiliate_name": "Partner",
          "cv": "CV",
          "cvr": "CVR",
          "epc": "EPC",
          "rpc": "RPC",
          "payout": "Payout",
          "revenue": "Revenue",
          "clicks": "Clicks",
          "profit": "Profit",
          "conversions": "CV",
          "conversion_rate": "CVR",
          "landing_page": "Offer URL",
        };
        
        // Determine which columns to export and in what order
        // Preserve the order from the modal (field list order, not selection order)
        let columnsToExport: string[] = [];
        let columnHeaders: string[] = [];
        
        if (selectedColumns.length > 0) {
          // Get the field list to determine the order
          const allFields = getAvailableExportFields(reportType);
          
          // Track which columns we've already added
          const addedColumns = new Set<string>();
          const addedFieldIds = new Set<string>();
          
          // Sort selected columns by their order in the field list
          const selectedFieldsOrdered = [...selectedColumns].sort((a, b) => {
            const indexA = allFields.findIndex(f => f.id === a);
            const indexB = allFields.findIndex(f => f.id === b);
            // If not found in list, put at end
            if (indexA === -1) return 1;
            if (indexB === -1) return -1;
            return indexA - indexB;
          });
          
          // Process in the order they appear in the field list
          selectedFieldsOrdered.forEach(fieldId => {
            // Always include each selected field ID as a separate column
            // Even if multiple field IDs map to the same data column
            columnsToExport.push(fieldId); // Use field ID as the key for extraction
            columnHeaders.push(fieldId); // Use field ID as header
            addedFieldIds.add(fieldId);
          });
        } else {
          // Use all available columns
          columnsToExport = currentReportData.columns;
          columnHeaders = currentReportData.columns;
        }
        
        // Generate CSV content
        const csvRows: string[] = [];
        
        // Add header row (use field IDs as headers for clarity)
        csvRows.push(columnHeaders.map(col => `"${col}"`).join(','));
        
        // Add data rows
        rowsToExport.forEach(row => {
          const values = columnsToExport.map(fieldId => {
            // Check if this is a field ID that needs special handling
            const mappedColumn = fieldIdToColumnName[fieldId.toLowerCase()];
            
            // Try multiple strategies to find the value
            let value: any = undefined;
            
            // Strategy 1: If it's a mapped field ID, try to get from mapped column first
            if (mappedColumn && currentReportData.columns.includes(mappedColumn)) {
              value = row[mappedColumn];
              
              // Special handling for offer_id - try to extract ID
              if (fieldId.toLowerCase() === 'offer_id') {
                // Try to extract ID from the value (might be "Offer Name (ID: 123)" or just the name)
                if (value) {
                  const idMatch = String(value).match(/\(ID:\s*(\d+)\)/i) || String(value).match(/ID:\s*(\d+)/i);
                  if (idMatch) {
                    value = idMatch[1];
                  } else {
                    // Check if row has offer_id directly
                    value = row['offer_id'] || row['Offer ID'] || undefined;
                  }
                }
              }
              // For offer_name, use the mapped column value (offer name)
              else if (fieldId.toLowerCase() === 'offer_name') {
                // Use the value from mapped column (which is the offer name)
                value = value; // Already set above
              }
              // For offer, use the mapped column value (offer name)
              else if (fieldId.toLowerCase() === 'offer') {
                // Use the value from mapped column (which is the offer name)
                value = value; // Already set above
              }
            }
            
            // Strategy 2: Direct key match in row
            if ((value === undefined || value === null || value === '') && row[fieldId] !== undefined && row[fieldId] !== null && row[fieldId] !== '') {
              value = row[fieldId];
            }
            
            // Strategy 3: Case-insensitive match
            if (value === undefined || value === null || value === '') {
              const caseInsensitiveKey = Object.keys(row).find(k => 
                k.toLowerCase() === fieldId.toLowerCase()
              );
              if (caseInsensitiveKey && row[caseInsensitiveKey] !== undefined && row[caseInsensitiveKey] !== null && row[caseInsensitiveKey] !== '') {
                value = row[caseInsensitiveKey];
              }
            }
            
            // Strategy 4: Match with spaces/underscores normalized
            if (value === undefined || value === null || value === '') {
              const normalizedKey = Object.keys(row).find(k => 
                k.toLowerCase().replace(/\s+/g, '_') === fieldId.toLowerCase().replace(/\s+/g, '_')
              );
              if (normalizedKey && row[normalizedKey] !== undefined && row[normalizedKey] !== null && row[normalizedKey] !== '') {
                value = row[normalizedKey];
              }
            }
            
            // Strategy 5: Partial match (contains)
            if (value === undefined || value === null || value === '') {
              const partialKey = Object.keys(row).find(k => 
                k.toLowerCase().includes(fieldId.toLowerCase()) || 
                fieldId.toLowerCase().includes(k.toLowerCase().replace(/\s+/g, '_'))
              );
              if (partialKey && row[partialKey] !== undefined && row[partialKey] !== null && row[partialKey] !== '') {
                value = row[partialKey];
              }
            }
            
            // Handle null/undefined/empty - return empty string for missing fields
            if (value === null || value === undefined || value === '') {
              return '""';
            }
            
            // Escape quotes and wrap in quotes
            const stringValue = String(value).replace(/"/g, '""');
            return `"${stringValue}"`;
          });
          csvRows.push(values.join(','));
        });
        
        // Create blob and download
        const csvContent = csvRows.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `export_${reportType}_${Date.now()}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        // Also try to call the backend for future implementation
        try {
          await exportReportCSV(exportRequest);
        } catch (error) {
          // Backend call failed, but we already downloaded the CSV from current data
          console.warn('Backend export call failed (using local data):', error);
        }
      } else {
        // Fallback: try backend export
        const response = await exportReportCSV(exportRequest);
        if (response.download_url) {
          // Try to download from URL
          try {
            const fileResponse = await fetch(response.download_url, {
              method: 'GET',
              mode: 'cors',
            });
            
            if (fileResponse.ok) {
              const blob = await fileResponse.blob();
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = `export_${reportType}_${Date.now()}.csv`;
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              window.URL.revokeObjectURL(url);
            } else {
              alert('Export failed: Unable to download from URL. Please try again.');
            }
          } catch (error) {
            alert('Export failed: ' + (error instanceof Error ? error.message : 'Unknown error'));
          }
        } else {
          alert('Export failed: ' + (response.message || 'Unknown error'));
        }
      }
    } catch (err) {
      let errorMessage = 'Failed to export report';
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err && typeof err === 'object') {
        // Handle error objects
        const errorObj = err as any;
        errorMessage = errorObj.message || errorObj.detail || errorObj.error || JSON.stringify(errorObj);
      }
      alert('Export error: ' + errorMessage);
    }
  };

  const submitMessage = async (messageContent: string) => {
    if (!messageContent.trim() || isLoading) {
      console.log('submitMessage: Skipping - empty message or already loading', { messageContent, isLoading });
      return;
    }

    console.log('submitMessage: Starting', { messageContent, threadId });

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: messageContent.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setLoadingProgress("Analyzing your query...");
    setError(null);

    // Declare progressTimers outside try block so it's accessible in finally
    const progressTimers: NodeJS.Timeout[] = [];

    try {
      console.log('submitMessage: Calling API', { message: userMessage.content, threadId });
      
      // Update progress based on query type with progressive updates
      const queryLower = userMessage.content.toLowerCase();
      
      // Set initial progress
      setLoadingProgress("Analyzing your query...");
      
      // Progressive progress updates based on elapsed time
      
      const progressStages = queryLower.includes('conversion') || queryLower.includes('fraud') 
        ? [
            { time: 500, message: "Understanding your request..." },
            { time: 1500, message: "Identifying conversion report parameters..." },
            { time: 2500, message: "Preparing Everflow API call..." },
            { time: 4000, message: "Fetching conversion data from Everflow..." },
            { time: 8000, message: "Processing conversion records..." },
            { time: 12000, message: "Calculating summary statistics..." },
            { time: 15000, message: "Formatting report table..." },
          ]
        : queryLower.includes('landing page') || queryLower.includes('top')
        ? [
            { time: 500, message: "Understanding your request..." },
            { time: 1500, message: "Analyzing landing page performance..." },
            { time: 4000, message: "Fetching data from Everflow..." },
            { time: 8000, message: "Calculating metrics..." },
            { time: 12000, message: "Formatting results..." },
          ]
        : queryLower.includes('export') || queryLower.includes('download')
        ? [
            { time: 500, message: "Understanding your request..." },
            { time: 2000, message: "Preparing export..." },
            { time: 5000, message: "Generating report..." },
            { time: 10000, message: "Finalizing export..." },
          ]
        : [
            { time: 500, message: "Understanding your request..." },
            { time: 2000, message: "Processing your query..." },
            { time: 5000, message: "Fetching data..." },
            { time: 10000, message: "Formatting response..." },
          ];
      
      // Set up progressive updates
      progressStages.forEach((stage) => {
        const timer = setTimeout(() => {
          setLoadingProgress(stage.message);
        }, stage.time);
        progressTimers.push(timer);
      });
      
      // Call the API
      const response = await sendChatMessage(userMessage.content, threadId || undefined);
      
      // Final progress update
      setLoadingProgress("Finalizing response...");
      console.log('submitMessage: API response received', { response });
      
      // Validate response is not empty
      if (!response || !response.response || response.response.trim().length === 0) {
        throw new Error("Received empty response from server. Please try again.");
      }
      
      // Update thread ID if provided
      if (response.thread_id) {
        setThreadId(response.thread_id);
      }

      // Extract date range from response if available
      let dateRange = 'last 30 days';
      if (response.response.toLowerCase().includes('year to date') || response.response.toLowerCase().includes('ytd')) {
        dateRange = 'year to date';
      } else if (response.response.toLowerCase().includes('last week')) {
        dateRange = 'last week';
      } else if (response.response.toLowerCase().includes('last month')) {
        dateRange = 'last month';
      }

      // Extract report type from response
      let reportType = 'wf2'; // Default to WF2 (landing pages/entity reports)
      if (response.response.toLowerCase().includes('landing page') || response.response.toLowerCase().includes('top landing')) {
        reportType = 'wf2';
      } else if (response.response.toLowerCase().includes('conversion') && response.response.toLowerCase().includes('fraud')) {
        reportType = 'wf3_fraud';
      } else if (response.response.toLowerCase().includes('conversion')) {
        reportType = 'wf3_conversions';
      } else if (response.response.toLowerCase().includes('variance')) {
        reportType = 'wf3_variance';
      } else if (response.response.toLowerCase().includes('scrub')) {
        reportType = 'wf3_scrub';
      } else if (response.response.toLowerCase().includes('stats')) {
        reportType = 'wf3_stats';
      }

      // Parse report data from response with metadata
      const reportData = parseReportData(response.response, { reportType, dateRange });
      const hasReport = hasReportData(response.response);

      // Check if response contains conversion report data (JSON format)
      let conversionReportData: ConversionReportData | undefined = undefined;
      try {
        // Try to parse JSON from the response
        const jsonMatch = response.response.match(/\{[\s\S]*"conversions"[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]);
          if (parsed.conversions && parsed.summary) {
            conversionReportData = parsed as ConversionReportData;
          }
        }
      } catch (e) {
        // Not a conversion report, continue
      }

      // Check if response suggests feature request
      // Look for patterns like "I don't have the capability to do X yet. Would you like to request this as a feature?"
      const suggestsFeatureRequest = /(?:don't have.*capability|don't support|can't do|not.*capable|would you like to request.*as.*feature|request.*as.*feature)/i.test(response.response);

      // Store comprehensive metadata for workflow-agnostic full report fetching
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.response,
        timestamp: new Date(),
        reportData: reportData || undefined,
        conversionReportData: conversionReportData,
        reportMetadata: hasReport || conversionReportData ? {
          reportType: reportType,
          dateRange: dateRange,
          originalQuery: messageContent.trim(), // Store original query for full report fetch
          filters: conversionReportData?.filters || reportData?.metadata?.filters,
          // Store any additional metadata from the report data
          ...(reportData?.metadata || {}),
        } : undefined,
        suggestsFeatureRequest: suggestsFeatureRequest,
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('submitMessage: Error occurred', err);
      const errorMessage = err instanceof Error ? err.message : "Failed to get response";
      setError(errorMessage);
      
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `**Error**\n\n${errorMessage}\n\nPlease check that the API server is running.`,
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      // Clear all progress timers
      progressTimers.forEach(timer => clearTimeout(timer));
      setIsLoading(false);
      setLoadingProgress("");
      console.log('submitMessage: Finished');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submitMessage(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleExampleClick = (query: string) => {
    console.log('handleExampleClick: Called with query', query);
    // Automatically submit the example query
    submitMessage(query);
  };

  const handleMarkAsFeatureRequest = () => {
    setShowFeatureRequestModal(true);
  };

  const handleConfirmFeatureRequest = () => {
    setIsFeatureRequest(true);
    setShowFeatureRequestModal(false);
    // Update the current session in storage
    if (messages.length > 0) {
      const firstUserMessage = messages.find(m => m.role === "user");
      if (firstUserMessage) {
        const chatId = currentChatId || Date.now().toString();
        setCurrentChatId(chatId);
        const session: ChatSession = {
          id: chatId,
          title: generateChatTitle(firstUserMessage.content),
          threadId,
          messages,
          timestamp: messages[0].timestamp,
          lastUpdated: new Date(),
          isFeatureRequest: true,
        };
        saveChatToStorage(session);
      }
    }
  };

  const handleCancelFeatureRequest = () => {
    setShowFeatureRequestModal(false);
  };

  const handleFeatureRequestYes = () => {
    setIsFeatureRequest(true);
    // Update the current session in storage
    if (messages.length > 0) {
      const firstUserMessage = messages.find(m => m.role === "user");
      if (firstUserMessage) {
        const chatId = currentChatId || Date.now().toString();
        setCurrentChatId(chatId);
        const session: ChatSession = {
          id: chatId,
          title: generateChatTitle(firstUserMessage.content),
          threadId,
          messages,
          timestamp: messages[0].timestamp,
          lastUpdated: new Date(),
          isFeatureRequest: true,
        };
        saveChatToStorage(session);
      }
    }
    // Remove the suggestsFeatureRequest flag from the message
    setMessages(prev => prev.map(msg => 
      msg.suggestsFeatureRequest ? { ...msg, suggestsFeatureRequest: false } : msg
    ));
  };

  const handleFeatureRequestNo = () => {
    // Just remove the suggestsFeatureRequest flag from the message
    setMessages(prev => prev.map(msg => 
      msg.suggestsFeatureRequest ? { ...msg, suggestsFeatureRequest: false } : msg
    ));
  };

  const formatContent = (content: string) => {
    // First, check if content contains a markdown table
    const tableRegex = /\|(.+)\|\s*\n\s*\|[-\s|:]+\|\s*\n((?:\|.+\|\s*\n?)+)/g;
    const tableMatches = Array.from(content.matchAll(tableRegex));
    
    if (tableMatches.length > 0) {
      // Split content by tables and process each part
      const parts: (string | React.ReactElement)[] = [];
      let lastIndex = 0;
      
      tableMatches.forEach((match, matchIndex) => {
        // Add text before table
        if (match.index !== undefined && match.index > lastIndex) {
          const textBefore = content.substring(lastIndex, match.index);
          parts.push(...formatTextContent(textBefore));
        }
        
        // Parse and render table
        const headerRow = match[1];
        const dataRows = match[2].trim().split('\n').filter(row => row.trim().startsWith('|'));
        
        const columns = headerRow
          .split('|')
          .map((col) => col.trim())
          .filter((col) => col.length > 0);
        
        // Determine default sort column based on table type
        const getDefaultSortColumn = (cols: string[]): { column: string; direction: 'asc' | 'desc' } | null => {
          // For landing pages, sort by Conversion Rate (CVR) or Conversions (CV) (desc)
          const lowerCols = cols.map(c => c.toLowerCase());
          if (lowerCols.includes('cvr') || lowerCols.includes('conversion rate')) {
            return { column: lowerCols.includes('cvr') ? 'cvr' : 'conversion rate', direction: 'desc' };
          }
          if (lowerCols.includes('cv') || lowerCols.includes('conversions')) {
            return { column: lowerCols.includes('cv') ? 'cv' : 'conversions', direction: 'desc' };
          }
          if (lowerCols.includes('revenue')) {
            return { column: 'revenue', direction: 'desc' };
          }
          if (lowerCols.includes('clicks')) {
            return { column: 'clicks', direction: 'desc' };
          }
          return null;
        };
        
        const defaultSort = getDefaultSortColumn(columns);
        
        // Parse and sort rows
        const parsedRows = dataRows.map((row) => {
          const cells = row
            .split('|')
            .map((cell) => cell.trim())
            .filter((cell) => cell.length > 0);
          return cells;
        });
        
        // Limit preview to 10 rows max
        const previewRows = parsedRows.slice(0, 10);
        const hasMoreRows = parsedRows.length > 10;
        const totalRows = parsedRows.length;
        
        // Sort rows if default sort column is found
        let sortedRows = previewRows;
        if (defaultSort) {
          const sortColIndex = columns.findIndex(
            col => col.toLowerCase() === defaultSort.column
          );
          
          if (sortColIndex >= 0) {
            sortedRows = [...parsedRows].sort((a, b) => {
              const aVal = a[sortColIndex] || '';
              const bVal = b[sortColIndex] || '';
              
              // Parse numbers from strings (handles "4,255", "12.76%", etc.)
              const parseNumber = (val: string): number | null => {
                const cleaned = val.replace(/[,\s%$]/g, "");
                const parsed = parseFloat(cleaned);
                return isNaN(parsed) ? null : parsed;
              };
              
              const aNum = parseNumber(aVal);
              const bNum = parseNumber(bVal);
              
              // If both are numbers, sort numerically
              if (aNum !== null && bNum !== null) {
                return defaultSort.direction === "asc"
                  ? aNum - bNum
                  : bNum - aNum;
              }
              
              // Fallback to string comparison
              const aStr = aVal.toLowerCase();
              const bStr = bVal.toLowerCase();
              return defaultSort.direction === "asc"
                ? aStr.localeCompare(bStr)
                : bStr.localeCompare(aStr);
            });
          }
        }
        
        parts.push(
          <div key={`table-${matchIndex}`} className="my-4 overflow-x-auto">
            <table className="border-collapse border border-border rounded-lg overflow-hidden" style={{ minWidth: 'max-content', width: '100%' }}>
              <thead>
                <tr className="bg-bg-tertiary border-b border-border">
                  {columns.map((col, colIndex) => (
                    <th
                      key={colIndex}
                      className="px-4 py-2 text-left text-xs font-semibold text-accent-yellow uppercase tracking-wide border-r border-border last:border-r-0 whitespace-nowrap"
                      style={{ minWidth: 'fit-content' }}
                    >
                      {col.trim()}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sortedRows.map((cells, rowIndex) => {
                  return (
                    <tr
                      key={rowIndex}
                      className="border-b border-border hover:bg-bg-secondary transition-colors last:border-b-0"
                    >
                      {columns.map((_, colIndex) => {
                        const cellContent = cells[colIndex] || '';
                        // Check if it's a number (for right alignment)
                        const isNumber = /^[\d,.\-%$]+$/.test(cellContent.trim());
                        return (
                          <td
                            key={colIndex}
                            className={`px-4 py-2 text-sm text-text-primary border-r border-border last:border-r-0 whitespace-nowrap ${
                              isNumber ? 'text-right font-mono' : 'text-left'
                            }`}
                            style={{ minWidth: 'fit-content' }}
                          >
                            {cellContent}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {hasMoreRows && (
              <div className="mt-2 text-xs text-text-muted italic text-center">
                Showing {previewRows.length} of {totalRows} records. Click "View Full Report" to see all records with all columns.
              </div>
            )}
          </div>
        );
        
        lastIndex = (match.index || 0) + match[0].length;
      });
      
      // Add remaining text after last table
      if (lastIndex < content.length) {
        parts.push(...formatTextContent(content.substring(lastIndex)));
      }
      
      return parts.length > 0 ? parts : [content];
    }
    
    // No tables found, format as regular text
    return formatTextContent(content);
  };

  const formatTextContent = (text: string) => {
    // Split by markdown patterns and format
    const parts = text.split(/(\*\*.*?\*\*|`.*?`|\n)/);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="text-accent-yellow font-semibold">
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith("`") && part.endsWith("`")) {
        return (
          <code key={i} className="bg-bg-secondary px-1 py-0.5 rounded text-xs font-mono">
            {part.slice(1, -1)}
          </code>
        );
      }
      if (part === "\n") {
        return <br key={i} />;
      }
      return part;
    });
  };

  return (
    <div className="flex flex-1 flex-col h-full bg-bg-primary">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        {/* Example Queries - Show when no messages */}
        {messages.length === 0 && (
          <div className="flex justify-start message-enter">
            <div className="max-w-[85%]">
              <div className="border-l-2 border-accent-yellow pl-4">
                <div className="space-y-4">
                  {exampleQueries.map((category, catIdx) => (
                    <div key={catIdx} className="space-y-2">
                      <div className="text-xs font-semibold text-accent-yellow uppercase tracking-wide mb-2">
                        {category.category}
                      </div>
                      <div className="space-y-3">
                        {category.queries.map((queryItem, qIdx) => {
                          const queryObj = typeof queryItem === 'string' ? { query: queryItem } : queryItem;
                          const { query, subheading } = queryObj;
                          const isHighlighted = category.highlightedIndex === qIdx;
                          
                          return (
                            <div key={qIdx} className="space-y-1.5">
                              {subheading && (
                                <div className="flex items-center gap-2">
                                  <span className="text-xs font-headline tracking-wider text-text-primary uppercase">
                                    {subheading.replace(/\s*\(SOON\)\s*$/, '')}
                                  </span>
                                  {subheading.includes('(SOON)') && (
                                    <span className="px-2 py-0.5 bg-cyan-500 text-slate-900 text-[10px] font-bold uppercase tracking-wider rounded">
                                      SOON
                                    </span>
                                  )}
                                </div>
                              )}
                              <button
                                onClick={() => handleExampleClick(query)}
                                className={`text-xs px-3 py-1.5 border transition-colors rounded cursor-pointer ${
                                  isHighlighted
                                    ? "border-accent-yellow bg-bg-secondary font-semibold text-accent-yellow hover:bg-bg-tertiary"
                                    : "border-border bg-bg-tertiary hover:bg-bg-secondary hover:border-accent-yellow text-text-primary"
                                }`}
                              >
                                {query}
                              </button>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`message-enter flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {message.role === "assistant" ? (
              // Agent message - left accent border style
              <div className="max-w-[85%]">
                <div className="flex items-center gap-2 mb-2">
                  <span className="label-caps text-accent-yellow">
                    ADSOMNIA AGENT
                  </span>
                  <span className="text-xs text-text-muted font-mono">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
                <div className="border-l-2 border-accent-yellow pl-4">
                  <div className="text-sm leading-relaxed text-text-primary whitespace-pre-wrap">
                    {formatContent(message.content)}
                  </div>
                  {/* View Full Report Button - Workflow Agnostic */}
                  {(message.reportData || message.conversionReportData || 
                    (message.reportMetadata && message.reportMetadata.originalQuery)) && (
                    <div className="mt-3">
                      <button
                        onClick={() => handleViewFullReport(message)}
                        disabled={isLoadingFullReport}
                        className="btn-primary px-4 py-2 text-xs disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                      >
                        {isLoadingFullReport ? (
                          <>
                            <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                            Loading...
                          </>
                        ) : (
                          'View Full Report'
                        )}
                      </button>
                    </div>
                  )}
                  {/* Feature Request CTAs */}
                  {message.suggestsFeatureRequest && (
                    <div className="mt-3 flex items-center gap-3">
                      <span className="text-xs text-text-muted">Would you like to request this as a feature?</span>
                      <button
                        onClick={handleFeatureRequestYes}
                        className="px-4 py-1.5 text-xs bg-accent-yellow text-black hover:bg-accent-yellow/90 transition-colors font-semibold"
                      >
                        YES
                      </button>
                      <button
                        onClick={handleFeatureRequestNo}
                        className="px-4 py-1.5 text-xs border border-border bg-bg-tertiary text-text-primary hover:bg-bg-secondary transition-colors"
                      >
                        NO
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              // User message - bordered box style
              <div className="max-w-[85%]">
                <div className="flex items-center justify-end gap-2 mb-2">
                  <span className="text-xs text-text-muted font-mono">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                  <span className="label-caps text-text-secondary">YOU</span>
                </div>
                <div className="border border-border bg-bg-tertiary px-4 py-3">
                  <div className="text-sm leading-relaxed text-text-primary whitespace-pre-wrap">
                    {message.content}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Progress indicator */}
        {isLoading && (
          <div className="flex justify-start message-enter">
            <div className="max-w-[85%]">
              <div className="flex items-center gap-2 mb-2">
                <span className="label-caps text-accent-yellow">
                  ADSOMNIA AGENT
                </span>
              </div>
              <div className="border-l-2 border-accent-yellow pl-4">
                <div className="flex items-center gap-3 py-2">
                  <div className="flex gap-1.5">
                    <span className="typing-dot h-2 w-2 bg-accent-yellow" />
                    <span className="typing-dot h-2 w-2 bg-accent-yellow" />
                    <span className="typing-dot h-2 w-2 bg-accent-yellow" />
                  </div>
                  {loadingProgress && (
                    <span className="text-xs text-text-muted font-mono">
                      {loadingProgress}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border px-6 py-4">
        {/* Request Feature Button */}
        {messages.length > 0 && !isFeatureRequest && (
          <div className="mb-3 flex justify-end">
            <button
              onClick={handleMarkAsFeatureRequest}
              className="px-4 py-1.5 text-xs border border-border bg-bg-tertiary text-text-primary hover:bg-bg-secondary hover:border-accent-yellow transition-colors flex items-center gap-2"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Request Feature
            </button>
          </div>
        )}
        <form onSubmit={handleSubmit} className="flex gap-4">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your Everflow data..."
              className="w-full resize-none border border-border bg-bg-tertiary px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-yellow transition-colors font-body"
              rows={1}
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="btn-primary px-8"
          >
            SEND
          </button>
        </form>
        {error && (
          <p className="text-xs text-accent-orange mt-2 text-center font-mono">
            ⚠️ {error}
          </p>
        )}
        <p className="text-xs text-text-muted mt-3 text-center font-mono tracking-wide">
          ENTER TO SEND • SHIFT+ENTER FOR NEW LINE
        </p>
      </div>

      {/* Report Modal */}
      {currentReportData && (
        <ReportModal
          isOpen={reportModalOpen}
          onClose={() => {
            setReportModalOpen(false);
            setCurrentReportData(null);
          }}
          data={currentReportData}
          onExport={handleExportReport}
        />
      )}

      {/* Conversion Report Modal */}
      {currentConversionReportData && (
        <ConversionReportModal
          isOpen={conversionReportModalOpen}
          onClose={() => {
            setConversionReportModalOpen(false);
            setCurrentConversionReportData(null);
          }}
          data={currentConversionReportData}
          onApprove={handleApproveConversions}
          onReject={handleRejectConversions}
          onExport={() => {
            // Export functionality can be added here
            alert('Export functionality coming soon');
          }}
        />
      )}

      {/* Feature Request Modal */}
      {showFeatureRequestModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-bg-secondary border border-border p-6 max-w-md w-full mx-4">
            <h3 className="font-headline text-lg tracking-wider text-text-primary mb-4">
              Request Feature
            </h3>
            <p className="text-sm text-text-primary mb-6">
              Do you want to mark this chat for a feature request?
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={handleCancelFeatureRequest}
                className="px-6 py-2 text-sm border border-border bg-bg-tertiary text-text-primary hover:bg-bg-secondary transition-colors"
              >
                NO
              </button>
              <button
                onClick={handleConfirmFeatureRequest}
                className="px-6 py-2 text-sm bg-accent-yellow text-black hover:bg-accent-yellow/90 transition-colors font-semibold"
              >
                YES
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

Chat.displayName = "Chat";

export default Chat;
