import { SelectInput } from "@/components/ui/Inputs";
import YesNoToggle from "@/components/ui/YesNoToggle";
import FileUpload from "@/components/FileUpload";
import { RELATED_REQUEST_TYPE } from "@/constants/formConstants";

const RelatedRequestSection = ({
  formData,
  setFormData,
  relatedRequestType,
  setRelatedRequestType,
  attachmentFiles,
  setAttachmentFiles,
  existingFiles,
  handleRemoveFile,
}) => {
  return (
    <>
      <div className="">
        <YesNoToggle
          label="Is this request related to another request?"
          value={formData.relatedRequest}
          onChange={(name, value) => {
            setFormData((prev) => ({
              ...prev,
              relatedRequest: value,
            }));
            if (!value) setRelatedRequestType(null);
          }}
          tooltipText="Your email address"
        />
      </div>

      {formData.relatedRequest && (
        <>
          <SelectInput
            label="Related Request Type"
            options={RELATED_REQUEST_TYPE}
            value={relatedRequestType}
            onChange={(selected) => setRelatedRequestType(selected)}
            placeholder="Select request type"
            className="w-full"
          />

          <div className="md:flex flex-col w-full">
            <h2 className="text-sm text-[#000000]">Upload Documents</h2>
            <div className="w-full">
              <FileUpload
                title="Supporting Documents"
                onFileSelect={setAttachmentFiles}
                existingFiles={existingFiles.attachments}
                onRemoveFile={() => handleRemoveFile("attachment")}
                multiple
              />
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default RelatedRequestSection;
