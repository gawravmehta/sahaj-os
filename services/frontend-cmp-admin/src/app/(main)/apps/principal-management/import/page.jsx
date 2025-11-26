"use client";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import { addNewTags, uploadFile } from "@/hooks/apiCall";
import Link from "next/link";
import { useState } from "react";
import toast from "react-hot-toast";
import { IoArrowBack } from "react-icons/io5";
import BulkAddDP from "./BulkAddDP";
import { getErrorMessage } from "@/utils/errorHandler";
import StickyFooterActions from "@/components/ui/StickyFooterActions";

const FileImport = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadComplete, setUploadComplete] = useState(false);
  const [tags, setTags] = useState([]);
  const [tagOptions, setTagOptions] = useState([]);
  const [isLegacy, setIsLegacy] = useState(true);
  const [selectedPersona, setSelectedPersona] = useState([]);
  const [missingFields, setMissingFields] = useState([]);

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
    const formData = new FormData();
    formData.append("file", file);

    let newTags = [];
    if (tags.length > 0) {
      const existingTagLabels = tagOptions.map((t) => t.label);
      newTags = tags.filter((tag) => !existingTagLabels.includes(tag));
      if (newTags.length > 0) {
        addNewTags({ newTags });
      }
    }

    const queryParams = new URLSearchParams();

    selectedPersona.forEach((id) => {
      queryParams.append("persona_id", id);
    });

    queryParams.append("is_legacy", `${isLegacy}`);

    tags.forEach((tag) => {
      queryParams.append("dp_tags", tag);
    });

    const uploadUrl = `/dp-bulk-internal/bulk-import-data-principal?${queryParams.toString()}`;

    try {
      const response = await uploadFile(uploadUrl, formData, setUploadProgress);

      toast.success("File uploaded successfully!");
      setUploadComplete(response?.row_count);
      setUploadedFiles([]);
    } catch (error) {
      console.error("This is error from add DP in Bulk:", error);
      const message = getErrorMessage(error);
      toast.error(message);
    } finally {
      setUploading(false);
    }
  };

  const breadcrumbsProps = {
    path: "/apps/principal-management/import",
    skip: "/apps",
  };

  return (
    <div className="flex">
      <div className="w-full">
        <div className="w-full border-b sm:border-borderheader">
          <Header
            title="Import Data Principal"
            subtitle="Upload your customer's data here."
            breadcrumbsProps={breadcrumbsProps}
          />
        </div>

        <BulkAddDP
          uploadComplete={uploadComplete}
          uploadedFiles={uploadedFiles}
          setUploadedFiles={setUploadedFiles}
          uploadProgress={uploadProgress}
          uploading={uploading}
          tags={tags}
          setTags={setTags}
          tagOptions={tagOptions}
          setTagOptions={setTagOptions}
          isLegacy={isLegacy}
          setIsLegacy={setIsLegacy}
          selectedPersona={selectedPersona}
          setSelectedPersona={setSelectedPersona}
          missingFields={missingFields}
        />
        {!uploadComplete && (
          <StickyFooterActions
            onCancelHref="/apps/principal-management"
            onSubmit={handleFileUpload}
            disableSubmit={uploadedFiles.length === 0 || uploading}
            submitLabel={uploading ? "Uploading..." : "Upload"}
            className="shadow-xl"
          />
        )}
      </div>
    </div>
  );
};

export default FileImport;
