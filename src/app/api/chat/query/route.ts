import { NextRequest, NextResponse } from 'next/server';

/**
 * Next.js API route for chat queries
 * 
 * NOTE: This endpoint requires Python backend code (workflow agent).
 * For Vercel deployment, you have two options:
 * 
 * 1. Deploy Python backend separately and proxy requests to it
 * 2. Use Vercel's Python runtime (functions in api/ directory)
 * 
 * For now, this returns an error indicating the setup needed.
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, thread_id } = body;

    if (!message) {
      return NextResponse.json(
        { 
          error: 'Message is required',
          response: 'Please provide a message to process.',
          thread_id: thread_id || 'default',
          status: 'error'
        },
        { status: 400 }
      );
    }

    // Check if we have a separate backend URL configured
    const backendUrl = process.env.BACKEND_API_URL;
    
    if (backendUrl) {
      // Proxy to separate Python backend
      try {
        const response = await fetch(`${backendUrl}/api/chat/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': process.env.API_KEY || 'your-secret-api-key-here',
          },
          body: JSON.stringify({ message, thread_id }),
        });

        if (!response.ok) {
          throw new Error(`Backend returned ${response.status}`);
        }

        const data = await response.json();
        return NextResponse.json(data);
      } catch (error) {
        console.error('Backend proxy error:', error);
        return NextResponse.json({
          error: 'Backend connection failed',
          detail: error instanceof Error ? error.message : 'Unknown error',
          response: 'Unable to connect to the Python backend. Please ensure the backend is running and BACKEND_API_URL is configured correctly.',
          thread_id: thread_id || 'default',
          status: 'error'
        }, { status: 503 });
      }
    }

    // No backend configured - return helpful error
    return NextResponse.json({
      error: 'Backend not configured',
      detail: 'The chat endpoint requires Python backend code. Please configure BACKEND_API_URL or set up Vercel Python serverless functions.',
      response: 'Chat functionality requires the Python workflow agent. Please configure a backend API URL or deploy the Python code as a serverless function.',
      thread_id: thread_id || 'default',
      status: 'error'
    }, { status: 503 });

  } catch (error) {
    console.error('Chat API error:', error);
    // Try to get thread_id from body if available, otherwise use default
    let threadId = 'default';
    try {
      const body = await request.json();
      threadId = body.thread_id || 'default';
    } catch {
      // If we can't parse body, use default
    }
    
    return NextResponse.json(
      { 
        error: 'Failed to process query',
        detail: error instanceof Error ? error.message : 'Unknown error',
        response: 'An error occurred while processing your request.',
        thread_id: threadId,
        status: 'error'
      },
      { status: 500 }
    );
  }
}

