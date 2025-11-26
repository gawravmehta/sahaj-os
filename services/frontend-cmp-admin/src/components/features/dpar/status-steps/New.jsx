import { capitalizeFirstLetter } from "@/utils/capitalizeFirstLetter";
import React from "react";

const New = ({ data }) => {
  return (
    <div className="p-8 text-sm">
      <div className="m-auto grid  grid-cols-2 gap-y-4">
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">First Name:</span>{" "}
          {capitalizeFirstLetter(data?.first_name) || "—"}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">Last Name:</span>{" "}
          {capitalizeFirstLetter(data?.last_name) || "—"}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">Core Identifier:</span>{" "}
          {data?.core_identifier || "—"}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">
            Secondary Identifier :
          </span>{" "}
          {data?.secondary_identifier || "—"}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">Country:</span>{" "}
          {capitalizeFirstLetter(data?.country || "—")}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">Category:</span>{" "}
          {capitalizeFirstLetter(data?.dp_type || "Not Yet")}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">Created At:</span>{" "}
          {data?.created_timestamp || "—"}
        </div>
      </div>
    </div>
  );
};

export default New;
