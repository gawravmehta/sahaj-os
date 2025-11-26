import Button from "@/components/ui/Button";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { useState } from "react";
import toast from "react-hot-toast";
import { RxCross2 } from "react-icons/rx";

const BulkDpDeleteModal = ({
  closeModal,
  selectedTags,
  setSelectedTags,
  getAllDataPrincipals,
}) => {
  const [dpDeleteType, setDpDeleteType] = useState(null);

  const handleDeleteDp = async () => {
    if (!dpDeleteType) {
      toast.error("Please select a delete option");
      return;
    }

    if (selectedTags.length === 0) {
      toast.error("Please select at least one tag");
      return;
    }

    try {
      const queryParams = new URLSearchParams();
      selectedTags.forEach((tag) => queryParams.append("tags", tag));
      queryParams.append("match_type", dpDeleteType);

      const response = await apiCall(
        `/dp-bulk-internal/delete-data-principals-by-tags?${queryParams.toString()}`,
        {
          method: "DELETE",
          headers: {
            accept: "application/json",
          },
        }
      );

      toast.success("Data Principals deleted successfully!");
      setDpDeleteType(null);
      setSelectedTags([]);
      closeModal();
      getAllDataPrincipals();
    } catch (error) {
      console.error(error);
      toast.error(getErrorMessage(error));
      setDpDeleteType(null);
      setSelectedTags([]);
      closeModal();
    }
  };

  return (
    <div
      onClick={closeModal}
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/70"
    >
      <div
        className="relative min-h-[200px] w-[450px] border border-[#c7cfe2] bg-white p-8 shadow-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <Button
          variant="close"
          className="absolute right-5 top-4"
          onClick={closeModal}
        >
          <RxCross2 size={20} />
        </Button>

        <div>
          <p className="mb-2">Selected Tags</p>
          <div className="flex flex-wrap gap-2">
            {selectedTags.map((tag, index) => (
              <span
                key={index}
                className="rounded-full bg-[#E9E9E9] px-3 py-1 text-center text-xs text-[#727272]"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        <div className="mt-4 space-y-2">
          <label className="flex items-center gap-2 text-sm text-[#333]">
            <input
              type="checkbox"
              className="h-4 w-4 rounded-none"
              checked={dpDeleteType === "contains all"}
              onChange={() =>
                setDpDeleteType((prev) =>
                  prev === "contains all" ? "" : "contains all"
                )
              }
            />
            Delete only if all tags are present
          </label>

          <label className="flex items-center gap-2 text-sm text-[#333]">
            <input
              type="checkbox"
              className="h-4 w-4 rounded-none"
              checked={dpDeleteType === "contains any"}
              onChange={() =>
                setDpDeleteType((prev) =>
                  prev === "contains any" ? "" : "contains any"
                )
              }
            />
            Delete if any tag is present
          </label>
        </div>

        <div className="mt-8 flex justify-center gap-4">
          <Button variant="cancel" onClick={closeModal}>
            Cancel
          </Button>
          <Button
            disabled={!dpDeleteType}
            variant={dpDeleteType ? "primary" : "ghost"}
            className="w-[40%]"
            onClick={() => handleDeleteDp()}
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
};

export default BulkDpDeleteModal;
