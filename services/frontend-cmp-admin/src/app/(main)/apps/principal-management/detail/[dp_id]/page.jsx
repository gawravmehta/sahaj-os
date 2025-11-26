"use client";

import Header from "@/components/ui/Header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import {
  useParams,
  usePathname,
  useRouter,
  useSearchParams,
} from "next/navigation";
import Button from "@/components/ui/Button";
import DeleteModal from "@/components/shared/modals/DeleteModal";
import InvalidIdWrapper, { isValidObjectId } from "@/utils/helperFunctions";

import General from "@/components/features/principalManagement/General";
import PersonalData from "@/components/features/principalManagement/PersonalData";
import DataProcessing from "@/components/features/principalManagement/DataProcessing";
import Consent from "@/components/features/principalManagement/Consent";
import Dpar from "@/components/features/principalManagement/Dpar";
import Audit from "@/components/features/principalManagement/Audit";
import Other from "@/components/features/principalManagement/Other";
import { usePermissions } from "@/contexts/PermissionContext";

const tabs = [
  { id: "general", label: "General" },
  { id: "personal-data", label: "Personal Data" },
  { id: "data-processing", label: "Data Processing" },
  { id: "consents", label: "Consents" },
  { id: "dpar", label: "DPAR" },
  { id: "audit", label: "Audit" },
  { id: "other", label: "Other" },
];

const tabComponents = {
  general: General,
  "personal-data": PersonalData,
  "data-processing": DataProcessing,
  consents: Consent,
  dpar: Dpar,
  audit: Audit,
  other: Other,
};

const Page = () => {
  const params = useParams();
  const dpId = params.dp_id;
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const { canWrite } = usePermissions();

  const [dpData, setDpData] = useState();
  const [showModal, setShowModal] = useState(false);
  const [selectedId, setSelectedId] = useState(null);

  useEffect(() => {
    if (isValidObjectId(dpId)) {
      getOneDataPrincipal();
    }
  }, [dpId]);

  const getOneDataPrincipal = async () => {
    try {
      const response = await apiCall(
        `/data-principal/view-data-principal/${dpId}`
      );
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
      await apiCall(`/data-principal/delete-data-principal/${dpId}`, {
        method: "DELETE",
      });
      toast.success("Data Principal deleted successfully");
      closeModal();
      router.push("/apps/principal-management");
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
    path: `/apps/principal-management/${dpId}`,
    skip: "/apps",
  };

  return (
    <InvalidIdWrapper id={dpId}>
      <div className="">
        <div className="flex">
          <div className="w-full">
            <div className="flex flex-col items-center justify-between pr-6 sm:flex sm:flex-row">
              <Header
                title="Data Principal Details"
                breadcrumbsProps={breadcrumbsProps}
              />
              <Button
                disabled={!canWrite("/apps/principal-management")}
                variant="delete"
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
                <TabsList className="gap-10">
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
              title="Do you want to delete this"
              id={selectedId}
              onConfirm={handleDelete}
              typeTitle="Data Principal"
              field="Data Principal?"
            />
          )}
        </div>
      </div>
    </InvalidIdWrapper>
  );
};

export default Page;
