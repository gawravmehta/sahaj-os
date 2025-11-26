"use client";
import { useCallback, useState } from "react";
import { FiUploadCloud } from "react-icons/fi";
import { AiOutlineDelete } from "react-icons/ai";
import Image from "next/image";
import { useDropzone } from "react-dropzone";
import { IoMdCloseCircle } from "react-icons/io";

const FileUpload = ({
  title = "Drag & drop files or click to browse",
  allowedTypes = ["pdf", "png", "jpg", "jpeg"],
  onFileSelect,
  multiple = false,
  maxSize = 50,
}) => {
  const [files, setFiles] = useState([]);
  const [fileError, setFileError] = useState("");

  const onDrop = useCallback(
    (acceptedFiles, rejectedFiles) => {
      setFileError("");

      if (rejectedFiles.length > 0) {
        const firstRejection = rejectedFiles[0].errors[0];
        if (firstRejection.code === "file-too-large") {
          setFileError(`File size exceeds the limit of ${maxSize}MB`);
        } else if (firstRejection.code === "file-invalid-type") {
          setFileError(
            `File type not allowed. Supported: ${allowedTypes.join(", ")}`
          );
        } else {
          setFileError("Invalid file. Please try again.");
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        const updatedFiles = multiple
          ? [...files, ...acceptedFiles]
          : acceptedFiles;
        setFiles(updatedFiles);

        if (onFileSelect) {
          onFileSelect(multiple ? updatedFiles : acceptedFiles[0]);
        }
      }
    },
    [allowedTypes, multiple, onFileSelect, files, maxSize]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/png": [".png"],
      "image/jpeg": [".jpg", ".jpeg"],
    },
    multiple,
    maxSize: maxSize * 1024 * 1024,
  });

  const handleDelete = (index, e) => {
    e.stopPropagation();
    const updatedFiles = files.filter((_, i) => i !== index);
    setFiles(updatedFiles);

    if (onFileSelect) {
      onFileSelect(multiple ? updatedFiles : null);
    }
  };

  const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  };

  const isSingleFileUpload = !multiple && files.length > 0;

  return (
    <div className="mt-4">
      <div className="flex flex-col">
        <div
          {...getRootProps()}
          className={`flex h-44 cursor-pointer justify-center items-center border-2 border-dashed  p-6 transition-colors ${
            isDragActive
              ? "border-blue-900 bg-[#F9FCFF]"
              : isSingleFileUpload
              ? "border-[#C7CFE2] bg-[#F9FCFF]"
              : "border-[#C7CFE2] bg-[#F9FCFF]"
          }`}
        >
          <input {...getInputProps()} />

          {isSingleFileUpload ? (
            <div className="flex flex-col items-center justify-center w-full h-full">
              {["png", "jpg", "jpeg"].includes(
                files[0].name.split(".").pop().toLowerCase()
              ) ? (
                <div className="relative w-20 h-20 mb-2">
                  <Image
                    src={URL.createObjectURL(files[0])}
                    alt={files[0].name}
                    fill
                    className="object-contain "
                  />
                </div>
              ) : (
                <div className="w-16 h-16 flex items-center justify-center bg-[#F9FCFF]  mb-2">
                  <span className="text-xs font-bold text-gray-600">
                    .{files[0].name.split(".").pop().toLowerCase()}
                  </span>
                </div>
              )}

              <div className="text-center max-w-full">
                <p
                  className="text-sm font-medium text-gray-700 truncate"
                  title={files[0].name}
                >
                  {files[0].name}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {formatBytes(files[0].size)}
                </p>
                <p className="text-xs text-gray-400 mt-2">
                  Click or drag to replace file
                </p>
              </div>

              <button
                onClick={(e) => handleDelete(0, e)}
                className=" text-red-500 p-1 cursor-pointer  transition-colors "
                aria-label="Delete file"
              >
                <AiOutlineDelete size={16} />
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center text-center">
              <FiUploadCloud size={32} className="text-gray-400 mb-2" />
              <div className="text-sm font-medium text-gray-700 mb-1">
                {isDragActive
                  ? "Drop files here"
                  : files.length > 0
                  ? "Add more files"
                  : title}
              </div>
              <p className="text-xs text-gray-500 mb-1">
                Supported: {allowedTypes.join(", ").toUpperCase()}
              </p>
              <p className="text-xs text-gray-400">
                Max file size: {maxSize}MB
              </p>
            </div>
          )}
        </div>

        {multiple && files.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">
              Uploaded Files ({files.length})
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {files.map((file, index) => {
                const fileExtension = file.name.split(".").pop().toLowerCase();
                const isImage = ["png", "jpg", "jpeg"].includes(fileExtension);

                return (
                  <div
                    key={`${file.name}-${index}`}
                    className="relative flex flex-col items-center border-2 border-dashed border-[#C7CFE2] bg-[#F9FCFF] p-3 "
                  >
                    {isImage ? (
                      <div className="w-16 h-16 relative mb-2">
                        <Image
                          src={URL.createObjectURL(file)}
                          alt={file.name}
                          fill
                          className="object-contain rounded"
                        />
                      </div>
                    ) : (
                      <div className="w-16 h-16 flex items-center justify-center  mb-2">
                        <span className="text-xs font-bold text-gray-600">
                          .{fileExtension}
                        </span>
                      </div>
                    )}

                    <div className="w-full text-center">
                      <p
                        className="text-xs font-medium text-gray-700 truncate mb-1"
                        title={file.name}
                      >
                        {file.name}
                      </p>
                      <p className="text-[11px] text-gray-500">
                        {formatBytes(file.size)}
                      </p>
                    </div>

                    <button
                      onClick={(e) => handleDelete(index, e)}
                      className="absolute -top-2 -right-2  text-red-500 cursor-pointer"
                      aria-label="Delete file"
                    >
                      <IoMdCloseCircle size={16} />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {fileError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 ">
            <p className="text-xs text-red-600 flex items-center">
              <svg
                className="w-4 h-4 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              {fileError}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
