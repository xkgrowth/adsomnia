import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Adsomnia | Talk-to-Data",
  description: "Natural language interface for Everflow marketing data",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}

