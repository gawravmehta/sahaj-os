import Button from "@/components/ui/Button";
import { SelectInput } from "@/components/ui/Inputs";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";

import Cookies from "js-cookie";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { BsFiletypeCsv, BsFiletypeXlsx } from "react-icons/bs";
import { FiDownload } from "react-icons/fi";
import { IoClose } from "react-icons/io5";

const ExportModal = ({ closeModal }) => {
  const accessToken = Cookies.get("access_token");
  const [selectedFormat, setSelectedFormat] = useState("");
  const [allTags, setAllTags] = useState([]);
  const [selectedTags, setSelectedTags] = useState([]);

  const [selectedMatchType, setSelectedMatchType] = useState("");

  const matchTypeOptions = [
    { label: "Contains All", value: "contains all" },
    { label: "Contains Any", value: "contains any" },
  ];

  const getAllTags = async () => {
    try {
      const response = await apiCall("/data-principal/get-all-dp-tags");
      setAllTags(response.dp_tags || []);
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error(error);
    }
  };

  useEffect(() => {
    getAllTags();
  }, []);

  const bulkExportDataPrincipal = async () => {
    if (!selectedFormat) {
      toast.error("Please select a format");
      return;
    }

    try {
      const url = new URL(
        `${process.env.NEXT_PUBLIC_API_URL}/dp-bulk-internal/bulk-export-data-principal`
      );
      url.searchParams.append("format", selectedFormat);
      url.searchParams.append("match_type", selectedMatchType);
      selectedTags.forEach((tag) => url.searchParams.append("tags", tag));

      const response = await fetch(url.toString(), {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        let errorMessage = response.statusText;
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorMessage;
        } catch (e) {}
        throw new Error(errorMessage);
      }

      const blob = await response.blob();
      const urlBlob = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = urlBlob;
      link.download = `data_principals_exports.${selectedFormat}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      toast.success("File downloaded successfully!");
      closeModal();
    } catch (error) {
      console.error("Error downloading file:", error);
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  const tagOptions = allTags.map((tag) => ({
    label: tag.charAt(0).toUpperCase() + tag.slice(1),
    value: tag,
  }));

  return (
    <div
      onClick={closeModal}
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/70 "
    >
      <div
        className="relative h-[430px] w-[536px] border border-[#c7cfe2] bg-white py-6 shadow-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <Button
          variant="cancel"
          className="absolute right-5 top-4 p-0.5"
          onClick={closeModal}
        >
          <IoClose size={30} />
        </Button>

        <h1 className="px-6 text-center text-3xl">Export Table</h1>
        <p className="mt-1 px-6 text-center text-sm text-subHeading">
          Select a file format and click download to export your table data.
        </p>

        <div className="mt-6 flex justify-center gap-10 px-6">
          <div className="">
            <button
              className={`flex h-36 w-36 flex-col items-center justify-center border p-4 transition ${
                selectedFormat === "csv"
                  ? "border-primary"
                  : "border-[#c7cfe2] hover:border-hover"
              }`}
              onClick={() => setSelectedFormat("csv")}
            >
              <BsFiletypeCsv size={40} className="text-green-500" />
            </button>
            <p className="mt-2 text-center font-medium">CSV</p>
          </div>

          <div className="">
            <button
              className={`flex h-36 w-36 flex-col items-center justify-center border p-4 transition ${
                selectedFormat === "xlsx"
                  ? "border-primary"
                  : "border-[#c7cfe2] hover:border-hover"
              }`}
              onClick={() => setSelectedFormat("xlsx")}
            >
              <BsFiletypeXlsx size={40} className="text-green-500" />
            </button>
            <p className="mt-2 text-center font-medium">XLSX</p>
          </div>
        </div>
        <div className="mt-8 flex justify-center w-full px-6 gap-4">
          <SelectInput
            options={tagOptions}
            value={tagOptions.filter((option) =>
              selectedTags.includes(option.value)
            )}
            onChange={(selectedOptions) => {
              const values = selectedOptions
                ? selectedOptions.map((opt) => opt.value)
                : [];
              setSelectedTags(values);
            }}
            placeholder="Select Tags"
            isMulti
            className="w-64 text-sm"
          />
          <SelectInput
            options={matchTypeOptions}
            value={
              matchTypeOptions.find(
                (option) => option.value === selectedMatchType
              ) || null
            }
            onChange={(selectedOption) => {
              setSelectedMatchType(selectedOption ? selectedOption.value : "");
            }}
            placeholder="Select Match Type"
            className="w-40 text-sm"
          />
        </div>

        <div className="relative mt-8 border-t border-[#d7d7d7] px-6 pt-4">
          <span className="absolute right-3 top-1/2 flex gap-3.5">
            <Button variant="cancel" className="px-3" onClick={closeModal}>
              Cancel
            </Button>
            <Button
              variant="primary"
              disabled={!selectedFormat}
              onClick={bulkExportDataPrincipal}
              className="px-4"
            >
              <span className="mr-2">
                <FiDownload size={20} />
              </span>
              Download
            </Button>
          </span>
        </div>
      </div>
    </div>
  );
};

export default ExportModal;
