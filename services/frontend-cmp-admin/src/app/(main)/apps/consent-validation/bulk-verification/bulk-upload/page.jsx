"use client";
import React, { useState } from "react";

import Header from "@/components/ui/Header";

import { uploadFile } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import BulkVerifyUpload from "@/components/features/consentValidation/BulkVerifyUpload";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { useRouter } from "next/navigation";

const Page = () => {
  const router = useRouter();

  const [uploadComplete, setUploadComplete] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);

  const breadcrumbsProps = {
    path: "/apps/consent-validation/bulk-verification/bulk-upload",
    skip: "/apps/consent-validation",
  };

  const handleFileUpload = async () => {
    if (!uploadedFiles || uploadedFiles.length === 0) {
      toast.error("Please select a file to upload.");
      return;
    }

    const fileObj = uploadedFiles[0];
    const file = fileObj.file;

    if (!(file instanceof File)) {
      console.error("Selected file is not valid:", file);
      toast.error("Invalid file format. Please try again.");
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await uploadFile(
        `/consent-validation/bulk-verify-consent-internal`,
        formData,
        (progress) => setUploadProgress(progress)
      );

      toast.success("File uploaded successfully!");
      router.push(
        "/apps/consent-validation/bulk-verification/previously-uploaded"
      );

      setUploadComplete(true);
      setUploadedFiles([]);
    } catch (error) {
      console.error("Error during bulk verification:", error);
      toast.error(error.message || "Failed to upload file. Please try again.");
    } finally {
      setUploading(false);
    }
  };
  return (
    <div>
      <div className="w-full border-b sm:border-borderheader">
        <Header
          title="Import Bulk Verification"
          subtitle="Upload your customer's data here."
          breadcrumbsProps={breadcrumbsProps}
        />
      </div>
      <div className="flex w-full justify-center gap-8 pt-5">
        <div className="h-full w-[35%]">
          <BulkVerifyUpload
            uploadedFiles={uploadedFiles}
            setUploadedFiles={setUploadedFiles}
            uploading={uploading}
            uploadProgress={uploadProgress}
          />
        </div>
      </div>
      {!uploadComplete && (
        <StickyFooterActions
          onCancelHref="/apps/consent-validation/bulk-verification"
          onSubmit={handleFileUpload}
          disableSubmit={uploadedFiles.length === 0 || uploading}
          submitLabel={uploading ? "Uploading..." : "Upload"}
          className="shadow-xl"
        />
      )}
    </div>
  );
};

export default Page;
