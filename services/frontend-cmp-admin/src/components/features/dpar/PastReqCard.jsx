import React from "react";
import { MdEmail, MdPhone, MdPublic } from "react-icons/md";
import Link from "next/link";

const PastReqCard = ({ relatedRequestData }) => {
  const statusStyles = {
    active: "bg-green-100 text-green-600",
    created: "bg-green-100 text-green-600",
    open: "bg-green-100 text-green-600",
    resolved: "bg-yellow-100 text-yellow-600",
    closed: "bg-yellow-100 text-yellow-600",
  };

  return (
    <Link href={`/apps/dpar/${relatedRequestData._id}`}>
      <div className="bg-white hover:shadow-md p-4 transition-all duration-300 border border-gray-200">
        <div className="flex justify-between items-start">
          <h2 className="text-primary  text-[16px]">
            {relatedRequestData.first_name || ""}{" "}
            {relatedRequestData.last_name || ""}
          </h2>
          <div className="flex items-center gap-1">
            <span className="text-xs italic text-[#7E7B7B]">
              {relatedRequestData.request_type}
            </span>
          </div>
        </div>
        <p className="text-[#7E7B7B] text-sm mt-1">
          {relatedRequestData.request_message || "No message provided"}
        </p>

        <div className="flex items-center text-gray-500 text-sm mt-1 space-x-4">
          {relatedRequestData.secondary_identifier && (
            <div className="flex items-center space-x-1 text-[#7E7B7B] text-xs">
              <MdEmail /> <span>{relatedRequestData.secondary_identifier}</span>
            </div>
          )}
          {relatedRequestData.core_identifier && (
            <div className="flex items-center space-x-1 text-[#7E7B7B] text-xs">
              <MdPhone /> <span>{relatedRequestData.core_identifier}</span>
            </div>
          )}
          {relatedRequestData.country && (
            <div className="flex items-center space-x-1 text-[#7E7B7B] text-xs">
              <MdPublic /> <span>{relatedRequestData.country}</span>
            </div>
          )}
        </div>

        <div className="flex justify-between items-center mt-1">
          {relatedRequestData.last_updated && (
            <span className="text-xs italic text-gray-400">
              Last Updated:{" "}
              {new Date(relatedRequestData.last_updated).toLocaleDateString()}
            </span>
          )}
          {relatedRequestData.status && (
            <span
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                statusStyles[relatedRequestData.status.toLowerCase()] ||
                "bg-gray-100 text-gray-600"
              }`}
            >
              {relatedRequestData.status}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
};

export default PastReqCard;
