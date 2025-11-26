"use client";

import Button from "@/components/ui/Button";
import {
  CreatableInputs,
  InputField,
  SelectInput,
} from "@/components/ui/Inputs";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import YesNoToggle from "@/components/ui/YesNoToggle";
import { useEffect, useState } from "react";
import { MdEdit } from "react-icons/md";
import { RxLockClosed, RxLockOpen1 } from "react-icons/rx";

const SmtpForm = ({
  formData,
  setFormData,
  edit,
  setEdit,
  handleSave,
  saving,
}) => {
  const [editData, setEditData] = useState(null);
  const [wrongFields, setWrongFields] = useState([]);
  const [eye, setEye] = useState(true);
  const [hovered, setHovered] = useState(false);

  const toggleEye = () => setEye((prev) => !prev);
  const isValidEmail = (email) => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  };

  useEffect(() => {
    if (formData?.communication?.smtp?.credentials) {
      setEditData({ ...formData?.communication?.smtp?.credentials });
    }
  }, [formData]);

  const handleEditClick = () => setEdit("smtp");

  const handleCancel = () => {
    setEditData({ ...formData?.communication?.smtp?.credentials });
    setEdit(false);
  };

  const handleInputChange = (field, value) => {
    setEditData((prev) => ({ ...prev, [field]: value }));
    setFormData((prev) => ({
      ...prev,
      communication: {
        ...prev.communication,
        smtp: {
          ...prev.communication.smtp,
          credentials: {
            ...prev.communication.smtp.credentials,
            [field]: value,
          },
        },
      },
    }));

    if (field === "from_email") {
      if (value && !isValidEmail(value)) {
        setWrongFields([{ value: field, message: "Invalid email address" }]);
      } else {
        setWrongFields((prev) => prev?.filter((item) => item?.value !== field));
      }
    }
  };

  const hasChanges = () =>
    JSON.stringify(editData) !==
    JSON.stringify(formData?.communication?.smtp?.credentials);

  const {
    provider,
    host,
    port,
    username,
    password,
    from_email,
    from_name,
    tls,
    encryption_type,
  } = editData || {};

  return (
    <div className="mx-auto flex w-[750px] px-4 sm:px-6 md:px-10 flex-col gap-6 py-5 mb-10">
      <div className="flex w-full flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold sm:text-xl">SMTP Details</h3>
          <p className="text-sm text-gray-500">
            Set up your SMTP settings for emails.
          </p>
        </div>

        {edit !== "smtp" && (
          <div className="flex gap-4">
            <Button
              variant="secondary"
              className="flex gap-2"
              onClick={handleEditClick}
            >
              <MdEdit /> Edit
            </Button>
          </div>
        )}
      </div>

      <div className="flex max-w-2xl flex-col gap-6">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            {edit === "smtp" ? (
              <InputField
                label="SMTP Provider"
                placeholder="Enter SMTP provider"
                value={provider || ""}
                onChange={(e) =>
                  handleInputChange("provider", e?.target?.value)
                }
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">SMTP Provider</h2>
                <p className="text-sm">{provider || "----"}</p>
              </>
            )}
          </div>

          <div>
            {edit === "smtp" ? (
              <CreatableInputs
                name="SMTP Port"
                label="SMTP Port"
                placeholder="Select or enter port"
                options={[
                  { value: "465", label: "465" },
                  { value: "587", label: "587" },
                  { value: "25", label: "25" },
                  { value: "2525", label: "2525" },
                ]}
                value={port ? { value: port, label: port } : null}
                onChange={(selected) =>
                  handleInputChange("port", selected?.value || "")
                }
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">SMTP Port</h2>
                <p className="text-sm">{port || "----"}</p>
              </>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            {edit === "smtp" ? (
              <InputField
                label="Host"
                placeholder="Enter host"
                value={host || ""}
                onChange={(e) => handleInputChange("host", e?.target?.value)}
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">Host</h2>
                <p className="text-sm">{host || "----"}</p>
              </>
            )}
          </div>

          <div>
            {edit === "smtp" ? (
              <InputField
                label="From Email"
                placeholder="Enter from email"
                value={from_email || ""}
                onChange={(e) =>
                  handleInputChange("from_email", e?.target?.value)
                }
                wrongFields={wrongFields}
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">From Email</h2>
                <p className="text-sm">{from_email || "----"}</p>
              </>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            {edit === "smtp" ? (
              <InputField
                label="Username"
                placeholder="Enter username"
                value={username || ""}
                onChange={(e) =>
                  handleInputChange("username", e?.target?.value)
                }
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">Username</h2>
                <p className="text-sm">{username || "----"}</p>
              </>
            )}
          </div>

          <div>
            {edit === "smtp" ? (
              <InputField
                label="From Name"
                placeholder="Enter from name"
                value={from_name || ""}
                onChange={(e) =>
                  handleInputChange("from_name", e?.target?.value)
                }
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">From Name</h2>
                <p className="text-sm">{from_name || "----"}</p>
              </>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          {edit === "smtp" ? (
            <div>
              <label htmlFor="password">Password</label>
              <div className="relative flex items-center border border-[#d4d1d1] bg-[#fdfdfd] placeholder:text-[#8a8a8a] placeholder:text-xs hover:border-primary focus:border-primary focus-within:border-primary">
                <input
                  className="h-9 w-full bg-[#FDFDFD] pl-2 pr-8 text-sm outline-none placeholder:text-xs"
                  value={password || ""}
                  type={eye ? "password" : "text"}
                  id="password"
                  placeholder="••••••••"
                  onChange={(e) =>
                    handleInputChange("password", e?.target?.value)
                  }
                  required
                />
                <span
                  onClick={toggleEye}
                  className="absolute right-2 text-[#c8c8c8]"
                >
                  {eye ? (
                    <RxLockClosed
                      size={18}
                      className="cursor-pointer hover:text-primary"
                    />
                  ) : (
                    <RxLockOpen1
                      size={18}
                      className="cursor-pointer text-primary"
                    />
                  )}
                </span>
              </div>
            </div>
          ) : (
            <div>
              <h2 className="text-sm text-gray-500">Password</h2>
              {password ? (
                <p
                  className="text-sm cursor-pointer"
                  onMouseEnter={() => setHovered(true)}
                  onMouseLeave={() => setHovered(false)}
                >
                  {hovered ? password : "••••••••"}
                </p>
              ) : (
                <p className="text-sm text-gray-400">----</p>
              )}
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            {edit === "smtp" ? (
              <YesNoToggle
                name="tls"
                label="TLS"
                value={tls ?? false}
                onChange={(field, value) => handleInputChange("tls", value)}
                tooltipText="Enable or disable TLS encryption for secure email communication."
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">TLS</h2>
                <p className="text-sm">
                  {tls === undefined ? "----" : tls ? "Enabled" : "Disabled"}
                </p>
              </>
            )}
          </div>

          <div>
            {edit === "smtp" ? (
              <SelectInput
                label="Encryption Type"
                placeholder="Select encryption type"
                options={[
                  { value: "TLS", label: "TLS" },
                  { value: "SSL", label: "SSL" },
                  { value: "None", label: "None" },
                ]}
                value={
                  encryption_type
                    ? { value: encryption_type, label: encryption_type }
                    : null
                }
                onChange={(selected) =>
                  handleInputChange("encryption_type", selected?.value || "TLS")
                }
                isClearable={false}
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">Encryption Type</h2>
                <p className="text-sm">{encryption_type || "----"}</p>
              </>
            )}
          </div>
        </div>

        {edit == "smtp" && (
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

export default SmtpForm;
