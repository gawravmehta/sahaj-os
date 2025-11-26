"use client";

import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import React, { useEffect, useState } from "react";

const Review = ({ data }) => {
  const [deData, setDeData] = useState({});

  const getOneDataElement = async () => {
    try {
      const response = await apiCall(
        `/data-elements/get-data-element/${data?.data_element_id}`
      );
      setDeData(response);
    } catch (error) {
      console.error(getErrorMessage(error));
    }
  };

  useEffect(() => {
    getOneDataElement();
  }, []);

  return (
    <div className="w-full max-w-3xl mx-auto bg-white  p-6 space-y-6 transition-all">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="flex flex-col bg-gray-50  p-3 border border-gray-100 ">
          <span className="text-sm text-gray-500  font-medium">
            Request Type:
          </span>
          <span className="text-base  text-gray-900  capitalize">
            {data?.request_type || "—"}
          </span>
        </div>

        <div className="flex flex-col bg-gray-50   p-3 border border-gray-100 ">
          <span className="text-sm text-gray-500  font-medium">
            Request Priority:
          </span>
          <span
            className={`text-base capitalize  ${
              data?.request_priority === "high"
                ? "text-red-600"
                : data?.request_priority === "medium"
                ? "text-yellow-600"
                : "text-green-600"
            }`}
          >
            {data?.request_priority || "—"}
          </span>
        </div>

        <div className="sm:col-span-2 flex flex-col bg-gray-50  p-3 border border-gray-100 ">
          <span className="text-sm text-gray-500  font-medium">
            Request Message:
          </span>
          <span className="text-base text-gray-900  whitespace-pre-line">
            {data?.request_message || "No message provided"}
          </span>
        </div>

        <div className="flex flex-col bg-gray-50  p-3 border border-gray-100 ">
          <span className="text-sm text-gray-500  font-medium">
            Data Element:
          </span>
          <span className="text-base  text-gray-900 ">
            {deData?.de_name || "—"}
          </span>
        </div>

        <div className="flex flex-col bg-gray-50  p-3 border border-gray-100 ">
          <span className="text-sm text-gray-500  font-medium">
            Data Element Original Name:
          </span>
          <span className="text-base  text-gray-900 ">
            {deData?.de_original_name || "—"}
          </span>
        </div>

        {data?.data_element_updated_value && (
          <div className="flex flex-col bg-gray-50 col-span-2  p-3 border border-gray-100 ">
            <span className="text-sm text-gray-500  font-medium">
              Requested Updated Value:
            </span>
            <span className="text-base  text-gray-900 ">
              {data?.data_element_updated_value || "—"}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default Review;
