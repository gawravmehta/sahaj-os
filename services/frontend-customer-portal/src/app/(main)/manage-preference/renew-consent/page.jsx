"use client";

import MyPreferences from "@/components/features/preferenceComponent/MyPreferences";
import Button from "@/components/ui/Button";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import { apiCall } from "@/hooks/apiCall";
import Loader from "@/components/ui/Loader";
import { useRouter } from "next/navigation";
import Breadcrumbs from "@/components/ui/BreadCrumb";
import RenewPreference from "@/components/features/preferenceComponent/RenewPreference";

function Page() {
  const searchParams = useSearchParams();
  const agreementId = searchParams.get("agreement_id");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [consentData, setConsentData] = useState(null);
  const [selectedConsents, setSelectedConsents] = useState([]);

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
                status: consent.consent_status || "unknown",
                expiry: consent.consent_expiry_period || "",
                timestamp: consent.consent_timestamp || "",
                description: consent.description || "",
                cross_border: consent.cross_border || false,
                legal_mandatory: consent.legal_mandatory || false,
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

  const handleRenewConsent = async (de_id, purpose_id) => {
    try {
      setLoading(true);

      const payload = {
        consent_scope: [
          {
            de_id: de_id,
            consent_purposes: [
              {
                purpose_id: purpose_id,
              },
            ],
          },
        ],
      };

      const response = await apiCall(
        `/api/v1/consents/renew-consent/${agreementId}`,
        {
          method: "PATCH",
          data: payload,
        }
      );

      fetchConsentData();
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

  return (
    <div className="mt-20 h-screen  ">
      <div
        className="flex justify-center flex-col items-center 
"
      >
        <div className="flex items-start justify-start  w-[800px] pl-2 ">
          <Breadcrumbs
            path="/manage-preference/renew-consent"
            labels={{
              "/manage-preference/renew-consent": "Renew Consent",
            }}
          />
        </div>
        <div className="flex flex-col w-[800px] pb-12 px-2">
          <div className="flex">
            <div>
              <h1 className="text-[#000000] text-[28px] ">Renew Consent</h1>
              <p className="text-xs  text-subHeading   md:w-[80%]">
                Renew the consents to extend the expiry of your consent purposes
              </p>
            </div>
          </div>

          <div className="w-full flex mt-5">
            <div className="border border-[#C7CFE2] w-full">
              <div className="md:flex gap-4 px-4 py-1">
                <div className="w-1/2 flex items-center">
                  <h1 className="text-[16px] text-[#000000]">
                    Consent Agreement
                  </h1>
                </div>
                <div className="w-1/2 flex gap-4 h-11 justify-end">
                  <div>
                    <div className="text-[16px] text-[#000000]">
                      Agreement ID
                    </div>
                    <div className="text-xs text-[#929090]">
                      {consentData.agreement_id}
                    </div>
                  </div>
                  <div className="flex items-center justify-center">
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
                <RenewPreference
                  preferenceData={consentData.preferenceData}
                  handleRenewConsent={handleRenewConsent}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Page;
