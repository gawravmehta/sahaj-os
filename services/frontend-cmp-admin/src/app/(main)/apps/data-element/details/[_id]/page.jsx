"use client";

import DeGeneral from "@/components/features/dataElement/DeGeneral";
import DeGovernance from "@/components/features/dataElement/DeGovernance";
import DeleteModal from "@/components/shared/modals/DeleteModal";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import { usePermissions } from "@/contexts/PermissionContext";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { AiOutlineDelete } from "react-icons/ai";

const Page = ({ params }) => {
  const { _id: deId } = use(params);

  const router = useRouter();
  const [deData, setDeData] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedId, setSelectedId] = useState(null);

  const { canWrite } = usePermissions();

  useEffect(() => {
    if (deId) {
      getOneDataElement();
    }
  }, [deId]);

  const getOneDataElement = async () => {
    try {
      const response = await apiCall(`/data-elements/get-data-element/${deId}`);
      setDeData(response);
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  const publishDataElement = async (id) => {
    try {
      const response = await apiCall(
        `/data-elements/publish-data-element/${id}`,
        {
          method: "PATCH",
        }
      );
      toast.success("Data element published successfully!");
      router.push("/apps/data-element");
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  const handleDelete = async () => {
    try {
      const response = await apiCall(
        `/data-elements/delete-data-element/${selectedId}`,
        {
          method: "DELETE",
        }
      );

      toast.success("Data element deleted successfully");
      closeModal();
      router.push("/apps/data-element");
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

  const breadcrumbsProps = {
    path: `/apps/data-element/${deData?.de_name || deId}`,
    skip: "/apps/",
  };

  const toTitleCase = (str) =>
    str
      ? str.replace(
          /\w\S*/g,
          (txt) => txt.charAt(0).toUpperCase() + txt.slice(1)
        )
      : "";

  return (
    <div className="flex flex-col justify-between">
      <div className="flex w-full items-center justify-between bg-background pr-6">
        <Header
          title={
            deData?.de_name
              ? `${toTitleCase(deData?.de_name)} Details`
              : "Data Element Details"
          }
          breadcrumbsProps={breadcrumbsProps}
        />
        <div className="flex items-center gap-3">
          {deData?.de_status === "draft" && (
            <Button
              variant="primary"
              className="px-3"
              onClick={() => publishDataElement(deData?.de_id)}
              disabled={!canWrite("/apps/data-element")}
            >
              Publish
            </Button>
          )}
          {deData?.de_status !== "archived" && (
            <Button
              variant="delete"
              onClick={() => handleDeleteClick(deData?.de_id)}
              disabled={!canWrite("/apps/data-element")}
            >
              <AiOutlineDelete size={16} />

              <span>
                {deData?.de_status === "published" ? "Archive" : "Delete"}
              </span>
            </Button>
          )}
        </div>
      </div>

      <Tabs defaultValue="general">
        <div className="flex w-full items-center justify-start border-y border-borderSecondary sm:justify-center">
          <div className="flex flex-wrap gap-4 sm:flex sm:flex-row">
            <TabsList className="w-full space-x-12">
              <TabsTrigger value="general" variant="secondary">
                General
              </TabsTrigger>
              <TabsTrigger value="governance" variant="secondary">
                Governance
              </TabsTrigger>
            </TabsList>
          </div>
        </div>

        <TabsContent value="general">
          <DeGeneral deData={deData} />
        </TabsContent>
        <TabsContent value="governance">
          <DeGovernance deData={deData} />
        </TabsContent>
      </Tabs>

      {showModal && (
        <DeleteModal
          closeModal={closeModal}
          title={`Do you want to ${
            deData?.de_status === "draft" ? "delete" : "archive"
          } this`}
          id={selectedId}
          onConfirm={handleDelete}
          typeTitle="Data Element"
          field="data element?"
          isArchive={deData?.de_status === "published" ? true : false}
        />
      )}
    </div>
  );
};

export default Page;
