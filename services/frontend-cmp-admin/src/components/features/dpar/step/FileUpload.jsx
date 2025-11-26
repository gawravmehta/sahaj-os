import { useEffect } from "react";
import { FiUploadCloud } from "react-icons/fi";
import { AiOutlineDelete } from "react-icons/ai";
import Image from "next/image";
import { useDropzone } from "react-dropzone";

const FileUpload = ({
  title,
  fileError,
  setFileError,
  progress,
  setProgress,
  fileName,
  setFileName,
  fileSize,
  setFileSize,
  fileExt,
  setFileExt,
  filePreview,
  setFilePreview,
  index,
  multiple = false,
}) => {
  const allowedFileTypes = ["pdf", "png", "jpg", "jpeg"];

  const onDrop = (acceptedFiles) => {
    if (multiple) {
      const validFiles = acceptedFiles.filter((file) => {
        const fileType = file.name.split(".").pop().toLowerCase();
        return (
          allowedFileTypes.includes(fileType) && file.size <= 50 * 1024 * 1024
        );
      });

      if (validFiles.length === 0) {
        setFileError(true);
        resetFileState();
        return;
      }

      setFileError(false);
      setFilePreview(validFiles);

      if (validFiles.length > 0) {
        const firstFile = validFiles[0];
        setFileName(`${validFiles.length} files selected`);
        setFileSize(
          formatBytes(validFiles.reduce((acc, file) => acc + file.size, 0))
        );
        setFileExt("Multiple");
      }
    } else {
      const file = acceptedFiles[0];
      if (!file) return;

      const fileType = file.name.split(".").pop().toLowerCase();

      if (
        !allowedFileTypes.includes(fileType) ||
        file.size > 50 * 1024 * 1024
      ) {
        setFileError(true);
        resetFileState();
        return;
      }

      setFileError(false);
      setFileName(file.name);
      setFileSize(formatBytes(file.size));
      setFileExt(fileType.toUpperCase());
      setFilePreview(file);
    }
  };

  const handleUpload = () => {
    if (fileName) {
      let uploadProgress = 0;
      const interval = setInterval(() => {
        if (uploadProgress < 100) {
          uploadProgress += 10;
          setProgress(uploadProgress);
        } else {
          clearInterval(interval);
        }
      }, 300);
    }
  };

  const handleDelete = () => {
    resetFileState();
  };

  const resetFileState = () => {
    setFileName("");
    setFileSize("");
    setFileExt("");
    setFilePreview(null);
    setProgress(0);
    setFileError(false);
  };

  const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  };

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    multiple: multiple,
    maxSize: 50 * 1024 * 1024,
  });

  return (
    <div className="mt-6">
      <div className="flex flex-col">
        {!fileName && (
          <div
            {...getRootProps()}
            className="flex h-44 cursor-pointer justify-center border-2 border-dashed border-[#C7CFE2] bg-[#F9FCFF] p-3"
          >
            <input {...getInputProps()} />
            <div className="flex flex-col items-center justify-center text-center">
              <FiUploadCloud size={30} className="text-[#7F7F7F]" />
              <div className="mt-4 text-sm font-medium text-gray-800">
                {title}
              </div>
              <p className="mt-1 text-xs text-gray-400">
                Drag & drop to upload instantly!
              </p>
              <p className="mt-1 text-[10px] text-gray-400">
                Supported: pdf, png, jpg (max 50MB)
              </p>
            </div>
          </div>
        )}

        {fileName && !fileError && (
          <div className="flex h-44 flex-col items-center justify-center border-2 border-dashed border-[#C7CFE2] bg-[#F9FCFF] p-3">
            <p className="text-center text-sm font-medium text-heading">
              {fileName}
            </p>
            <p className="text-xs text-gray-500">{fileSize}</p>

            {progress === 100 && filePreview && !multiple ? (
              <div className="mt-2">
                {["png", "jpg", "jpeg"].includes(fileExt.toLowerCase()) ? (
                  <Image
                    src={URL.createObjectURL(filePreview)}
                    alt="File Preview"
                    width={40}
                    height={40}
                    className="object-contain"
                  />
                ) : (
                  <div className="flex items-center justify-center">
                    <span className="text-xs">PDF File</span>
                  </div>
                )}
              </div>
            ) : progress === 100 && multiple && filePreview?.length > 0 ? (
              <div className="mt-2">
                <p className="text-xs">{filePreview.length} files selected</p>
              </div>
            ) : (
              <div className="mt-2 h-3 w-full overflow-hidden rounded-full bg-gray-200">
                <div
                  className="relative h-full bg-blue-600 transition-all duration-300 ease-in-out"
                  style={{ width: `${progress}%` }}
                >
                  <span className="absolute inset-0 flex items-center justify-center text-[10px] font-medium text-white">
                    {progress}%
                  </span>
                </div>
              </div>
            )}

            {progress === 100 ? (
              <button onClick={handleDelete} className="mt-3 px-4 py-1">
                <AiOutlineDelete className="size-6 text-red-600" />
              </button>
            ) : (
              <button
                onClick={handleUpload}
                className="mt-5 bg-blue-600 px-4 py-1 text-white"
              >
                Upload
              </button>
            )}
          </div>
        )}

        {fileError && (
          <p className="mt-4 text-xs text-red-500">
            Invalid file type or size exceeded (max 50MB).
          </p>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
