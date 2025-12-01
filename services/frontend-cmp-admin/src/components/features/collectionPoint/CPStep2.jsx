"use client";

import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { IoIosAdd, IoIosArrowUp } from "react-icons/io";
import { GrSubtractCircle } from "react-icons/gr";
import Button from "@/components/ui/Button";
import { InputField, SelectInput } from "@/components/ui/Inputs";
import { languagesOptions } from "@/constants/countryOptions";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import ShowPurposeModal from "./ShowPurposeModal";
import YesNoToggle from "@/components/ui/YesNoToggle";
import { customStyles } from "@/utils/selectCustomStyles";

const Notice_TYPE_OPTIONS = [
  {
    value: "single",
    label: "Simple",
    description:
      "A short, easy-to-understand notice used when only minimal data is collected for a very limited purpose. It provides quick clarity without overwhelming the user.",
  },
  {
    value: "multiple",
    label: "Multiple",
    description:
      "Used when several personal data elements are collected, but the purposes are still limited and clearly defined. Allows users to choose consent for different data items or activities.",
  },
  {
    value: "layered",
    label: "Layered",
    description:
      "Ideal when collecting a wide range of PII for multiple or complex purposes. Gives a brief summary upfront with detailed information available in expandable layers.",
  },
  {
    value: "boxed",
    label: "Boxed",
    description:
      "A compact, visually boxed section showing essential information for simple data and consent collection. Helps users see key points at a glance without reading long text.",
  },
];

const VERIFICATION_DONE_BY_OPTIONS = [
  { value: "df", label: "Data Fiducary" },
  { value: "sahaj", label: "Sahaj" },
];

const PREFERED_VERIFICATION_MEDIUM = [
  { value: "email", label: "Email" },
  // { value: "mobile", label: "Mobile" },
];

