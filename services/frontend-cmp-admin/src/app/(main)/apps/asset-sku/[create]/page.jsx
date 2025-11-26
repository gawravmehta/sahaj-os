"use client";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import { InputField, SelectInput, TextareaField } from "@/components/ui/Inputs";
import { techOptions } from "@/constants/assets";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { getUpdatedFields } from "@/utils/getUpdatedFields";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";
import toast from "react-hot-toast";

const Page = ({ params }) => {
  const { create: id } = use(params);
  const router = useRouter();

  const [formData, setFormData] = useState({
    assetName: "",
    category: "",
    description: "",
    image: "",
    usageUrl: "",
  });

  const [originalData, setOriginalData] = useState(null);
  const [btnLoading, setBtnLoading] = useState(false);
  const [btnLoading2, setBtnLoading2] = useState(false);
  const [missingFields, setMissingFields] = useState([]);
  const [wrangField, setWrangField] = useState([]);

  useEffect(() => {
    if (id !== "create") {
      handleOneAsset();
    }
  }, []);

  const handleOneAsset = async () => {
    try {
      const assetResponse = await apiCall(`/assets/get-asset/${id}`);
      setFormData({
        assetName: assetResponse.asset_name || "",
        category: assetResponse.category || "",
        description: assetResponse.description || "",
        image: assetResponse.image || "",
        usageUrl: assetResponse.usage_url || "",
      });
      setOriginalData(assetResponse);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handlePublishAsset = async (id) => {
    try {
      await apiCall(`/assets/publish-asset/${id}`, { method: "PATCH" });
      router.push("/apps/asset-sku");
      toast.success("Assets Published Successfully");
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setBtnLoading(false);
      setBtnLoading2(false);
    }
  };

  const handleCreateOrUpdateAsset = async (published) => {
    const missing = [];
    if (!formData.assetName?.trim()) missing.push("Name");
    if (!formData.category?.trim()) missing.push("Category");
    setMissingFields(missing);

    if (missing.length > 0) {
      toast.error("Please fill in all required fields.");
      return;
    }

    const wrangField = [];
    if (formData.usageUrl && !/^https?:\/\//i.test(formData.usageUrl)) {
      wrangField.push({
        value: "Asset URL",
        message: "Please enter a valid URL starting with http:// or https://",
      });
    }
    setWrangField(wrangField);
    if (wrangField.length > 0) {
      toast.error("Please correct the highlighted fields.");
      return;
    }

    const payload = {
      asset_name: formData.assetName,
      category: formData.category,
      description: formData.description,
      image: formData.image,
      usage_url: formData.usageUrl,
    };

    try {
      published ? setBtnLoading2(true) : setBtnLoading(true);

      let response;

      if (id === "create") {
        response = await apiCall("/assets/create-asset", {
          method: "POST",
          data: payload,
        });

        if (published) {
          await handlePublishAsset(response.asset_id);
        } else {
          toast.success("Assets Drafted Successfully");
          router.push("/apps/asset-sku");
        }
      } else {
        const updatedFields = getUpdatedFields(originalData, payload, {
          asset_name: "assetName",
          category: "category",
          description: "description",
          image: "image",
          usage_url: "usageUrl",
        });

        if (Object.keys(updatedFields).length === 0) {
          if (published) {
            await handlePublishAsset(id);
          } else {
            toast("No changes detected");
            router.push("/apps/asset-sku");
          }
          return;
        }

        response = await apiCall(`/assets/update-asset/${id}`, {
          method: "PATCH",
          data: updatedFields,
        });

        if (published) {
          await handlePublishAsset(id);
        } else {
          toast.success("Assets Updated Successfully");
          router.push("/apps/asset-sku");
        }
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error(error);
    } finally {
      setBtnLoading(false);
      setBtnLoading2(false);
    }
  };

  const breadcrumbsProps = {
    path: `/apps/asset-sku/${id === "create" ? " create" : "Update "}`,
    skip: "/apps/",
  };

  return (
    <>
      <div className="flex flex-col justify-between gap-4 border-b border-borderheader pr-6 sm:flex-row">
        <Header
          title={`${id === "create" ? "  Create Assets" : "Update Assets"}`}
          breadcrumbsProps={breadcrumbsProps}
        />
      </div>

      <div className="custom-scrollbar flex h-[calc(100vh-195px)] w-full justify-center overflow-auto">
        <div className="flex w-full max-w-lg pt-4 flex-col space-y-4">
          <div>
            <h1 className="text-[28px] ">General Information</h1>
            <p className="text-xs text-subHeading">
              Provide detailed information about each asset to ensure accurate
              categorization and proper usage.
            </p>
          </div>

          <InputField
            name="Name"
            label="Name"
            placeholder="Enter asset name"
            value={formData.assetName}
            onChange={(e) =>
              setFormData({ ...formData, assetName: e.target.value })
            }
            required={true}
            missingFields={missingFields}
            tooltipText="Asset name should be unique and descriptive."
          />

          <SelectInput
            name="Category"
            label="Category"
            placeholder="Enter category"
            options={techOptions}
            value={techOptions.find((opt) => opt.value === formData.category)}
            onChange={(selected) => {
              if (selected) {
                setFormData({
                  ...formData,
                  category: selected.value,
                  image: selected.image,
                  description: selected.description,
                });
              } else {
                setFormData({
                  ...formData,
                  category: "",
                  image: "",
                  description: "",
                });
              }
            }}
            required={true}
            missingFields={missingFields}
            tooltipText="Select a category that best fits the asset."
            createOption={true}
          />

          <TextareaField
            label="Description"
            placeholder="Write description"
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            tooltipText="Provide a detailed description of the asset."
          />

          <InputField
            name="Asset URL"
            label="Asset URL"
            placeholder="Paste asset URL"
            value={formData.usageUrl}
            wrongFields={wrangField}
            onChange={(e) =>
              setFormData({ ...formData, usageUrl: e.target.value })
            }
            tooltipText="Provide a URL for the asset usage details."
          />
        </div>
      </div>

      <div className="fixed bottom-0 right-0 z-0 mt-10 flex h-12 w-full items-center justify-end gap-3 border-t bg-[#fafafa] px-5 py-4 shadow-xl">
        <div className="flex gap-3">
          <Link href="/apps/asset-sku">
            <Button variant="cancel" className="py-1.5">
              Cancel
            </Button>
          </Link>

          <Button
            variant="secondary"
            disabled={btnLoading}
            btnLoading={btnLoading}
            onClick={() => handleCreateOrUpdateAsset()}
            className="w-24 py-1.5"
          >
            Save Draft
          </Button>
          <Button
            variant="primary"
            disabled={btnLoading2}
            btnLoading={btnLoading2}
            onClick={() => handleCreateOrUpdateAsset("published")}
            className="w-24 py-1.5"
          >
            Publish
          </Button>
        </div>
      </div>
    </>
  );
};

export default Page;
