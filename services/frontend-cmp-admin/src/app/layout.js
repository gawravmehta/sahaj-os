import localFont from "next/font/local";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import { OrgProvider } from "@/components/shared/OrgContext";

const concurFont = localFont({
  src: [
    {
      path: "/fonts/Concur-Regular.otf",
      weight: "400",
      style: "normal",
    },
    {
      path: "./fonts/Concur-Medium.otf",
      weight: "500",
      style: "normal",
    },
    {
      path: "./fonts/Concur-Bold.otf",
      weight: "700",
      style: "normal",
    },
  ],
});

export const metadata = {
  title: "SAHAJ - Start your compliance journey, Today.",
  description:
    "SAHAJ (Simplified Architecture for Harmonized & Accountable Jurisprudence) is an open-source Consent Management System designed for compliance with the Digital Personal Data Protection Act (DPDPA), 2023.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body
        className={`${concurFont.className} custom-nav-scrollbar antialiased`}
      >
        <OrgProvider>
          <Toaster
            position="top-center"
            toastOptions={{
              duration: 3000,
              style: {
                background: "#F8F8F8",
                color: "black",
                borderRadius: "0px",
                border: "1px solid #1D478E",
                boxShadow: "none",
              },
            }}
          />
          <>{children}</>
        </OrgProvider>
      </body>
    </html>
  );
}
