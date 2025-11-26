"use client";
import { useState } from "react";

import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";

const CopyToClipboard = ({ value }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="ml-2 p-1 text-xs text-indigo-600 hover:text-indigo-800 transition duration-150 ease-in-out font-medium rounded-md hover:bg-indigo-50"
      aria-label={copied ? "Copied" : "Copy to clipboard"}
    >
      {copied ? "Copied! 🎉" : "Copy"}
    </button>
  );
};

const WebhookDetailModal = ({ isOpen, onClose, webhook }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Webhook Details">
      <div className="p-4 text-center">
        <p className="mb-4">
          Detailed webhook information is now available on a dedicated page.
        </p>
        {webhook?._id?.$oid && (
          <p className="mb-4">
            Navigate to the webhook details page for ID: {webhook._id.$oid}
          </p>
        )}
        <Button type="button" variant="secondary" onClick={onClose}>
          Close
        </Button>
      </div>
    </Modal>
  );
};

export default WebhookDetailModal;
