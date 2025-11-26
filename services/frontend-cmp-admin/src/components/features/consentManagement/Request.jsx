import React from "react";

const Request = ({ artificatData }) => {
  if (!artificatData || Object.keys(artificatData).length === 0) {
    return (
      <div className="text-gray-600">No Request Header Data Available</div>
    );
  }

  return (
    <div className="">
      <div className="grid grid-cols-2  rounded p-4">
        {Object.entries(artificatData).map(([key, value]) => (
          <div key={key} className="pb-2">
            <p className="text-sm capitalize text-subHeading">{key}</p>
            <p className="wrap-break-words text-sm text-gray-900">
              {typeof value === "string" ? value : JSON.stringify(value)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Request;
