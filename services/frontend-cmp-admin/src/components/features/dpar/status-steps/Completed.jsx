"use client";

import React from "react";
import { IoCheckmarkCircle } from "react-icons/io5";

const Completed = ({ data }) => {
  if (!data) return null;

  const {
    first_name,
    last_name,
    core_identifier,
    data_element_updated_value,
    request_type,
    request_message,
    kyc_document,
    created_timestamp,
    completed_timestamp,
    turn_around_time,
  } = data;

  return (
    <div className="w-full p-6 bg-white border border-gray-300 space-y-6">
      <div className="flex items-center gap-3 border-b pb-4">
        <IoCheckmarkCircle className="text-green-600 text-3xl" />
        <div>
          <h2 className="text-xl font-semibold text-gray-800">
            DPAR Request Approved
          </h2>
          <p className="text-sm text-gray-600">
            The DPAR request has been successfully approved.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
        <InfoRow label="Name" value={`${first_name} ${last_name}`} />
        <InfoRow label="Primary Identifier" value={core_identifier} />
        <InfoRow label="Request Type" value={request_type?.replace("_", " ")} />
        <InfoRow label="Updated Value" value={data_element_updated_value} />
        <InfoRow label="KYC Document" value={kyc_document} />
        <InfoRow
          label="Requested On"
          value={new Date(created_timestamp).toLocaleString()}
        />
        <InfoRow
          label="Completed On"
          value={new Date(completed_timestamp).toLocaleString()}
        />
        <InfoRow
          label="Turnaround Time"
          value={`${Math.round(turn_around_time / 60)} minutes`}
        />
      </div>

      {request_message && (
        <div className="p-3  bg-gray-50 border border-grey-300 text-gray-700 text-sm">
          <p className="font-medium mb-1">Request Note:</p>
          <p>{request_message}</p>
        </div>
      )}
    </div>
  );
};

const InfoRow = ({ label, value }) => (
  <div>
    <p className="text-gray-500">{label}</p>
    <p className="font-medium text-gray-800">{value || "—"}</p>
  </div>
);

export default Completed;
