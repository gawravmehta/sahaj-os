"use client";

import Button from "@/components/ui/Button";
import { InputField, SelectInput, TextareaField } from "@/components/ui/Inputs";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { MdEdit } from "react-icons/md";
import { useState, useEffect } from "react";
import OrganizationEditModal from "./OrganizationEditModal";
import Link from "next/link";
import { countryOptions } from "@/constants/countryOptions";

const Organization = ({
  formData,
  setFormData,
  edit,
  setEdit,
  handleSave,
  setModalOpen,
  modalOpen,
  saving,
}) => {
  const [editData, setEditData] = useState(null);
  const [loading, setLoading] = useState(false);
  useEffect(() => {
    if (formData?.org_info) {
      setEditData({ ...formData.org_info });
    }
  }, [formData]);

  if (!formData?.org_info) {
    return <p className="text-center py-10">No organization data found.</p>;
  }

  const {
    name,
    website_url,
    country,
    cookie_policy_url,
    privacy_policy_url,
    df_logo_url,
    address,
  } = editData || {};

  const { full_name, email, mobile } = formData?.dpo_information || {};
  const handleEditClick = () => setEdit("organization");

  const handleEdits = () => {
    setModalOpen(true);
  };

  const handleCancel = () => {
    setEditData({ ...formData.org_info });
    setEdit(false);
  };

  const handleInputChange = (field, value) => {
    setEditData((prev) => ({ ...prev, [field]: value }));
    setFormData((prev) => ({
      ...prev,
      org_info: { ...prev.org_info, [field]: value },
    }));
  };

  const handleDpoChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      dpo_information: {
        ...prev.dpo_information,
        [field]: value,
      },
    }));
  };

  const hasChanges = () =>
    JSON.stringify(editData) !== JSON.stringify(formData.org_info);

  return (
    <div className="mx-auto w-[750px] px-4 sm:px-6 md:px-10 py-5 mb-5">
      <div className="border-b border-borderheader pb-4 ">
        <h3 className="text-[18px]">Basic Information</h3>
        <p className="text-xs text-subHeading">
          Set up your sub-organization, customize branding.
        </p>
        <div className="mt-3 flex items-center justify-between -z-50">
          <div className="mt-2 flex gap-4">
            <div className="relative h-20 w-20 rounded-full border">
              <img
                alt="Organization Logo"
                src={df_logo_url || "/assets/other/org-logo.png"}
                className="h-full w-full rounded-full p-1 object-contain"
                onError={(e) => {
                  e.target.src = "/assets/other/user-copy.png";
                }}
              />

              <div className="absolute bottom-0 right-0 flex h-5 w-5 -rotate-90 items-center justify-center rounded-full bg-white shadow">
                <MdEdit
                  className="cursor-pointer text-[10px] text-gray-600"
                  onClick={handleEdits}
                />
              </div>
            </div>
            <div>
              <h1 className="text-[16px] font-medium">
                {formData.organizationName || "Organization Name"}
              </h1>
              <p className="text-[14px] text-gray-600">
                {formData.industry || "Industry"}
              </p>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-5 flex items-center justify-between ">
        <h3 className="text-lg font-semibold">Organization Details</h3>
        {edit !== "organization" && (
          <Button
            variant="secondary"
            className="flex gap-2"
            onClick={handleEditClick}
          >
            <MdEdit /> Edit
          </Button>
        )}
      </div>

      <div
        className={`${
          edit == "organization" ? "mt-3" : "mt-5"
        } grid grid-cols-2 gap-6  border-b border-borderheader pb-4`}
      >
        {edit == "organization" ? (
          <>
            <InputField
              label="Organization Name"
              placeholder="Enter organization name"
              value={name || ""}
              onChange={(e) => handleInputChange("name", e.target.value)}
            />
            <InputField
              label="Website"
              placeholder="Enter website URL"
              value={website_url || ""}
              onChange={(e) => handleInputChange("website_url", e.target.value)}
            />
            <SelectInput
              label="Country"
              placeholder="Select Country"
              options={countryOptions}
              value={countryOptions?.find((value) => value?.value === country)}
              onChange={(selected) =>
                handleInputChange("country", selected?.value || "IN")
              }
            />
            <InputField
              label="Cookie Policy URL"
              value={cookie_policy_url || ""}
              onChange={(e) =>
                handleInputChange("cookie_policy_url", e.target.value)
              }
            />
            <InputField
              label="Privacy Policy URL"
              placeholder="Enter privacy policy URL"
              value={privacy_policy_url || ""}
              onChange={(e) =>
                handleInputChange("privacy_policy_url", e.target.value)
              }
            />
            
            <TextareaField
              label="Address"
              placeholder="Enter address"
              value={address || ""}
              onChange={(e) => handleInputChange("address", e.target.value)}
              className="col-span-2"
            />
          </>
        ) : (
          <>
            <div>
              <h2 className="text-sm text-subHeading">Organization Name</h2>
              <p>{name}</p>
            </div>
            <div>
              <h2 className="text-sm text-subHeading">Website</h2>
              <Link
                href={website_url || "#"}
                target="_blank"
                className="text-blue-400 hover:underline truncate block max-w-[18rem]"
              >
                {website_url}
              </Link>
            </div>
            <div>
              <h2 className="text-sm text-subHeading">Country</h2>
              <p className="capitalize">{country}</p>
            </div>
            <div>
              <h2 className="text-sm text-subHeading">Cookie Policy</h2>
              <Link
                href={cookie_policy_url || "#"}
                target="_blank"
                className="text-blue-400 hover:underline truncate block max-w-[18rem]"
              >
                {cookie_policy_url}
              </Link>
            </div>
            <div>
              <h2 className="text-sm text-subHeading">Privacy Policy</h2>
              <Link
                href={privacy_policy_url || "#"}
                target="_blank"
                className="text-blue-400 hover:underline truncate block max-w-[18rem]"
              >
                {privacy_policy_url}
              </Link>
            </div>

            <div className="col-span-2">
              <h2 className="text-sm text-subHeading">Address</h2>
              <p>{address}</p>
            </div>
          </>
        )}
      </div>

      <div className="mt-5 flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          Data Protection Officer (DPO) Details
        </h3>
      </div>

      <div
        className={`${
          edit == "organization" ? "mt-3" : "mt-5"
        } grid grid-cols-2 gap-6 border-b border-borderheader pb-4`}
      >
        {edit == "organization" ? (
          <>
            <InputField
              label="Full Name"
              value={full_name || ""}
              onChange={(e) => handleDpoChange("full_name", e.target.value)}
            />
            <InputField
              label="Email"
              value={email || ""}
              onChange={(e) => handleDpoChange("email", e.target.value)}
            />
            <InputField
              label="Mobile"
              maxLength={10}
              inputMode="numeric"
              value={mobile || ""}
              onChange={(e) => handleDpoChange("mobile", e.target.value)}
            />
          </>
        ) : (
          <>
            <div>
              <h2 className="text-sm text-subHeading">Full Name</h2>
              <p>{full_name}</p>
            </div>
            <div>
              <h2 className="text-sm text-subHeading">Email</h2>
              <p>{email}</p>
            </div>
            <div>
              <h2 className="text-sm text-subHeading">Mobile</h2>
              <p>{mobile}</p>
            </div>
          </>
        )}
      </div>

      {edit == "organization" && (
        <StickyFooterActions
          showCancel
          cancelLabel="Cancel"
          onCancel={handleCancel}
          showSubmit
          onSubmit={handleSave}
          submitLabel={saving ? "Saving..." : "Save Changes"}
          submitDisabled={!hasChanges() || saving}
          className="mt-10 py-4 shadow-xl"
        />
      )}
      {modalOpen && (
        <OrganizationEditModal
          visible={modalOpen}
          onClose={() => setModalOpen(false)}
          df_logo_url={df_logo_url}
          onChange={handleInputChange}
          onSave={handleSave}
          loading={loading}
        />
      )}
    </div>
  );
};

export default Organization;
