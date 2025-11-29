import React, { useState } from "react";
import { FaEye, FaEyeSlash, FaCopy } from "react-icons/fa";
import { toast } from "react-hot-toast";

const SecretField = ({ label, value, isSecret = false }) => {
  const [show, setShow] = useState(!isSecret);

  const handleCopy = () => {
    if (value) {
      navigator.clipboard.writeText(value);
      toast.success("Copied to clipboard!");
    }
  };

  return (
    <div className="mb-4">
      <label className="mb-1 block text-sm font-medium text-gray-700">
        {label}
      </label>
      <div className="flex items-center gap-2">
        <div className="relative w-full">
          <input
            type={show ? "text" : "password"}
            value={value || ""}
            readOnly
            className="w-full rounded border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none"
          />
          {isSecret && (
            <button
              type="button"
              onClick={() => setShow(!show)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              {show ? <FaEyeSlash /> : <FaEye />}
            </button>
          )}
        </div>
        <button
          type="button"
          onClick={handleCopy}
          className="rounded border border-gray-300 bg-white p-2 text-gray-500 hover:bg-gray-50 hover:text-gray-700"
          title="Copy"
        >
          <FaCopy />
        </button>
      </div>
    </div>
  );
};

const Secrets = ({ secretData }) => {
  if (!secretData) {
    return (
      <div className="p-4 text-center text-gray-500">
        No secrets data available.
      </div>
    );
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="mb-6">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">
          General Keys
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <SecretField label="DF Key" value={secretData.df_key} />
          <SecretField
            label="DF Secret"
            value={secretData.df_secret}
            isSecret={true}
          />
        </div>
      </div>

      <div className="mb-6">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">API Keys</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <SecretField
            label="Add DP Key"
            value={secretData.api_keys?.add_dp_key}
          />
          <SecretField
            label="Add DP Secret"
            value={secretData.api_keys?.add_dp_secret}
            isSecret={true}
          />
        </div>
      </div>

      <div className="mb-6">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">
          Cogniscan Keys
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <SecretField
            label="Cogniscan Default Key"
            value={secretData.cogniscan_keys?.cogniscan_default_key}
          />
        </div>
      </div>

      <div className="mb-6">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">Webhooks</h3>
        <div className="grid grid-cols-1 gap-4 col-span-2">
          <SecretField
            label="CMP Webhook Secret"
            value={secretData.cmp_webhook_secret}
            isSecret={true}
          />
        </div>
      </div>
    </div>
  );
};

export default Secrets;
