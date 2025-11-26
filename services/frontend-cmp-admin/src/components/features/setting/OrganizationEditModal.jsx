"use client";

import Button from "@/components/ui/Button";
import { InputField } from "@/components/ui/Inputs";
import { useEffect, useRef } from "react";
import { IoMdClose } from "react-icons/io";

const OrganizationEditModal = ({
  visible,
  onClose,
  df_logo_url,
  onChange,
  onSave,
  loading,
}) => {
  const modalRef = useRef();

  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (!modalRef.current) return;
      if (!modalRef.current.contains(e.target)) {
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
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-[#DEEBF7]/50">
      <div
        ref={modalRef}
        className="relative max-h-[90vh] w-[600px] overflow-y-auto rounded-md bg-white p-6 shadow-md"
      >
        <button
          className="absolute right-4 top-4 text-xl text-gray-600 hover:text-black"
          onClick={onClose}
        >
          <IoMdClose />
        </button>

        <h2 className="text-lg font-semibold">Edit Organization Logo</h2>
        <p className="mb-4 text-xs text-gray-500">
          Update your organization's logo URL.
        </p>

        <InputField
          label="Logo URL"
          value={df_logo_url || ""}
          onChange={(e) => onChange("df_logo_url", e.target.value)}
          placeholder="https://example.com/logo.png"
        />

        {df_logo_url && (
          <div className="mb-3 mt-4">
            <p className="mb-1 text-xs text-gray-400">Preview:</p>
            <img
              src={df_logo_url}
              alt="Logo preview"
              className="h-16 w-16 rounded-full border object-contain p-1"
              onError={(e) => (e.target.style.display = "none")}
            />
          </div>
        )}

        <div className="mt-6 flex justify-end gap-4">
          <Button variant="cancel" onClick={onClose} disabled={loading}>
            Close
          </Button>
          <Button onClick={onSave} disabled={loading} className="px-3">
            {loading ? "Saving..." : "Update"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default OrganizationEditModal;
