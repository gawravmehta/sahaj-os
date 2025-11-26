import React from "react";

const ArtifactDetails = ({ artificatData }) => {
  if (!artificatData) return <div>Loading...</div>;

  const {
    agreement_hash_id,
    cp_name,
    agreement_version,
    linked_agreement_hash,
    metadata,
    data_principal,
    data_fiduciary,
  } = artificatData;

  return (
    <div className="space-y-4 text-sm">
      <div className="grid grid-cols-2 gap-4">
        <div className="flex-col">
          <span className="text-subHeading">Collection Point:</span>{" "}
          <p>{artificatData?.artifact.cp_name}</p>
        </div>
        <div>
          <span className="text-subHeading">Agreement Version:</span>{" "}
          <p>{artificatData?.artifact.agreement_version}</p>
        </div>
      </div>
      <div>
        <span className="text-subHeading">Agreement Hash ID:</span>{" "}
        {agreement_hash_id}
      </div>

      <div>
        <span className="text-subHeading">Linked Agreement Hash:</span>{" "}
        {artificatData?.artifact.linked_agreement_hash}
      </div>

      <h3 className="text-md text-subHeading">Metadata</h3>
      <div>
        <span className="text-subHeading">IP Address:</span>{" "}
        <p>{artificatData?.artifact.metadata?.ip_address}</p>
      </div>
      <div>
        <span className="text-subHeading">Request Header Hash:</span>{" "}
        {metadata?.request_header_hash}
      </div>

      <h3 className="text-md text-subHeading">Data Principal</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <span className="text-subHeading">DP DF ID:</span>{" "}
          <p>{artificatData?.artifact.data_principal?.dp_df_id}</p>{" "}
        </div>
        <div>
          <span className="text-subHeading">Residency:</span>{" "}
          <p>{artificatData?.artifact.data_principal?.dp_residency}</p>{" "}
        </div>
      </div>
      <div>
        <span className="text-subHeading">DP ID:</span>{" "}
        <p>{artificatData?.artifact.data_principal?.dp_id}</p>{" "}
      </div>

      <div>
        <span className="text-subHeading">Email (Hashed):</span>{" "}
        <p>{artificatData?.artifact.data_principal?.dp_e}</p>{" "}
      </div>
      <div>
        <span className="text-subHeading">Mobile (Hashed):</span>{" "}
        <p>{artificatData?.artifact.data_principal?.dp_m}</p>{" "}
      </div>
      <div>
        <span className="text-subHeading">Verified:</span>{" "}
        <p>
          {artificatData?.artifact.data_principal?.dp_verification
            ? "Yes"
            : "No"}
        </p>{" "}
      </div>

      <h3 className="text-md text-subHeading">Data Fiduciary</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <span className="text-subHeading">DF ID:</span>{" "}
          <p>{artificatData?.artifact.data_fiduciary?.df_id}</p>{" "}
        </div>
        <div>
          <span className="text-subHeading">Agreement Date:</span>{" "}
          <p>{new Date(data_fiduciary?.agreement_date).toLocaleString()}</p>{" "}
        </div>
      </div>
    </div>
  );
};

export default ArtifactDetails;
