"use client";
import Breadcrumbs from "@/components/ui/BreadCrumb";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import dayjs from "dayjs";

function Page() {
  const [timelineData, setTimelineData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const timelineResponse = await apiCall(
          `/api/v1/consents/consent-timeline/{agreement_id}/audit`
        );

        if (timelineResponse?.logs) {
          setTimelineData(timelineResponse.logs.reverse());
        }
      } catch (error) {
        console.error("Error fetching timeline:", error);
        toast.error(getErrorMessage(error));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className=" flex justify-center">
      <div className="w-[622px] pt-12">
        <div className="flex items-center justify-start mt-10 mb-5">
          <div>
            <Breadcrumbs
              path="/manage-preference/time-line"
              labels={{
                "/manage-preference/time-line": "Time Line",
              }}
            />
          </div>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex flex-col gap-1 max-w-3xl">
            <div className="text-sm text-gray-500">
              Here is the history of your consent interactions.
            </div>
          </div>
        </div>
        <div className="mt-10 ">
          {timelineData.map((item, index) => {
            let displayTitle = "Consent Updated";
            if (item.operation === "insert") {
              displayTitle = "New Consent";
            }

            return (
              <div key={index} className={`relative mb-8`}>
                <div className="absolute -left-3 top-0">
                  <div className="size-16 bg-gray-300 rounded-full flex items-center justify-center text-xs text-gray-600 font-medium">
                    {dayjs(item.timestamp).format("DD MMM")}
                  </div>
                  {index !== timelineData.length - 1 && (
                    <div className="w-2 h-full bg-gray-300 absolute top-16 left-[43%] -z-10"></div>
                  )}
                </div>
                <div className="ml-20">
                  <div className="flex items-center justify-between">
                    <div className="pb-5">
                      <h3 className="text-lg font-semibold text-gray-800">
                        {displayTitle}
                      </h3>
                      <p className="text-gray-600 max-w-3xl text-sm mb-2">
                        {item.artifact?.consent_scope?.data_elements
                          ?.map((de) => de.title)
                          .join(", ")}
                      </p>
                      <div className="flex flex-col gap-1">
                        <p className="text-sm text-gray-600">
                          Agreement: {item.agreement_id}
                        </p>
                        <p className="text-sm text-gray-600">
                          Time:{" "}
                          {dayjs(item.timestamp).format("h:mm A, D MMMM YYYY")}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
          {timelineData.length === 0 && (
            <div className="text-center text-gray-500 mt-10">
              No timeline data available.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Page;
