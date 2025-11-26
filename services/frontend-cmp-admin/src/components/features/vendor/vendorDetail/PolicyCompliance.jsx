import Skeleton from "@/components/ui/Skeleton";

import React from "react";

const PolicyCompliance = ({ vendorData, loading }) => {
  return (
    <div className="mx-auto mt-4 w-full max-w-2xl space-y-4">
      <div>
        <span className="flex items-center justify-between text-subHeading">
          <h1> Privacy Policy: </h1>
        </span>
        {!loading ? (
          <p>{vendorData?.dpr_privacy_policy}</p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-28"} />
        )}
      </div>
      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1>Data Policy: </h1>
        </span>
        {!loading ? (
          <p>{vendorData?.dpr_data_policy}</p>
        ) : (
          <Skeleton variant="multiple" />
        )}
      </div>
      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1>Security Policy: </h1>
        </span>
        {!loading ? (
          <p>{vendorData?.dpr_security_policy}</p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-64"} />
        )}
      </div>
      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1>Legal Basis of Processing: </h1>
        </span>
        {!loading ? (
          <p className="capitalize">{vendorData?.legal_basis_of_processing}</p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-64"} />
        )}
      </div>
      <div className="flex items-center justify-between">
        <div>
          <span className="flex items-center justify-between text-subHeading">
            <h1>Signed DPA: </h1>
          </span>
          {!loading ? (
            <p>
              {vendorData.dpdpa_compliance_status?.signed_dpa === false
                ? "No"
                : "Yes"}
            </p>
          ) : (
            <Skeleton variant="single" className={"h-4 w-28"} />
          )}
        </div>
        <div>
          <span className="flex items-center justify-between  text-subHeading">
            <h1>Transfer Outside India: </h1>
          </span>
          {!loading ? (
            <p>
              {vendorData?.dpdpa_compliance_status?.transfer_outside_india ===
              false
                ? "No"
                : "Yes"}
            </p>
          ) : (
            <Skeleton variant="single" className={"h-4 w-28"} />
          )}
        </div>
        <div>
          <span className="flex items-center justify-between text-subHeading">
            <h1>Cross Border Mechanism: </h1>
          </span>
          {!loading ? (
            <p className="capitalize">
              {" "}
              {vendorData?.dpdpa_compliance_status?.cross_border_mechanism?.replace(
                /_/g,
                " "
              )}
            </p>
          ) : (
            <Skeleton variant="single" className={"h-4 w-28"} />
          )}
        </div>
      </div>
      <div>
        <span className="flex items-center justify-between text-subHeading">
          <h1>Breach Notification Time: </h1>
        </span>
        {!loading ? (
          <p>
            {" "}
            {vendorData?.dpdpa_compliance_status?.breach_notification_time}
          </p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-28"} />
        )}
      </div>
    </div>
  );
};

export default PolicyCompliance;
