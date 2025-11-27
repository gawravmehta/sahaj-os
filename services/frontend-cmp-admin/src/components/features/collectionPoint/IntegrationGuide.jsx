"use client";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { BsArrowRight } from "react-icons/bs";
import { LuCopy } from "react-icons/lu";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomDark } from "react-syntax-highlighter/dist/esm/styles/prism";

const IntegrationGuide = ({ cpId, hasHeader = true }) => {
  const [activeTab, setActiveTab] = useState("Plain HTML");
  const [copied, setCopied] = useState(false);
  const [configCopied, setConfigCopied] = useState(false);

  const router = useRouter();

  const languageTabs = [
    "Plain HTML",
    "React",
    "Angular",
    "Vue",
    "Svelte",
    "React Native",
    "Flutter",
  ];

  const configCode = `export const CONFIG = {
  DF_ID: "9f091721-24fc-4f70-9770-c2e9f5623573",
  DF_KEY: "Gd0KlIaNXVCdU2Sy",
  DF_SECRET: "zkp?x!8T6riEY3tgFgbSp?hnxh20uNUnp25pr$&?2Qo33l!CDL14FeuNVLpzfPvE",
  CMP_CUSTOMER_FRONTEND_URL: "http://localhost:3001",
};`;

  const codeSamples = {
    "Plain HTML": `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Notice</title>
  </head>
  <body>
    <button id="test-button">Test Notice</button>
    <div id="message"></div>
  </body>
  <script type="module">
    import { invokeNotice } from "./concur-notice.js";

    document.getElementById("test-button").addEventListener("click", () => {
      invokeNotice({
        cp_id: "${cpId}",
      });
    });
  </script>
</html>`,

    React: `import React from 'react';
import { invokeNotice } from './concur-notice';

const ConsentComponent = () => {
  const handleNotice = () => {
    invokeNotice({
      cp_id: "${cpId}",
    });
  };

  return (
    <div>
      <button onClick={handleNotice}>Manage Consent</button>
    </div>
  );
};

export default ConsentComponent;`,

    Angular: `import { Component } from '@angular/core';
import { invokeNotice } from './concur-notice';

@Component({
  selector: 'app-consent',
  template: \`<button (click)="showNotice()">Privacy Settings</button>\`,
})
export class ConsentComponent {
  showNotice() {
    invokeNotice({
      cp_id: "${cpId}",
    });
  }
}`,

    Vue: `<script setup>
import { invokeNotice } from './concur-notice';

const showNotice = () => {
  invokeNotice({
    cp_id: "${cpId}",
  });
};
</script>

<template>
  <button @click="showNotice">Privacy Settings</button>
</template>`,

    Svelte: `<script>
  import { invokeNotice } from './concur-notice.js';

  function showNotice() {
    invokeNotice({
      cp_id: "${cpId}",
    });
  }
</script>

<button on:click={showNotice}>Privacy Settings</button>`,

    "React Native": `import React from 'react';
import { WebView } from 'react-native-webview';

const ConsentWebView = () => {
  const htmlContent = \`
    <!DOCTYPE html>
    <html>
      <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
      <body>
        <script>
          // import remotely or inline your script here
          // invokeNotice({ cp_id: "${cpId}" })
        </script>
      </body>
    </html>
  \`;

  return (
    <WebView 
      source={{ html: htmlContent }} 
      originWhitelist={['*']}
    />
  );
};

export default ConsentWebView;`,

    Flutter: String.raw`import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class ConsentScreen extends StatefulWidget {
  @override
  _ConsentScreenState createState() => _ConsentScreenState();
}

class _ConsentScreenState extends State<ConsentScreen> {
  late final WebViewController controller;

  @override
  void initState() {
    super.initState();
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..loadHtmlString("""
        <!DOCTYPE html>
        <html>
          <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
          <body>
            <script>
              // invoke notice with cp_id: ${cpId}
            </script>
          </body>
        </html>
      """);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Consent Manager')),
      body: WebViewWidget(controller: controller),
    );
  }
}`,
  };

  const handleCopy = async (text, setCopiedFunc) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedFunc(true);
      setTimeout(() => setCopiedFunc(false), 2000);
    } catch (err) {
      console.error("Failed to copy: ", err);
    }
  };

  const getSyntaxLanguage = (lang) => {
    if (lang === "React" || lang === "React Native") return "jsx";
    if (lang === "Angular") return "typescript";
    if (lang === "Vue" || lang === "Plain HTML") return "html";
    if (lang === "Flutter") return "dart";
    return "javascript";
  };

  return (
    <div className="w-full">
      {hasHeader && (
        <>
          <div className="flex justify-between border-b border-borderheader">
            <Header
              title="Integration Guide"
              subtitle="Explained how you can integrate this collection point in your application"
            />
            <div className="flex items-center justify-center gap-2 pr-6">
              <Button
                onClick={() => router.push("/apps/collection-point")}
                variant="secondary"
                className="hover:none gap-1"
              >
                Back to Collection Point <BsArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </>
      )}

      <div className="h-full">
        <div className=" shadow-all relative mx-auto flex flex-col items-center justify-center gap-4 p-4">
          <div className=" mb-16 w-[750px] border-2 border-dashed border-[#D7D7D7] px-5 py-4">
            <div className="mb-4 flex flex-wrap gap-2">
              {languageTabs.map((lang) => (
                <button
                  key={lang}
                  onClick={() => setActiveTab(lang)}
                  className={`px-3 py-1 text-sm  transition-colors ${
                    activeTab === lang
                      ? "bg-primary text-white font-medium"
                      : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  {lang}
                </button>
              ))}
            </div>

            <div className="relative h-[450px] overflow-hidden bg-[#1D1F21]">
              <button
                onClick={() => handleCopy(codeSamples[activeTab], setCopied)}
                className="absolute right-0 top-0 z-10 flex cursor-pointer items-center gap-2 rounded-bl-xl bg-primary px-3 py-2 text-xs text-white hover:bg-primary/80 transition-colors"
              >
                {copied ? "Copied!" : "Copy"} <LuCopy />
              </button>

              <div className="custom-scrollbar h-full w-full overflow-auto">
                <SyntaxHighlighter
                  language={getSyntaxLanguage(activeTab)}
                  style={atomDark}
                  wrapLongLines={false}
                  customStyle={{
                    margin: 0,
                    padding: "1.5rem",
                    backgroundColor: "transparent",
                    fontSize: "13px",
                    lineHeight: "1.5",
                  }}
                >
                  {codeSamples[activeTab]}
                </SyntaxHighlighter>
              </div>
            </div>

            <div className="mt-6 space-y-4 text-sm text-[#4f4f4f]">
              <div>
                <p className="mb-2">
                  <strong>1. Download the SDK:</strong> Download the{" "}
                  <code className="bg-gray-100 px-1 py-0.5 rounded text-[#175FC9]">
                    concur-notice.js
                  </code>{" "}
                  file and place it in your project.
                </p>
              </div>

              <div>
                <p className="mb-2">
                  <strong>2. Create Config File:</strong> Create a file named{" "}
                  <code className="bg-gray-100 px-1 py-0.5 rounded text-[#175FC9]">
                    config.js
                  </code>{" "}
                  with the following content:
                </p>
                <div className="relative overflow-hidden bg-[#1D1F21] ">
                  <button
                    onClick={() => handleCopy(configCode, setConfigCopied)}
                    className="absolute right-0 top-0 z-10 flex cursor-pointer items-center gap-2 rounded-bl-xl bg-primary px-3 py-2 text-xs text-white hover:bg-primary/80 transition-colors"
                  >
                    {configCopied ? "Copied!" : "Copy"} <LuCopy />
                  </button>
                  <SyntaxHighlighter
                    language="javascript"
                    style={atomDark}
                    wrapLongLines={false}
                    customStyle={{
                      margin: 0,
                      padding: "1rem",
                      backgroundColor: "transparent",
                      fontSize: "12px",
                      lineHeight: "1.5",
                    }}
                  >
                    {configCode}
                  </SyntaxHighlighter>
                </div>
              </div>

              <div className="bg-gray-50 p-4  border border-gray-300">
                <p className="font-semibold mb-2 text-primary">
                  Available Parameters:
                </p>
                <ul className="list-disc list-inside space-y-1 text-primary text-xs font-mono">
                  <li>cp_id (required): Collection Point ID</li>
                  <li>dp_id (optional): Data Principal ID</li>
                  <li>dp_e (optional): Email Address</li>
                  <li>dp_m (optional): Mobile Number</li>
                  <li>pref_language (default: "eng"): Preferred Language</li>
                  <li>
                    redirect_url (optional): URL to redirect after consent
                  </li>
                  <li>height (default: 600): Modal height</li>
                  <li>width (default: 900): Modal width</li>
                </ul>
              </div>

              <p>
                For more details, refer to our{" "}
                <Link
                  href="https://docs.sahaj.live/docs/category/integration"
                  className="text-primary underline hover:text-primary/80"
                  target="_blank"
                >
                  documentation
                </Link>
                .
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntegrationGuide;
