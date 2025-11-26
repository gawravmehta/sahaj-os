"use client";

import { FaAngleRight } from "react-icons/fa6";

function CommunicationSidebar({ openIndex, setOpenIndex }) {
  const dropDownButtons = ["SMTP", "SMS"];

  const handleButtonClick = (index) => {
    if (openIndex.includes(index)) {
      setOpenIndex(openIndex.filter((i) => i !== index));
    } else {
      setOpenIndex([index]);
    }
  };

  return (
    <div className="w-full">
      {dropDownButtons.map((button, index) => (
        <div key={index} className="border-b border-[#C7CFE2]">
          <div
            onClick={() => handleButtonClick(index)}
            className={`flex cursor-pointer items-center gap-2 px-4 py-3 text-sm ${
              openIndex.includes(index) ? "bg-[#ECF6FF]" : ""
            }`}
          >
            <div className="">
              <FaAngleRight size={14} className="text-placeholder" />
            </div>
            <div>{button}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default CommunicationSidebar;
