import React from "react";

const Signature = ({ artificatData }) => {
  if (!artificatData) return <div>Loading Signature...</div>;

  const { scheme, signature_value, signature_timestamp } = artificatData;

  return (
    <div className="space-y-4 text-sm">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-subHeading">Scheme:</p> {scheme || "N/A"}
        </div>
        <div>
          <p className="text-subHeading">Timestamp: </p>
          {signature_timestamp
            ? new Date(signature_timestamp).toLocaleString()
            : "N/A"}
        </div>
      </div>
      <div>
        <p className="text-subHeading">Signature Value:</p>
        <pre className="whitespace-pre-wrap break-all rounded">
          {signature_value || "N/A"}
        </pre>
      </div>
    </div>
  );
};

export default Signature;
