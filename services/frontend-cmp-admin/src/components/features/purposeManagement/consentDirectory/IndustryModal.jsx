"use client";

import React, { useState } from "react";
import Button from "@/components/ui/Button";
import { apiCall } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import { MdOutlineContentCopy } from "react-icons/md";
import { getErrorMessage } from "@/utils/errorHandler";
import Tag from "@/components/ui/Tag";
import { useRouter } from "next/navigation";

const IndustryModal = ({ showModal, setShowModal }) => {
  const [selectedDataElements, setSelectedDataElements] = useState([]);
  const [loading, setLoading] = useState(false);
  const touter = useRouter();

  const handleDataElementSelect = (name) => {
    setSelectedDataElements((prevState) => {
      if (prevState.includes(name)) {
        return prevState.filter((item) => item !== name);
      } else {
        return [...prevState, name];
      }
    });
  };

  const handleCopyConsent = async () => {
    setLoading(true);
    try {
      const response = await apiCall(
        `/purposes/copy-purpose?purpose_id=${showModal[0]?.purpose_id}`,
        {
          method: "POST",
          data: selectedDataElements,
        }
      );
      toast.success("Consent copied successfully");
      touter.push(`/apps/purpose-management`);
      setShowModal(null);
      setLoading(false);
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
      console.error("Error copying consent:", error);
      setLoading(false);
    }
  };

  return (
    <div>
      {showModal &&
        showModal.map((item, index) => (
          <div
            onClick={() => setShowModal(null)}
            key={index}
            className="fixed inset-0 z-50 flex items-center justify-center bg-sky-100/40"
          >
            <div
              onClick={(e) => e.stopPropagation()}
              className="w-1/3 border bg-white "
            >
              <div className="p-6">
                <h1 className="text-center text-xl mb-4">
                  Select Data Elements to Copy Consent
                </h1>
                <h2 className="text-2xl text-center capitalize">
                  {item?.industry_name}
                </h2>
                <p className=" text-center text-[12px] text-subHeading">
                  Pick the data fields you want to copy. Only the selected
                  information will be used as needed for your task.
                </p>
              </div>

              <div className=" flex items-center justify-center  flex-wrap gap-2 pb-4  px-9">
                {item?.data_elements?.length > 0 ? (
                  item?.data_elements.map((dataElement, index) => {
                    return (
                      <Tag
                        key={index}
                        className="cursor-pointer text-xs mt-1"
                        variant={
                          selectedDataElements.some(
                            (item) => item === dataElement
                          )
                            ? "solidBlue"
                            : "outlineBlue"
                        }
                        label={dataElement}
                        onClick={() => handleDataElementSelect(dataElement)}
                      />
                    );
                  })
                ) : (
                  <span>No data elements</span>
                )}
              </div>

              <div className="mt-5 flex gap-2 justify-end border-t py-3 px-6">
                <Button
                  label="Cancel"
                  variant="cancel"
                  onClick={() => setShowModal(null)}
                  className=" text-[14px]"
                >
                  Cancel
                </Button>
                <Button
                  className=" w-24 flex "
                  label="Copy"
                  variant={"primary"}
                  btnLoading={loading}
                  disabled={loading}
                  onClick={() => {
                    handleCopyConsent();
                  }}
                >
                  <MdOutlineContentCopy size={16} className="mr-1" />
                  Copy
                </Button>
              </div>
            </div>
          </div>
        ))}
    </div>
  );
};

export default IndustryModal;
