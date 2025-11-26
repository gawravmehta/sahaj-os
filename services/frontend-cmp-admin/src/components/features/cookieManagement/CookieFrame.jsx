"use client";
import React, { useMemo } from "react";

export default function CookieIframePreview({ scriptUrl }) {
  const srcDoc = useMemo(
    () => `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta
      http-equiv="Content-Security-Policy"
      content="default-src 'self' ${new URL(scriptUrl).origin};
               script-src 'unsafe-inline' 'unsafe-eval' ${
                 new URL(scriptUrl).origin
               };
               style-src 'self' 'unsafe-inline';
               img-src * data:;
               connect-src *;
               frame-ancestors 'none';"
    />
    <meta name="color-scheme" content="light dark" />
    <style>html,body{margin:0;padding:0; background-color: #d2d2d2}</style>
  </head>
  <body>
    <div id="cookie-preview-root"></div>
    <script>
      
      try {
        Object.defineProperty(document, 'cookie', {
          get() { return ''; },
          set()
          configurable: true
        });
        
        const noopStore = { getItem(){return null}, setItem(){}, removeItem(){}, clear(){}, key(){return null}, length:0 };
        Object.defineProperty(window, 'localStorage', { value: noopStore });
        Object.defineProperty(window, 'sessionStorage', { value: noopStore });
      } catch(e) {}
    </script>
    <script src="${scriptUrl}"></script>
  </body>
</html>`,
    [scriptUrl]
  );

  return (
    <iframe
      sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox"
      referrerPolicy="no-referrer"
      srcDoc={srcDoc}
      width={"100%"}
      height={490}
      style={{ border: "1px solid #ddd" }}
      key={scriptUrl}
    />
  );
}
