import React, { useState } from "react";
import { FaAngleDown, FaAngleUp } from "react-icons/fa";
import ConsentToggle from "./ConsentToggle";
import Button from "@/components/ui/Button";
import { useEffect } from "react";
import ConsentStatusBar from "./ConsentStatusBar";

const MyPreferences = ({
  preferenceData,
  onSelectionChange,
  isDisabled = false,
  hideMandatory = false,
}) => {
  const [activeIndex, setActiveIndex] = useState(null);
  const [consentChanges, setConsentChanges] = useState({});

  const handleOpenDropDown = (index) => {
    setActiveIndex(index === activeIndex ? null : index);
  };

  const calculateDuration = (expiryDate) => {
    const expiry = new Date(expiryDate);
    const now = new Date();
    const diffTime = Math.abs(expiry - now);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return `${diffDays} Days`;
  };

  const handleToggleChange = (de_id, purpose_id, newStatus, originalStatus) => {
    setConsentChanges((prev) => {
      const key = `${de_id}-${purpose_id}`;
      const updatedChanges = { ...prev };

      if (newStatus === originalStatus) {
        delete updatedChanges[key];
      } else {
        updatedChanges[key] = {
          de_id,
          purpose_id,
          newStatus,
          originalStatus,
        };
      }

      return updatedChanges;
    });
  };

  useEffect(() => {
    const toRevoke = [];
    const toGive = [];

    Object.values(consentChanges).forEach((change) => {
      if (
        change.originalStatus === "approved" &&
        change.newStatus === "denied"
      ) {
        toRevoke.push({ de_id: change.de_id, purpose_id: change.purpose_id });
      } else if (
        change.originalStatus === "denied" &&
        change.newStatus === "approved"
      ) {
        toGive.push({ de_id: change.de_id, purpose_id: change.purpose_id });
      }
    });

    onSelectionChange?.({ toRevoke, toGive });
  }, [consentChanges, onSelectionChange]);

  return (
    <div className="relative space-y-2">
      {preferenceData.map((data, index) => (
        <div
          key={index}
          className="flex flex-col w-full items-center justify-between py-1"
        >
          <div
            className="flex items-center gap-2 justify-between w-full px-3 py-2 bg-[#F6F8FF] cursor-pointer"
            onClick={() => handleOpenDropDown(index)}
          >
            <div className="flex gap-2 items-center">
              {index === activeIndex ? (
                <FaAngleUp className="text-[#514C4C]" />
              ) : (
                <FaAngleDown className="text-[#514C4C]" />
              )}
              <h3 className="text-sm">{data.title}</h3>
            </div>
            {data.data_retention_period && (
              <span className="text-xs text-[#514C4C] font-light">
                Data Retention: {calculateDuration(data.data_retention_period)}
              </span>
            )}
          </div>

          {index === activeIndex && (
            <div className={` ml-14 w-[97%]`}>
              {data.consents.map((consent, i) => (
                <div
                  key={i}
                  className={`relative py-2 px-3  mr-2 my-1 flex flex-col justify-between`}
                  onClick={(e) => e.stopPropagation()}
                >
                  <div
                    className={`absolute -left-5 ${
                      i == 0 ? "-top-1" : "-top-16"
                    }`}
                  >
                    <div
                      className={`${i == 0 ? "h-10" : "h-24"} w-1 bg-[#F6F8FF]`}
                    ></div>
                    <div className="h-px w-8 bg-[#F6F8FF]"></div>
                  </div>

                  <div
                    className={`flex text-[#323232] text-sm justify-between flex-col py-2 px-2 border border-[#D9D9D9]  bg-gray-50`}
                  >
                    <div className="flex justify-between items-center">
                      <h3 className="text-[#323232]">{consent.title}</h3>

                      <ConsentToggle
                        initialStatus={consent.status}
                        currentStatus={
                          consentChanges[`${data.de_id}-${consent.purpose_id}`]
                            ?.newStatus
                        }
                        onToggle={(newStatus) =>
                          handleToggleChange(
                            data.de_id,
                            consent.purpose_id,
                            newStatus,
                            consent.status
                          )
                        }
                        hideMandatory={hideMandatory}
                        isDisabled={isDisabled}
                        isServiceMendatory={consent.is_service_mandatory}
                        serviceMendatoryMessage={
                          consent.service_mandatory_message
                        }
                        isLegalMendatory={consent.is_legal_mandatory}
                        legalMendatoryMessage={consent.legal_mandatory_message}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default MyPreferences;
