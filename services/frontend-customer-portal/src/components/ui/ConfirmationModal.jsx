"use client";
import React from "react";
import Button from "@/components/ui/Button";
import { RxCross2 } from "react-icons/rx";
import toast from "react-hot-toast";

const ConfirmationModal = ({
  isOpen,
  onClose,
  onConfirm,
  title = "Are you sure?",
  message = "",
  confirmText = "Yes",
  cancelText = "No",
  loading = false,
  showConfirm = true,
}) => {
  if (!isOpen) return null;

  const handleConfirm = async () => {
    try {
      await onConfirm?.();
    } catch (error) {
      toast.error("An error occurred");
      console.error(error);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-[90%] max-w-md bg-white shadow-md p-6 border border-gray-300"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-end">
          <RxCross2
            size={22}
            className="cursor-pointer text-gray-500 hover:text-gray-700"
            onClick={onClose}
          />
        </div>

        <div className="text-center px-4 pb-2">
          <h2 className="text-lg font-semibold">{title}</h2>
          {message && (
            <p className="mt-2 text-sm text-gray-600 leading-relaxed">
              {message}
            </p>
          )}
        </div>

        <div className="mt-5 flex items-center justify-center gap-4">
          <Button
            variant="no"
            className={"cursor-pointer"}
            onClick={onClose}
            disabled={loading}
          >
            {cancelText}
          </Button>

          {showConfirm && (
            <Button
              variant="yes"
              className={"cursor-pointer"}
              onClick={handleConfirm}
              loading={loading}
            >
              {confirmText}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
