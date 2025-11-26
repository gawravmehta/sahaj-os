"use client";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import Link from "next/link";
import { useEffect, useLayoutEffect, useState } from "react";
import { IoArrowBackOutline } from "react-icons/io5";
import { LuCopy } from "react-icons/lu";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomDark } from "react-syntax-highlighter/dist/esm/styles/prism";

const DataPrincipalAPI = () => {
  const [activeTab, setActiveTab] = useState("Javascript");
  const [copied, setCopied] = useState(false);
  const [apiKey, setApiKey] = useState("");

  useLayoutEffect(() => {
    fetchSteps();
  }, []);

  const fetchSteps = async () => {
    try {
      const response = await apiCall(
        "/dp_management/get-api-key?key_type=add_dp_key"
      );
      if (response) {
        setApiKey(response);
      }
    } catch (error) {
      console.error("This is error from add DP by API:", error);
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  const languageTabs = [
    "Javascript",
    "cURL",
    ,
    "Python",
    "Java",
    "C#",
    "Go",
    "php",
    "Ruby",
  ];

  const codeSamples = {
    cURL: `curl --fail -v -X POST 
  "http://api.concur.live/api/v1/data_principal/add_bulk?api_key=${apiKey}" \
     -H "Content-Type: application/json" \
     -d '[
           {
             "dp_system_id": "122114454",
             "dp_identifiers": ["email", "mobile number"],
             "dp_email": "example@example.com",
             "dp_mobile": 1234567890,
             "dp_preferred_lang": ["hi"],
             "dp_country": "India",
             "dp_state": "Maharashtra",
             "dp_persona": "customer",
             "dp_tags": ["inactive", "2024"],
             "dp_active_devices": ["app", "website"],
             "is_active": false,
             "is_legacy": true,
             "created_at_df": "2025-03-01T13:25:26.556000Z",
             "last_activity": "2025-03-31T13:25:26.556000Z"
           }
         ]'

`,

    Javascript: `async function sendRequest() {
  const url = "http://api.concur.live/api/v1/data_principal/add_bulk?api_key=${apiKey}";

  const data = [
   {
          "dp_system_id": "122114454",
          "dp_identifiers": ["email", "mobile number"],
          "dp_email": "example@example.com",
          "dp_mobile": 1234567890,
          "dp_preferred_lang": ["hi"],
          "dp_country": "India",
          "dp_state": "Maharashtra",
          "dp_persona": "customer",
          "dp_tags": ["inactive", "2024"],
          "dp_active_devices": ["app", "website"],
          "is_active": false,
          "is_legacy": true,
          "created_at_df": "2025-03-01T13:25:26.556000Z",
          "last_activity": "2025-03-31T13:25:26.556000Z"
     }
  ];

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(HTTP error! status: \${response.status});
    }
    
    const result = await response.json();
    console.log("Success:", result);
  } catch (error) {
    console.error("Error:", error);
  }
}

sendRequest();
`,

    Python: `import requests
import json

url = "http://api.concur.live/api/v1/data_principal/add_bulk?api_key=${apiKey}"
headers = {"Content-Type": "application/json"}
data = [
    {
             "dp_system_id": "122114454",
             "dp_identifiers": ["email", "mobile number"],
             "dp_email": "example@example.com",
             "dp_mobile": 1234567890,
             "dp_preferred_lang": ["hi"],
             "dp_country": "India",
             "dp_state": "Maharashtra",
             "dp_persona": "customer",
             "dp_tags": ["inactive", "2024"],
             "dp_active_devices": ["app", "website"],
             "is_active": false,
             "is_legacy": true,
             "created_at_df": "2025-03-01T13:25:26.556000Z",
             "last_activity": "2025-03-31T13:25:26.556000Z"
           }
]

try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()
    print("Success:", response.json())
except requests.exceptions.RequestException as e:
    print("Error:", e)

  `,

    Java: `import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class Main {
    public static void main(String[] args) {
        String url = "http://api.concur.live/api/v1/data_principal/add_bulk?api_key=${apiKey}";
                String json = "[ { " +
                      "\"dp_system_id\": \"122114454\", " +
                      "\"dp_identifiers\": [\"email\", \"mobile number\"], " +
                      "\"dp_email\": \"example@example.com\", " +
                      "\"dp_mobile\": 1234567890, " +
                      "\"dp_preferred_lang\": [\"hi\"], " +
                      "\"dp_country\": \"India\", " +
                      "\"dp_state\": \"Maharashtra\", " +
                      "\"dp_persona\": \"customer\", " +
                      "\"dp_tags\": [\"inactive\", \"2024\"], " +
                      "\"dp_active_devices\": [\"app\", \"website\"], " +
                      "\"is_active\": false, " +
                      "\"is_legacy\": true, " +
                      "\"created_at_df\": \"2025-03-01T13:25:26.556000Z\", " +
                      "\"last_activity\": \"2025-03-31T13:25:26.556000Z\" " +
                      "} ]";

        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                .uri(new URI(url))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

            if (response.statusCode() < 200 || response.statusCode() >= 300) {
                System.err.println("HTTP error code: " + response.statusCode());
            } else {
                System.out.println("Success: " + response.body());
            }
        } catch (Exception e) {
            System.err.println("Error during request: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

  `,

    "C#": `using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

class Program {
    static async Task Main() {
        string url = "http://api.concur.live/api/v1/data_principal/add_bulk?api_key=${apiKey}";
        var json = "[ { " +
                   "\"dp_system_id\": \"122114454\", " +
                   "\"dp_identifiers\": [\"email\", \"mobile number\"], " +
                   "\"dp_email\": \"example@example.com\", " +
                   "\"dp_mobile\": 1234567890, " +
                   "\"dp_preferred_lang\": [\"hi\"], " +
                   "\"dp_country\": \"India\", " +
                   "\"dp_state\": \"Maharashtra\", " +
                   "\"dp_persona\": \"customer\", " +
                   "\"dp_tags\": [\"inactive\", \"2024\"], " +
                   "\"dp_active_devices\": [\"app\", \"website\"], " +
                   "\"is_active\": false, " +
                   "\"is_legacy\": true, " +
                   "\"created_at_df\": \"2025-03-01T13:25:26.556000Z\", " +
                   "\"last_activity\": \"2025-03-31T13:25:26.556000Z\" " +
                   "} ]";

        try {
            using (HttpClient client = new HttpClient()) {
                var content = new StringContent(json, Encoding.UTF8, "application/json");
                HttpResponseMessage response = await client.PostAsync(url, content);

                if (!response.IsSuccessStatusCode) {
                    Console.Error.WriteLine($"HTTP error: {response.StatusCode}");
                } else {
                    string responseString = await response.Content.ReadAsStringAsync();
                    Console.WriteLine("Success: " + responseString);
                }
            }
        } catch (Exception ex) {
            Console.Error.WriteLine("Error during request: " + ex.Message);
        }
    }
}

  `,

    Go: `package main

import (
    "bytes"
    "fmt"
    "io/ioutil"
    "log"
    "net/http"
)

func main() {
    url := "http://api.concur.live/api/v1/data_principal/add_bulk?api_key=${apiKey}"
    jsonStr := \`[{
             "dp_system_id": "122114454",
             "dp_identifiers": ["email", "mobile number"],
             "dp_email": "example@example.com",
             "dp_mobile": 1234567890,
             "dp_preferred_lang": ["hi"],
             "dp_country": "India",
             "dp_state": "Maharashtra",
             "dp_persona": "customer",
             "dp_tags": ["inactive", "2024"],
             "dp_active_devices": ["app", "website"],
             "is_active": false,
             "is_legacy": true,
             "created_at_df": "2025-03-01T13:25:26.556000Z",
             "last_activity": "2025-03-31T13:25:26.556000Z"
           }]\`

    req, err := http.NewRequest("POST", url, bytes.NewBuffer([]byte(jsonStr)))
    if err != nil {
        log.Fatalf("Error creating request: %v", err)
    }
    req.Header.Set("Content-Type", "application/json")
    
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        log.Fatalf("Error performing request: %v", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode < 200 || resp.StatusCode >= 300 {
        log.Printf("HTTP error: %s", resp.Status)
    }

    body, err := ioutil.ReadAll(resp.Body)
    if err != nil {
        log.Fatalf("Error reading response: %v", err)
    }
    fmt.Println("Response:", string(body))
}

  `,

    php: `<?php
$url = "http://api.concur.live/api/v1/data_principal/add_bulk?api_key=${apiKey}";
$data = '[ { 
             "dp_system_id": "122114454",
             "dp_identifiers": ["email", "mobile number"],
             "dp_email": "example@example.com",
             "dp_mobile": 1234567890,
             "dp_preferred_lang": ["hi"],
             "dp_country": "India",
             "dp_state": "Maharashtra",
             "dp_persona": "customer",
             "dp_tags": ["inactive", "2024"],
             "dp_active_devices": ["app", "website"],
             "is_active": false,
             "is_legacy": true,
             "created_at_df": "2025-03-01T13:25:26.556000Z",
             "last_activity": "2025-03-31T13:25:26.556000Z"
            } ]';

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    'Content-Type: application/json',
    'Content-Length: ' . strlen($data))
);

$result = curl_exec($ch);
if ($result === false) {
    echo 'cURL Error: ' . curl_error($ch);
} else {
    echo $result;
}
curl_close($ch);
?>

  `,

    Ruby: `require 'net/http'
require 'uri'
require 'json'

begin
  uri = URI.parse("http://api.concur.live/api/v1/data_principal/add_bulk?api_key=${apiKey}")
  header = { "Content-Type" => "application/json" }
  data = [{
    dp_system_id: "122114454",
    dp_identifiers: ["email", "mobile number"],
    dp_email: "example@example.com",
    dp_mobile: 1234567890,
    dp_preferred_lang: ["hi"],
    dp_country: "India",
    dp_state: "Maharashtra",
    dp_persona: "customer",
    dp_tags: ["inactive", "2024"],
    dp_active_devices: ["app", "website"],
    is_active: false,
    is_legacy: true,
    created_at_df: "2025-03-01T13:25:26.556000Z",
    last_activity: "2025-03-31T13:25:26.556000Z"
  }]

  http = Net::HTTP.new(uri.host, uri.port)
  request = Net::HTTP::Post.new(uri.request_uri, header)
  request.body = data.to_json

  response = http.request(request)
  if response.code.to_i >= 200 && response.code.to_i < 300
    puts "Success: #{response.body}"
  else
    puts "HTTP Error #{response.code}: #{response.body}"
  end
rescue StandardError => e
  puts "Error during request: #{e.message}"
end
  `,
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(codeSamples[activeTab]);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy: ", err);
    }
  };

  const getSyntaxLanguage = (lang) => {
    if (lang === "C#") return "csharp";
    if (lang.toLowerCase() === "curl") return "bash";
    return lang.toLowerCase();
  };

  const breadcrumbsProps = {
    path: "/apps/principal-management/import/API",
    skip: "/apps",
  };

  return (
    <div className="w-full">
      <div className="w-full">
        <Header
          title="API"
          subtitle="Upload your customer data using our API"
          breadcrumbsProps={breadcrumbsProps}
        />
      </div>
      <div className="h-0.5 w-full bg-[#FAFAFA] sm:border-t sm:border-[#D7D7D7]"></div>
      <div className="medium-scrollbar relative h-[calc(100vh-153px)] overflow-y-auto">
        <div className="absolute right-5 top-0 z-50 mt-4">
          <Link href="/apps/principal-management/import">
            <Button variant="secondary" className="h-9 px-5">
              Upload
            </Button>
          </Link>
        </div>
        <div className="absolute left-10 top-0 z-50 mt-4">
          <Link
            href="/apps/principal-management/import"
            className="flex w-[30%] cursor-pointer items-center justify-center bg-white"
          >
            <Button variant="back">
              <IoArrowBackOutline /> Back
            </Button>
          </Link>
        </div>

        <div className="rounded-xs shadow-all relative mx-auto flex flex-col items-center justify-center gap-4 p-4">
          <div className="rounded-xs mb-16 w-[650px] border-2 border-dashed border-[#D7D7D7] px-5 py-4">
            <div className="mb-1 flex justify-between">
              {languageTabs.map((lang) => (
                <button
                  key={lang}
                  onClick={() => setActiveTab(lang)}
                  className={`px-4 py-2 text-sm ${
                    activeTab === lang
                      ? "cursor-pointer border-b-2 border-[#175FC9] font-medium text-[#175FC9]"
                      : "border-[#175FC9] text-gray-600 hover:border-b-2"
                  }`}
                >
                  {lang}
                </button>
              ))}
            </div>

            <div className="relative h-[450px] overflow-hidden bg-[#1D1F21]">
              <button
                onClick={handleCopy}
                className="absolute right-0 top-0 flex cursor-pointer items-center gap-2 rounded-bl-xl bg-[#175FC9] px-3 py-2 text-xs text-white hover:bg-[#175FC9]"
              >
                {copied ? "Copied!" : "Copy"} <LuCopy />
              </button>

              <div className="custom-scrollbar h-[450px] w-[600px] overflow-auto overflow-x-hidden">
                <SyntaxHighlighter
                  language={getSyntaxLanguage(activeTab)}
                  style={atomDark}
                  wrapLongLines={false}
                  customStyle={{
                    whiteSpace: "pre",
                    overflowX: "scroll",
                    overflowY: "auto",
                    wordBreak: "normal",
                    minHeight: "100%",
                    fontSize: "12px",
                    scrollbarWidth: "none",
                    msOverflowStyle: "none",
                  }}
                >
                  {codeSamples[activeTab]}
                </SyntaxHighlighter>
              </div>
            </div>

            <p className="mt-5 max-w-xl pb-4 text-sm text-[#4f4f4f]">
              Use the above code snippets to add data principals to your
              application using our API. Make sure to replace{" "}
              <code>api_key</code> with your actual API key. You can find your
              API key in the{" "}
              <Link
                href="/user/principal-management/data-principal/import/api"
                className="text-[#175FC9] underline"
              >
                API Key section
              </Link>
              . If you have any questions, please refer to our{" "}
              <Link
                href="/user/principal-management/data-principal/import/api"
                className="text-[#175FC9] underline"
              >
                documentation
              </Link>
              .
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataPrincipalAPI;
