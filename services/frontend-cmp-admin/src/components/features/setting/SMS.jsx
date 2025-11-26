"use client";

import Button from "@/components/ui/Button";
import { InputField, SelectInput, TextareaField } from "@/components/ui/Inputs";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { countryOptions } from "@/constants/countryOptions";
import { AiOutlineDelete } from "react-icons/ai";
import { MdEdit } from "react-icons/md";
import { useState } from "react";
import YesNoToggle from "@/components/ui/YesNoToggle";
import { RxLockClosed, RxLockOpen1 } from "react-icons/rx";

const SMS = ({ formData, setFormData, edit, setEdit, handleSave, saving }) => {
  const credentials = formData?.communication?.sms?.credentials || {};
  const templates = formData?.communication?.sms?.templates || [];
  const [hovered, setHovered] = useState(false);
  const [newTemplate, setNewTemplate] = useState({ name: "", content: "" });
  const [eye, setEye] = useState(true);

  const toggleEye = () => setEye((prev) => !prev);

  const handleEditClick = () => setEdit("sms");
  const handleCancel = () => setEdit("");

  const handleInputChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      communication: {
        ...prev?.communication,
        sms: {
          ...prev?.communication?.sms,
          credentials: {
            ...prev?.communication?.sms?.credentials,
            [field]: value,
          },
        },
      },
    }));
  };

  const handleAddTemplate = () => {
    if (!newTemplate?.name || !newTemplate?.content) return;
    setFormData((prev) => ({
      ...prev,
      communication: {
        ...prev?.communication,
        sms: {
          ...prev?.communication.sms,
          templates: [
            ...(prev?.communication?.sms?.templates || []),
            newTemplate,
          ],
        },
      },
    }));
    setNewTemplate({ name: "", content: "" });
  };

  const handleDeleteTemplate = (index) => {
    setFormData((prev) => {
      const updated = [...(prev?.communication?.sms?.templates || [])];
      updated?.splice(index, 1);
      return {
        ...prev,
        communication: {
          ...prev?.communication,
          sms: {
            ...prev?.communication?.sms,
            templates: updated,
          },
        },
      };
    });
  };

  return (
    <div className="mx-auto flex w-[750px] px-4 sm:px-6 md:px-10 mb-10 py-5 flex-col gap-6">
      <div className="flex w-full flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold sm:text-xl">SMS Details</h3>
          <p className="text-sm text-gray-500">
            Configure SMS provider and credentials.
          </p>
        </div>

        {edit !== "sms" && (
          <Button
            variant="secondary"
            className="flex gap-2"
            onClick={handleEditClick}
          >
            <MdEdit /> Edit
          </Button>
        )}
      </div>

      <div className="flex max-w-2xl flex-col gap-6">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            {edit === "sms" ? (
              <InputField
                label="Provider"
                placeholder="Enter provider"
                value={credentials?.provider || ""}
                onChange={(e) => handleInputChange("provider", e.target.value)}
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">Provider</h2>
                <p className="text-sm">{credentials?.provider}</p>
              </>
            )}
          </div>

          <div>
            {edit === "sms" ? (
              <InputField
                label="API Key"
                placeholder="Enter API key"
                value={credentials?.api_key || ""}
                onChange={(e) => handleInputChange("api_key", e.target.value)}
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">API Key</h2>
                <p className="text-sm">••••••••</p>
              </>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            {edit === "sms" ? (
              <InputField
                label="Username"
                placeholder="Enter username"
                value={credentials?.username || ""}
                onChange={(e) => handleInputChange("username", e.target.value)}
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">Username</h2>
                <p className="text-sm">{credentials?.username}</p>
              </>
            )}
          </div>

          <div>
            {edit === "sms" ? (
              <div>
                <label
                  htmlFor="password"
                  className="text-sm font-medium text-gray-700"
                >
                  Password
                </label>
                <div className="relative flex items-center border border-[#d4d1d1] bg-[#fdfdfd] placeholder:text-[#8a8a8a] placeholder:text-xs hover:border-primary focus-within:border-primary  mt-1">
                  <input
                    className="h-9 w-full bg-[#FDFDFD] pl-2 pr-8 text-sm outline-none placeholder:text-xs rounded-md"
                    type={eye ? "password" : "text"}
                    id="password"
                    placeholder="••••••••"
                    value={credentials?.password || ""}
                    onChange={(e) =>
                      handleInputChange("password", e.target.value)
                    }
                    required
                  />
                  <span
                    onClick={toggleEye}
                    className="absolute right-2 text-[#c8c8c8] cursor-pointer"
                  >
                    {eye ? (
                      <RxLockClosed size={18} className="hover:text-primary" />
                    ) : (
                      <RxLockOpen1 size={18} className="text-primary" />
                    )}
                  </span>
                </div>
              </div>
            ) : (
              <div>
                <h2 className="text-sm text-gray-500">Password</h2>
                <p
                  className="text-sm cursor-pointer"
                  onMouseEnter={() => setHovered(true)}
                  onMouseLeave={() => setHovered(false)}
                >
                  {hovered ? credentials?.password || "" : "••••••••"}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            {edit === "sms" ? (
              <InputField
                label="Sender ID"
                placeholder="Enter sender ID"
                value={credentials?.sender_id || ""}
                onChange={(e) => handleInputChange("sender_id", e.target.value)}
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">Sender ID</h2>
                <p className="text-sm">{credentials?.sender_id}</p>
              </>
            )}
          </div>

          <div>
            {edit === "sms" ? (
              <InputField
                label="Base URL"
                placeholder="Enter base URL"
                value={credentials?.base_url || ""}
                onChange={(e) => handleInputChange("base_url", e.target.value)}
              />
            ) : (
              <>
                <h2 className="text-sm text-gray-500">Base URL</h2>
                <p className="text-sm">{credentials?.base_url}</p>
              </>
            )}
          </div>
        </div>

        <div>
          {edit === "sms" ? (
            <SelectInput
              label="Region"
              placeholder="Select region"
              options={countryOptions}
              value={countryOptions?.find(
                (lang) => lang?.value === credentials?.region
              )}
              onChange={(selected) =>
                handleInputChange("region", selected?.value || "IN")
              }
            />
          ) : (
            <>
              <h2 className="text-sm text-gray-500">Region</h2>
              <p className="text-sm">{credentials?.region}</p>
            </>
          )}
        </div>

        <div>
          {edit === "sms" ? (
            <YesNoToggle
              name="unicode"
              label="Unicode"
              value={credentials?.unicode ?? false}
              onChange={(field, value) => handleInputChange("unicode", value)}
              tooltipText="Enable Unicode support for multi-language SMS content."
            />
          ) : (
            <>
              <h2 className="text-sm text-gray-500">Unicode</h2>
              <p className="text-sm">
                {credentials?.unicode ? "Enabled" : "Disabled"}
              </p>
            </>
          )}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold sm:text-xl">Templates</h3>
        <p className="text-sm text-gray-500">Manage SMS templates</p>
      </div>

      <div className="flex flex-col gap-4">
        {templates?.length > 0 &&
          templates?.map((tpl, index) => (
            <div
              key={index}
              className="flex justify-between items-start border p-3"
            >
              <div>
                <h4 className="font-medium">{tpl?.name}</h4>
                <p className="text-sm text-gray-600">{tpl?.content}</p>
              </div>
              {edit === "sms" && (
                <AiOutlineDelete
                  className="cursor-pointer text-red-500 mt-1"
                  onClick={() => handleDeleteTemplate(index)}
                />
              )}
            </div>
          ))}
      </div>

      {edit === "sms" && (
        <div className="border p-4 flex flex-col gap-3">
          <InputField
            label="Template Name"
            placeholder="Template Name"
            value={newTemplate?.name}
            onChange={(e) =>
              setNewTemplate({ ...newTemplate, name: e.target.value })
            }
          />
          <TextareaField
            label="Template Content"
            placeholder="Template Content"
            value={newTemplate?.content}
            onChange={(e) =>
              setNewTemplate({ ...newTemplate, content: e.target.value })
            }
          />
          <Button
            variant="primary"
            onClick={handleAddTemplate}
            disabled={!newTemplate?.name || !newTemplate?.content}
          >
            Add Template
          </Button>
        </div>
      )}

      {edit === "sms" && (
        <StickyFooterActions
          showCancel
          cancelLabel="Cancel"
          onCancel={handleCancel}
          showSubmit
          onSubmit={handleSave}
          submitLabel={saving ? "Saving..." : "Save Changes"}
          submitDisabled={saving}
          className="mt-10 py-4 shadow-xl"
        />
      )}
    </div>
  );
};

export default SMS;
