"use client";

import Header from "@/components/ui/Header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";

import { apiCall } from "@/hooks/apiCall";

import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import AuditTrail from "@/components/features/dpar/AuditTrail";
import General from "@/components/features/dpar/General";
import Status from "@/components/features/dpar/Status";
import Message from "@/components/features/dpar/Message";
import Integration from "@/components/features/dpar/Integration";
import Report from "@/components/features/dpar/Report";
import { use } from "react";
import { getErrorMessage } from "@/utils/errorHandler";

const Page = ({ params }) => {
  const { ["core-id"]: id } = use(params);

  const searchParams = useSearchParams();
  const router = useRouter();
  const [requestData, setRequestData] = useState(null);
  const [loading, setLoading] = useState(true);

  const tabActive = searchParams.get("activeTab") || "general";
  const [refreshMessages, setRefreshMessages] = useState(false);

  const handleReportSent = () => {
    router.push(`?activeTab=message`, undefined, { shallow: true });

    fetchData();

    setRefreshMessages((prev) => !prev);
  };
  const fetchData = async () => {
    try {
      const data = await apiCall(`/dpar/get-one/${id}`);
      setRequestData(data?.data);
      return data?.data;
    } catch (err) {
      console.error("Error fetching data:", err);
      toast.error(getErrorMessage(err));
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) fetchData();
  }, [id]);

  const tabs = [
    { id: "general", label: "General" },
    { id: "status", label: "Status" },
  ];

  const tabComponents = {
    general: General,
    status: Status,
  };

  const handleTabChange = (tabId) => {
    router.push(`?activeTab=${tabId}`, undefined, { shallow: true });
  };

  const breadcrumbsProps = {
    path: `/apps/dpar/${requestData?.core_identifier || id}`,
    skip: "/apps",
  };
  const toTitleCase = (str) =>
    str
      ? str.replace(
          /\w\S*/g,
          (txt) => txt.charAt(0).toUpperCase() + txt.slice(1)
        )
      : "";

  return (
    <div className="h-full w-full">
      <div className="flex justify-between">
        <Header
          title={
            requestData?.core_identifier
              ? `${toTitleCase(requestData?.core_identifier)} Details`
              : "Incoming Request Details"
          }
          breadcrumbsProps={breadcrumbsProps}
        />

        {tabActive === "status" && requestData && (
          <div className="flex flex-col justify-center gap-2 pr-6">
            <h1 className="text-sm text-gray-600 font-medium">
              Request Status
            </h1>

            {(() => {
              const createdAt = new Date(requestData.created_timestamp);
              const deadline = new Date(requestData.deadline);
              const now = new Date();

              const totalDays = Math.max(
                Math.ceil((deadline - createdAt) / (1000 * 60 * 60 * 24)),
                1
              );
              const elapsedDays = Math.min(
                Math.ceil((now - createdAt) / (1000 * 60 * 60 * 24)),
                totalDays
              );
              const remainingDays = Math.max(totalDays - elapsedDays, 0);
              const progressPercent = Math.min(
                Math.round((elapsedDays / totalDays) * 100),
                100
              );

              return (
                <>
                  <div className="h-4 w-60 rounded-full bg-gray-100 overflow-hidden shadow-inner">
                    <div
                      className={`h-full bg-primary transition-all duration-500`}
                      style={{ width: `${progressPercent}%` }}
                    ></div>
                  </div>

                  <h1
                    className={`text-right text-xs font-semibold ${
                      remainingDays <= 5 ? "text-red-500" : "text-gray-600"
                    }`}
                  >
                    {remainingDays}/{totalDays} days remaining
                  </h1>

                  <p className="text-[11px] text-gray-400 italic text-right">
                    Created on {createdAt.toLocaleDateString()} | Deadline{" "}
                    {deadline.toLocaleDateString()}
                  </p>
                </>
              );
            })()}
          </div>
        )}
      </div>

      <Tabs
        defaultValue={tabActive}
        value={tabActive}
        onValueChange={handleTabChange}
      >
        <div className="flex w-full items-center justify-center border-b border-t border-borderheader">
          <TabsList className="gap-8 sm:gap-10">
            {tabs.map((tab) => (
              <TabsTrigger
                key={tab.id}
                value={tab.id}
                variant="secondary"
                className="text-sm"
              >
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </div>

        <div className="custom-scrollbar overflow-auto">
          {Object.entries(tabComponents).map(([key, Component]) => (
            <TabsContent key={key} value={key}>
              <Component
                data={requestData}
                fetchData={fetchData}
                refreshTrigger={key === "message" ? refreshMessages : undefined}
                onReportSent={key === "report" ? handleReportSent : undefined}
                loading={loading}
              />
            </TabsContent>
          ))}
        </div>
      </Tabs>
    </div>
  );
};

export default Page;
