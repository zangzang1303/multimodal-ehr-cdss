import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const geist = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Multimodal EHR CDSS | Clinical Decision Support System",
  description:
    "Multimodal Clinical Decision Support System - Phase 1: Baselines & Research Benchmark.",
  keywords: [
    "Clinical Decision Support",
    "EHR",
    "Multimodal AI",
    "Healthcare ML",
    "FT-Transformer",
    "Bio_ClinicalBERT",
    "XGBoost",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  const storedTheme = localStorage.getItem('theme');
                  if (storedTheme === 'light') {
                    document.documentElement.classList.remove('dark');
                  } else {
                    document.documentElement.classList.add('dark');
                  }
                } catch (e) {
                  document.documentElement.classList.add('dark');
                }
              })();
            `,
          }}
        />
      </head>
      <body
        className={`${geist.variable} font-sans bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 antialiased min-h-screen selection:bg-emerald-500/20 selection:text-emerald-500`}
      >
        <div className="relative min-h-screen flex flex-col bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(14,165,233,0.1),rgba(255,255,255,0))] dark:bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(14,165,233,0.15),rgba(255,255,255,0))]">
          {children}
        </div>
      </body>
    </html>
  );
}
