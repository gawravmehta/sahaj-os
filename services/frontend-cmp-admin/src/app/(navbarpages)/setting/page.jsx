"use client";

import AddSmtpModal from "@/components/features/setting/AddSmtpModal";
import AI from "@/components/features/setting/AI";
import InApp from "@/components/features/setting/InApp";
import Organization from "@/components/features/setting/Organization";
import Profile from "@/components/features/setting/Profile";
import SMS from "@/components/features/setting/SMS";
import SmtpForm from "@/components/features/setting/SmtpForm";
import Webhook from "@/components/features/setting/Webhook";
import { useOrg } from "@/components/shared/OrgContext";
import Header from "@/components/ui/Header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { getUpdatedFields } from "@/utils/getUpdatedFields";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";

const Page = () => {
  const [loading, setLoading] = useState(false);
  const [edit, setEdit] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("my_profile");
  const [formData, setFormData] = useState(null);
  const [originalData, setOriginalData] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const { setOrgName } = useOrg();
  const tabs = [
    { id: "my_profile", label: "My Profile" },
    { id: "organization", label: "Organization" },
    { id: "smtp", label: "SMTP" },
    { id: "sms", label: "SMS" },
    { id: "in_app", label: "In App" },
    { id: "ai", label: "AI" },
  ];

  const tabComponents = {
    my_profile: Profile,
    organization: Organization,
    smtp: SmtpForm,
    sms: SMS,
    in_app: InApp,
    ai: AI,
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await apiCall("/data-fiduciary/data-fiduciary-details");
      setFormData(response || null);
      setOriginalData(response || null);
      const orgName = response?.org_info?.name || "";
      setOrgName(orgName);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const closeModal = () => setIsModalOpen(false);

  const handleSave = async () => {
    if (!formData || !originalData) return;

    const updatedFields = getUpdatedFields(originalData, formData);

    if (Object.keys(updatedFields).length === 0) {
      toast("No changes to save.");
      return;
    }

    setSaving(true);
    try {
      await apiCall("/data-fiduciary/setup-data-fiduciary", {
        method: "POST",
        data: updatedFields,
      });
      toast.success("Settings updated successfully");
      setOriginalData(formData);
      setEdit(false);
      setModalOpen(false);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex">
      <div className="w-full">
        <div className="flex flex-col justify-between gap-4 pr-6 sm:flex-row sm:border-borderheader">
          <Header
            title="Setting"
            subtitle="Manage your account settings and preference"
          />
        </div>

        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          defaultValue="my_profile"
        >
          <div className="flex w-full items-center justify-center border-b border-t border-borderheader">
            <TabsList className="gap-10">
              {tabs.map((tab) => (
                <TabsTrigger key={tab.id} value={tab.id} variant="secondary">
                  {tab.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </div>

          <div className="custom-scrollbar  h-[calc(100vh-175px)] overflow-auto">
            {isModalOpen && (
              <AddSmtpModal closeModal={closeModal} fetchData={fetchData} />
            )}

            {Object.entries(tabComponents).map(([key, Component]) => (
              <TabsContent key={key} value={key}>
                <Component
                  formData={formData}
                  setFormData={setFormData}
                  edit={edit}
                  setEdit={setEdit}
                  loading={loading}
                  handleSave={handleSave}
                  saving={saving}
                  fetchData={fetchData}
                  setModalOpen={setModalOpen}
                  modalOpen={modalOpen}
                />
              </TabsContent>
            ))}
          </div>
        </Tabs>
      </div>
    </div>
  );
};

export default Page;
