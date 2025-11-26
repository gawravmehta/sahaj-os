"use client";

import React, { use, useEffect, useState } from "react";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { CiClock1 } from "react-icons/ci";
import { MdOutlineEmail } from "react-icons/md";
import TimeAgo from "@/components/ui/TimeAgo";

const Page = ({ params }) => {
  const { id } = use(params);
  const [notificationData, setNotificationData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchNotificationData = async () => {
    try {
      setLoading(true);
      const res = await apiCall(`/api/v1/notifications/notifications/${id}`);
      setNotificationData(res);
    } catch (error) {
      console.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotificationData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  if (!notificationData) {
    return (
      <div className="flex h-[80vh] items-center justify-center text-gray-500">
        Notification not found
      </div>
    );
  }

  const getIcon = (type) => {
    if (type === "CONSENT_RENEWAL") return <CiClock1 />;
    return <MdOutlineEmail />;
  };

  return (
    <div className="mx-auto max-w-4xl px-4 pt-16">
      <div className=" border border-gray-200 bg-white p-6 ">
        {/* Header */}
        <div className="mb-2 flex items-start gap-4 border-b border-gray-100 pb-6">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-gray-300 text-2xl text-primary">
            {getIcon(notificationData.type)}
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-semibold text-gray-900">
              {notificationData.title}
            </h1>
            <div className="mt-1 flex items-center gap-2 text-sm text-gray-500">
              <TimeAgo timestamp={notificationData.created_at} />
              <span>•</span>
              <span className="capitalize">
                {notificationData.type?.replace(/_/g, " ").toLowerCase()}
              </span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="space-y-6">
          <div className="prose max-w-none text-gray-600">
            <p>{notificationData.message}</p>
          </div>

          {/* INCIDENT_MITIGATION Specific Content */}
          {notificationData.type === "INCIDENT_MITIGATION" && (
            <div className="mt-6 space-y-6">
              {notificationData.mitigation_steps?.length > 0 && (
                <div className=" border border-gray-300 bg-red-50 p-4">
                  <h3 className="mb-3 font-medium text-red-900">
                    Recommended Mitigation Steps
                  </h3>
                  <ul className="list-disc space-y-2 pl-5 text-sm text-red-800">
                    {notificationData.mitigation_steps.map((step, index) => (
                      <li key={index}>{step}</li>
                    ))}
                  </ul>
                </div>
              )}

              {notificationData.data_elements?.length > 0 && (
                <div className=" border border-gray-300 bg-gray-50 p-4">
                  <h3 className="mb-3 font-medium text-gray-900">
                    Affected Data Elements
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {notificationData.data_elements.map((element, index) => (
                      <span
                        key={index}
                        className="rounded-full bg-white px-3 py-1 text-sm text-gray-700  ring-1 ring-gray-200"
                      >
                        {element}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* DATA_RETENTION_EXPIRY Specific Content */}
          {notificationData.type === "DATA_RETENTION_EXPIRY" && (
            <div className="mt-6  bg-blue-50 p-4 border border-gray-300">
              <h3 className="mb-4 font-medium text-blue-900">Expiry Details</h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className=" bg-white p-3 ">
                  <p className="text-xs text-gray-500">Data Element</p>
                  <p className="font-medium text-gray-900">
                    {notificationData.data_element_title}
                  </p>
                </div>
                <div className=" bg-white p-3 ">
                  <p className="text-xs text-gray-500">Expiry Date</p>
                  <p className="font-medium text-gray-900">
                    {new Date(notificationData.expiry_date).toLocaleString()}
                  </p>
                </div>
                {notificationData.cp_name && (
                  <div className=" bg-white p-3  sm:col-span-2">
                    <p className="text-xs text-gray-500">Collection Point</p>
                    <p className="font-medium text-gray-900">
                      {notificationData.cp_name}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* CONSENT_HALTED Specific Content */}
          {notificationData.type === "CONSENT_HALTED" && (
            <div className="mt-6  bg-gray-50 p-4">
              <h3 className="mb-4 font-medium text-gray-900">
                Halted Processing Details
              </h3>
              <div className="space-y-4">
                <div className=" bg-white p-3 ">
                  <p className="text-xs text-gray-500">Affected Purpose</p>
                  <p className="font-medium text-gray-900">
                    {notificationData.purpose_title}
                  </p>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className=" bg-white p-3 ">
                    <p className="text-xs text-gray-500">Data Element</p>
                    <p className="font-medium text-gray-900">
                      {notificationData.data_element_title}
                    </p>
                  </div>
                  <div className=" bg-white p-3 ">
                    <p className="text-xs text-gray-500">Collection Point</p>
                    <p className="font-medium text-gray-900">
                      {notificationData.cp_name}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Page;
