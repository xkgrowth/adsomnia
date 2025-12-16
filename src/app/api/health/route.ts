import { NextResponse } from 'next/server';

/**
 * Health check endpoint for Next.js API routes
 */
export async function GET() {
  return NextResponse.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
  });
}

