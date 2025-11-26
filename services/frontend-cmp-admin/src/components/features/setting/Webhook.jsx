"use client";
import Button from "@/components/ui/Button";
import { InputField } from "@/components/ui/Inputs";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { AiOutlinePlus } from "react-icons/ai";
import { MdEdit } from "react-icons/md";

const Webhook = ({
  formData,
  setFormData,
  edit,
  setEdit,
  handleSave,
  saving,
}) => {
  if (!formData?.communication?.webhooks) return null;

  const handleEdit = () => setEdit("webhook");

  const handleWebhookChange = (key, value) => {
    setFormData((prev) => ({
      ...prev,
      communication: {
        ...prev.communication,
        webhooks: { ...prev.communication.webhooks, [key]: value },
      },
    }));
  };

  const addWebhook = () => {
    const newKey = `webhook_${
      Object.keys(formData.communication.webhooks).length + 1
    }`;
    setFormData((prev) => ({
      ...prev,
      communication: {
        ...prev.communication,
        webhooks: { ...prev.communication.webhooks, [newKey]: "" },
      },
    }));
  };

  const removeWebhook = (key) => {
    const { [key]: _, ...rest } = formData.communication.webhooks;
    setFormData((prev) => ({
      ...prev,
      communication: { ...prev.communication, webhooks: rest },
    }));
  };

  return (
    <div className="mx-auto flex w-[750px]  px-4 sm:px-6 md:px-10 py-5 flex-col gap-6">
      <div className="flex w-full flex-wrap items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold sm:text-xl">
            Webhook Configuration
          </h3>
          <p className="text-sm text-gray-500">
            Manage external webhook endpoints.
          </p>
        </div>

        {edit != "webhook" && (
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

      <div className="flex max-w-2xl flex-col gap-6">
        <div>
          <h2 className="text-sm text-gray-500">Webhook URLs</h2>
          <div className="flex flex-col gap-4">
            {Object.entries(formData.communication.webhooks || {}).map(
              ([key, value]) => (
                <div key={key} className="flex items-center gap-2 relative">
                  {edit == "webhook" ? (
                    <>
                      <InputField
                        layoutClass="w-full mr-32"
                        label={key}
                        placeholder="https://example.com/"
                        value={value}
                        onChange={(e) =>
                          handleWebhookChange(key, e.target.value)
                        }
                      />
                      <Button
                        variant="secondary"
                        type="button"
                        className="border border-red-500 text-red-500 absolute bottom-0 right-0"
                        onClick={() => removeWebhook(key)}
                      >
                        Remove
                      </Button>
                    </>
                  ) : (
                    <p className="text-sm">
                      <span className="font-medium">{key}:</span> {value}
                    </p>
                  )}
                </div>
              )
            )}

            {edit && (
              <Button
                variant="secondary"
                type="button"
                className="flex items-center gap-2"
                onClick={addWebhook}
              >
                <AiOutlinePlus /> Add Webhook
              </Button>
            )}
          </div>
        </div>

        {edit && (
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

export default Webhook;
