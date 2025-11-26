"use client";

import Header from "@/components/ui/Header";
import { useState, useEffect } from "react";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";
import AddEditWebhookModal from "@/components/features/webhook-management/AddEditWebhookModal";
import WebhookCreationDetailsModal from "@/components/features/webhook-management/WebhookCreationDetailsModal";
import Button from "@/components/ui/Button";
import { FiPlus } from "react-icons/fi";
import DataTable from "@/components/shared/data-table/DataTable";
import { MdDelete, MdEdit, MdSend } from "react-icons/md";
import ConfirmationModal from "@/components/ui/ConfirmationModal";

const WebhookManagementPage = () => {
  const [loading, setLoading] = useState(false);
  const [webhooks, setWebhooks] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingWebhook, setEditingWebhook] = useState(null);
  const [isCreationDetailsModalOpen, setIsCreationDetailsModalOpen] =
    useState(false);
  const [newWebhookDetails, setNewWebhookDetails] = useState(null);

  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [totalPages, setTotalPages] = useState("");
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [webhookToTest, setWebhookToTest] = useState(null);
  const [webhookToDelete, setWebhookToDelete] = useState(null);
  const [isTestModalOpen, setIsTestModalOpen] = useState(false);

  const fetchWebhooks = async () => {
    setLoading(true);
    try {
      const response = await apiCall(
        `/webhooks/get-all-webhooks?current_page=${currentPage}&data_per_page=${rowsPerPageState}`
      );
      setWebhooks(response.webhooks || []);
      setTotalPages(response.total_pages);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const confirmTest = async () => {
    if (!webhookToTest) return;
    try {
      const response = await apiCall(
        `/webhooks/test/${webhookToTest.webhook_id}`,
        {
          method: "POST",
        }
      );
      if (response.status === "success") {
        toast.success(response.message || "Webhook tested successfully.");
      } else {
        toast.error(response.message || "Failed to test webhook.");
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsTestModalOpen(false);
      setWebhookToTest(null);
    }
  };

  const confirmDelete = async () => {
    if (!webhookToDelete) return;
    try {
      await apiCall(`/webhooks/delete-webhook/${webhookToDelete.webhook_id}`, {
        method: "DELETE",
      });
      toast.success("Webhook deleted successfully");
      fetchWebhooks();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsDeleteModalOpen(false);
      setWebhookToDelete(null);
    }
  };

  useEffect(() => {
    fetchWebhooks();
  }, []);

  const openAddModal = () => {
    setEditingWebhook(null);
    setIsModalOpen(true);
  };

  const openEditModal = (webhook) => {
    setEditingWebhook(webhook);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingWebhook(null);
  };

  const handleWebhookCreated = (details) => {
    setNewWebhookDetails(details);
    setIsCreationDetailsModalOpen(true);
  };

  const closeCreationDetailsModal = () => {
    setIsCreationDetailsModalOpen(false);
    setNewWebhookDetails(null);
  };

  const handleDeleteClick = (webhook) => {
    setWebhookToDelete(webhook);
    setIsDeleteModalOpen(true);
  };

  const handleTestClick = (webhook) => {
    setWebhookToTest(webhook);
    setIsTestModalOpen(true);
  };

  const webhookColumn = [
    {
      header: "URL",
      accessor: "url",
      headerClassName: "text-left ",
      render: (element) => {
        return (
          <div className="max-w-44 truncate text-ellipsis font-medium ">
            {element}
          </div>
        );
      },
    },
    {
      header: "Subscribed Events",
      accessor: "subscribed_events",
      headerClassName: "text-left",
      render: (element) => {
        return (
          <div className="flex items-center gap-1 flex-wrap py-4">
            {element.slice(0, 4).map((event, idx) => (
              <span
                key={idx}
                className="inline-flex items-center px-2 py-1 border text-xs font-medium bg-gray-100"
              >
                {event}
              </span>
            ))}

            {element.length > 4 && (
              <span className="text-xs text-gray-500 font-medium">...</span>
            )}
          </div>
        );
      },
    },
    {
      header: "Environment",
      accessor: "environment",
      headerClassName: "text-left",
      render: (element) => {
        return (
          <div className="flex max-w-64 flex-col">
            <span className="max-w-44 truncate text-ellipsis font-medium capitalize">
              {element}
            </span>
          </div>
        );
      },
    },

    {
      header: "Status",
      accessor: "status",
      headerClassName: "text-center w-32",
      render: (element) => {
        let bgColor;

        if (element === "active") {
          bgColor = "bg-[#e1ffe7] text-[#06a42a]";
        } else if (element === "inactive") {
          bgColor = "bg-[#fbeaea] text-[#d94e4e]";
        }

        return (
          <div className="flex items-center justify-center">
            <div
              className={`w-20 rounded-full py-1 text-center capitalize ${bgColor}`}
            >
              {element}
            </div>
          </div>
        );
      },
    },
    {
      accessor: "webhook_id",
      headerClassName: "text-center w-20",
      render: (element, row) => {
        return (
          <div className="flex items-center gap-2 whitespace-nowrap text-right text-sm font-medium">
            <Button
              variant="icon"
              onClick={(e) => {
                e.stopPropagation();
                openEditModal(row);
              }}
              className="text-indigo-600 hover:text-indigo-900 "
            >
              <MdEdit />
            </Button>

            <Button
              variant="icon"
              onClick={(e) => {
                e.stopPropagation();
                handleTestClick(row);
              }}
              className="text-green-600 hover:text-green-900 "
            >
              <MdSend />
            </Button>

            <Button
              variant="icon"
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteClick(row);
              }}
              className="text-red-600 hover:text-red-900"
            >
              <MdDelete />
            </Button>
          </div>
        );
      },
    },
  ];

  return (
    <div>
      <>
        <div className="flex justify-between border-b border-borderheader">
          <Header
            title="Webhook Management"
            subtitle="Manage your webhook configurations."
          />

          <div className="flex items-center justify-center gap-2 px-5">
            <Button
              variant="secondary"
              onClick={openAddModal}
              className="flex w-[120px] gap-1 px-1"
            >
              <FiPlus className="text-base" />
              <p>New Webhook</p>
            </Button>
          </div>
        </div>

        <div className="relative w-full">
          <DataTable
            tableHeight={"213.5px"}
            columns={webhookColumn}
            data={webhooks}
            loading={loading}
            totalPages={totalPages}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            rowsPerPageState={rowsPerPageState}
            setRowsPerPageState={setRowsPerPageState}
            getRowRoute={(row) =>
              row?.webhook_id
                ? `/webhook-management/details/${row?.webhook_id}`
                : null
            }
            illustrationText="No Web hooks Available"
            illustrationImage="/assets/illustrations/no-data-find.png"
            noDataText="No Web hooks Found"
            noDataImage="/assets/illustrations/no-data-find.png"
          />
          {isModalOpen && (
            <AddEditWebhookModal
              closeModal={closeModal}
              fetchWebhooks={fetchWebhooks}
              editingWebhook={editingWebhook}
              onWebhookCreated={handleWebhookCreated}
            />
          )}

          {isCreationDetailsModalOpen && (
            <WebhookCreationDetailsModal
              isOpen={isCreationDetailsModalOpen}
              onClose={closeCreationDetailsModal}
              webhookDetails={newWebhookDetails}
            />
          )}

          {isDeleteModalOpen && (
            <ConfirmationModal
              isOpen={isDeleteModalOpen}
              onClose={() => setIsDeleteModalOpen(false)}
              onConfirm={confirmDelete}
              title="Confirm Deactivating Webhook"
              message={`Are you sure you want to delete the webhook at URL: ${webhookToDelete?.url}? This action cannot be undone.`}
            />
          )}

          {isTestModalOpen && (
            <ConfirmationModal
              isOpen={isTestModalOpen}
              onClose={() => setIsTestModalOpen(false)}
              onConfirm={confirmTest}
              title="Confirm Test Webhook"
              message={`Are you sure you want to send a test payload to the webhook at URL: ${webhookToTest?.url}?`}
            />
          )}
        </div>
      </>
    </div>
  );
};

export default WebhookManagementPage;
