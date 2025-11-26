"use client";
import React, { useState, useEffect } from "react";
import Card from "@/components/features/pastRequest/Card";
import Button from "@/components/ui/Button";
import { apiCall } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";
import Loader from "@/components/ui/Loader";

const Page = () => {
  const [activeTab, setActiveTab] = useState("DPAR");
  const [dparData, setDparData] = useState([]);
  const [grievanceData, setGrievanceData] = useState([]);
  const [loading, setLoading] = useState({
    dpar: true,
    grievance: true,
  });

  const getDparData = async () => {
    try {
      const response = await apiCall("/api/v1/dpar/get-my-requests");

      setDparData(response);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading((prev) => ({ ...prev, dpar: false }));
    }
  };

  const getGrievanceData = async () => {
    try {
      const response = await apiCall(
        "/api/v1/grievance/get-all-grievances?skip=0&limit=20"
      );

      setGrievanceData(response);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading((prev) => ({ ...prev, grievance: false }));
    }
  };

  useEffect(() => {
    getDparData();
    getGrievanceData();
  }, []);

  const currentData =
    activeTab === "DPAR" ? dparData : grievanceData.data || [];
  const currentLoading =
    activeTab === "DPAR" ? loading.dpar : loading.grievance;

  if (currentLoading) {
    return (
      <div className=" text-center">
        <Loader />
      </div>
    );
  }

  return (
    <div className="mt-20 flex flex-col items-center ">
      <div className="flex  mb-6 fixed top-[55px] py-5 w-[700px] justify-end z-10 bg-white">
        <Button
          variant={activeTab === "DPAR" ? "primary" : "secondary"}
          className="w-24"
          onClick={() => setActiveTab("DPAR")}
        >
          DPAR
        </Button>
        <Button
          variant={activeTab === "Grievance" ? "primary" : "secondary"}
          className="w-24"
          onClick={() => setActiveTab("Grievance")}
        >
          Grievance
        </Button>
      </div>

      <div className="flex flex-col gap-4 justify-center w-[700px] mb-10 mt-16  ">
        {Array.isArray(currentData) && currentData.length > 0 ? (
          currentData.map((item, index) => (
            <Card key={index} data={item} getDparData={getDparData} />
          ))
        ) : (
          <p className="text-gray-500">No {activeTab} requests found</p>
        )}
      </div>
    </div>
  );
};

export default Page;
