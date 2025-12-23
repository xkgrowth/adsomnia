/**
 * Everflow API Export Fields
 * Comprehensive list of all available export fields from Everflow API
 * Generic and available for any export, regardless of workflow
 */

export interface ExportField {
  id: string;
  label: string;
  category: string;
  description?: string;
}

/**
 * Get all available export fields from Everflow API
 * Returns a comprehensive list of all fields available for any export
 * Not restricted to specific workflows - shows all possible fields
 */
export function getAvailableExportFields(reportType?: string): ExportField[] {
  // Return all available fields regardless of report type
  // Users can select any combination of fields for their export
  return getAllEverflowExportFields();
}

/**
 * Get all available Everflow export fields
 * Comprehensive list of all fields available across all workflows
 */
function getAllEverflowExportFields(): ExportField[] {
  return [
    // Entity Columns
    { id: 'offer', label: 'Offer', category: 'Entities', description: 'Offer ID and name' },
    { id: 'offer_id', label: 'Offer ID', category: 'Entities', description: 'Offer ID only' },
    { id: 'offer_name', label: 'Offer Name', category: 'Entities', description: 'Offer name only' },
    { id: 'offer_url', label: 'Offer URL', category: 'Entities', description: 'Landing page ID and name' },
    { id: 'offer_url_id', label: 'Offer URL ID', category: 'Entities', description: 'Landing page ID only' },
    { id: 'offer_url_name', label: 'Offer URL Name', category: 'Entities', description: 'Landing page name only' },
    { id: 'affiliate', label: 'Affiliate', category: 'Entities', description: 'Affiliate/Partner ID and name' },
    { id: 'affiliate_id', label: 'Affiliate ID', category: 'Entities', description: 'Affiliate/Partner ID only' },
    { id: 'affiliate_name', label: 'Affiliate Name', category: 'Entities', description: 'Affiliate/Partner name only' },
    { id: 'country', label: 'Country', category: 'Entities', description: 'Country code and name' },
    { id: 'country_code', label: 'Country Code', category: 'Entities', description: 'ISO country code (e.g., US, DE)' },
    { id: 'country_name', label: 'Country Name', category: 'Entities', description: 'Full country name' },
    { id: 'source', label: 'Source', category: 'Entities', description: 'Traffic source' },
    
    // Tracking Parameters
    { id: 'sub1', label: 'Sub1', category: 'Tracking', description: 'Sub-tracking parameter 1' },
    { id: 'sub2', label: 'Sub2', category: 'Tracking', description: 'Sub-tracking parameter 2' },
    { id: 'sub3', label: 'Sub3', category: 'Tracking', description: 'Sub-tracking parameter 3' },
    { id: 'sub4', label: 'Sub4', category: 'Tracking', description: 'Sub-tracking parameter 4' },
    { id: 'sub5', label: 'Sub5', category: 'Tracking', description: 'Sub-tracking parameter 5' },
    
    // Metrics (Performance)
    { id: 'clicks', label: 'Clicks', category: 'Metrics', description: 'Total clicks' },
    { id: 'cv', label: 'CV (Conversions)', category: 'Metrics', description: 'Total conversions' },
    { id: 'cvr', label: 'CVR (Conversion Rate)', category: 'Metrics', description: 'Conversion rate percentage' },
    { id: 'revenue', label: 'Revenue', category: 'Metrics', description: 'Total revenue' },
    { id: 'payout', label: 'Payout', category: 'Metrics', description: 'Total payout' },
    { id: 'profit', label: 'Profit', category: 'Metrics', description: 'Revenue minus payout' },
    { id: 'epc', label: 'EPC (Earnings Per Click)', category: 'Metrics', description: 'Payout per click' },
    { id: 'rpc', label: 'RPC (Revenue Per Click)', category: 'Metrics', description: 'Revenue per click' },
    { id: 'event_conversion', label: 'Event Conversions', category: 'Metrics', description: 'Event-based conversions' },
    
    // Conversion Identifiers (for conversion-level exports)
    { id: 'conversion_id', label: 'Conversion ID', category: 'Identifiers', description: 'Unique conversion identifier' },
    { id: 'click_id', label: 'Click ID', category: 'Identifiers', description: 'Unique click identifier' },
    
    // Network Information
    { id: 'click_ip', label: 'Click IP', category: 'Network', description: 'IP address of the click' },
    { id: 'conversion_ip', label: 'Conversion IP', category: 'Network', description: 'IP address of the conversion' },
    { id: 'user_agent', label: 'User Agent', category: 'Network', description: 'Browser user agent string' },
    
    // Status & Fraud
    { id: 'status', label: 'Status', category: 'Status', description: 'Conversion status' },
    { id: 'is_fraud', label: 'Is Fraud', category: 'Fraud', description: 'Whether conversion is marked as fraud' },
    { id: 'fraud_reason', label: 'Fraud Reason', category: 'Fraud', description: 'Reason for fraud marking' },
    
    // Timestamps
    { id: 'created_at', label: 'Created At', category: 'Timestamps', description: 'Conversion creation timestamp' },
    { id: 'click_time', label: 'Click Time', category: 'Timestamps', description: 'Click timestamp' },
    { id: 'conversion_time', label: 'Conversion Time', category: 'Timestamps', description: 'Conversion timestamp' },
    
    // Variance/Comparison Fields (for variance reports)
    { id: 'previous_period_clicks', label: 'Previous Period Clicks', category: 'Variance', description: 'Clicks from previous period' },
    { id: 'previous_period_cv', label: 'Previous Period CV', category: 'Variance', description: 'Conversions from previous period' },
    { id: 'previous_period_revenue', label: 'Previous Period Revenue', category: 'Variance', description: 'Revenue from previous period' },
    { id: 'variance_clicks', label: 'Clicks Variance', category: 'Variance', description: 'Percentage change in clicks' },
    { id: 'variance_cv', label: 'CV Variance', category: 'Variance', description: 'Percentage change in conversions' },
    { id: 'variance_revenue', label: 'Revenue Variance', category: 'Variance', description: 'Percentage change in revenue' },
    { id: 'variance_cvr', label: 'CVR Variance', category: 'Variance', description: 'Percentage change in conversion rate' },
  ];
}


/**
 * Get fields grouped by category for better UI organization
 */
export function getFieldsByCategory(fields: ExportField[]): Record<string, ExportField[]> {
  return fields.reduce((acc, field) => {
    if (!acc[field.category]) {
      acc[field.category] = [];
    }
    acc[field.category].push(field);
    return acc;
  }, {} as Record<string, ExportField[]>);
}

