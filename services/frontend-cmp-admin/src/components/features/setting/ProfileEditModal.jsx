import React, { useRef, useEffect } from "react";
import { InputField } from "@/components/ui/Inputs";
import Button from "@/components/ui/Button";
import { IoMdClose } from "react-icons/io";

const ProfileEditModal = ({
  visible,
  onClose,
  editData,
  onChange,
  onSave,
  loading,
}) => {
  const modalRef = useRef();

  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (modalRef.current && !modalRef.current.contains(e.target)) {
        onClose();
      }
    };

    if (visible) {
      document.addEventListener("mousedown", handleOutsideClick);
    }

    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, [visible, onClose]);

  if (!visible) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#DEEBF7] bg-opacity-50">
      <div ref={modalRef} className="relative w-[461px] bg-white p-6 shadow-xl">
        <button
          className="absolute right-4 top-4 text-xl text-gray-600 hover:text-black"
          onClick={onClose}
        >
          <IoMdClose />
        </button>

        <h2 className="text-lg font-semibold">Profile Information</h2>
        <p className="mb-4 text-xs text-gray-500">
          Provide detailed information about the data element to ensure accurate
          categorization and usage.
        </p>

        <InputField
          label="Profile Logo Url"
          name="image_url"
          value={editData.image_url}
          onChange={(e) => onChange("image_url", e.target.value)}
          placeholder="Paste URL"
        />

        {editData.image_url && (
          <div className="mb-2 mt-2">
            <p className="mb-1 text-xs text-gray-400">Preview:</p>
            <img
              src={editData.image_url}
              alt="Profile preview"
              className="h-16 w-16 rounded-full border object-cover"
              onError={(e) => (e.target.style.display = "none")}
            />
          </div>
        )}

        <div className="mt-6 flex w-full justify-end gap-3">
          <button className="text-red-600" onClick={onClose}>
            Cancel
          </button>
          <Button onClick={onSave} disabled={loading} className="px-3">
            {loading ? "Saving..." : "Update"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProfileEditModal;
