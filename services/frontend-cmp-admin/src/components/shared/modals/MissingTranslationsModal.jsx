import Button from "@/components/ui/Button";
import { useState } from "react";

const MissingTranslationsModal = ({
  missing,
  onClose,
  onSaveDraft,
  module = "Purpose"
}) => {
  const missingArray = Array.isArray(missing) ? missing : [];
  if (!missingArray?.length) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-[#f2f9ff]/50 z-50">
      <div className="bg-white shadow-xl p-6 w-[450px]">
        <h2 className="text-lg font-semibold mb-3 text-gray-900">
          Missing Translations
        </h2>

        <p className="text-sm text-gray-700 mb-4 leading-relaxed">
          To <span className="font-semibold">publish</span> this {module}, all
          translations must be added. Currently, the following translations are
          missing:
        </p>

        <ul className="list-disc pl-5 space-y-1 text-sm text-red-600 mb-4 max-h-40 overflow-y-auto medium-scrollbar">
          {missingArray.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>

        <p className="text-sm text-gray-600 mb-5 leading-relaxed">
          If you don’t want to add them right now, you can{" "}
          <span className="font-medium ">save as draft</span>. Or
          use <span className="font-medium ">Auto Translate</span>{" "}
          to generate them automatically.
        </p>

        <div className="flex justify-end gap-3">
          <Button
            onClick={onClose}
           variant="cancel"
          >
            Cancel
          </Button>
          <Button
            onClick={onSaveDraft}
           variant="secondary"
          >
            Save as Draft
          </Button>
        </div>
      </div>
    </div>
  );
};

export default MissingTranslationsModal;
