"use client";

import Button from "@/components/ui/Button";
import { InputField } from "@/components/ui/Inputs";
import NoDataFound from "@/components/ui/NoDataFound";
import Skeleton from "@/components/ui/Skeleton";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { MdEdit } from "react-icons/md";
import { useState, useEffect } from "react";
import Cookies from "js-cookie";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";

const Profile = ({ edit, setEdit }) => {
  const [formData, setFormData] = useState(null);
  const [editData, setEditData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await apiCall("/auth/get-my-profile");
      setFormData(res);
      setEditData(res);
    } catch (err) {
      console.error("Failed to load profile", err);
      toast.error(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto flex max-w-[750px] flex-col items-center justify-center py-10">
        <Skeleton variant="multiple" />
      </div>
    );
  }

  if (!formData) {
    return (
      <div className="flex flex-col items-center justify-center py-10">
        <NoDataFound />
      </div>
    );
  }

  const { first_name, last_name, phone, designation } = formData;

  const handleEditClick = () => setEdit("profile");

  const handleCancel = () => {
    setEdit(null);
    setEditData(formData);
  };

  const handleInputChange = (field, value) => {
    setEditData((prev) => ({ ...prev, [field]: value }));
  };

  const hasChanges = () =>
    JSON.stringify(editData) !== JSON.stringify(formData);

  const handleSave = async () => {
    setSaving(true);
    try {
      const params = new URLSearchParams({
        first_name: editData.first_name || "",
        last_name: editData.last_name || "",
        email: editData.email || "",
        phone: editData.phone || "",
        designation: editData.designation || "",
      });

      await apiCall(`/auth/update-my-profile?${params.toString()}`, {
        method: "PATCH",
      });

      setFormData(editData);
      setEdit(null);
    } catch (err) {
      console.error("Update failed", err);
      toast.error(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="w-[750px] px-10">
        <div className="mt-5 flex items-center justify-between">
          <div>
            <h3 className="text-[18px]">Profile Information</h3>
            <p className="text-xs text-subHeading">
              Update your personal details.
            </p>
          </div>

          {edit !== "profile" && (
            <Button
              variant="secondary"
              className="flex gap-2"
              onClick={handleEditClick}
            >
              <MdEdit />
              Edit
            </Button>
          )}
        </div>

        <div
          className={`${edit == "profile" ? "mt-3" : "mt-5"} flex w-full gap-4`}
        >
          <div className="w-1/2">
            {edit == "profile" ? (
              <InputField
                label="First Name"
                value={editData?.first_name || ""}
                onChange={(e) =>
                  handleInputChange("first_name", e.target.value)
                }
                placeholder="Enter first name"
              />
            ) : (
              <>
                <h2 className="text-sm text-subHeading">First Name</h2>
                <p className="text-[16px]">{first_name}</p>
              </>
            )}
          </div>

          <div className="w-1/2">
            {edit == "profile" ? (
              <InputField
                label="Last Name"
                value={editData?.last_name || ""}
                onChange={(e) => handleInputChange("last_name", e.target.value)}
                placeholder="Enter last name"
              />
            ) : (
              <>
                <h2 className="text-sm text-subHeading">Last Name</h2>
                <p className="text-[16px]">{last_name}</p>
              </>
            )}
          </div>
        </div>

        <div
          className={`${edit == "profile" ? "mt-3" : "mt-5"} flex w-full gap-4`}
        >
          <div className="w-1/2">
            {edit == "profile" ? (
              <InputField
                label="Designation"
                value={editData?.designation || ""}
                onChange={(e) =>
                  handleInputChange("designation", e.target.value)
                }
                placeholder="Enter designation"
              />
            ) : (
              <>
                <h2 className="text-sm text-subHeading">Designation</h2>
                <p className="text-[16px]">{designation}</p>
              </>
            )}
          </div>
        </div>

        <div
          className={`${edit == "profile" ? "mb-12 mt-3" : "mt-5"} flex w-full`}
        >
          <div className="w-1/2">
            {edit == "profile" ? (
              <InputField
                label="Mobile Number"
                type="tel"
                value={editData?.phone || ""}
                onChange={(e) => handleInputChange("phone", e.target.value)}
                placeholder="Enter mobile number"
                inputMode="numeric"
                maxLength={10}
              />
            ) : (
              <>
                <h2 className="text-sm text-subHeading">Mobile Number</h2>
                <p className="text-sm">{phone}</p>
              </>
            )}
          </div>
        </div>

        {edit == "profile" && (
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
      </div>
    </div>
  );
};

export default Profile;
