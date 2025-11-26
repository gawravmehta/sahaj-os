import Button from "@/components/ui/Button";
import { InputField, SelectInput } from "@/components/ui/Inputs";
import { apiCall } from "@/hooks/apiCall";
import React, { useEffect, useState } from "react";

const ComplianceStep3 = ({ formData, setFormData, handleInputChange }) => {
  const [dataElementsOptions, setDataElementsOptions] = useState([]);

  const [affectedCount, setAffectedCount] = useState(0);

  const getAllDataElements = async () => {
    try {
      const response = await apiCall(`/data-elements/get-all-data-element`);
      const formattedData = response.data_elements.map((item) => ({
        value: item.de_id,
        label: item.de_name,
      }));
      setDataElementsOptions(formattedData);
    } catch (error) {
      console.error(error);
    }
  };

  const fetchDpData = async () => {
    try {
      const data = await apiCall(`/data-principal/search-data-principals`, {
        method: "POST",
        data: {
          filter: {
            data_elements: formData.data_element,
          },
        },
      });
      setFormData((prev) => ({
        ...prev,
        affected_population: data.count,
      }));
    } catch (error) {
      console.error("Error fetching Dp data:", error);
    }
  };

  useEffect(() => {
    getAllDataElements();
  }, []);

  useEffect(() => {
    fetchDpData();
  }, [formData.data_element]);

  return (
    <div className="w-[480px] p-4">
      <h2 className="font-lato text-[22px] text-[#000000]">Mitigations</h2>
      <p className="mb-5 text-[12px] text-[#000000] opacity-70">
        Enter key dates and check if any reporting or legal rules apply to this
        incident.
      </p>{" "}
      <div className="mt-2 flex flex-col gap-4">
        <SelectInput
          name="consentPurposeDataElements"
          label="Data Element"
          tooltipText="Select the data elements that are relevant to this consent purpose."
          options={dataElementsOptions}
          isMulti
          value={dataElementsOptions.filter((opt) =>
            formData.data_element?.includes(opt.label)
          )}
          placeholder="Select Data Elements"
          onChange={(selected) =>
            setFormData((prev) => ({
              ...prev,
              data_element: selected ? selected.map((opt) => opt.label) : [],
            }))
          }
        />
        <InputField
          label="Affected Population"
          type="number"
          value={formData.affected_population}
          onChange={(e) =>
            handleInputChange("affected_population", Number(e.target.value))
          }
          placeholder="Enter number of affected individuals"
          tooltipText="Approximate number of people affected."
        />

        <h3 className="text-lg">Mitigation Steps</h3>
        <div className="flex flex-col gap-4">
          {formData.mitigation_steps?.map((step, index) => (
            <div key={index} className="flex flex-col gap-2">
              <InputField
                label={`Step ${index + 1}`}
                value={step}
                onChange={(e) => {
                  const newSteps = [...formData.mitigation_steps];
                  newSteps[index] = e.target.value;
                  handleInputChange("mitigation_steps", newSteps);
                }}
                placeholder="Enter mitigation step"
              />
            </div>
          ))}
          <Button
            type="button"
            onClick={() =>
              setFormData((prev) => ({
                ...prev,
                mitigation_steps: [...prev.mitigation_steps, ""],
              }))
            }
            className={"mb-10"}
          >
            Add Mitigation Step
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ComplianceStep3;
