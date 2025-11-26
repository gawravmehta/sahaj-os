import React from "react";
const Attestation = ({ artificatData }) => {
  if (!artificatData) return <div>Loading...</div>;

  const { dlt_id, dp_public_key, txn } = artificatData;

  return (
    <div className="space-y-4 text-sm">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-subHeading">DLT ID:</p> {dlt_id || "N/A"}
        </div>
        <div>
          <p className="text-subHeading">Data Principal Public Key:</p>{" "}
          {dp_public_key || "N/A"}
        </div>
      </div>

      <div>
        <p className="text-subHeading">Transaction Hash:</p> {txn || "N/A"}
      </div>
    </div>
  );
};

export default Attestation;
