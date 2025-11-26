import Button from "@/components/ui/Button";
import Link from "next/link";
import React from "react";

import { FaEnvelope } from "react-icons/fa";

const Modal = ({ isOpen, onClose, title, message, onConfirm }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-[#FBFCFE/50] z-50">
      <div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.8, opacity: 0 }}
        className="bg-white p-6  shadow-xl text-center w-[400px]"
      >
        <FaEnvelope className="text-green-600 text-4xl mx-auto mb-3" />
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="text-gray-600 text-sm mt-2">{message}</p>

        <div className="mt-5 flex flex-col justify-center items-center gap-2 ">
          <Link href="https://mail.google.com/mail/u/0/#index" target="_blank">
            <Button variant="primary" className="w-24">
              Sure !
            </Button>
          </Link>
          <button
            onClick={onClose}
            className="text-sm text-gray-600 underline cursor-pointer"
          >
            ← Back
          </button>
        </div>
      </div>
    </div>
  );
};

export default Modal;
