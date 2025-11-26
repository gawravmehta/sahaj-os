"use client";

import { useRouter } from "next/navigation";
import { FaArrowRight } from "react-icons/fa6";
import Button from "@/components/ui/Button";
import { FiArrowUpRight } from "react-icons/fi";

const ErrorPopup = ({ errorData, onClose, onSaveDraft }) => {
  const router = useRouter();
  
  const { not_published } = errorData || {};

  if (!not_published) return null;

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 flex items-center justify-center bg-[#f2f9ff]/50 z-50"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="bg-white shadow-xl p-6 w-[500px] max-h-[80vh] overflow-y-auto"
      >
        <h2 className="text-lg font-semibold text-gray-900">
          You cannot publish this Collection Point until all
           Elements and
          Purposes are published.
        </h2>

        <p className="text-sm text-gray-700 mb-4 leading-relaxed">
          Please review the following items and update them before publishing:
        </p>

        {not_published?.data_elements?.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-800 mb-3">
              Not Published Data Elements
            </h3>
            <ul className="space-y-2 text-sm text-gray-700 max-h-40 overflow-auto pr-1.5 medium-scrollbar ">
              {not_published.data_elements.map((d) => (
               <li
               key={d.de_id}
               className="flex justify-between items-center gap-2"
             >
               <span className="border border-gray-300 w-full px-3 py-2">
                 {d.de_name}
               </span>
               <button
                 onClick={() =>
                   router.push(`/apps/data-element/${d.de_id}`)
                 }
                 className="border border-gray-300 py-2 cursor-pointer px-3 hover:bg-gray-50"
               >
                 <FiArrowUpRight size={20} className="text-primary text-base" />
               </button>
             </li>
                
              ))}
            </ul>
          </div>
        )}
        {not_published?.purposes?.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-800 mb-3">
              Not Published Purposes
            </h3>
            <ul className="space-y-2 text-sm text-gray-700 max-h-40 overflow-auto pr-1.5 medium-scrollbar ">
              {not_published.purposes.map((p) => (
                <li
                  key={p.purpose_id}
                  className="flex justify-between items-center gap-2"
                >
                  <span className="border border-gray-300 w-full px-3 py-2">
                    {p.purpose_title}
                  </span>
                  <button
                    onClick={() =>
                      router.push(`/apps/purpose-management/${p.purpose_id}`)
                    }
                    className="border border-gray-300 py-2 cursor-pointer px-3 hover:bg-gray-50"
                  >
                    <FiArrowUpRight size={20} className="text-primary text-base" />
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex justify-end gap-3 mt-6">
          <Button onClick={onClose} variant="cancel">
            Close
          </Button>
          <Button onClick={onSaveDraft} variant="secondary">
            Save as Draft
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ErrorPopup;
