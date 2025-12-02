import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import MainNav from "@/components/MainNav";
import MainFooter from "@/components/MainFooter";
import Script from "next/script";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Sahaj DPDPA Consent Manager - Dummy DF",
  description: "Sahaj DPDPA Consent Manager - Dummy DF",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>

      </head>
      <body className={inter.className}>
        <div>
          <div className="sr-only">
            This is a training or testing environment. No real banking services
            are provided.
          </div>

          <div className="sr-only">
            This site is a mimicry and not associated with any actual bank. For
            educational purposes only.
          </div>
          <MainNav />
          <Toaster />
          {children}
          <MainFooter />
        </div>
        <Script
          dangerouslySetInnerHTML={{
            __html: `
              document.cookie = "_ga=abc123; path=/; Secure; SameSite=Lax";
              document.cookie = "session_id22=abc123; path=/; Secure; SameSite=Lax";
              document.cookie = "session_id2211=abc123; path=/; Secure; SameSite=Lax";
              console.log("Essential cookies have been loaded.");
            `,
          }}
        />
        <Script src="https://minio.catax.me/cookie-consent-scripts/69298db97ab01f21ebcbf272_.js"></Script>
      </body>
    </html>
  );
}
