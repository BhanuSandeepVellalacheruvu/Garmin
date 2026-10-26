import type { Metadata } from "next";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { DemoModeBanner } from "@/components/layout/DemoModeBanner";
import "./globals.css";

export const metadata: Metadata = {
  title: "Garmin AI Performance Lab",
  description: "Personal endurance analytics dashboard and open-weight AI training coach powered by Garmin Connect.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#030712] text-gray-100 flex min-h-screen">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0">
          <DemoModeBanner />
          <Header />
          <main className="flex-1 p-8 overflow-y-auto">{children}</main>
        </div>
      </body>
    </html>
  );
}
