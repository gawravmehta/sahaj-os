import { InputField, SelectInput, TextareaField } from "@/components/ui/Inputs";
import Image from "next/image";
import { useRef, useState } from "react";
import FileUpload from "./FileUpload";

const StepTwo = ({
  entity,
  setEntity,
  priority,
  setPriority,
  type,
  setType,
  relatedType,
  setRelatedType,
  relatedRequest,
  setRelatedRequest,
}) => {
  const entityOptions = ["Entity 01", "Entity 02", "Entity 03", "Entity 04"];
  const typeOptions = ["Type 01", "Type 02", "Type 03", "Type 04"];
  const requestTypeOptions = [
    "Request Type 01",
    "Request Type 02",
    "Request Type 03",
  ];

  const handleEntity = (entityOptions) => {
    setPriority(entityOptions);
  };
  const handleType = (typeOptions) => {
    setType(typeOptions);
  };
  const handleRelatedType = (requestTypeOptions) => {
    setRelatedType(requestTypeOptions);
  };

  const createOptions = (options) => {
    return options.map((option) => ({
      label: option,
      value: option.toLowerCase().replace(/\s+/g, "-"),
    }));
  };

  const formattedEntityOptions = createOptions(entityOptions);
  const formattedTypeOptions = createOptions(typeOptions);
  const formattedRequestTypes = createOptions(requestTypeOptions);

  return (
    <div className="">
      <h1 className="text-[22px] font-semibold text-heading">
        Request Details
      </h1>
      <p className="text-xs font-light text-subHeading">
        Fill in the request information for processing your inquiry.
      </p>

      <div className="mt-3 flex gap-3">
        <div className="mb-2 flex w-full flex-col">
          <SelectInput
            label=" Type"
            options={formattedTypeOptions}
            value={type}
            onChange={handleType}
            placeholder="Select Type"
            required={false}
          />
        </div>

        <div className="mb-2 flex w-full flex-col">
          <SelectInput
            label="Priority"
            options={formattedEntityOptions}
            value={priority}
            onChange={handleEntity}
            placeholder="Select Priority"
            required={false}
          />
        </div>
      </div>
      <div className="mt-3 flex flex-col gap-3">
        <InputField
          label="Related Request"
          placeholder="Enter Request ID."
          value={relatedRequest}
          onChange={(e) => setRelatedRequest(e.target.value)}
          required
        />
        <SelectInput
          label="Related Request Type"
          options={formattedRequestTypes}
          value={relatedType}
          onChange={handleRelatedType}
          placeholder="Select Request Type"
          required={false}
        />
      </div>
      <div className="mb-4 mt-3">
        <TextareaField
          label="Message"
          placeholder="Write Message"
          required={false}
        />
      </div>
    </div>
  );
};

export default StepTwo;
