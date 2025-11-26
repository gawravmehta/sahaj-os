import Image from "next/image";
import React, { useRef, useState } from "react";
import FileUpload from "./FileUpload";

const StepThree = ({
  visible,
  setVisible,
  active,
  setActive,
  fileFront,
  setFileFront,
  fileBack,
  setFileBack,
  selectedKycType,
  setSelectedKycType,
  attachmentFiles,
  setAttachmentFiles,
}) => {
  const scrollRef = useRef(null);
  const [selectedOption, setSelectedOption] = useState(null);
  const [activeIndex, setActiveIndex] = useState(null);
  const [isAttachmentChecked, setIsAttachmentChecked] = useState(false);

  const [fileStates, setFileStates] = useState({
    front: {
      error: false,
      progress: 0,
      name: "",
      size: "",
      ext: "",
    },
    back: {
      error: false,
      progress: 0,
      name: "",
      size: "",
      ext: "",
    },
    attachment: {
      error: false,
      progress: 0,
      name: "",
      size: "",
      ext: "",
    },
  });

  const items = [
    { label: "Aadhaar Card", src: "/id-proof/aadhaar.png" },
    { label: "Pan Card", src: "/id-proof/pan-card.png" },
    { label: "Driving License", src: "/id-proof/driving-license.png" },
    { label: "Passport", src: "/id-proof/passport.png" },
    { label: "Voter ID", src: "/id-proof/voter-id.png" },
    { label: "Other", src: "/id-proof/other.png" },
  ];

  const handleOptionChange = (option) => {
    setSelectedOption(option);
    setVisible(option === "Upload KYC");
    setActive(false);
    setActiveIndex(null);
    setSelectedKycType(option);
  };

  const handleActive = (index) => {
    setActive(true);
    setActiveIndex(index === activeIndex ? null : index);
    setSelectedKycType(items[index].label);
    setTimeout(() => {
      scrollRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  };

  const getFileProps = (side) => ({
    title:
      side === "front"
        ? "Front Side Upload"
        : side === "back"
        ? "Back Side Upload"
        : "Attachment Upload",
    fileError: fileStates[side].error,
    setFileError: (val) =>
      setFileStates((prev) => ({
        ...prev,
        [side]: { ...prev[side], error: val },
      })),
    progress: fileStates[side].progress,
    setProgress: (val) =>
      setFileStates((prev) => ({
        ...prev,
        [side]: { ...prev[side], progress: val },
      })),
    fileName: fileStates[side].name,
    setFileName: (val) =>
      setFileStates((prev) => ({
        ...prev,
        [side]: { ...prev[side], name: val },
      })),
    fileSize: fileStates[side].size,
    setFileSize: (val) =>
      setFileStates((prev) => ({
        ...prev,
        [side]: { ...prev[side], size: val },
      })),
    fileExt: fileStates[side].ext,
    setFileExt: (val) =>
      setFileStates((prev) => ({
        ...prev,
        [side]: { ...prev[side], ext: val },
      })),
    filePreview:
      side === "front"
        ? fileFront
        : side === "back"
        ? fileBack
        : attachmentFiles,
    setFilePreview:
      side === "front"
        ? setFileFront
        : side === "back"
        ? setFileBack
        : setAttachmentFiles,
    index: side === "front" ? 0 : side === "back" ? 1 : 2,
    multiple: side === "attachment",
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-black">KYC</h2>
        <p className="text-sm text-gray-500">
          Select the appropriate KYC action as needed.
        </p>

        <div className="mt-4 flex flex-wrap gap-4">
          {["Request KYC", "Upload KYC", "Not Required"].map((option) => (
            <label
              key={option}
              className="flex cursor-pointer items-center gap-2"
            >
              <input
                type="checkbox"
                value={option}
                checked={selectedOption === option}
                onChange={() => handleOptionChange(option)}
                className="accent-blue-600"
              />
              <span className="text-sm text-black">{option}</span>
            </label>
          ))}
        </div>
      </div>

      {selectedOption === "Request KYC" && (
        <div className="flex gap-6">
          {["Core Identifier", "Secondary Identifier"].map((id) => (
            <label key={id} className="flex items-center gap-2">
              <input type="checkbox" className="accent-blue-600" />
              <span className="text-sm text-black">{id}</span>
            </label>
          ))}
        </div>
      )}

      {visible && (
        <div ref={scrollRef} className="grid grid-cols-3 gap-4">
          {items.map((item, index) => (
            <div
              key={item.label}
              className={`flex cursor-pointer items-center justify-center gap-2 border py-2 text-sm text-black ${
                activeIndex === index ? "border-blue-600" : "border-gray-300"
              }`}
              onClick={() => handleActive(index)}
            >
              <Image
                src={item.src}
                alt={item.label}
                width={24}
                height={24}
                className="size-4 object-contain"
              />
              {item.label}
            </div>
          ))}
        </div>
      )}

      {active && visible && (
        <div className="flex gap-4" ref={scrollRef}>
          <div className="w-1/2">
            <FileUpload {...getFileProps("front")} />
          </div>
          <div className="w-1/2">
            <FileUpload {...getFileProps("back")} />
          </div>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold text-black">Related Attachment</h2>
        <p className="text-sm text-gray-500">
          Indicate if any supporting documents are available.
        </p>
        <label className="mt-3 flex items-center gap-2">
          <input
            type="checkbox"
            className="accent-blue-600"
            checked={isAttachmentChecked}
            onChange={(e) => setIsAttachmentChecked(e.target.checked)}
          />
          <span className="text-sm font-medium">
            Is there any Related Attachment
          </span>
        </label>
        {isAttachmentChecked && (
          <div className="mt-4 bg-slate-400">
            <FileUpload
              {...getFileProps("attachment")}
              title="Upload Attachment"
              className="w-full"
              multiple={true}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default StepThree;
