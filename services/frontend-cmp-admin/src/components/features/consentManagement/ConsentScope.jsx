import React, { useState } from "react";
import { IoIosArrowDown, IoIosArrowUp } from "react-icons/io";

const ConsentScope = ({ artificatData }) => {
  const dataElements = artificatData?.data_elements;
  const [openIndexes, setOpenIndexes] = useState({});

  const toggleOpen = (index) => {
    setOpenIndexes((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  if (!Array.isArray(dataElements) || dataElements.length === 0) {
    return (
      <div className="text-center text-gray-500">
        No consent scope data available.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {dataElements.map((element, index) => {
        const isOpen = openIndexes[index];

        return (
          <div key={index} className="w-full border-b">
            <button
              onClick={() => toggleOpen(index)}
              className="flex w-[600px] items-center gap-2 px-4 py-3 text-left font-medium text-gray-800"
            >
              <span>{isOpen ? <IoIosArrowDown /> : <IoIosArrowUp />}</span>
              {element.title}
            </button>

            {isOpen && (
              <div className="space-y-4 border-t px-6 py-4">
                <p className="text-sm text-gray-600">
                  <span className="font-medium">Data Retention Period:</span>{" "}
                  {new Date(element.data_retention_period).toLocaleString()}
                </p>

                <div className="space-y-4">
                  {element.consents.map((consent, cIndex) => (
                    <div key={cIndex} className=" p-4">
                      <div className="mb-3">
                        <p className="text-sm font-semibold text-gray-800">
                          P{cIndex + 1}:{" "}
                          {consent.purpose_title || "No Title provided"}
                        </p>
                        <p className="mt-1 text-xs text-gray-500">
                          Purpose ID: {consent.purpose_id}
                        </p>
                      </div>

                      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div className="space-y-2">
                          <p className="text-sm text-gray-700">
                            <span className="font-medium">Consent Status:</span>{" "}
                            {consent.consent_status}
                          </p>
                          <p className="text-sm text-gray-700">
                            <span className="font-medium">Consent Mode:</span>{" "}
                            {consent.consent_mode}
                          </p>
                          <p className="text-sm text-gray-700">
                            <span className="font-medium">Shared:</span>{" "}
                            {consent.shared ? "Yes" : "No"}
                          </p>
                          <p className="text-sm text-gray-700">
                            <span className="font-medium">Cross Border:</span>{" "}
                            {consent.cross_border ? "Yes" : "No"}
                          </p>
                        </div>

                        <div className="space-y-2">
                          <p className="text-sm text-gray-700">
                            <span className="font-medium">
                              Consent Timestamp:
                            </span>{" "}
                            {new Date(
                              consent.consent_timestamp
                            ).toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-700">
                            <span className="font-medium">
                              Retention Timestamp:
                            </span>{" "}
                            {new Date(
                              consent.retention_timestamp
                            ).toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-700">
                            <span className="font-medium">
                              Legal Mandatory:
                            </span>{" "}
                            {consent.legal_mandatory ? "Yes" : "No"}
                          </p>
                          <p className="text-sm text-gray-700">
                            <span className="font-medium">
                              Reconsent Required:
                            </span>{" "}
                            {consent.reconsent ? "Yes" : "No"}
                          </p>
                        </div>
                      </div>

                      {consent.data_processors.length > 0 && (
                        <div className="mt-4">
                          <h4 className="mb-2 pb-1 text-sm font-semibold text-gray-800">
                            Data Processors:
                          </h4>
                          {consent.data_processors.map((processor, pIndex) => (
                            <div
                              key={pIndex}
                              className="mb-3 border-gray-300 text-sm text-gray-600"
                            >
                              <p>
                                <span className="font-medium">
                                  Processor Name:
                                </span>{" "}
                                {processor.data_processor_name || "N/A"}
                              </p>
                              <p>
                                <span className="font-medium">
                                  Cross Border Transfer:
                                </span>{" "}
                                {processor.cross_border_data_transfer
                                  ? "Yes"
                                  : "No"}
                              </p>
                              <p>
                                <span className="font-medium">
                                  Consent Mode:
                                </span>{" "}
                                {processor.consent_mode}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default ConsentScope;
