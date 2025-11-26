"use client";

import React, { useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { IoMdClose } from "react-icons/io";
import Button from "@/components/ui/Button";
import { InputField } from "@/components/ui/Inputs";

const PasswordResetModal = ({ onClose, visible }) => {
  const [form, setForm] = useState({
    oldPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [loading, setLoading] = useState(false);
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

  const handleInputChange = (name, value) => {
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    const { oldPassword, newPassword, confirmPassword } = form;

    if (!oldPassword || !newPassword || !confirmPassword) {
      toast.error("Please fill all fields");
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      const query = new URLSearchParams({
        current_password: oldPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      }).toString();

      const res = await apiCall(`/user/update-password?${query}`, {
        method: "PATCH",
      });

      toast.success(res?.message || "Password updated successfully");
      onClose();
    } catch (error) {
      const msg = getErrorMessage(error);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#DEEBF7] bg-opacity-50">
      <div
        ref={modalRef}
         className="relative w-[90%] max-w-md bg-white p-6 shadow-lg"
      >
        <button
          className="absolute right-3 top-3 text-gray-500 hover:text-black"
          onClick={onClose}
        >
          <IoMdClose size={20} />
        </button>
        <h2 className="mb-4 text-lg font-semibold">Reset Password</h2>

        <div className="space-y-4">
          <InputField
            label="Old Password"
            type="password"
            value={form.oldPassword}
            onChange={(e) => handleInputChange("oldPassword", e.target.value)}
          />
          <InputField
            label="New Password"
            type="password"
            value={form.newPassword}
            onChange={(e) => handleInputChange("newPassword", e.target.value)}
          />
          <InputField
            label="Confirm Password"
            type="password"
            value={form.confirmPassword}
            onChange={(e) =>
              handleInputChange("confirmPassword", e.target.value)
            }
          />
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <Button variant="cancel" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            className="px-4"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? "Saving..." : "Save"}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PasswordResetModal;
