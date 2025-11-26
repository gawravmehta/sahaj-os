import UploadFile from "@/components/features/principalManagement/import/UploadFile.jsx";
import UploadSucessfully from "@/components/features/principalManagement/import/UploadSucessfully";
import { usePathname } from "next/navigation";

const BulkAddDP = ({
  uploadComplete,
  uploadedFiles,
  setUploadedFiles,
  uploadProgress,
  uploading,
  tags,
  setTags,
  tagOptions,
  setTagOptions,
  isLegacy,
  setIsLegacy,
  selectedPersona,
  setSelectedPersona,
  missingFields
}) => {
  const pathname = usePathname();

  return (
    <div className="custom-scrollbar relative h-[calc(100vh-200px)] overflow-auto">
      {uploadComplete ? (
        <div className="flex h-[80%] items-center justify-center">
          <UploadSucessfully dpLength={uploadComplete} pathname={pathname} />
        </div>
      ) : (
        <div className="flex w-full justify-center gap-8 pt-5">
          <div className="h-full w-[35%]">
            <UploadFile
              pathname={pathname}
              setUploadedFiles={setUploadedFiles}
              uploadedFiles={uploadedFiles}
              uploadProgress={uploadProgress}
              uploading={uploading}
              tags={tags}
              setTags={setTags}
              tagOptions={tagOptions}
              setTagOptions={setTagOptions}
              isLegacy={isLegacy}
              setIsLegacy={setIsLegacy}
              selectedPersona={selectedPersona}
              setSelectedPersona={setSelectedPersona}
              missingFields={missingFields}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default BulkAddDP;
