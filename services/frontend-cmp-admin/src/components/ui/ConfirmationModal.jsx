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
  description = null,
  confirmText = "Yes",
  cancelText = "No",
  loading = false,
  confirmVariant = "yes",
  cancelVariant = "no",
  cancelButton,
  confirmButton,
}) => {
  if (!isOpen) return null;

  const handleConfirm = async () => {
    try {
      await onConfirm();
    } catch (error) {
      toast.error("An error occurred");
      console.error(error);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50"
      onClick={onClose}
    >
      <div
        className=" h-[200px] w-[500px] border border-[#c7cfe2] bg-white p-5"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-end gap-1 p-1">
          <RxCross2
            size={24}
            className="cursor-pointer text-red-500"
            onClick={onClose}
          />
        </div>
        <div className="m-auto flex w-[80%] flex-col items-center justify-center text-center">
          <p>{title}</p>
          {description && (
            <p className="mt-2 text-sm text-gray-600">{description}</p>
          )}
          <div className="mt-4 flex w-full h-8 items-center justify-center gap-4">
            <Button
              variant={cancelVariant}
              onClick={onClose}
              disabled={loading}
              className={cancelButton}
            >
              {cancelText}
            </Button>
            <Button
              variant={confirmText == "Remove" ? "delete" : confirmVariant}
              onClick={handleConfirm}
              loading={loading}
              className={confirmButton}
            >
              {confirmText}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
