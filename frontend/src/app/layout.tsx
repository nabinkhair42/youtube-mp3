import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/provider";

export const metadata: Metadata = {
  title: "YouTube Audio Extractor",
  description: "Extract audio from YouTube videos and download as MP3",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html suppressHydrationWarning>
      <body suppressHydrationWarning>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
