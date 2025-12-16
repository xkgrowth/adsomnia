/**
 * API client for Adsomnia - uses Next.js API routes (serverless functions)
 */

// Use relative paths for Next.js API routes (works in both dev and production)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

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
  try {
    // Use Next.js API route (relative path)
    const apiUrl = API_BASE_URL ? `${API_BASE_URL}/api/chat/query` : '/api/chat/query';
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        thread_id: threadId,
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
    throw new Error('Failed to send message');
  }
}

/**
 * Check if the API is healthy
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const apiUrl = API_BASE_URL ? `${API_BASE_URL}/api/health` : '/api/health';
    const response = await fetch(apiUrl);
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
    // Use Next.js API route (relative path)
    const apiUrl = API_BASE_URL 
      ? `${API_BASE_URL}/api/entities/all?limit=5` 
      : '/api/entities/all?limit=5';
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
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

