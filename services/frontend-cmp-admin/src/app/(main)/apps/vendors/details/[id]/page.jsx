"use client";

import { useParams, useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";

import DeleteModal from "@/components/shared/modals/DeleteModal";
import { apiCall } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import Header from "@/components/ui/Header";
import Button from "@/components/ui/Button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import General from "@/components/features/vendor/vendorDetail/General";
import PolicyCompliance from "@/components/features/vendor/vendorDetail/PolicyCompliance";
import DataProcessing from "@/components/features/vendor/vendorDetail/DataProcessing";
import SecurityAudit from "@/components/features/vendor/vendorDetail/SecurityAudit";
import { AiOutlineDelete } from "react-icons/ai";

const Page = () => {
  const params = useParams();

  const [vendorData, setVendorData] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedId, setSelectedId] = useState(params.id);

  const router = useRouter();
  const breadcrumbsProps = {
    path: `/apps/vendors/${vendorData?.dpr_name}`,
    skip: "/apps",
  };

  const closeModal = () => {
    setShowModal(false);
  };

  useEffect(() => {
    fetchVendorData();
  }, [params.id]);
  const fetchVendorData = async () => {
    setLoading(true);
    try {
      const response = await apiCall(
        `/vendor/get-one-vendor?vendor_id=${params.id}`
      );

      setLoading(false);
      setVendorData(response);
    } catch (error) {
      console.error("Error fetching vendor data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteVendor = async () => {
    try {
      const response = await apiCall(`/vendor/delete-my-vendor/${params.id}`, {
        method: "DELETE",
      });

      toast.success(response.message);
      router.push("/apps/vendors");
      setShowModal(false);
    } catch (error) {
      const message = error?.message || "Failed to delete the vendor.";
      toast.error(message);
    }
  };

  return (
    <>
      <div className="flex flex-col justify-between gap-4 pr-6 sm:flex-row">
        <Header
          title={vendorData?.dpr_name || "Vendor Details"}
          breadcrumbsProps={breadcrumbsProps}
        />
        {vendorData.status !== "archived" && (
          <div className="mt-0 flex items-center gap-3.5 sm:mt-2 ">
            <Button
              onClick={() => {
                setShowModal(true);
              }}
              variant="delete"
              className="cursor-pointer"
            >
              <AiOutlineDelete className="text-[16px]" />
              Delete
            </Button>
          </div>
        )}
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
                  value="Policy & Compliance"
                  variant="secondary"
                  className="cursor-pointer"
                >
                  Policy & Compliance
                </TabsTrigger>
                <TabsTrigger
                  value="Data Processing"
                  variant="secondary"
                  className="cursor-pointer"
                >
                  Data Processing
                </TabsTrigger>
                <TabsTrigger
                  value="Security & Audit"
                  variant="secondary"
                  className="cursor-pointer"
                >
                  Security & Audit
                </TabsTrigger>
              </TabsList>
            </div>
          </div>

          <TabsContent value="General">
            <General vendorData={vendorData} loading={loading} />
          </TabsContent>

          <TabsContent value="Policy & Compliance">
            <PolicyCompliance vendorData={vendorData} loading={loading} />
          </TabsContent>

          <TabsContent value="Data Processing">
            <DataProcessing vendorData={vendorData} loading={loading} />
          </TabsContent>

          <TabsContent value="Security & Audit">
            <SecurityAudit vendorData={vendorData} loading={loading} />
          </TabsContent>
        </Tabs>
      </div>
      {showModal && (
        <DeleteModal
          closeModal={closeModal}
          title="Do you want to delete this"
          id={selectedId}
          onConfirm={handleDeleteVendor}
          typeTitle="Vendor"
          field="Vendor?"
        />
      )}
    </>
  );
};

export default Page;
