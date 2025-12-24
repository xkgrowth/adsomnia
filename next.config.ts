import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable React strict mode for better development experience
  reactStrictMode: true,
  
  // Environment variables available to the browser
  env: {
    NEXT_PUBLIC_APP_NAME: "Adsomnia Talk-to-Data",
    // API URL will be set via environment variable at build time
    // Defaults to localhost for local development
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  
  // Output standalone for Docker deployment
  output: 'standalone',
};

export default nextConfig;









