"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import MyPreferences from "@/components/features/preferenceComponent/MyPreferences";
import PIICollected from "@/components/features/preferenceComponent/PIICollected";
import DataProcessor from "@/components/features/preferenceComponent/DataProcessor";
import { apiCall } from "@/hooks/apiCall";
import Button from "@/components/ui/Button";
import Loader from "@/components/ui/Loader";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";

function Page() {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [collectionPoints, setCollectionPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [agreementIds, setAgreementIds] = useState([]);
  const [processors, setProcessors] = useState([]);
  const [dataElements, setDataElements] = useState([]);

  useEffect(() => {
    if (!localStorage.getItem("privacy_modal")) {
      localStorage.setItem("privacy_modal", true);
    }
    if (localStorage.getItem("privacy_modal") === "true") {
      return;
    }
  }, []);

  const fetchDataElements = async () => {
    try {
      const response = await apiCall(`/api/v1/preferences/data-elements/by-dp`);

      setDataElements(response?.data_elements);

      const allProcessors =
        response?.data_elements?.flatMap((el) => el.data_processors || []) ??
        [];

      setProcessors(allProcessors);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchDataElements();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await apiCall(
          `/api/v1/preferences/get-all-consent-transactions`
        );

        const data =
          typeof response === "string" ? JSON.parse(response) : response;

        if (!data.data) {
          throw new Error("Invalid data format from API");
        }

        const transformedData = data.data.map((item, index) => ({
          cp_name: item.artifact?.cp_name || "Consent Point",
          agreement_id: item.artifact?.agreement_id || "",
          preferenceData:
            item.artifact?.consent_scope?.data_elements?.map((element) => ({
              title: element.title || "No Title",
              data_retention_period: element.data_retention_period || "",
              consents:
                element.consents?.map((consent) => ({
                  title: consent.purpose_title || "No Purpose Title",
                  status: consent.consent_status,
                  expiry: consent.consent_expiry_period || "",
                  is_legal_mandatory: consent.is_legal_mandatory,
                  legal_mandatory_message: consent.legal_mandatory_message,
                  is_service_mandatory: consent.is_service_mandatory,
                  service_mandatory_message: consent.service_mandatory_message,
                })) || [],
            })) || [],
        }));

        setCollectionPoints(transformedData);
        setAgreementIds(transformedData.map((item) => item.agreement_id));
      } catch (error) {
        toast.error(getErrorMessage(error));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="">
        <div className="flex justify-center items-center w-full  ">
          <Loader />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-10">
        <div className="flex flex-col w-[622px] py-12 ">
          <div className="flex justify-center items-center h-64">
            <p className="text-red-500">Error: {error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-14 flex justify-center ">
      <div className="flex flex-col w-[800px] py-5  ">
        <div className="sm:flex justify-between ">
          <div className="max-w-md">
            <h1 className="text-[#000000] font-semibold text-[28px] ">
              Privacy Preference Centre
            </h1>
            <p className="text-sm text-subHeading ">
              Control how your personal data is collected, used, and shared.
              Update your preferences anytime.
            </p>
          </div>
          <div className="flex gap-2 items-center">
            <Link
              href={`/manage-preference/update-preference?agreement_id=${agreementIds[selectedIndex]}`}
            >
              <Button variant="secondary" className="w-38">
                Update Preferences
              </Button>
            </Link>
            <Link
              href={`/manage-preference/renew-consent?agreement_id=${agreementIds[selectedIndex]}`}
            >
              <Button variant="secondary">Renew Consent</Button>
            </Link>
          </div>
        </div>
        <div>
          <div className="py-4 space-y-2 md:space-y-0 w-full md:flex gap-4">
            <div className="w-full flex flex-col gap-3">
              <div className="flex">
                <div className="border border-[#C7CFE2] md:min-w-[29%] py-2">
                  <h2 className="  text-[#000000] px-4 py-2 border-b border-[#C7CFE2]">
                    Collection Points
                  </h2>
                  <ul className="text-sm">
                    {collectionPoints.map((point, index) => {
                      const isSelected = selectedIndex === index;
                      return (
                        <li
                          key={index}
                          onClick={() => setSelectedIndex(index)}
                          className={`flex items-center justify-between px-4 py-2 border-b border-[#C7CFE2] cursor-pointer ${
                            isSelected ? "bg-gray-100" : "bg-white"
                          } hover:bg-gray-50`}
                        >
                          <span className="text-gray-800 capitalize">
                            {point.cp_name.replace(/_/g, " ")}
                          </span>
                          {isSelected && (
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="w-4 h-4 text-gray-700"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                              strokeWidth={2}
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </div>

                <div className="border border-[#C7CFE2] min-h-[50vh] overflow-y-auto w-full sm:px-8 py-2">
                  <div className="flex justify-between items-center mb-2">
                    <h1 className="text-[#000000] ">My Privacy Preference</h1>{" "}
                  </div>
                  <div className="space-y-2">
                    <MyPreferences
                      preferenceData={
                        collectionPoints[selectedIndex]?.preferenceData || []
                      }
                      isDisabled={true}
                      hideMandatory={true}
                    />
                  </div>
                </div>
              </div>
              <div className="flex flex-col w-full gap-3">
                <PIICollected dataElements={dataElements} />
                <DataProcessor processors={processors} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Page;
