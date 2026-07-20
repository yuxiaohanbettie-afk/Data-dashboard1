import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Marketing Intelligence Platform",
  description: "Google Ads & Meta Ads local intelligence workspace",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="zh-CN"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-zinc-50 text-zinc-950 dark:bg-zinc-950 dark:text-zinc-50">
        <div className="min-h-full flex">
          <aside className="hidden md:flex w-64 flex-col border-r border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950">
            <div className="px-5 py-4 font-semibold tracking-tight">
              Marketing Intel
            </div>
            <nav className="px-2 py-2 text-sm">
              <a
                className="block rounded px-3 py-2 hover:bg-zinc-100 dark:hover:bg-zinc-900"
                href="/"
              >
                首页
              </a>
              <a
                className="block rounded px-3 py-2 hover:bg-zinc-100 dark:hover:bg-zinc-900"
                href="/upload"
              >
                Upload Center
              </a>
              <a
                className="block rounded px-3 py-2 hover:bg-zinc-100 dark:hover:bg-zinc-900"
                href="/analysis"
              >
                分析
              </a>
            </nav>
            <div className="mt-auto px-5 py-4 text-xs text-zinc-500">
              Local DB + AI Agent (v0)
            </div>
          </aside>
          <main className="flex-1 min-w-0">{children}</main>
        </div>
      </body>
    </html>
  );
}
