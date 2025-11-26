"use client";

import { useState } from "react";
import Button from "@/components/ui/Button";
import { InputField, TextareaField } from "@/components/ui/Inputs";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { AiOutlineDelete } from "react-icons/ai";
import { MdEdit } from "react-icons/md";

const InApp = ({
  formData,
  setFormData,
  edit,
  setEdit,
  handleSave,
  saving,
}) => {
  const templates = formData?.communication?.in_app || [];
  const [newTemplate, setNewTemplate] = useState({ name: "", content: "" });

  const handleEditClick = () => setEdit("in_app");
  const handleCancel = () => setEdit("");

  const handleAddTemplate = () => {
    const updated = [...templates, newTemplate];
    setFormData((prev) => ({
      ...prev,
      communication: {
        ...prev.communication,
        in_app: updated,
      },
    }));
    setNewTemplate({ name: "", content: "" });
  };

  const handleDeleteTemplate = (index) => {
    const updated = templates.filter((_, i) => i !== index);
    setFormData((prev) => ({
      ...prev,
      communication: {
        ...prev.communication,
        in_app: updated,
      },
    }));
  };

  return (
    <div className="mx-auto flex w-[750px] px-4 sm:px-6 md:px-10 py-5 mb-10 flex-col gap-6">
      <div className="flex w-full justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold sm:text-xl">In-App Templates</h3>
          <p className="text-sm text-gray-500">
            Manage in-app notification templates.
          </p>
        </div>
        {edit !== "in_app" && (
          <Button
            variant="secondary"
            className="flex gap-2"
            onClick={handleEditClick}
          >
            <MdEdit /> Edit
          </Button>
        )}
      </div>

      <div className="flex flex-col gap-4">
        {templates.length > 0 &&
          templates.map((tpl, index) => (
            <div
              key={index}
              className="flex justify-between items-start border p-3"
            >
              <div>
                <h4 className="font-medium">{tpl.name}</h4>
                <p className="text-sm text-gray-600">{tpl.content}</p>
              </div>
              {edit === "in_app" && (
                <AiOutlineDelete
                  className="cursor-pointer text-red-500 mt-1"
                  onClick={() => handleDeleteTemplate(index)}
                />
              )}
            </div>
          ))}
        {templates.length === 0 && (
          <p className="text-sm text-gray-500">No templates available.</p>
        )}
      </div>

      {edit === "in_app" && (
        <div className="border p-4 flex flex-col gap-3">
          <InputField
            label="Template Name"
            placeholder="Template Name"
            value={newTemplate.name}
            onChange={(e) =>
              setNewTemplate({ ...newTemplate, name: e.target.value })
            }
          />
          <TextareaField
            label="Template Content"
            placeholder="Template Content"
            value={newTemplate.content}
            onChange={(e) =>
              setNewTemplate({ ...newTemplate, content: e.target.value })
            }
          />
          <Button
            variant="primary"
            onClick={handleAddTemplate}
            disabled={!newTemplate.name || !newTemplate.content}
          >
            Add Template
          </Button>
        </div>
      )}

      {edit === "in_app" && (
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

export default InApp;
