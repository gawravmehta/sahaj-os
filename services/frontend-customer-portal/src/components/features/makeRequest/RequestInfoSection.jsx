import { SelectInput, TextareaField } from "@/components/ui/Inputs";
import {
  REQUEST_TYPE_OPTIONS,
  PRIORITY_OPTIONS,
  FORM_TEXT,
} from "@/constants/formConstants";

const RequestInfoSection = ({
  requestType,
  setRequestType,
  choosePriority,
  setChoosePriority,
  formData,
  handleChange,
}) => {
  return (
    <>
      <h2 className="text-xl lg:2xl">{FORM_TEXT.REQUEST_INFO}</h2>
      <div className="sm:flex w-full gap-6">
        <div className="w-1/2">
          <SelectInput
            label="Request Type"
            options={REQUEST_TYPE_OPTIONS}
            value={requestType}
            onChange={(selected) => setRequestType(selected)}
            placeholder="Select request"
            tooltipText="Your email address"
          />
        </div>
        <div className="w-1/2">
          <SelectInput
            label="Request Priority"
            options={PRIORITY_OPTIONS}
            value={choosePriority}
            onChange={(selected) => setChoosePriority(selected)}
            placeholder="Choose Priority"
            tooltipText="Your email address"
          />
        </div>
      </div>
      <TextareaField
        label="Request Details"
        name="requestDetails"
        placeholder="Write details"
        value={formData.requestDetails}
        onChange={handleChange}
      />
    </>
  );
};

export default RequestInfoSection;
