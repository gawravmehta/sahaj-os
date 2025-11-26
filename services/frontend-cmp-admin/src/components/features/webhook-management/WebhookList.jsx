"use client";

import Button from "@/components/ui/Button";
import { AiOutlinePlus } from "react-icons/ai";
import { MdEdit, MdDelete, MdSend, MdInfoOutline } from "react-icons/md";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";
import { useState } from "react";
import { useRouter } from "next/navigation";
import ConfirmationModal from "@/components/ui/ConfirmationModal";

const WebhookList = ({
  webhooks,
  loading,
  fetchWebhooks,
  openEditModal,
  openAddModal,
}) => {
  const router = useRouter();
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [webhookToDelete, setWebhookToDelete] = useState(null);
  const [isTestModalOpen, setIsTestModalOpen] = useState(false);
  const [webhookToTest, setWebhookToTest] = useState(null);

  const handleDeleteClick = (webhook) => {
    setWebhookToDelete(webhook);
    setIsDeleteModalOpen(true);
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

  const handleTestClick = (webhook) => {
    setWebhookToTest(webhook);
    setIsTestModalOpen(true);
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

  const handleDetailClick = (webhook) => {
    router.push(`/webhook-management/details/${webhook.webhook_id}`);
  };

  const eventColor = (event) => {
    switch (event.toLowerCase()) {
      case "consent_granted":
        return "bg-green-100 text-green-700";
      case "consent_withdrawn":
        return "bg-red-100 text-red-700";
      case "consent_updated":
        return "bg-yellow-100 text-yellow-700";
      default:
        return "bg-blue-100 text-blue-700";
    }
  };

  if (loading) {
    return <div className="p-4 text-center">Loading webhooks...</div>;
  }

  return (
    <div className="mx-auto w-full px-4 sm:px-6 md:px-10 py-5 flex flex-col gap-6">
      <div className="flex justify-end">
        <Button onClick={openAddModal} className="flex items-center gap-2">
          <AiOutlinePlus /> Add New Webhook
        </Button>
      </div>

      {webhooks.length === 0 ? (
        <div className="text-center text-gray-500">No webhooks configured.</div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  URL
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Events
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Environment
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Details
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>

            <tbody className="bg-white divide-y divide-gray-200">
              {webhooks.map((webhook) => (
                <tr
                  key={webhook.webhook_id}
                  className="hover:bg-gray-50 transition"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {webhook.url}
                  </td>

                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex flex-wrap gap-2">
                      {webhook.subscribed_events.map((event, idx) => (
                        <span
                          key={idx}
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${eventColor(
                            event
                          )}`}
                        >
                          {event}
                        </span>
                      ))}
                    </div>
                  </td>

                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {webhook.status}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {webhook.environment}
                  </td>

                  <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                    <Button
                      variant="ghost"
                      onClick={() => handleDetailClick(webhook)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      <MdInfoOutline />
                    </Button>
                  </td>

                  <td className="px-6 py-4 flex items-center whitespace-nowrap text-right text-sm font-medium">
                    <Button
                      variant="ghost"
                      onClick={() => openEditModal(webhook)}
                      className="text-indigo-600 hover:text-indigo-900 mr-2"
                    >
                      <MdEdit />
                    </Button>

                    <Button
                      variant="ghost"
                      onClick={() => handleTestClick(webhook)}
                      className="text-green-600 hover:text-green-900 mr-2"
                    >
                      <MdSend />
                    </Button>

                    <Button
                      variant="ghost"
                      onClick={() => handleDeleteClick(webhook)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <MdDelete />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {isDeleteModalOpen && (
        <ConfirmationModal
          isOpen={isDeleteModalOpen}
          onClose={() => setIsDeleteModalOpen(false)}
          onConfirm={confirmDelete}
          title="Confirm Deletion"
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
  );
};

export default WebhookList;
