"use client";
import Link from "next/link";
import { useState } from "react";
import { LuCopy } from "react-icons/lu";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomDark } from "react-syntax-highlighter/dist/esm/styles/prism";

const CookieIntegration = ({ scriptUrl = "script_url" }) => {
  const [activeTab, setActiveTab] = useState("Plain HTML");
  const [copied, setCopied] = useState(false);

  const languageTabs = [
    "Plain HTML",
    "React",
    "Angular",
    "Vue",
    "Svelte",
    "React Native",
    "Flutter",
  ];

  const codeSamples = {
    "Plain HTML": `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Widget Test Page</title>
  </head>
  <body>
    <h1>Testing my CMP Widget</h1>
    <p>The cookie consent banner should appear at the bottom of the page.</p>
    <script>
      // Example of setting essential cookies
      document.cookie = "_ga=abc123; path=/; Secure; SameSite=Lax";
      document.cookie = "session_id22=abc123; path=/; Secure; SameSite=Lax";
      console.log("Essential cookies have been loaded.");
    </script>
    
    <!-- Cookie Consent Script -->
    <script src="${scriptUrl}"></script>
  </body>
</html>`,

    React: `import React, { useEffect } from 'react';

const App = () => {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = "${scriptUrl}";
    script.async = true;
    document.body.appendChild(script);

    return () => {
      // Cleanup if necessary
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div>
      <h1>My React App</h1>
      {/* Your app content */}
    </div>
  );
};

export default App;`,

    Angular: `// Option 1: Add to index.html
<body>
  <app-root></app-root>
  <script src="${scriptUrl}"></script>
</body>

// Option 2: Load in a component
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  template: '<h1>My Angular App</h1>',
})
export class AppComponent implements OnInit {
  ngOnInit() {
    const script = document.createElement('script');
    script.src = "${scriptUrl}";
    script.async = true;
    document.body.appendChild(script);
  }
}`,

    Vue: `<!-- Option 1: Add to index.html -->
<body>
  <div id="app"></div>
  <script src="${scriptUrl}"></script>
</body>

<!-- Option 2: In App.vue -->
<script setup>
import { onMounted } from 'vue';

onMounted(() => {
  const script = document.createElement('script');
  script.src = "${scriptUrl}";
  script.async = true;
  document.body.appendChild(script);
});
</script>`,

    Svelte: `<script>
  import { onMount } from 'svelte';

  onMount(() => {
    const script = document.createElement('script');
    script.src = "${scriptUrl}";
    script.async = true;
    document.body.appendChild(script);
  });
</script>

<h1>My Svelte App</h1>`,

    "React Native": `import React from 'react';
import { WebView } from 'react-native-webview';

const CookieConsentWebView = () => {
  const htmlContent = \`
    <!DOCTYPE html>
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
      </head>
      <body>
        <h1>App Content</h1>
        <script src="${scriptUrl}"></script>
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

export default CookieConsentWebView;`,

    Flutter: String.raw`import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class CookieConsentScreen extends StatefulWidget {
  @override
  _CookieConsentScreenState createState() => _CookieConsentScreenState();
}

class _CookieConsentScreenState extends State<CookieConsentScreen> {
  late final WebViewController controller;

  @override
  void initState() {
    super.initState();
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..loadHtmlString("""
        <!DOCTYPE html>
        <html>
          <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
          </head>
          <body>
            <h1>App Content</h1>
            <script src="${scriptUrl}"></script>
          </body>
        </html>
      """);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Cookie Consent')),
      body: WebViewWidget(controller: controller),
    );
  }
}`,
  };

  const handleCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
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
                onClick={() => handleCopy(codeSamples[activeTab])}
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
                <p className="mb-2 flex items-center gap-2">
                  <strong>Integration Steps:</strong>
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Copy the code snippet for your framework.</li>

                  <li>
                    Ensure the script is loaded on every page where you want the
                    cookie banner to appear.
                  </li>
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

export default CookieIntegration;
