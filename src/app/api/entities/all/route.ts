import { NextRequest, NextResponse } from 'next/server';

/**
 * Next.js API route for fetching entities (affiliates and offers)
 * This runs as a serverless function on Vercel
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const limit = parseInt(searchParams.get('limit') || '5', 10);

    // Get Everflow API credentials from environment
    const everflowApiKey = process.env.EVERFLOW_API_KEY;
    const everflowBaseUrl = process.env.EVERFLOW_BASE_URL || 'https://api.eflow.team';

    if (!everflowApiKey) {
      return NextResponse.json(
        { 
          error: 'EVERFLOW_API_KEY not configured',
          detail: 'Please set EVERFLOW_API_KEY in Vercel environment variables'
        },
        { status: 500 }
      );
    }

    // Fetch affiliates
    const affiliatesResponse = await fetch(
      `${everflowBaseUrl}/v1/networks/affiliates`,
      {
        method: 'GET',
        headers: {
          'X-Eflow-API-Key': everflowApiKey,
          'Content-Type': 'application/json',
        },
      }
    );

    if (!affiliatesResponse.ok) {
      throw new Error(`Everflow API error: ${affiliatesResponse.status}`);
    }

    const affiliatesData = await affiliatesResponse.json();
    const affiliates = (affiliatesData.affiliates || []).slice(0, limit).map((aff: any) => ({
      affiliate_id: aff.network_affiliate_id,
      affiliate_name: aff.name || `Partner ${aff.network_affiliate_id}`,
    }));

    // Fetch offers
    const offersResponse = await fetch(
      `${everflowBaseUrl}/v1/networks/offers`,
      {
        method: 'GET',
        headers: {
          'X-Eflow-API-Key': everflowApiKey,
          'Content-Type': 'application/json',
        },
      }
    );

    if (!offersResponse.ok) {
      throw new Error(`Everflow API error: ${offersResponse.status}`);
    }

    const offersData = await offersResponse.json();
    const offers = (offersData.offers || []).slice(0, limit).map((offer: any) => ({
      offer_id: offer.network_offer_id,
      offer_name: offer.name || `Offer ${offer.network_offer_id}`,
    }));

    return NextResponse.json({
      status: 'success',
      affiliates,
      offers,
      affiliate_count: affiliates.length,
      offer_count: offers.length,
    });

  } catch (error) {
    console.error('Entities API error:', error);
    return NextResponse.json(
      {
        status: 'error',
        affiliates: [],
        offers: [],
        affiliate_count: 0,
        offer_count: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

