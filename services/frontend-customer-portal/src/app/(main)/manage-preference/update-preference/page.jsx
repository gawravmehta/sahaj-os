"use client";

import MyPreferences from "@/components/features/preferenceComponent/MyPreferences";
import Button from "@/components/ui/Button";
import Image from "next/image";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import { FaCheckCircle } from "react-icons/fa";
import { apiCall } from "@/hooks/apiCall";
import Loader from "@/components/ui/Loader";
import { useRouter } from "next/navigation";
import Breadcrumbs from "@/components/ui/BreadCrumb";

function Page() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const agreementId = searchParams.get("agreement_id");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [consentData, setConsentData] = useState(null);
  const [consentChanges, setConsentChanges] = useState({
    toRevoke: [],
    toGive: [],
  });

  const fetchConsentData = async () => {
    try {
      const response = await apiCall(
        `/api/v1/preferences/get-consent-transaction/${agreementId}`
      );

      const data =
        typeof response === "string" ? JSON.parse(response) : response;

      if (!data.agreement_chain || data.agreement_chain.length === 0) {
        throw new Error("No consent data found");
      }

      const latestConsent = data.agreement_chain[0].artifact;

      const transformedData = {
        title: latestConsent.cp_name || "Consent Point",
        agreement_id: latestConsent.agreement_id || "",
        preferenceData:
          latestConsent.consent_scope?.data_elements?.map((element) => ({
            de_id: element.de_id,
            title: element.title || "No Title",
            data_retention_period: element.data_retention_period || "",
            consents:
              element.consents?.map((consent) => ({
                purpose_id: consent.purpose_id,
                title: consent.purpose_title || "No Purpose Title",
                status:
                  consent.consent_status == "expired"
                    ? "denied"
                    : consent.consent_status,
                expiry: consent.consent_expiry_period || "",
                timestamp: consent.consent_timestamp || "",
                description: consent.description || "",
                cross_border: consent.cross_border || false,
                is_legal_mandatory: consent.is_legal_mandatory,
                legal_mandatory_message: consent.legal_mandatory_message,
                is_service_mandatory: consent.is_service_mandatory,
                service_mandatory_message: consent.service_mandatory_message,
              })) || [],
          })) || [],
      };

      setConsentData(transformedData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (agreementId) {
      fetchConsentData();
    }
  }, [agreementId]);

  const handlePdfDownload = async () => {
    try {
      const response = await apiCall(
        `/api/v1/consents/pdf-document/${agreementId}`,
        {
          method: "GET",
          responseType: "blob",
        }
      );

      // Create a blob URL and trigger download
      const blob = new Blob([response], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `agreement_${agreementId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Error downloading PDF:", err);
      alert("Failed to download PDF. Please try again.");
    }
  };

  const handleUpdateConsent = async () => {
    if (
      consentChanges.toRevoke.length === 0 &&
      consentChanges.toGive.length === 0
    ) {
      alert("No changes to update");
      return;
    }

    try {
      setLoading(true);

      if (consentChanges.toRevoke.length > 0) {
        const revokePayload = {
          consent_scope: consentChanges.toRevoke.map(
            ({ de_id, purpose_id }) => ({
              de_id,
              consent_purposes: [{ purpose_id }],
            })
          ),
        };

        await apiCall(`/api/v1/consents/revoke-consent/${agreementId}`, {
          method: "PATCH",
          data: revokePayload,
        });
      }

      if (consentChanges.toGive.length > 0) {
        const givePayload = {
          consent_scope: consentChanges.toGive.map(({ de_id, purpose_id }) => ({
            de_id,
            consent_purposes: [{ purpose_id }],
          })),
        };

        await apiCall(`/api/v1/consents/give-consent/${agreementId}`, {
          method: "PATCH",
          data: givePayload,
        });
      }

      router.push("/manage-preference");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Loader />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen">
        <p className="text-red-500">Error: {error}</p>
      </div>
    );
  }

  if (!consentData) {
    return (
      <div className="flex justify-center items-center h-screen">
        <p>No consent data found</p>
      </div>
    );
  }

  const hasChanges =
    consentChanges.toRevoke.length > 0 || consentChanges.toGive.length > 0;

  return (
    <div className="mt-20 h-screen  ">
      <div
        className="flex justify-center flex-col items-center 
"
      >
        <div className="flex items-start justify-start  w-[800px] pl-2 ">
          <Breadcrumbs
            path="/manage-preference/update-preference"
            labels={{
              "/manage-preference/update-preference": "Update Preferences",
            }}
          />
        </div>
        <div className="flex flex-col w-[800px] pb-12 px-2">
          <div className="flex">
            <div>
              <h1 className="text-[#000000] text-[28px] ">
                Update Preferences
              </h1>
              <p className="text-xs  text-subHeading   md:w-[80%]">
                Update your preferences by giving or revoking consent. You can
                also renew your consent.
              </p>
            </div>
          </div>

          <div className="xl:flex gap-2 w-full h-20 mt-5">
            <div className="w-full">
              <div className="border border-[#C7CFE2] w-full ">
                <div className="md:flex gap-4 px-4 py-1">
                  <div className="w-1/2 flex items-center">
                    <h1 className="text-[16px] text-[#000000]">
                      Consent Agreement
                    </h1>
                  </div>
                  <div
                    onClick={handlePdfDownload}
                    className="w-1/2 flex gap-4 h-11 justify-end "
                  >
                    <div>
                      <div className="text-[16px] text-[#000000]">
                        Agreement ID
                      </div>
                      <div className="text-xs text-[#929090]">
                        {consentData.agreement_id}
                      </div>
                    </div>
                    <div
                      className="flex items-center justify-center cursor-pointer hover:opacity-70 transition-opacity"
                      title="Download Agreement PDF"
                    >
                      <Image
                        src={"/pdf.png"}
                        height={100}
                        width={100}
                        alt="pdf"
                        className="size-6"
                      />
                    </div>
                  </div>
                </div>
                <div className="w-full h-px bg-[#EEEEEE] my-2"></div>

                <div className="mb-4 text-lg px-4 space-y-3">
                  <MyPreferences
                    preferenceData={consentData.preferenceData}
                    onSelectionChange={setConsentChanges}
                  />
                </div>
              </div>

              {hasChanges && (
                <div className="mt-4 p-3  border border-gray-300">
                  <p className="text-sm text-red-800">
                    {consentChanges.toRevoke.length > 0 && (
                      <span className="block">
                        ✕ Revoking {consentChanges.toRevoke.length} consent(s)
                      </span>
                    )}
                    {consentChanges.toGive.length > 0 && (
                      <span className="block text-green-500">
                        ✓ Granting {consentChanges.toGive.length} consent(s)
                      </span>
                    )}
                  </p>
                </div>
              )}
              <div className="flex justify-end items-center py-8">
                <Button
                  onClick={handleUpdateConsent}
                  variant="secondary"
                  disabled={!hasChanges || loading}
                >
                  {loading ? "Updating..." : "Update Consent"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Page;
