"use client";
import Audit from "@/components/features/breachManagement/details/Audit";
import GeneralTab from "@/components/features/breachManagement/details/GeneralTab";
import Steps from "@/components/features/breachManagement/details/Steps";
import Header from "@/components/ui/Header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import { apiCall } from "@/hooks/apiCall";
import React, { use, useEffect, useState } from "react";

const Page = ({ params }) => {
  const { id } = use(params);

  const [breachData, setBreachData] = useState({});
  const [loading, setLoading] = useState(false);
  const [showPublishButton, setShowPublishButton] = useState(false);

  const breadcrumbsProps = {
    path: `/apps/breach-management/${id} `,
    skip: "/apps",
  };

  const fetchBreachData = async () => {
    try {
      setLoading(true);
      const data = await apiCall(`/incidents/get-incidents/${id}`);
      setBreachData(data);
      setShowPublishButton(data?.status === "draft");
    } catch (error) {
      console.error("Error fetching breach data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {};

  useEffect(() => {
    fetchBreachData();
  }, [id]);

  return (
    <>
      <div className="flex flex-col justify-between gap-4 pr-6 sm:flex-row">
        <Header
          title={breachData?._id || "Breach Details"}
          breadcrumbsProps={breadcrumbsProps}
        />
      </div>
      <div>
        <Tabs defaultValue="General">
          <div className="flex w-full items-center justify-start border-y border-borderSecondary sm:justify-center">
            <div className="flex flex-wrap gap-4 sm:flex sm:flex-row">
              <TabsList className="w-full space-x-14  ">
                <TabsTrigger
                  value="General"
                  variant="secondary"
                  className="cursor-pointer"
                >
                  General
                </TabsTrigger>
                <TabsTrigger
                  value="steps"
                  variant="secondary"
                  className="cursor-pointer"
                >
                  Steps
                </TabsTrigger>
                
              </TabsList>
            </div>
          </div>

          <TabsContent value="General">
            <GeneralTab
              breachData={breachData}
              loading={loading}
              handlePublish={handlePublish}
              id={id}
              showPublishButton={showPublishButton}
            />
          </TabsContent>

          <TabsContent value="steps">
            <Steps breachData={breachData} refreshData={fetchBreachData} />
          </TabsContent>

          
        </Tabs>
      </div>
    </>
  );
};

export default Page;
