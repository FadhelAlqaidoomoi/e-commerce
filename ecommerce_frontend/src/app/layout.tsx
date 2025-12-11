import { Footer } from "@/components/layout/footer";
import { Header } from "@/components/layout/header";
import { Providers } from "@/components/providers";
import { Toaster } from "@/components/ui/toaster";
import type { Metadata } from "next";
import { Inter, Plus_Jakarta_Sans } from "next/font/google";
import { Toaster as SonnerToaster } from "sonner";
import "./globals.css";

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
});

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta",
});

export const metadata: Metadata = {
  title: process.env.NEXT_PUBLIC_APP_NAME || "Store | Premium E-Commerce",
  description: "Discover extraordinary products curated for you. Shop the future of e-commerce today.",
  keywords: ["e-commerce", "online shopping", "store", "products"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${plusJakarta.variable} ${inter.variable} font-sans`} suppressHydrationWarning>
        <Providers>
          <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1">{children}</main>
            <Footer />
          </div>
          <Toaster />
          <SonnerToaster 
            position="top-right" 
            richColors 
            toastOptions={{
              style: {
                borderRadius: '16px',
              },
            }}
          />
        </Providers>
      </body>
    </html>
  );
}
