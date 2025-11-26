"use client";
import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Header from "@/components/ui/Header";
import { apiCall } from "@/hooks/apiCall";
import React, { useEffect, useState } from "react";
import { FiDownload } from "react-icons/fi";

import toast from "react-hot-toast";
import Image from "next/image";
import Skeleton from "@/components/ui/Skeleton";
import { getErrorMessage } from "@/utils/errorHandler";

const Page = () => {
  const [prevUploadedFiles, setPrevUploadedFiles] = useState([]);
  const [downloadTypes, setDownloadTypes] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    handleGetUploadedFiles();
  }, []);

  const breadcrumbsProps = {
    path: "/apps/consent-validation/bulk-verification/previously-uploaded",
    skip: "/apps/consent-validation",
  };

  const handleGetUploadedFiles = async () => {
    setLoading(true);
    try {
      const response = await apiCall(
        "/consent-validation/get-all-uploaded-verification-files"
      );
      setPrevUploadedFiles(response);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching uploaded files:", error);
      setLoading(false);
    }
  };

  const handleDownload = async (fileToDownload, type) => {
    try {
      const response = await apiCall(
        `/consent-validation/download-verified-file?file_name=${fileToDownload}&download_type=${type}`
      );

      if (!response.ok) {
        throw new Error("Failed to download file");
      }

      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);

      const contentDisposition = response.headers.get("content-disposition");
      let filename = `verification_logs.${type}`;

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      }

      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      toast.error(getErrorMessage(error) || "Download failed");
    }
  };

  const handleTypeChange = (filename, type) => {
    setDownloadTypes((prev) => ({
      ...prev,
      [filename]: type,
    }));
  };

  const truncateCenter = (str, frontLen = 5, backLen = 5) => {
    if (!str) return "";
    if (str.length <= frontLen + backLen) return str;
    return `${str.slice(0, frontLen)}...${str.slice(-backLen)}`;
  };

  return (
    <div>
      <div className="w-full border-b sm:border-borderheader">
        <Header
          title="Previously Uploaded"
          subtitle="Review your uploaded files with status indicators. Check upload time or download them anytime."
          breadcrumbsProps={breadcrumbsProps}
        />
      </div>
      {loading ? (
        <div className="grid grid-cols-4 gap-4 p-6">
          <Skeleton variant="Box" className={"h-20"} />
          <Skeleton variant="Box" className={"h-20"} />
          <Skeleton variant="Box" className={"h-20"} />
          <Skeleton variant="Box" className={"h-20"} />
          <Skeleton variant="Box" className={"h-20"} />
          <Skeleton variant="Box" className={"h-20"} />
          <Skeleton variant="Box" className={"h-20"} />
        </div>
      ) : prevUploadedFiles.length === 0 ? (
        <div className="flex min-h-[calc(100vh-250px)] items-center justify-center">
          <div className="flex flex-col items-center justify-center">
            <div className="w-52">
              <Image
                height={200}
                width={200}
                src="/data-element/business.png"
                alt="Circle Image"
                className="h-full w-full object-cover"
              />
            </div>
            <div>
              <p className="mt-2 text-subText">No file added yet</p>
            </div>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-4 gap-4 p-6">
          {prevUploadedFiles.map((item, i) => (
            <div
              key={i}
              className="relative flex items-center gap-5 bg-white px-4 py-2.5 shadow"
            >
              <div className="w-full">
                {truncateCenter(item.filename, 8, 8)}

                <div className="mt-1 flex w-full items-center justify-between gap-2">
                  <DateTimeFormatter
                    dateTime={item.created_at}
                    className="flex gap-1 text-[10px] text-subText"
                  />
                  <div className="flex items-center gap-2">
                    
                    <FiDownload
                      className={`${
                        item.status === "completed"
                          ? "cursor-pointer text-black"
                          : "cursor-not-allowed opacity-50"
                      }`}
                      onClick={() => {
                        if (item.status === "completed") {
                          handleDownload(
                            item.filename,
                            downloadTypes[item.filename] || "csv"
                          );
                        }
                      }}
                    />

                    <div className="flex w-max overflow-hidden border border-[#C3C8D1] text-sm font-medium">
                      <button
                        className={`px-3 py-1 ${
                          (downloadTypes[item.filename] || "csv") === "json"
                            ? "bg-[#D1E7FF] text-black"
                            : "bg-white text-black"
                        }`}
                        onClick={() => handleTypeChange(item.filename, "json")}
                      >
                        JSON
                      </button>
                      <button
                        className={`px-3 py-1 ${
                          (downloadTypes[item.filename] || "csv") === "csv"
                            ? "bg-[#D1E7FF] text-black"
                            : "bg-white text-black"
                        }`}
                        onClick={() => handleTypeChange(item.filename, "csv")}
                      >
                        CSV
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <div className="group absolute right-4 top-2">
                <div
                  className={`size-2.5 rounded-full ${
                    item.status === "completed"
                      ? "bg-green-600"
                      : item.status === "pending"
                      ? "bg-yellow-500"
                      : "bg-red-800"
                  }`}
                />
                <div className="pointer-events-none absolute -right-16 -top-7 z-10 hidden whitespace-nowrap border border-borderSecondary bg-slate-50 px-2 py-1 text-xs text-black group-hover:block">
                  {item.status}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Page;
