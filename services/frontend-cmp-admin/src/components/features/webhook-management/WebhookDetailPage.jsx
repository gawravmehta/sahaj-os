"use client";
import { useState } from "react";

const useIdStub = () => ({ id: "68dbb7fbe4e540b68fd01000" });
const useParams =
  typeof window !== "undefined" &&
  window.location.pathname.includes("/webhooks/")
    ? useIdStub
    : useIdStub;

export const CopyToClipboard = ({ value }) => {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    const tempTextArea = document.createElement("textarea");
    tempTextArea.value = value;
    document.body.appendChild(tempTextArea);
    tempTextArea.select();
    try {
      document.execCommand("copy");
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text", err);
    } finally {
      document.body.removeChild(tempTextArea);
    }
  };

  return (
    <button
      onClick={handleCopy}
      className="ml-2 px-2 py-1 text-xs font-medium rounded-full text-primary hover:bg-primary/10 border transition duration-150 ease-in-out whitespace-nowrap"
      aria-label={copied ? "Copied successfully" : "Copy to clipboard"}
    >
      {copied ? "Copied 🎉" : "Copy"}
    </button>
  );
};

export const DetailItem = ({
  label,
  value,
  isLink = false,
  isSecret = false,
  isCopyable = false,
  isMonospace = false,
  isValueHighlight = false,
}) => {
  const displayValue =
    value !== undefined && value !== null && value !== ""
      ? value.toString()
      : "N/A";
  let valueClasses = "text-gray-900 text-base break-all";
  if (isMonospace || isSecret) {
    valueClasses +=
      " font-mono text-sm bg-gray-100  p-2 rounded-lg tracking-wider";
  }
  if (isValueHighlight) {
    valueClasses = "font-extrabold text-2xl text-primary";
  }
  if (isLink) {
    valueClasses += " text-blue-600 hover:text-blue-700 hover:underline";
  }

  const maskedValue = isSecret ? "••••••••••••••••••••••••" : displayValue;
  const copyValue = displayValue;

  return (
    <div className="flex flex-col space-y-1">
      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
        {label}
      </span>
      <div
        className={`flex items-center justify-between ${
          isMonospace || isSecret ? "rounded-lg bg-gray-100" : ""
        }`}
      >
        {isLink && value ? (
          <a
            href={value}
            target="_blank"
            rel="noopener noreferrer"
            className={`${valueClasses} grow min-w-0 truncate`}
            title={value}
          >
            {value}
          </a>
        ) : (
          <span
            className={`${valueClasses} grow min-w-0 ${
              isMonospace || isSecret ? "p-2" : ""
            }`}
            title={isSecret ? "Click copy to view secret" : undefined}
          >
            {maskedValue}
          </span>
        )}
        {(isCopyable || isSecret) && copyValue !== "N/A" && (
          <div className={`${isMonospace || isSecret ? "p-1" : ""}`}>
            <CopyToClipboard value={copyValue} />
          </div>
        )}
      </div>
    </div>
  );
};

export const MetricItem = ({
  label,
  value,
  isSuccess = false,
  isFailure = false,
  dateTime = null,
}) => {
  let icon = (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className="h-6 w-6"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M13 10V3L4 14h7v7l9-11h-7z"
      />
    </svg>
  );
  let bgColor = "bg-white border border-gray-200 text-gray-800";
  let textColor = "text-gray-900";

  if (isSuccess) {
    bgColor = "bg-green-50 border border-green-200";
    textColor = "text-green-600";
    icon = (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    );
  } else if (isFailure) {
    bgColor = "bg-red-50 border border-red-200";
    textColor = "text-red-600";
    icon = (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    );
  }

  return (
    <div className={`flex flex-col p-5 border`}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold uppercase text-gray-500 tracking-wider">
          {label}
        </span>
        <div className={textColor}>{icon}</div>
      </div>
      <span className={`text-4xl font-extrabold text-primary mt-2`}>
        {value?.toLocaleString()}
      </span>
      {dateTime && (
        <span className="text-xs text-gray-400 mt-2">
          {dateTime !== "N/A" ? `Last: ${dateTime}` : ""}
        </span>
      )}
    </div>
  );
};

export const formatDateTime = (dateString) => {
  if (!dateString) return "N/A";
  try {
    const date = new Date(dateString.$date || dateString);
    return date?.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    });
  } catch (error) {
    return "Invalid Date";
  }
};

export const eventColor = (event) => {
  const lower = event.toLowerCase();
  if (lower.includes("granted") || lower.includes("validated"))
    return "bg-green-100 text-green-700 hover:bg-green-200";
  if (lower.includes("withdrawn") || lower.includes("expired"))
    return "bg-red-100 text-red-700 hover:bg-red-200";
  if (lower.includes("updated") || lower.includes("renewed"))
    return "bg-yellow-100 text-yellow-700 hover:bg-yellow-200";
  if (lower.includes("erasure") || lower.includes("grievance"))
    return "bg-purple-100 text-purple-700 hover:bg-purple-200";
  return "bg-slate-100 text-slate-700 hover:bg-slate-200";
};

export const getStatusBadge = (status) => {
  const baseStyle = "px-4 py-1 text-base font-bold rounded-full capitalize";
  switch (status?.toLowerCase()) {
    case "active":
      return (
        <span className={`${baseStyle} bg-green-500 text-white shadow-lg`}>
          Active
        </span>
      );
    case "disabled":
      return (
        <span className={`${baseStyle} bg-red-500 text-white shadow-lg`}>
          Disabled
        </span>
      );
    case "pending":
      return (
        <span className={`${baseStyle} bg-yellow-500 text-white shadow-lg`}>
          Pending
        </span>
      );
    default:
      return (
        <span className={`${baseStyle} bg-gray-500 text-white shadow-lg`}>
          {status || "N/A"}
        </span>
      );
  }
};
