"use client";

import { useState, useRef, useEffect, useImperativeHandle, forwardRef } from "react";
import { sendChatMessage, fetchEntities, exportReportCSV, type Affiliate, type Offer, type ReportData, type ExportRequest } from "@/lib/api";
import ReportModal, { type ReportRow } from "./ReportModal";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  reportData?: ReportData; // Optional report data for this message
  reportMetadata?: {
    reportType?: string;
    dateRange?: string;
    filters?: Record<string, any>;
    originalQuery?: string; // Store original user query for fetching full reports
  };
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
          subheading: "WF3.1: Conversion Report (Fraud Detection)",
          query: "Show me conversion report for fraud detection for Papoaolado - BR - DOI - (responsive) with partner iMonetizeIt and source ID 134505 for last month",
        },
        
        // WF3.2: Variance Report
        {
          subheading: "WF3.2: Variance Report",
          query: "Show me variance report for this week with parent Partner and child Offer",
        },
        
        // WF3.3: Check Average EPC per offer
        {
          subheading: "WF3.3: Check Average EPC per Offer",
          query: "Check average EPC per offer for Matchaora - IT - DOI - (Responsive) with Traffic_FB label and conversions greater than or equal to 50 for last week",
        },
        
        // WF3.4: Check CR Drop
        {
          subheading: "WF3.4: Check CR Drop",
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
};

export type ChatHandle = {
  clearChat: () => void;
  loadChat: (session: ChatSession) => void;
  getCurrentSession: () => ChatSession | null;
};

const STORAGE_KEY = "adsomnia_recent_chats";
const MAX_RECENT_CHATS = 20;

// Helper functions for localStorage
const saveChatToStorage = (session: ChatSession) => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    const chats: ChatSession[] = stored ? JSON.parse(stored) : [];
    
    // Remove existing chat with same ID if it exists
    const filtered = chats.filter(c => c.id !== session.id);
    
    // Add updated chat at the beginning
    const updated = [session, ...filtered].slice(0, MAX_RECENT_CHATS);
    
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
  const [threadId, setThreadId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [affiliates, setAffiliates] = useState<Affiliate[]>(FALLBACK_AFFILIATES);
  const [offers, setOffers] = useState<Offer[]>(FALLBACK_OFFERS);
  const [entitiesLoading, setEntitiesLoading] = useState(true);
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [currentReportData, setCurrentReportData] = useState<ReportData | null>(null);
  const [isLoadingFullReport, setIsLoadingFullReport] = useState(false);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
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
      setReportModalOpen(false);
      setCurrentReportData(null);
    },
    loadChat: (session: ChatSession) => {
      setMessages(session.messages);
      setThreadId(session.threadId);
      setCurrentChatId(session.id);
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
        };
        saveChatToStorage(session);
      }
    }
  }, [messages, threadId, currentChatId]);

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

  const handleViewReport = async (message: Message) => {
    // If we have report metadata with original query, fetch ALL records from the API
    if (message.reportMetadata && 
        message.reportMetadata.reportType === 'landing_pages' &&
        message.reportMetadata.originalQuery) {
      try {
        setIsLoadingFullReport(true);
        
        // Make a new API call to get ALL landing pages (no top_n limit)
        // Modify the query to explicitly request all results
        const fullQuery = `${message.reportMetadata.originalQuery} - show all landing pages, no limit`;
        const fullReportResponse = await sendChatMessage(
          fullQuery,
          threadId || undefined
        );
        
        // Parse the full report data
        const fullReportData = parseReportData(fullReportResponse.response);
        if (fullReportData && fullReportData.rows.length > 0) {
          // Use the full report data with all records
          setCurrentReportData(fullReportData);
          setReportModalOpen(true);
          setIsLoadingFullReport(false);
          return;
        }
      } catch (error) {
        console.error('Error fetching full report:', error);
        // Fall back to using the existing report data
      } finally {
        setIsLoadingFullReport(false);
      }
    }
    
    // Fallback: use the existing report data
    if (message.reportData) {
      setCurrentReportData(message.reportData);
      setReportModalOpen(true);
    }
  };

  const handleExportReport = async (
    selectedRows: ReportRow[],
    selectedColumns: string[]
  ) => {
    if (!currentReportData || !currentReportData.metadata) return;

    try {
      const exportRequest: ExportRequest = {
        report_type: currentReportData.metadata.reportType || 'stats',
        date_range: currentReportData.metadata.dateRange || 'last 30 days',
        columns: selectedColumns,
        filters: currentReportData.metadata?.filters,
        selected_rows: selectedRows.map((row) => row.id),
      };

      const response = await exportReportCSV(exportRequest);

      if (response.download_url) {
        // Open download link in new tab
        window.open(response.download_url, '_blank');
      } else {
        alert('Export failed: ' + (response.message || 'Unknown error'));
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
    setError(null);

    try {
      console.log('submitMessage: Calling API', { message: userMessage.content, threadId });
      // Call the API
      const response = await sendChatMessage(userMessage.content, threadId || undefined);
      console.log('submitMessage: API response received', { response });
      
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

      // Store the original user query for fetching full reports
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.response,
        timestamp: new Date(),
        reportData: reportData || undefined,
        reportMetadata: hasReport ? {
          reportType: reportType,
          dateRange: dateRange,
          originalQuery: messageContent.trim(), // Store original query for full report fetch
        } : undefined,
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('submitMessage: Error occurred', err);
      const errorMessage = err instanceof Error ? err.message : "Failed to get response";
      setError(errorMessage);
      
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `**Error**\n\n${errorMessage}\n\nPlease check that the API server is running at http://localhost:8000`,
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
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
        
        // Sort rows if default sort column is found
        let sortedRows = parsedRows;
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
            <table className="w-full border-collapse border border-border rounded-lg overflow-hidden">
              <thead>
                <tr className="bg-bg-tertiary border-b border-border">
                  {columns.map((col, colIndex) => (
                    <th
                      key={colIndex}
                      className="px-4 py-2 text-left text-xs font-semibold text-accent-yellow uppercase tracking-wide border-r border-border last:border-r-0"
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
                            className={`px-4 py-2 text-sm text-text-primary border-r border-border last:border-r-0 ${
                              isNumber ? 'text-right font-mono' : 'text-left'
                            }`}
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
                                <div className="text-xs font-medium text-text-secondary uppercase tracking-wide">
                                  {subheading}
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
                  {/* View Full Report Button */}
                  {message.reportData && (
                    <div className="mt-3">
                      <button
                        onClick={() => handleViewReport(message)}
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

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex justify-start message-enter">
            <div className="max-w-[85%]">
              <div className="flex items-center gap-2 mb-2">
                <span className="label-caps text-accent-yellow">
                  ADSOMNIA AGENT
                </span>
              </div>
              <div className="border-l-2 border-accent-yellow pl-4">
                <div className="flex gap-1.5 py-2">
                  <span className="typing-dot h-2 w-2 bg-accent-yellow" />
                  <span className="typing-dot h-2 w-2 bg-accent-yellow" />
                  <span className="typing-dot h-2 w-2 bg-accent-yellow" />
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border px-6 py-4">
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
    </div>
  );
});

Chat.displayName = "Chat";

export default Chat;
