import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable React strict mode for better development experience
  reactStrictMode: true,
  
  // Environment variables available to the browser
  env: {
    NEXT_PUBLIC_APP_NAME: "Adsomnia Talk-to-Data",
  },
  
  // Output standalone for Docker deployment
  output: 'standalone',
};

export default nextConfig;








