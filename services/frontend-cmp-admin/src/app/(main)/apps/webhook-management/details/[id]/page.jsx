"use client";

import {
  DetailItem,
  eventColor,
  formatDateTime,
  MetricItem,
} from "@/components/features/webhook-management/WebhookDetailPage";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import { apiCall } from "@/hooks/apiCall";
import { use, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";
import ConfirmationModal from "@/components/ui/ConfirmationModal";

const WebhookDetailsRoute = ({ params }) => {
  const { id } = use(params);
  const [webhookDetails, setWebhookDetails] = useState({});
  const [loading, setLoading] = useState(false);
  const [isActivateModalOpen, setIsActivateModalOpen] = useState(false);
  const [webhookToActOn, setWebhookToActOn] = useState(null);

  const getOneWebhookDetails = async () => {
    try {
      const response = await apiCall(`/webhooks/get-one-webhook/${id}`);
      setWebhookDetails(response);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleActivateWebhook = async () => {
    setLoading(true);
    try {
      await apiCall(`/webhooks/update-webhook/${webhookDetails.webhook_id}`, {
        method: "PUT",
        data: { status: "active" },
      });
      toast.success("Webhook activated successfully");
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
      setIsActivateModalOpen(false);
      setWebhookToActOn(null);
      getOneWebhookDetails();
    }
  };

  useEffect(() => {
    getOneWebhookDetails();
  }, []);

  const breadcrumbsProps = {
    path: `/apps/webhook-management/${id}`,
    skip: "/",
  };

  return (
    <div className="flex flex-col justify-between">
      <div className="flex w-full items-center justify-between bg-background pr-6">
        <Header
          title={
            webhookDetails?.webhook_id
              ? `${webhookDetails?.webhook_id} Details`
              : "Webhook Details"
          }
          breadcrumbsProps={breadcrumbsProps}
        />
        <div className="flex items-center gap-3">
          {webhookDetails?.status === "inactive" && (
            <Button
              variant="primary"
              className="px-3"
              onClick={() => {
                setWebhookToActOn(webhookDetails);
                setIsActivateModalOpen(true);
              }}
              disabled={loading}
            >
              Activate Webhook
            </Button>
          )}
        </div>
      </div>

      <Tabs defaultValue="metrics">
        <div className="flex w-full items-center justify-start border-y border-borderSecondary sm:justify-center">
          <div className="flex flex-wrap gap-4 sm:flex sm:flex-row">
            <TabsList className="w-full space-x-12">
              <TabsTrigger value="metrics" variant="secondary">
                Metrics
              </TabsTrigger>
              <TabsTrigger value="config" variant="secondary">
                Configuration
              </TabsTrigger>
              <TabsTrigger value="retry" variant="secondary">
                Retry Policy
              </TabsTrigger>
              <TabsTrigger value="subs" variant="secondary">
                Subscribed Events
              </TabsTrigger>
              <TabsTrigger value="security" variant="secondary">
                Security
              </TabsTrigger>
              <TabsTrigger value="audit" variant="secondary">
                Audit
              </TabsTrigger>
            </TabsList>
          </div>
        </div>

        <TabsContent value="metrics">
          <section className="mx-auto w-full max-w-3xl rounded-sm px-4 sm:px-6 mt-5">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricItem
                label="Delivered Events"
                value={webhookDetails?.metrics?.delivered}
                isSuccess
                dateTime={formatDateTime(webhookDetails?.metrics?.last_success)}
              />
              <MetricItem
                label="Failed Deliveries"
                value={webhookDetails?.metrics?.failed}
                isFailure
                dateTime={formatDateTime(webhookDetails?.metrics?.last_failure)}
              />
              <div className="col-span-1 sm:col-span-2 lg:col-span-2 space-y-4 pt-2">
                <DetailItem
                  label="Last Successful Delivery"
                  value={formatDateTime(webhookDetails?.metrics?.last_success)}
                />
                <DetailItem
                  label="Last Failed Delivery"
                  value={formatDateTime(webhookDetails?.metrics?.last_failure)}
                />
              </div>
            </div>
          </section>
        </TabsContent>
        <TabsContent value="config">
          <section className="mx-auto w-full max-w-3xl rounded-sm px-4 sm:px-6 mt-5">
            <div className="space-y-4">
              <DetailItem
                label="Webhook URL"
                value={webhookDetails.url}
                isLink
              />

              <div className="flex flex-col gap-4">
                <DetailItem
                  label="Webhook Target"
                  value={
                    webhookDetails?.webhook_for
                      ? webhookDetails?.webhook_for
                          .replace(/_/g, " ")
                          .toUpperCase()
                      : "Webhook target"
                  }
                />

                <DetailItem
                  label="Environment"
                  value={webhookDetails?.environment?.toUpperCase() ?? ""}
                />

                <DetailItem
                  label="DF ID"
                  value={webhookDetails.df_id}
                  isCopyable
                  isMonospace
                />
              </div>
            </div>
          </section>
        </TabsContent>
        <TabsContent value="retry">
          <section className="mx-auto w-full max-w-3xl rounded-sm px-4 sm:px-6 mt-5">
            <div className="space-y-5">
              <DetailItem
                label="Max Retries"
                value={webhookDetails?.retry_policy?.max_retries}
                isValueHighlight
              />

              <DetailItem
                label="Retry Interval (sec)"
                value={webhookDetails?.retry_policy?.retry_interval_sec}
                isValueHighlight
              />

              <DetailItem
                label="Backoff Strategy"
                value={webhookDetails?.retry_policy?.backoff_strategy}
              />
            </div>
          </section>
        </TabsContent>
        <TabsContent value="subs">
          <section className="mx-auto w-full max-w-3xl rounded-sm px-4 sm:px-6 mt-5">
            <div className="flex flex-wrap gap-3">
              {webhookDetails?.subscribed_events?.map((event, index) => (
                <span
                  key={index}
                  className={`px-3 py-1 border text-sm  ${eventColor(event)}`}
                >
                  {event.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          </section>
        </TabsContent>
        <TabsContent value="security">
          <section className="mx-auto w-full max-w-3xl rounded-sm px-4 sm:px-6 mt-5">
            <div className="space-y-4">
              <DetailItem
                label="Auth Type"
                value={webhookDetails?.auth?.type?.toUpperCase()}
              />

              <DetailItem
                label="Auth Key Header"
                value={webhookDetails?.auth?.key}
                isMonospace
              />

              <DetailItem
                label="Auth Secret Value"
                value={webhookDetails?.auth?.secret}
                isSecret
              />

              <DetailItem
                label="HMAC Token (for verification)"
                value={webhookDetails?.hmac_token}
                isSecret
                isMonospace
              />
            </div>
          </section>
        </TabsContent>
        <TabsContent value="audit">
          <section className="mx-auto w-full max-w-3xl rounded-sm px-4 sm:px-6 mt-5">
            <div className="space-y-4">
              <DetailItem
                label="Created By User ID"
                value={webhookDetails?.created_by}
                isCopyable
                isMonospace
              />

              <DetailItem
                label="Created At"
                value={formatDateTime(webhookDetails?.created_at)}
              />

              <DetailItem
                label="Updated By User ID"
                value={webhookDetails?.updated_by}
                isCopyable
                isMonospace
              />

              <DetailItem
                label="Updated At"
                value={formatDateTime(webhookDetails?.updated_at)}
              />
            </div>
          </section>
        </TabsContent>
      </Tabs>

      {isActivateModalOpen && (
        <ConfirmationModal
          isOpen={isActivateModalOpen}
          onClose={() => setIsActivateModalOpen(false)}
          onConfirm={handleActivateWebhook}
          title="Confirm Activate Webhook"
          message={`Are you sure you want to activate the webhook at URL: ${webhookToActOn?.url}? This will trigger a test event, and if successful, set the webhook status to 'active'.`}
          btnLoading={loading}
        />
      )}
    </div>
  );
};

export default WebhookDetailsRoute;
