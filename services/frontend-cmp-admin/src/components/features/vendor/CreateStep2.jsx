import { InputField, SelectInput, TextareaField } from "@/components/ui/Inputs";
import YesNoToggle from "@/components/ui/YesNoToggle";

import { countryOptions } from "@/constants/countryOptions";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";

import { useEffect, useState } from "react";
import "react-datepicker/dist/react-datepicker.css";
import toast from "react-hot-toast";
import {
  dataCategoryOptions,
  processingCategoryOptions,
  lawfulBasisOptions,
  frequencyOptions,
  crossBorderMechanismOptions,
} from "@/constants/vendorOptions";

const CreateStep2 = ({
  processing_category,
  setProcessing_category,
  data_categories,
  setData_categories,
  data_location,
  setData_location,
  cross_border,
  setCross_border,
  data_processing_activity,
  setData_processing_activity,
  sub_processors,
  setSub_processors,
  sub_processor,
  setSub_processor,
  legal_basis_of_processing,
  setLegal_basis_of_processing,
  dpdpa_compliance_status,
  setDpdpa_compliance_status,
  data_retention_policy,
  setData_retention_policy,
  missingFields,
  wrongFields,
}) => {
  const [purposeOptions, setPurposeOptions] = useState([]);
  const [dataElementsOptions, setDataElementsOptions] = useState([]);

  const [allDparData, setAllDparData] = useState([]);
  const [loading, setLoading] = useState(false);

  const legalBasisOfProcessingOptions = [
    {
      value: "consent",
      label: "Consent",
    },
    {
      value: "contract",
      label: "Contract",
    },
    {
      value: "legal_obligation",
      label: "Legal Obligation",
    },
    {
      value: "vital_interest",
      label: "Vital Interest",
    },
    {
      value: "public_task",
      label: "Public Task",
    },
    {
      value: "public_interest",
      label: "Public Interest",
    },
    {
      value: "legitimate_interest",
      label: "Legitimate Interest",
    },
  ];

  useEffect(() => {
    getAllDataPurpose();
    getAllDataElement();
    getAllVendors();
  }, []);

  const getAllDataPurpose = async () => {
    let URL = `/purposes/get-all-purposes`;

    try {
      const response = await apiCall(URL);

      const purposesData = response.purposes || response.data || [];

      setPurposeOptions(
        purposesData
          ?.filter((data) => data.purpose_id && data.purpose_title)
          ?.map((data) => ({
            value: data.purpose_id,
            label: data.purpose_title,
          }))
      );
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
      setLoading(false);
    }
  };

  const getAllDataElement = async () => {
    try {
      const response = await apiCall(
        "/data-elements/get-all-data-element?status=published"
      );
      if (response) {
        const dataElements = response.data || response.data_elements || [];

        setDataElementsOptions(
          dataElements
            ?.filter((data) => data?.de_id && data?.de_name)
            ?.map((data) => ({
              value: data?.de_id,
              label: data?.de_name,
            })) || []
        );
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      setDataElementsOptions([]);
    }
  };

  const getAllVendors = async () => {
    try {
      const response = await apiCall(`/vendor/get-all-vendors?sort_order=desc`);

      if (response) {
        setAllDparData(
          response?.vendors
            ?.filter((data) => data?._id && data?.dpr_name)
            ?.map((data) => ({
              value: data?._id,
              label: data?.dpr_name,
            }))
        );
      }
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
      setLoading(false);
    }
  };

  return (
    <div className="flex w-full max-w-lg flex-col px-3 py-6">
      <h1 className="text-[22px]">Data Processing & Compliance</h1>
      <p className="mb-6 text-xs text-subHeading">
        Outlines how data is processed, shared, and retained to ensure lawful
        and transparent operations.
      </p>
      <div className="flex flex-col gap-3.5 px-1 pb-6">
        <div className="flex flex-col gap-3">
          <SelectInput
            name="processing_category"
            label="Processing Category "
            className="mb-0.9"
            tooltipText="Types of data processing operations."
            options={processingCategoryOptions}
            value={processingCategoryOptions?.filter((option) =>
              processing_category?.includes(option?.value)
            )}
            onChange={(selectedOptions) =>
              setProcessing_category(selectedOptions?.map((opt) => opt.value))
            }
            isMulti
            placeholder="Select Processing Category"
            missingFields={missingFields}
          />
          <SelectInput
            name="data_categories"
            label="Data Categories "
            tooltipText="Types of data being handled.
"
            options={dataCategoryOptions}
            value={dataCategoryOptions?.filter((option) =>
              data_categories?.includes(option?.value)
            )}
            onChange={(selectedOptions) =>
              setData_categories(selectedOptions?.map((opt) => opt?.value))
            }
            isMulti
            placeholder="Select Data Categories"
            missingFields={missingFields}
            className="mt-0.5"
          />

          <SelectInput
            name="dpr_security_policy"
            label="Purpose"
            options={purposeOptions}
            className="mb-0.5"
            isMulti={true}
            value={purposeOptions.filter((option) =>
              data_processing_activity.some(
                (activity) => activity.purpose_id === option.value
              )
            )}
            onChange={(selected) => {
              const selectedPurposes = selected || [];
              const updatedActivities = selectedPurposes.map((p) => {
                const existing = data_processing_activity.find(
                  (a) => a.purpose_id === p.value
                );
                return (
                  existing || {
                    activity_name: "",
                    purpose_id: p.value,
                    purpose: p.label,
                    lawful_basis: "",
                    data_elements: [],
                    frequency: "",
                    storage_location: "",
                  }
                );
              });
              setData_processing_activity(updatedActivities);
            }}
            placeholder="Select Purposes"
            tooltipText="Why this activity is carried out."
            missingFields={missingFields}
          />

          {data_processing_activity.length > 0 &&
            data_processing_activity?.map((activity, index) => (
              <div
                key={activity.purpose_id}
                className="border border-[#d4d1d1] p-3 my-2 flex flex-col gap-3"
              >
                <h4 className=" mb-2">
                  <span className="font-semibold">For Purpose</span> :{" "}
                  {activity.purpose}
                </h4>

                <InputField
                  name={`activity_name_${index}`}
                  label="Activity Name"
                  placeholder={"Enter Activity Name"}
                  value={activity.activity_name}
                  onChange={(e) => {
                    const updated = [...data_processing_activity];
                    updated[index].activity_name = e.target.value;
                    setData_processing_activity(updated);
                  }}
                />

                <SelectInput
                  name={`lawful_basis_${index}`}
                  label="Lawful Basis"
                  placeholder={"Select Lawful Basis"}
                  options={lawfulBasisOptions}
                  value={
                    lawfulBasisOptions.find(
                      (opt) => opt.value === activity.lawful_basis
                    ) || null
                  }
                  onChange={(selected) => {
                    const updated = [...data_processing_activity];
                    updated[index].lawful_basis = selected?.value || "";
                    setData_processing_activity(updated);
                  }}
                />

                <SelectInput
                  name={`data_elements_${index}`}
                  label="Data Elements"
                  options={dataElementsOptions}
                  isMulti={true}
                  placeholder={"Select Data Elements"}
                  value={dataElementsOptions.filter((opt) =>
                    activity.data_elements.includes(opt.value)
                  )}
                  onChange={(selected) => {
                    const updated = [...data_processing_activity];
                    updated[index].data_elements = selected
                      ? selected.map((s) => s.value)
                      : [];
                    setData_processing_activity(updated);
                  }}
                />

                <InputField
                  name={`frequency_${index}`}
                  label="Frequency"
                  placeholder="Enter Frequency"
                  value={activity.frequency}
                  onChange={(e) => {
                    const updated = [...data_processing_activity];
                    updated[index].frequency = e.target.value;
                    setData_processing_activity(updated);
                  }}
                />

                <InputField
                  name={`storage_location_${index}`}
                  label="Storage Location"
                  placeholder="Enter Storage Location"
                  value={activity.storage_location}
                  onChange={(e) => {
                    const updated = [...data_processing_activity];
                    updated[index].storage_location = e.target.value;
                    setData_processing_activity(updated);
                  }}
                />
              </div>
            ))}
        </div>

        <div className="">
          <TextareaField
            name={"dpr_address"}
            label="Data Retention Policy"
            value={data_retention_policy}
            className="h-20 mb-1"
            onChange={(e) => setData_retention_policy(e.target.value)}
            placeholder="Write Retention Policy"
            tooltipText="Duration for which data is retained.
"
          />
          <SelectInput
            name="dpr_country_risk"
            label="Data Storage Location"
            tooltipText="Countries where data is stor"
            value={countryOptions.filter((item) =>
              data_location.includes(item.value)
            )}
            onChange={(selectedOptions) =>
              setData_location(selectedOptions.map((option) => option.value))
            }
            options={countryOptions}
            placeholder="Select Data Storage Location"
            className="w-full mb-0.1"
            isMulti={true}
          />
        </div>
        <div className="flex w-full gap-5">
          <div className="w-1/2">
            <YesNoToggle
              key={"dpr_country"}
              name={"dpr_country"}
              label="Cross Border Transfer "
              tooltipText="Whether data is transferred outside India."
              value={cross_border}
              onChange={() => setCross_border(!cross_border)}
              className="w-full "
            />
          </div>

          <div className="w-1/2">
            <YesNoToggle
              name={"Sub-Processors"}
              label="Uses Sub-Processors"
              tooltipText="
Whether any third-party processors are involved.
"
              value={sub_processor}
              onChange={() => setSub_processor(!sub_processor)}
              className="w-full mb-0.5"
            />
          </div>
        </div>

        {sub_processor && (
          <SelectInput
            name="Addsubprocessors"
            label="Add Sub-Processors"
            className="mb-0.5"
            options={allDparData}
            value={allDparData?.filter((option) =>
              sub_processors?.includes(option?.value)
            )}
            onChange={(selectedOptions) =>
              setSub_processors(selectedOptions?.map((opt) => opt.value))
            }
            placeholder="Select Sub-Processors"
            isMulti={true}
          />
        )}

        <div className="mb-5 flex flex-col gap-3">
          <SelectInput
            name="dpr_country_risk"
            label="Legal Basis of Processing"
            tooltipText="Legal justification for processing.
"
            value={
              legalBasisOfProcessingOptions.find(
                (item) => item.value === legal_basis_of_processing
              ) || null
            }
            onChange={(selectedOptions) =>
              setLegal_basis_of_processing(selectedOptions.value || "")
            }
            options={legalBasisOfProcessingOptions}
            placeholder="Select Legal Basic of Processing "
            className="w-full mb-0.5"
          />
          <div className="flex w-full gap-5">
            <div className="w-1/2">
              <YesNoToggle
                key={"dpr_country"}
                name={"Signed DPA"}
                label="Signed DPA"
                tooltipText="Whether a Data Processing Agreement is signed.
"
                value={dpdpa_compliance_status.signed_dpa}
                onChange={() =>
                  setDpdpa_compliance_status((prev) => ({
                    ...prev,
                    signed_dpa: !prev.signed_dpa,
                  }))
                }
                className="w-full mb-0.5"
              />
            </div>

            <div className="w-1/2">
              <YesNoToggle
                name={"Sub-Processors"}
                label="Transfer Outside India"
                tooltipText="Whether data is transferred outside India"
                value={dpdpa_compliance_status.transfer_outside_india}
                onChange={() =>
                  setDpdpa_compliance_status((prev) => ({
                    ...prev,
                    transfer_outside_india: !prev.transfer_outside_india,
                  }))
                }
                className="w-full mb-0.5"
              />
            </div>
          </div>
          <SelectInput
            name="dpr_country_risk"
            label="Cross Border Mechanism"
            tooltipText="Legal safeguard used for cross-border transfers.
"
            options={crossBorderMechanismOptions}
            value={
              crossBorderMechanismOptions.find(
                (item) =>
                  item.value === dpdpa_compliance_status.cross_border_mechanism
              ) || null
            }
            onChange={(selectedOption) =>
              setDpdpa_compliance_status((prev) => ({
                ...prev,
                cross_border_mechanism: selectedOption?.value || "",
              }))
            }
            placeholder="Select Cross Border Mechanism"
            className="w-full mb-0.5"
          />
          <InputField
            name="dpr_security_policy"
            label="Breach Notification Time"
            value={dpdpa_compliance_status?.breach_notification_time || ""}
            onChange={(e) =>
              setDpdpa_compliance_status((prev) => ({
                ...prev,
                breach_notification_time: e.target.value,
              }))
            }
            placeholder="Enter Breach Notification Time"
            tooltipText="Max time allowed to report a data breach.
"
            missingFields={missingFields}
          />
        </div>
      </div>
    </div>
  );
};

export default CreateStep2;
