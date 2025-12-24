/**
 * API client for Adsomnia backend
 */

import type { ReportRow } from '@/components/ReportModal';

// Get API URL from environment variable (set at build time for production)
// Falls back to localhost for local development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || 'your-secret-api-key-here';

// Log the API URL being used (helpful for debugging)
if (typeof window !== 'undefined') {
  console.log('API Base URL:', API_BASE_URL);
}

export interface ChatRequest {
  message: string;
  thread_id?: string;
}

export interface ChatResponse {
  response: string;
  thread_id: string;
  status: string;
}

/**
 * Send a chat message to the workflow agent
 */
export async function sendChatMessage(
  message: string,
  threadId?: string
): Promise<ChatResponse> {
  console.log('sendChatMessage: Starting', { 
    API_BASE_URL, 
    message: message.substring(0, 50) + '...',
    threadId 
  });
  
  try {
    const requestBody = {
      message,
      thread_id: threadId,
    };
    
    console.log('sendChatMessage: Making fetch request', {
      url: `${API_BASE_URL}/api/chat/query`,
      method: 'POST',
      hasApiKey: !!API_KEY,
    });
    
    // Add timeout to fetch request (90 seconds - should be fast with pre-formatted responses)
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.error('sendChatMessage: Request timeout after 90 seconds');
      controller.abort();
    }, 90000); // 90 second timeout
    
    let response;
    try {
      response = await fetch(`${API_BASE_URL}/api/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': API_KEY,
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
    } catch (fetchError) {
      clearTimeout(timeoutId);
      if (fetchError instanceof Error && fetchError.name === 'AbortError') {
        throw new Error('Request timeout: The server took too long to respond. Please try again.');
      }
      throw fetchError;
    }

    console.log('sendChatMessage: Response received', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('sendChatMessage: Error response', {
        status: response.status,
        errorText,
      });
      
      let error;
      try {
        error = JSON.parse(errorText);
      } catch {
        error = { detail: errorText || 'Unknown error' };
      }
      
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    const data = await response.json();
    console.log('sendChatMessage: Success', {
      responseLength: data.response?.length || 0,
      hasThreadId: !!data.thread_id,
    });
    
    return data;
  } catch (error) {
    console.error('sendChatMessage: Exception caught', error);
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to send message');
  }
}

/**
 * Check if the API is healthy
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export interface Affiliate {
  affiliate_id: number;
  affiliate_name: string;
}

export interface Offer {
  offer_id: number;
  offer_name: string;
}

export interface EntitiesResponse {
  status: string;
  affiliates: Affiliate[];
  offers: Offer[];
  affiliate_count: number;
  offer_count: number;
}

/**
 * Fetch real affiliates and offers from Everflow API
 */
export async function fetchEntities(): Promise<EntitiesResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/entities/all?limit=5`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to fetch entities');
  }
}

// Report-related interfaces and functions
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

export interface ExportRequest {
  report_type: string;
  date_range: string;
  columns?: string[];
  filters?: Record<string, any>;
  selected_rows?: string[]; // Row IDs to export
}

export interface ExportResponse {
  status: string;
  download_url?: string;
  expires_in?: number;
  message?: string;
}

/**
 * Fetch report data for viewing in modal
 */
export async function fetchReportData(
  reportType: string,
  dateRange: string,
  filters?: Record<string, any>
): Promise<ReportData> {
  try {
    // This would call a backend endpoint that returns structured report data
    // For now, we'll use the export endpoint but request JSON format
    const response = await fetch(`${API_BASE_URL}/api/workflows/wf3/export-report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
      body: JSON.stringify({
        report_type: reportType,
        date_range: dateRange,
        filters: filters,
        format: 'json', // Request JSON instead of CSV for viewing
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to fetch report data');
  }
}

/**
 * Export report as CSV with selected fields and rows
 */
export async function exportReportCSV(
  request: ExportRequest
): Promise<ExportResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/workflows/wf3/export-report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
      body: JSON.stringify({
        report_type: request.report_type,
        date_range: request.date_range,
        columns: request.columns,
        filters: request.filters,
        selected_rows: request.selected_rows,
      }),
    });

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || error.error || JSON.stringify(error);
      } catch (e) {
        // If JSON parsing fails, try to get text
        try {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        } catch (e2) {
          // Keep default error message
        }
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to export report');
  }
}

// ============================================================================
// WF3.1 - Conversion Reports (Viewing)
// ============================================================================

export interface FetchConversionsRequest {
  report_type: "fraud" | "conversions";
  date_range: string;
  filters?: Record<string, any>;
  page?: number;
  page_size?: number;
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
  [key: string]: any;
}

export interface FetchConversionsResponse {
  status: string;
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
  message?: string;
}

export async function fetchConversions(
  request: FetchConversionsRequest
): Promise<FetchConversionsResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/workflows/wf3/fetch-conversions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
      body: JSON.stringify({
        report_type: request.report_type,
        date_range: request.date_range,
        filters: request.filters,
        page: request.page || 1,
        page_size: request.page_size || 50,
      }),
    });

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || error.error || JSON.stringify(error);
      } catch (e) {
        try {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        } catch (e2) {
          // Keep default error message
        }
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to fetch conversions');
  }
}

export interface UpdateConversionStatusRequest {
  conversion_id: string;
  status: "approved" | "rejected" | "invalid";
}

export interface UpdateConversionStatusResponse {
  status: string;
  message: string;
  conversion_id?: string;
  updated_count?: number;
}

export async function updateConversionStatus(
  request: UpdateConversionStatusRequest
): Promise<UpdateConversionStatusResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/workflows/wf3/conversions/${request.conversion_id}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
      body: JSON.stringify({
        status: request.status,
      }),
    });

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || error.error || JSON.stringify(error);
      } catch (e) {
        try {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        } catch (e2) {
          // Keep default error message
        }
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to update conversion status');
  }
}

export interface BulkUpdateConversionStatusRequest {
  conversion_ids: string[];
  status: "approved" | "rejected" | "invalid";
}

export async function bulkUpdateConversionStatus(
  request: BulkUpdateConversionStatusRequest
): Promise<UpdateConversionStatusResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/workflows/wf3/conversions/bulk-status`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY,
      },
      body: JSON.stringify({
        conversion_ids: request.conversion_ids,
        status: request.status,
      }),
    });

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const error = await response.json();
        errorMessage = error.detail || error.message || error.error || JSON.stringify(error);
      } catch (e) {
        try {
          const errorText = await response.text();
          errorMessage = errorText || errorMessage;
        } catch (e2) {
          // Keep default error message
        }
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to bulk update conversion statuses');
  }
}

