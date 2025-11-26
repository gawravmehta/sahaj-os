"use client";

import Header from "@/components/ui/Header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { use, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import Legal from "@/components/features/purposeManagement/Legal";
import Translation from "@/components/features/purposeManagement/Translation";
import General from "@/components/features/purposeManagement/General";
import Button from "@/components/ui/Button";
import DeleteModal from "@/components/shared/modals/DeleteModal";
import InvalidIdWrapper, { isValidObjectId } from "@/utils/helperFunctions";
import processing_activity from "@/components/features/purposeManagement/processing_activity";
import data_processor from "@/components/features/purposeManagement/data_processor";
import { usePermissions } from "@/contexts/PermissionContext";

const tabs = [
  { id: "general", label: "General" },
  { id: "legal", label: "Legal" },
  { id: "processing_activity", label: "Processing Activity" },
  { id: "data_processor", label: "Data Processor" },
  { id: "translation", label: "Translation" },
];
const tabComponents = {
  general: General,
  legal: Legal,
  translation: Translation,
  processing_activity: processing_activity,
  data_processor: data_processor,
};

const Page = ({ params }) => {
  const { Id: dpId } = use(params);
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const [dpData, setDpData] = useState();
  const [showModal, setShowModal] = useState(false);
  const [selectedId, setSelectedId] = useState(null);
  const { canWrite } = usePermissions();

  useEffect(() => {
    if (isValidObjectId(dpId)) {
      getOneDataPurpose();
    }
  }, [dpId]);

  const getOneDataPurpose = async () => {
    try {
      const response = await apiCall(`/purposes/get-purpose/${dpId}`);
      setDpData(response);
      return response;
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
      console.error(error);
    }
  };

  const handleDelete = async () => {
    try {
      await apiCall(`/purposes/delete-purpose/${dpId}`, {
        method: "DELETE",
      });

      toast.success("Purpose Archive successfully");
      closeModal();
      router.push("/apps/purpose-management");
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  const handleDeleteClick = (id) => {
    setSelectedId(id);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
  };

  const tab = searchParams.get("tab") || "general";
  const handleTabChange = (newTab) => {
    const params = new URLSearchParams(window.location.search);
    params.set("tab", newTab);
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  };

  const breadcrumbsProps = {
    path: `/apps/purpose-management/${dpId}`,
    skip: "/apps",
  };
  return (
    <InvalidIdWrapper id={dpId}>
      <div className="">
        <div className="flex">
          <div className="w-full">
            <div className="flex flex-col items-center justify-between pr-6 sm:flex sm:flex-row">
              <Header
                title="Purpose Details"
                breadcrumbsProps={breadcrumbsProps}
              />

              <Button
                variant="delete"
                disabled={!canWrite("/apps/purpose-management")}
                onClick={() => handleDeleteClick(dpId)}
              >
                Delete
              </Button>
            </div>

            <Tabs
              onValueChange={handleTabChange}
              value={tab}
              defaultValue="general"
            >
              <div className="flex w-full items-center justify-center border-b border-t border-borderheader">
                <TabsList className="gap-32">
                  {tabs.map((tab) => (
                    <TabsTrigger
                      key={tab?.id}
                      value={tab?.id}
                      variant="secondary"
                    >
                      {tab?.label}
                    </TabsTrigger>
                  ))}
                </TabsList>
              </div>

              {Object.entries(tabComponents)?.map(([key, Component]) => (
                <TabsContent key={key} value={key}>
                  <Component dpData={dpData} />
                </TabsContent>
              ))}
            </Tabs>
          </div>

          {showModal && (
            <DeleteModal
              closeModal={closeModal}
              title={`Do you want to ${
                dpData?.purpose_status === "draft" ? "delete" : "archive"
              } this`}
              id={selectedId}
              onConfirm={handleDelete}
              typeTitle="Consent Purpose"
              field="Consent Purpose?"
              isArchive={dpData?.purpose_status === "published" ? true : false}
            />
          )}
        </div>
      </div>
    </InvalidIdWrapper>
  );
};

export default Page;
