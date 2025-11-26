"use client";

import React from "react";
import { RxArrowTopRight, RxCross2 } from "react-icons/rx";
import toast from "react-hot-toast";
import Link from "next/link";

const ActiveConsentsModal = ({ isOpen, onClose, activeConsents }) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative bg-white p-6 rounded-lg shadow-lg max-w-lg w-full mx-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-gray-700 focus:outline-none"
        >
          <RxCross2 size={20} />
        </button>
        <h2 className="text-xl font-semibold text-gray-800 mb-4 text-center">
          Active Consents Detected
        </h2>
        <p className="text-gray-600 text-center mb-4">
          The following consents must be revoked before the request can be
          processed.
        </p>
        <div className="max-h-60 overflow-y-auto mb-4">
          <ul className="list-disc list-inside space-y-2">
            {activeConsents && activeConsents.length > 0 ? (
              activeConsents.map((consent, idx) => (
                <li
                  key={idx}
                  className="text-sm text-gray-700 mb-2 flex flex-col gap-1"
                >
                  {consent.purposes?.map((p) => (
                    <Link
                      key={p.purpose_id}
                      href={`/manage-preference/update-preference?agreement_id=${consent.agreement_id}`}
                      className="px-2 py-2 border border-gray-200 bg-gray-50 hover:bg-gray-100 flex items-center justify-between"
                    >
                      <span>{p.purpose_title}</span>
                      <span>
                        <RxArrowTopRight size={20} color="gray" />
                      </span>
                    </Link>
                  ))}
                </li>
              ))
            ) : (
              <li className="text-gray-500">
                No active consents data available.
              </li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ActiveConsentsModal;
