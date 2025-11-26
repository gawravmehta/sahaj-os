import React, { useState } from "react";
import { FaAngleDown, FaAngleUp } from "react-icons/fa";
import Button from "@/components/ui/Button";
import ConsentStatusBar from "./ConsentStatusBar";

const RenewPreference = ({ preferenceData, handleRenewConsent }) => {
  const [activeIndex, setActiveIndex] = useState(null);

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

  return (
    <div className="relative space-y-2">
      {preferenceData.map((data, index) => (
        <div key={index} className="flex flex-col w-full justify-between py-1">
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
            <div className={`"w-full"`}>
              {data.consents.map((consent, i) => (
                <div
                  key={i}
                  className={`relative py-2 my-1 flex flex-col justify-between`}
                  onClick={(e) => e.stopPropagation()}
                >
                  <div
                    className={`flex text-[#323232] text-sm justify-between flex-col py-2 px-2 border border-[#D9D9D9]  bg-gray-50 w-full`}
                  >
                    <div className="flex justify-between w-full">
                      <h3 className="text-[#323232]">{consent.title}</h3>
                      <Button
                        variant="secondary"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRenewConsent(data.de_id, consent.purpose_id);
                        }}
                      >
                        Renew
                      </Button>
                    </div>

                    <ConsentStatusBar consent={consent} />
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

export default RenewPreference;
