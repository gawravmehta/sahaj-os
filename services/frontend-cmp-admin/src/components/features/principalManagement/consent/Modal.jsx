"use client";
import React, { useEffect, useState } from "react";

import { RxCross2 } from "react-icons/rx";

import { apiCall } from "@/hooks/apiCall";
import Button from "@/components/ui/Button";
import { SelectInput } from "@/components/ui/Inputs";

export default function Modal({
  isOpen,
  onClose,
  children,
  onConfirm,
  isSubmitting = false,
  isConfirmDisabled = false,
  dpTags = [],
  setDpTags = () => {},
  wrongFields = [],
  selectedMediums = [],
  setSmsInApp,
  smsInApp,
}) {
  const [tagOptions, setTagOptions] = useState([]);
  const [loading, setLoading] = useState(false);

  const [templateOption, setTemplateOption] = useState({
    sms: [],
    in_app: [],
  });

  useEffect(() => {
    if (!isOpen) return;

    const fetchTags = async () => {
      try {
        const res = await apiCall("/data-principal/get-all-dp-tags");

        const tags = res.dp_tags || [];

        const formatted = tags.map((tag) => ({
          value: tag,
          label: tag,
        }));

        setTagOptions(formatted);
      } catch (err) {
        console.error("Failed to fetch tags:", err);
        setTagOptions([]);
      }
    };

    fetchTags();
    fetchTemplates();
  }, [isOpen]);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const smsRes = await apiCall("/data-fiduciary/get-all-sms-templates");
      const smsData = Array.isArray(smsRes)
        ? smsRes.map((item) => ({
            value: item.name,
            label: item.name,
          }))
        : [];

      const inAppRes = await apiCall(
        "/data-fiduciary/get-all-in-app-notification-templates"
      );
      const inAppData = Array.isArray(inAppRes)
        ? inAppRes.map((item) => ({
            value: item.name,
            label: item.name,
          }))
        : [];

      setTemplateOption({
        sms: smsData,
        in_app: inAppData,
      });
    } catch (err) {
      console.error("Failed to load templates", err);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/40"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-3xl border border-[#C7CFE2] bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="mb-4 text-xl text-center border-b-1 font-semibold text-gray-800">
          Send Notice Notification
        </h2>
        <Button
          variant="cancel"
          className="absolute right-5 top-4 p-0.5 cursor-pointer"
          onClick={onClose}
        >
          <RxCross2 size={26} />
        </Button>
        {children}
        <div className="grid grid-cols-3 gap-5 w-full mt-10">
          <SelectInput
            isMulti
            name="tags"
            label="Tags"
            tooltipText="Used to segment or categorize data principals into different cohorts for easier management, personalized notices, language personalization, and advanced consent collection strategies."
            options={tagOptions}
            value={dpTags?.map((val) =>
              tagOptions.find((item) => item.value === val)
            )}
            placeholder="Select Tags"
            onChange={(selectedOptions) => {
              const values = selectedOptions
                ? selectedOptions.map((opt) => opt.value)
                : [];
              setDpTags(values);
            }}
          />

          {selectedMediums.includes("in-app") && (
            <SelectInput
              name="inAppTags"
              label="Select Template for In App"
              options={templateOption.in_app}
              value={
                smsInApp.in_app
                  ? templateOption.in_app.find(
                      (item) => item.value === smsInApp.in_app
                    )
                  : null
              }
              placeholder="Select In App Tags"
              onChange={(selectedOption) => {
                setSmsInApp((prev) => ({
                  ...prev,
                  in_app: selectedOption ? selectedOption.value : "",
                }));
              }}
            />
          )}

          {selectedMediums.includes("sms") && (
            <SelectInput
              name="smsTags"
              label="Select Template for SMS"
              options={templateOption.sms}
              value={
                smsInApp.sms
                  ? templateOption.sms.find(
                      (item) => item.value === smsInApp.sms
                    )
                  : null
              }
              placeholder="Select SMS Tags"
              onChange={(selectedOption) => {
                setSmsInApp((prev) => ({
                  ...prev,
                  sms: selectedOption ? selectedOption.value : "",
                }));
              }}
            />
          )}
        </div>
        {wrongFields.some((field) => field.value === "tags") && (
          <span className="text-sm text-red-500">
            {wrongFields.find((field) => field.value === "tags")?.message}
          </span>
        )}

        <div className="mt-8 flex justify-end gap-4">
          <Button
            variant="primary"
            onClick={onConfirm}
            disabled={isConfirmDisabled || isSubmitting}
            className="w-full"
          >
            {isSubmitting ? "Sending..." : "Send Notification"}
          </Button>
        </div>
      </div>
    </div>
  );
}
