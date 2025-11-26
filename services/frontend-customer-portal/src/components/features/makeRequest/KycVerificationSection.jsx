import Image from "next/image";
import { FaEye } from "react-icons/fa";
import FileUpload from "@/components/FileUpload";
import Button from "@/components/ui/Button";
import { KYC_OPTIONS } from "@/constants/formConstants";

const KycVerificationSection = ({
  selectType,
  handleSelectType,
  fileFront,
  setFileFront,
  fileBack,
  setFileBack,
  existingFiles,
  handleRemoveFile,
  hasKycFiles,
  setShowKycPreview,
}) => {
  return (
    <div className="">
      <div className="flex justify-between items-center">
        <h2 className="text-xl pb-4 lg:2xl">KYC Verification</h2>
        {hasKycFiles() && (
          <Button
            variant="outline"
            type="button"
            onClick={() => setShowKycPreview(true)}
            className="flex items-center gap-2"
          >
            <FaEye className="text-sm" />
            Preview KYC
          </Button>
        )}
      </div>
      <div className="flex flex-col gap-3">
        <div className="min-w-max">Select Type</div>
        <div className="grid sm:grid-cols-3 lg:grid-cols-4 gap-3 w-full">
          {KYC_OPTIONS.map((kyc, index) => (
            <div
              key={index}
              onClick={() => handleSelectType(index)}
              className={`flex items-center border gap-x-4 px-2 py-1 cursor-pointer rounded-md transition-all ${
                selectType === index
                  ? "border-primary border-2 bg-blue-50 shadow-sm"
                  : "border-[#C7CFE2] hover:border-gray-400"
              }`}
            >
              <Image
                src={kyc.src}
                alt={kyc.label}
                height={100}
                width={100}
                className="size-6"
              />
              <div className="text-xs text-[#000000]">{kyc.label}</div>
            </div>
          ))}
        </div>
      </div>

      {(selectType !== false ||
        existingFiles.kycFront ||
        existingFiles.kycBack) && (
        <div className="flex flex-col mt-3">
          <div className="min-w-max">Upload Images</div>
          <div className="sm:flex gap-6">
            <div className="w-1/2">
              <FileUpload
                title="Front Side KYC"
                onFileSelect={setFileFront}
                existingFile={existingFiles.kycFront}
                onRemoveFile={() => handleRemoveFile("front")}
              />
            </div>
            <div className="w-1/2">
              <FileUpload
                title="Back Side KYC"
                onFileSelect={setFileBack}
                existingFile={existingFiles.kycBack}
                onRemoveFile={() => handleRemoveFile("back")}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KycVerificationSection;
