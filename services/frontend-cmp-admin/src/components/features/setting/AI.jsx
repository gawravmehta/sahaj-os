"use client";
import { InputField } from "@/components/ui/Inputs";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { AiOutlineDelete, AiOutlinePlus } from "react-icons/ai";
import { MdEdit } from "react-icons/md";
import Button from "@/components/ui/Button";

const AI = ({ formData, setFormData, edit, setEdit, handleSave, saving }) => {
  if (!formData?.ai) return null;

  const handleEdit = () => setEdit("ai");

  const handleCustomModelChange = (key, value) => {
    setFormData((prev) => ({
      ...prev,
      ai: {
        ...prev.ai,
        custom_models: { ...prev.ai.custom_models, [key]: value },
      },
    }));
  };

  const addCustomModel = () => {
    const newKey = `custom_${
      Object.keys(formData.ai.custom_models).length + 1
    }`;
    setFormData((prev) => ({
      ...prev,
      ai: {
        ...prev.ai,
        custom_models: { ...prev.ai.custom_models, [newKey]: "" },
      },
    }));
  };

  const removeCustomModel = (key) => {
    const { [key]: _, ...rest } = formData.ai.custom_models;
    setFormData((prev) => ({
      ...prev,
      ai: { ...prev.ai, custom_models: rest },
    }));
  };

  return (
    <div className="mx-auto flex w-[750px]  px-4 sm:px-6 md:px-10 py-5 flex-col gap-6 mb-10">
      <div className="flex w-full flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold sm:text-xl">AI Configuration</h3>
          <p className="text-sm text-gray-500">
            Manage API keys and custom AI models.
          </p>
        </div>

        {edit !== "ai" && (
          <Button
            variant="secondary"
            className="flex gap-2"
            onClick={handleEdit}
          >
            <MdEdit />
            Edit
          </Button>
        )}
      </div>

      <div className="flex  max-w-2xl flex-col gap-6">
        <div className="grid grid-cols-2 gap-5">
          {["openrouter_api_key"].map((field) => (
            <div key={field}>
              {edit == "ai" ? (
                <InputField
                  label={field.replace(/_/g, " ").toUpperCase()}
                  placeholder={`Enter ${field.replace(/_/g, " ")}`}
                  value={formData.ai[field] || ""}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      ai: { ...prev.ai, [field]: e.target.value },
                    }))
                  }
                />
              ) : (
                <>
                  <h2 className="text-sm text-gray-500">
                    {field.replace(/_/g, " ").toUpperCase()}
                  </h2>
                  <p className="text-sm">
                    {formData.ai[field] ? "••••••••" : "Not configured"}
                  </p>
                </>
              )}
            </div>
          ))}
        </div>

        

        {edit == "ai" && (
          <StickyFooterActions
            showCancel={true}
            cancelLabel="Cancel"
            onCancel={() => setEdit("")}
            showSubmit={true}
            onSubmit={handleSave}
            submitLabel={saving ? "Saving..." : "Save Changes"}
            submitDisabled={saving}
            className="mt-10 py-4 shadow-xl"
          />
        )}
      </div>
    </div>
  );
};

export default AI;
