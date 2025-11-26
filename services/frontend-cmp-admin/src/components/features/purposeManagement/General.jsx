import Image from "next/image";
import React from "react";
import dayjs from "dayjs";

const General = ({ dpData }) => {
  if (!dpData) {
    return (
      <div className="p-6">
        <div className="flex min-h-[calc(100vh-270px)] items-center justify-center">
          <div className="flex flex-col items-center justify-center">
            <div className="w-[200px]">
              <Image
                height={200}
                width={200}
                src="/assets/illustrations/no-data-find.png"
                alt="Circle Image"
                className="h-full w-full object-cover"
              />
            </div>
            <div className="mt-5">
              <p>No General Data Available</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const {
    purpose_title,
    purpose_description,
    consent_directory_category,
    geographical_scope,
    purpose_priority,
    purpose_status,
    review_frequency,
    legal_revocation_message,
    created_at,
    revocation_message,
    service_mandatory_consent,
    purpose_id,
    updated_at,
    consent_purpose_owner_department,
  } = dpData;

  return (
    <div className="flex items-center justify-center">
      <div className="mt-6 flex h-[calc(100vh-240px)] max-w-3xl justify-center">
        <div className="flex w-225 justify-between px-3">
          <div className="flex w-full flex-col gap-4">
            <div>
              <h1 className="text-subHeading">Consent Statement</h1>
              <p className="text-[16px]">{purpose_title}</p>
            </div>
            <div>
              <h1 className="text-subHeading">Description</h1>
              <p className="text-[16px]"> {purpose_description}</p>
            </div>
            <div className="grid w-full grid-cols-3 gap-10">
              <div>
                <h1 className="text-subHeading">Category</h1>
                <p className="text-[16px]">{consent_directory_category}</p>
              </div>
              <div>
                <h1 className="text-subHeading">Owner Department</h1>
                <p className="text-[16px]">
                  {consent_purpose_owner_department || "N/A"}
                </p>
              </div>
              <div>
                <h1 className="text-subHeading">Geographical Scope</h1>
                <p className="text-[16px]">{geographical_scope || "N/A"}</p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-10">
              <div>
                <h1 className="text-subHeading">Frequency</h1>
                <p className="text-[16px]">{review_frequency}</p>
              </div>
              <div>
                <h1 className="text-subHeading">Priority</h1>
                <p className="text-[16px]">{purpose_priority || "N/A"}</p>
              </div>
            </div>
            <div className="flex justify-between">
              <div>
                <h1 className="text-subHeading">Created At</h1>
                <p className="text-[16px]">
                  {dayjs(created_at).format("MMM D, YYYY, h:mm A")}
                </p>
              </div>
              {updated_at && (
                <div>
                  <h1 className="text-subHeading">Updated At</h1>
                  <p className="text-[16px]">
                    {dayjs(updated_at).format("MMM D, YYYY, h:mm A")}
                  </p>
                </div>
              )}
            </div>
          </div>
          <div className="flex justify-end gap-4">
            <button
              className={`h-6 rounded-full px-6 text-xs capitalize ${
                purpose_status === "draft"
                  ? "bg-gray-200 text-gray-500"
                  : purpose_status === "published"
                  ? "bg-[#e1ffe7] text-[#06a42a]"
                  : purpose_status === "archived"
                  ? "bg-[#fbeaea] text-[#d94e4e]"
                  : "bg-gray-100 text-white"
              }`}
            >
              {purpose_status}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default General;
