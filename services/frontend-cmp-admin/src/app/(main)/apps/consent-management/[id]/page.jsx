"use client";

import React, { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";
import Header from "@/components/ui/Header";
import ArtifactDetails from "@/components/features/consentManagement/ArtifactDetails";
import ConsentScope from "@/components/features/consentManagement/ConsentScope";
import Request from "@/components/features/consentManagement/Request";
import Signature from "@/components/features/consentManagement/Signature";
import Attestation from "@/components/features/consentManagement/Attestation";

const tabs = [
  { id: "artifacts", label: "Artifacts" },
  { id: "consent_scope", label: "Consent Scope" },
  { id: "request", label: "Request Header" },
  { id: "signature", label: "Signature" },
  { id: "attestation", label: "Attestation" },
];

const Page = ({ params }) => {
  const { id } = React.use(params);

  const router = useRouter();
  const searchParams = useSearchParams();
  const tabActive = searchParams.get("activeTab") || "artifacts";

  const [artificatData, setArtificatData] = useState(null);

  useEffect(() => {
    getOneArtifact();
  }, []);

  const getOneArtifact = async () => {
    try {
      const response = await apiCall(
        `/consent-artifact/get-consent-artifact-by-id?id=${id}`
      );

      setArtificatData(response);
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  const handleTabChange = (tabId) => {
    router.push(`?activeTab=${tabId}`, undefined, { shallow: true });
  };

  const breadcrumbsProps = {
    path: `/apps/consent-management/${artificatData?.artifact?.data_principal?.dp_df_id}`,
    skip: "/apps",
  };

  return (
    <div className="flex flex-col justify-between">
      <div className="flex w-full items-center justify-between bg-background pr-6">
        <Header
          title={
            artificatData?.artifact?.data_principal?.dp_df_id +
              " Artifact Details" || "Consent Artifact Details"
          }
          breadcrumbsProps={breadcrumbsProps}
        />
      </div>
      <div className="flex items-center justify-center border-b border-t border-borderheader bg-background">
        <div className="grid grid-cols-3 gap-3 sm:flex sm:flex-row">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id)}
              className={`py-4 sm:px-4 lg:px-5 ${
                tabActive === tab.id
                  ? "border-b border-primary text-primary"
                  : "text-[#6B7280]"
              } font-medium`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      <div className="flex flex-col items-center justify-center">
        <div className="custom-scrollbar ju flex h-[calc(100vh-210px)] w-[800px] overflow-auto px-6 pt-7">
          {tabActive === "artifacts" && (
            <ArtifactDetails artificatData={artificatData} />
          )}
          {tabActive === "consent_scope" && (
            <ConsentScope
              artificatData={artificatData?.artifact?.consent_scope}
            />
          )}
          {tabActive === "request" && (
            <Request artificatData={artificatData?.request_header} />
          )}
          {tabActive === "signature" && (
            <Signature artificatData={artificatData?.signature} />
          )}
          {tabActive === "attestation" && (
            <Attestation artificatData={artificatData?.attestation} />
          )}
        </div>
      </div>
    </div>
  );
};

export default Page;
