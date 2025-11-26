"use client";

import Button from "@/components/ui/Button";
import { SelectInput, TextareaField } from "@/components/ui/Inputs";
import YesNoToggle from "@/components/ui/YesNoToggle";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import Link from "next/link";
import { useEffect, useState } from "react";
import "react-datepicker/dist/react-datepicker.css";
import toast from "react-hot-toast";
import { MdKeyboardArrowDown, MdKeyboardArrowUp } from "react-icons/md";

const CreateStep2 = ({
  formData,
  updateField,
  missingFields = [],
  wrongFields = [],
}) => {
  const [filteredData, setFilteredData] = useState([]);
  const [openElement, setOpenElement] = useState(
    formData.data_elements?.[0]?.de_id || null
  );
  const toggleDropdown = (id) => {
    setOpenElement(openElement === id ? null : id);
  };

  useEffect(() => {
    getAllDataPrincipals();
  }, []);

  const getAllDataPrincipals = async () => {
    try {
      const response = await apiCall(`/data-elements/get-all-data-element`);
      setFilteredData(response.data_elements);
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error(error);
    }
  };

  const dataElementOption = filteredData?.map((item) => ({
    value: item.de_id,
    label: item.de_name,
  }));

  const handleDataElementChange = (selectedOptions) => {
    const updatedElements = selectedOptions.map((option) => {
      const existing = formData.data_elements.find(
        (el) => el.de_id === option.value
      );

      return (
        existing || {
          de_id: option.value,
          de_name: option.label,
          service_mandatory: false,
          service_message: "",
          legal_mandatory: false,
          legal_message: "",
        }
      );
    });

    updateField(
      "consentPurposeDataElements",
      selectedOptions.map((opt) => ({
        de_id: opt.value,
        de_name: opt.label,
      }))
    );

    updateField("data_elements", updatedElements);
  };

  const updateDataElementField = (de_id, key, value) => {
    const updated = formData.data_elements.map((el) =>
      el.de_id === de_id ? { ...el, [key]: value } : el
    );
    updateField("data_elements", updated);
  };

  return (
    <div className="flex w-full max-w-lg flex-col px-3 py-6">
      <h1 className="text-[22px]">Legal and Compliance</h1>
      <p className="mb-6 text-xs text-subHeading">
        Enter details related to the user and security aspects of the data
        element to ensure compliance and protection.
      </p>

      <div className="flex flex-col gap-3.5 px-1 pb-6">
        <div>
          <div className="flex justify-end">
            <Link className="-mb-5 mr-7" href="/apps/data-element">
              <Button variant="secondary" className="h-7 text-xs">
                Create Data Element
              </Button>
            </Link>
          </div>

          <SelectInput
            name="consentPurposeDataElements"
            label="Data Element"
            tooltipText="Select the data elements that are relevant to this consent purpose."
            options={dataElementOption}
            isMulti
            value={formData.data_elements?.map((item) => ({
              value: item.de_id,
              label: item.de_name,
            }))}
            onChange={handleDataElementChange}
            placeholder="Select Data Elements"
          />
        </div>

        <div className="mb-5 flex flex-col gap-3">
          {formData.data_elements?.map((element) => (
            <div
              key={element.de_id}
              className="border border-[#d4d1d1] bg-white"
            >
              <button
                type="button"
                onClick={() => toggleDropdown(element.de_id)}
                className="flex w-full items-center justify-between px-4 py-3 text-left text-gray-600 hover:bg-gray-50"
              >
                <span className="font-medium">{element.de_name}</span>
                {openElement === element.de_id ? (
                  <MdKeyboardArrowUp className="h-5 w-5 text-gray-500" />
                ) : (
                  <MdKeyboardArrowDown className="h-5 w-5 text-gray-500" />
                )}
              </button>

              {openElement === element.de_id && (
                <div className="border-t border-[#d4d1d1] px-4 py-3 space-y-4">
                  <YesNoToggle
                    name={`service_mandatory_${element.de_id}`}
                    label="Is this data element mandatory for business?"
                    tooltipText="Mark yes if this data element is mandatory for business purpose."
                    value={element.service_mandatory}
                    onChange={(field, value) =>
                      updateDataElementField(
                        element.de_id,
                        "service_mandatory",
                        value
                      )
                    }
                  />

                  {element.service_mandatory && (
                    <TextareaField
                      name={`service_message_${element.de_id}`}
                      label="Mandatory Message"
                      tooltipText="Message shown to users when the data is legally required."
                      value={element.service_message}
                      onChange={(e) =>
                        updateDataElementField(
                          element.de_id,
                          "service_message",
                          e.target.value
                        )
                      }
                      placeholder="Write a mandatory message"
                    />
                  )}

                  <YesNoToggle
                    name={`legal_mandatory_${element.de_id}`}
                    label="Do you have legal basis for this element?"
                    tooltipText="Mark yes if you have legal basis for this element."
                    value={element.legal_mandatory}
                    onChange={(field, value) =>
                      updateDataElementField(
                        element.de_id,
                        "legal_mandatory",
                        value
                      )
                    }
                  />

                  {element.legal_mandatory && (
                    <TextareaField
                      name={`legal_message_${element.de_id}`}
                      label="Justification"
                      tooltipText="Message shown to users when the data is legally required."
                      value={element.legal_message}
                      onChange={(e) =>
                        updateDataElementField(
                          element.de_id,
                          "legal_message",
                          e.target.value
                        )
                      }
                      placeholder="Write a justification"
                    />
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CreateStep2;