const CPStep2 = ({ formData, setFormData, missingFields }) => {
  const [dataElementOptions, setDataElementOptions] = useState([]);
  const [purposeOptions, setPurposeOptions] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPageState, setRowsPerPageState] = useState(100);
  const [totalPages, setTotalPages] = useState();
  const [selectedDeForPurpose, setSelectedDeForPurpose] = useState(null);
  const [showPurposes, setShowPurposes] = useState(false);
  const [openAccordion, setOpenAccordion] = useState({});

  useEffect(() => {
    (async () => {
      try {
        const res = await apiCall("/data-elements/get-all-data-element");
        setDataElementOptions(
          res.data_elements?.map((item) => ({
            value: item.de_id,
            label: item.de_name,
          })) || []
        );
      } catch (error) {
        toast.error(getErrorMessage(error));
      }
    })();
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const res = await apiCall(
          `/purposes/get-all-purposes?current_page=${currentPage}&data_per_page=${rowsPerPageState}`
        );
        setPurposeOptions(res.purposes);
        setCurrentPage(res.current_page);
        setRowsPerPageState(res.data_per_page);
        setTotalPages(res.total_pages);
      } catch (error) {
        toast.error(getErrorMessage(error));
      }
    })();
  }, [currentPage, rowsPerPageState]);

  const handleAddPurpose = (de) => {
    setShowPurposes(true);
    setSelectedDeForPurpose(de);
  };

  const handleRemovePurpose = (deId, purposeId) => {
    const updatedDataElements = formData.data_elements.map((de) =>
      de.de_id === deId
        ? {
            ...de,
            purposes: de.purposes.filter((p) => p.purpose_id !== purposeId),
          }
        : de
    );

    setFormData({ ...formData, data_elements: updatedDataElements });
  };

  useEffect(() => {
    if (!formData.currentDataElement) return;

    setFormData((prev) => {
      const mappedDataElements = prev.currentDataElement.map((de) => {
        const existingDE = prev.data_elements?.find(
          (d) => d.de_id === de.value
        );
        return {
          de_id: de.value,
          de_name: de.label,
          purposes: existingDE?.purposes || [],
        };
      });

      return { ...prev, data_elements: mappedDataElements };
    });
  }, [formData.currentDataElement]);

  const toggleAccordion = (id) =>
    setOpenAccordion((prev) => ({ ...prev, [id]: !prev[id] }));

  const noticeTypeStyles = {
    ...customStyles,
    option: (base, state) => ({
      ...customStyles.option(base, state),
      color: state.isSelected ? "#ffffff" : "#4b5563",
    }),
    singleValue: (base) => ({
      ...customStyles.singleValue(base),
      color: "#4b5563",
    }),
  };

  return (
    <div className="custom-scrollbar h-[calc(100vh-239px)] w-full overflow-auto">
      <div className="mx-auto flex w-full max-w-lg flex-col px-3 pb-3 pt-6">
        <h1 className="text-[28px] leading-9">Details</h1>
        <p className="mb-6 mt-0.5 text-xs text-subHeading">
          Select data elements and assign relevant purposes for this collection
          point.
        </p>

        <div className="flex flex-col gap-4">
          <SelectInput
            name="notice_type"
            label="Notice Type"
            options={Notice_TYPE_OPTIONS}
            value={
              Notice_TYPE_OPTIONS.find(
                (item) => item.value === formData.notice_type
              ) || null
            }
            onChange={(e) => setFormData({ ...formData, notice_type: e.value })}
            placeholder="Select Type"
            tooltipText="Select the type of notice for the collection point."
            isClearable={false}
            required
            missingFields={missingFields}
            styles={noticeTypeStyles}
            formatOptionLabel={({ label, description }, { context }) => (
              <div className="flex flex-col">
                <span className="font-medium">{label}</span>
                {context === "menu" && description && (
                  <span className="text-xs font-normal">{description}</span>
                )}
              </div>
            )}
          />
          <InputField
            name={"notice_popup_window_timeout"}
            label={"Notice Popup Window Timeout (in Minutes)"}
            placeholder={"Enter Notice Popup Window Timeout"}
            value={formData.notice_popup_window_timeout}
            onChange={(e) =>
              setFormData({
                ...formData,
                notice_popup_window_timeout: e.target.value,
              })
            }
          />
          <YesNoToggle
            label="Is Verification Required?"
            value={formData.is_verification_required}
            onChange={() =>
              setFormData((prev) => ({
                ...prev,
                is_verification_required: !prev.is_verification_required,
              }))
            }
            tooltipText="Select whether authentication is required for this collection point."
            tooltipCss={"gap-3"}
          />
          {formData.is_verification_required && (
            <div className="flex flex-col gap-4">
              <SelectInput
                name="verification_done_by"
                label={"Verification Done By"}
                options={VERIFICATION_DONE_BY_OPTIONS}
                value={
                  VERIFICATION_DONE_BY_OPTIONS.find(
                    (item) => item.value === formData.verification_done_by
                  ) || null
                }
                onChange={(e) =>
                  setFormData({ ...formData, verification_done_by: e.value })
                }
                placeholder="Select Verification Done By"
                tooltipText="Select the method by which verification is done for this collection point."
                required
                missingFields={missingFields}
              />
              <SelectInput
                name="prefered_verification_medium"
                label="Prefered Verification Medium"
                options={PREFERED_VERIFICATION_MEDIUM}
                value={
                  PREFERED_VERIFICATION_MEDIUM.find(
                    (item) =>
                      item.value === formData.prefered_verification_medium
                  ) || null
                }
                onChange={(val) =>
                  setFormData({
                    ...formData,
                    prefered_verification_medium: val.value,
                  })
                }
                placeholder="Select Prefered Verification Medium"
                tooltipText="Select the preferred verification medium for this collection point."
                missingFields={missingFields}
              />
            </div>
          )}
          <SelectInput
            name="dataElements"
            label="Data Elements"
            options={dataElementOptions}
            value={formData.currentDataElement}
            onChange={(val) =>
              setFormData({ ...formData, currentDataElement: val })
            }
            isMulti
            placeholder="Select Data Elements"
            tooltipText="Choose published data elements to link with this collection point."
            missingFields={missingFields}
          />

          {formData.currentDataElement?.map((de) => {
            const isOpen = openAccordion[de.value] || false;

            const purposes =
              formData.data_elements.find((d) => d.de_id === de.value)
                ?.purposes || [];

            return (
              <div key={de.value} className="border-b border-gray-200 pb-4">
                <div className="flex cursor-pointer items-center justify-between gap-2">
                  <div
                    onClick={() => toggleAccordion(de.value)}
                    className="flex w-full items-center gap-2"
                  >
                    <IoIosArrowUp
                      className={`text-placeholder transition-transform duration-300 ${
                        isOpen ? "rotate-0" : "rotate-180"
                      }`}
                    />
                    <span className="font-medium">
                      Collecting{" "}
                      <span className="italic border-gray-200 border font-light bg-gray-100 px-2 text-gray-600 rounded-sm">
                        {de.label}
                      </span>{" "}
                      for:
                    </span>
                  </div>
                  <Button
                    variant="secondary"
                    onClick={() => handleAddPurpose(de)}
                    className="h-6 text-sm"
                  >
                    <IoIosAdd size={16} /> Purposes
                  </Button>
                </div>

                {isOpen && (
                  <>
                    {purposes.length > 0 ? (
                      <div className="ml-6 mt-4 space-y-2">
                        {purposes.map((p, idx) => (
                          <div
                            key={p.purpose_id}
                            className="flex items-center justify-between gap-4"
                          >
                            <span className="mb-2 w-full border border-gray-200 bg-[#fdfdfd] p-2 text-sm">
                              {idx + 1}. {p.purpose_title}
                            </span>
                            <button
                              onClick={() =>
                                handleRemovePurpose(de.value, p.purpose_id)
                              }
                              className="flex items-center justify-center text-red-600 hover:text-red-800"
                            >
                              <GrSubtractCircle size={20} className="mr-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="py-2 text-center text-sm text-gray-500">
                        No Purposes Selected
                      </p>
                    )}
                  </>
                )}
              </div>
            );
          })}

          <SelectInput
            name="preferredLanguage"
            label="Preferred Language"
            options={languagesOptions}
            value={
              languagesOptions.find(
                (opt) => opt.alt == formData.default_language
              ) || null
            }
            onChange={(selected) =>
              setFormData({ ...formData, default_language: selected.alt })
            }
            isClearable={false}
            placeholder="Select Default Language"
            tooltipText="Select the preferred language for the collection point. This will be used as the default language for notices and data elements."
          />
        </div>

        {showPurposes && (
          <ShowPurposeModal
            selectedDeForPurpose={selectedDeForPurpose}
            purposeOptions={purposeOptions}
            totalPages={totalPages}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            rowsPerPageState={rowsPerPageState}
            setRowsPerPageState={setRowsPerPageState}
            setShowPurposes={setShowPurposes}
            existingPurposes={
              formData.data_elements.find(
                (d) => d.de_id === selectedDeForPurpose?.value
              )?.purposes || []
            }
            formData={formData}
            setFormData={setFormData}
          />
        )}
      </div>
    </div>
  );
};

export default CPStep2;
