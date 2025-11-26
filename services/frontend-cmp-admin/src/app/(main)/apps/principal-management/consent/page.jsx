"use client";

import React, { useEffect, useState } from "react";

import ConsentMain from "@/components/features/principalManagement/consent/ConsentMain";
import Modal from "@/components/features/principalManagement/consent/Modal";
import CampaignMedium from "@/components/features/principalManagement/consent/CampaignMedium";
import NoticeTemplates from "@/components/features/principalManagement/consent/NoticeTemplates";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";
import Header from "@/components/ui/Header";
import Button from "@/components/ui/Button";
import { SelectInput } from "@/components/ui/Inputs";
import { usePermissions } from "@/contexts/PermissionContext";

function Page() {
  const [tableDataRows, setTableDataRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState("");

  const { canWrite } = usePermissions();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCpId, setSelectedCpId] = useState(null);
  const [selectedMediums, setSelectedMediums] = useState([]);
  const [isNoticeValid, setIsNoticeValid] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [dpTags, setDpTags] = useState([]);
  const [wrongFields, setWrongFields] = useState([]);
  const [smsInApp, setSmsInApp] = useState({
    sms: "",
    in_app: "",
  });

  const breadcrumbsProps = {
    path: "/apps/principal-management/consent",
    skip: "/apps",
  };

  useEffect(() => {
    getCampaignNotifications();
  }, [currentPage, rowsPerPageState]);

  const getCampaignNotifications = async () => {
    setLoading(true);
    try {
      const response = await apiCall(
        `/notice-notification/get-all-notice-notifications?page=${currentPage}&limit=${rowsPerPageState}`
      );

      const { notifications, pagination } = response;

      setTotalPages(pagination.total_pages);
      setCurrentPage(pagination.current_page);

      const formattedData = notifications.map((notification) => ({
        email: notification.dp_email,
        mobile: notification.dp_mobile,
        preferredLanguage: notification.preferred_language,
        dpId: notification.dp_id,
        addedBy: notification.created_by,
        createdAt: notification.created_at,
        sentAt: notification.sent_at,
        status: notification.notification_status,
        notificationMedium: notification.notification_medium.join(", "),
        noticeName: notification.notice_name,
        clickStatus: notification.is_notification_clicked,
        readStatus: notification.is_notification_read,
        consentStatus:
          notification.notification_status === "sent"
            ? "Pending"
            : notification.notification_status,
      }));

      setTableDataRows(formattedData);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleSendNotification = async () => {
    if (!selectedCpId) {
      toast.error("Please select a template");
      return;
    }

    if (selectedMediums.length === 0) {
      toast.error("Please select at least one medium");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        cp_id: selectedCpId,
        sending_medium: selectedMediums,
        dp_tags: dpTags,
        sms_template_name: smsInApp.sms,
        in_app_template_name: smsInApp.in_app,
      };

      await apiCall(`/notice-notification/send-notice`, {
        method: "POST",
        data: payload,
      });

      toast.success("Notification sent successfully!");
      setIsModalOpen(false);
      setSelectedCpId(null);
      setSelectedMediums([]);
      setIsNoticeValid(false);

      getCampaignNotifications();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-h-[calc(100vh-53px)]">
      <div className="flex items-center justify-between pr-6">
        <Header
          title="Consent"
          subtitle="Individuals who have given you the consent"
          breadcrumbsProps={breadcrumbsProps}
        />
        <Button
          variant="secondary"
          className="float-right flex cursor-pointer items-center gap-1 px-3 py-1 font-medium"
          onClick={() => setIsModalOpen(true)}
          disabled={!canWrite("/apps/principal-management")}
        >
          Send Notification
        </Button>
      </div>
      <div className="h-0.5 w-full py-2 sm:border-t sm:border-borderheader"></div>

      <ConsentMain
        tableDataRows={tableDataRows}
        loading={loading}
        currentPage={currentPage}
        totalPages={totalPages}
        setCurrentPage={setCurrentPage}
        rowsPerPageState={rowsPerPageState}
        setRowsPerPageState={setRowsPerPageState}
      />

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirm={handleSendNotification}
        isSubmitting={isSubmitting}
        isConfirmDisabled={!isNoticeValid || selectedMediums.length === 0}
        dpTags={dpTags}
        setDpTags={setDpTags}
        wrongFields={wrongFields}
        selectedMediums={selectedMediums}
        setSmsInApp={setSmsInApp}
        smsInApp={smsInApp}
      >
        <CampaignMedium
          selectedMediums={selectedMediums}
          setSelectedMediums={setSelectedMediums}
        />
        <NoticeTemplates
          setCpId={setSelectedCpId}
          cpId={selectedCpId}
          setNoticeAvailable={() => {}}
          setIsNoticeValid={setIsNoticeValid}
        />

      </Modal>
    </div>
  );
}

export default Page;
