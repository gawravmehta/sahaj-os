"use client";
import React, { useEffect } from "react";
import { FaCheck } from "react-icons/fa";
import { RxCross2 } from "react-icons/rx";

const ProgressBar = ({
  progress,
  startDate,
  endDate,
  setConsentStartDate,
  setConsentEndDate,
  consentStates,
}) => {
  useEffect(() => {
    if (startDate && endDate) {
      setConsentStartDate(new Date(startDate));
      setConsentEndDate(new Date(endDate));
    }
  }, [startDate, endDate]); // Add startDate and endDate as dependencies

  return (
    <div className=" w-full pr-8">
      <div className="w-full bg-gray-100 rounded-full relative">
        <div
          className={`${
            consentStates ? "border-blue-600 " : "border-red-600 "
          }  border-b border-[1px] rounded-full transition-all duration-300`}
          style={{ width: `${progress}%` }}
        ></div>

        <div
          className={`${
            consentStates ? "bg-green-600 text-xs" : "bg-red-600 text-md "
          } absolute -top-2.5 h-5 w-5 rounded-full flex items-center justify-center text-white   font-bold shadow-lg transition-transform duration-300`}
          style={{ left: `calc(${progress}% - 0rem)` }}
        >
          {consentStates ? <FaCheck /> : <RxCross2 />}
        </div>
      </div>
    </div>
  );
};

export default ProgressBar;
