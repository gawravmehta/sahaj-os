"use client";
import CircleProgressBar from "@/components/features/principalManagement/import/CircleProgressBar";
import { apiCall } from "@/hooks/apiCall";
import { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";
import { AiOutlineDelete } from "react-icons/ai";
import { BsFiletypeCsv, BsFiletypeXlsx } from "react-icons/bs";
import { FiUploadCloud } from "react-icons/fi";
import { PiDownloadSimple } from "react-icons/pi";
import { getErrorMessage } from "@/utils/errorHandler";
import Button from "@/components/ui/Button";
import { SelectInput, TagInput } from "@/components/ui/Inputs";
import YesNoToggle from "@/components/ui/YesNoToggle";

const UploadFile = ({
  dataFields,
  setUploadedFiles,
  uploadedFiles,
  uploadProgress,
  uploading,
  tags,
  setTags,
  tagOptions,
  setTagOptions,
  isLegacy,
  setIsLegacy,
  pathname,
  selectedPersona,
  setSelectedPersona,
  missingFields,
}) => {
  const supportedFileTypes = dataFields?.[0]?.supported_format || [];
  const maxFiles = dataFields?.[0]?.number_files || 1;
  const [personaData, setPersonaData] = useState("");

  const acceptedFileTypes = supportedFileTypes.reduce((acc, type) => {
    switch (type) {
      case "csv":
        acc["text/csv"] = [".csv"];
        break;
      case "xlsx":
        acc[
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ] = [".xlsx"];
        break;
      default:
        break;
    }
    return acc;
  }, {});

  useEffect(() => {
    return () => {
      uploadedFiles.forEach(({ preview }) => URL.revokeObjectURL(preview));
    };
  }, [uploadedFiles]);

  const onDrop = useCallback(
    (acceptedFiles) => {
      if (uploadedFiles.length + acceptedFiles.length > maxFiles) {
        toast.error(`You can only upload up to ${maxFiles} files at a time.`);
        return;
      }
      const newFiles = acceptedFiles.map((file) => ({
        file,
        preview: URL.createObjectURL(file),
        id: `${file.name}-${file.size}-${file.lastModified}-${Date.now()}`,
      }));
      setUploadedFiles((prev) => [...prev, ...newFiles]);
    },
    [uploadedFiles, maxFiles, setUploadedFiles]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject, open } =
    useDropzone({
      onDrop,
      accept: acceptedFileTypes,
      multiple: true,
      noClick: true,
      noKeyboard: true,
    });

  const handleDelete = (id) => {
    setUploadedFiles((prev) => prev.filter((file) => file.id !== id));
  };

  const handleDownloadTemplate = () => {
    const headers = [
      "dp_system_id",
      "dp_identifiers",
      "dp_email",
      "dp_mobile",
      "dp_other_identifier",
      "dp_preferred_lang",
      "dp_country",
      "dp_state",
      "dp_active_devices",
      "is_active",
      "created_at_df",
      "last_activity",
      "dp_tags",
    ];

    const numberOfEmptyRows = 5;
    const emptyRows = Array.from({ length: numberOfEmptyRows }, () =>
      headers.map(() => "").join(",")
    );

    const csvContent = headers.join(",") + "\n" + emptyRows.join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "dp_template.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleLegacyChange = () => {
    setIsLegacy((prevState) => !prevState);
  };

  return (
    <div className="mx-auto h-full w-full rounded-md pb-5">
      {!uploading && uploadedFiles.length <= 0 && (
        <div>
          <div
            {...getRootProps()}
            className={`flex flex-col items-center justify-between rounded-md border-2 border-dashed bg-[#F9FCFF] p-8 transition-colors duration-200 ${
              isDragActive ? "border-[#f2f9ff] bg-[#f2f9ff]" : "border-gray-300"
            } ${isDragReject ? "border-red-500 bg-red-300 text-white" : ""}`}
          >
            <input {...getInputProps({ accept: ".csv, .xlsx" })} />
            <FiUploadCloud size={52} className="text-gray-600" />
            <p className="mt-5 text-center text-lg text-gray-700">
              {isDragActive
                ? "Drop the files here..."
                : "Drag and Drop file to upload"}
            </p>

            <p className="py-3">or</p>
            <Button
              variant="primary"
              className="w-48 cursor-pointer text-nowrap py-2"
              onClick={open}
            >
              Browse File
            </Button>
            <p className="mt-2 text-xs text-gray-500">
              Supported Files : - CSV, XLSX Upto 30 Mb
              {supportedFileTypes.join(", ")}
            </p>
          </div>
          <div className="flex w-full justify-end pt-3">
            <Button
              variant="back"
              onClick={handleDownloadTemplate}
              className="flex cursor-pointer items-center justify-end gap-2 pl-4 text-xs font-normal"
            >
              Download Template <PiDownloadSimple size={16} />
            </Button>
          </div>
        </div>
      )}

      {!uploading && uploadedFiles.length > 0 && (
        <>
          <div className="mt-4">
            <div className="flex max-h-52 flex-col gap-2 overflow-y-auto">
              {uploadedFiles.map(({ file, id }) => (
                <div
                  key={id}
                  className="flex h-[250px] flex-col items-center justify-center rounded border-2 border-dashed border-gray-300 bg-[#F9FCFF] transition-colors duration-200"
                >
                  <div className="flex flex-col items-center justify-center gap-4">
                    {file.type === "text/csv" ? (
                      <BsFiletypeCsv size={42} className="text-green-500" />
                    ) : (
                      <BsFiletypeXlsx size={42} className="text-green-500" />
                    )}

                    <div>
                      <p className="line-clamp-1 py-2 text-base font-medium text-black">
                        {file.name}
                      </p>
                      <p className="text-center text-xs text-gray-500">
                        <span className="text-sm font-medium text-gray-700">
                          Size :{" "}
                        </span>
                        {(file.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="deleteIcon"
                    className="mt-2"
                    onClick={() => handleDelete(id)}
                  >
                    <AiOutlineDelete size={20} className="" />
                  </Button>
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-4 pt-5">
            {[{ label: "Is legacy customer?", name: "isLegacy" }].map(
              ({ label, name }) => (
                <YesNoToggle
                  key={name}
                  name={name}
                  label={label}
                  value={isLegacy}
                  onChange={(field, value) => setIsLegacy(value)}
                />
              )
            )}

            <TagInput
              name="tags"
              tags={tags}
              setTags={setTags}
              setTagOptions={setTagOptions}
              tagOptions={tagOptions}
              missingFields={missingFields}
              label="Tags"
              placeholder="Add Tags"
              tooltipText="Add tags to the customer"
            />
          </div>
        </>
      )}

      {uploading && (
        <div className="flex flex-col items-center justify-center rounded border-2 border-dashed border-gray-300 bg-[#F9FCFF]">
          <div className="flex flex-col items-center justify-center p-20">
            <CircleProgressBar score={uploadProgress} />

            <h1 className="mt-20">Loading...</h1>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadFile;
