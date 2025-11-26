"use client";
import Header from "@/components/ui/Header";
import StickyFooterActions from "@/components/ui/StickyFooterActions";
import { addNewTags, apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";
import toast from "react-hot-toast";
import CreateEditDp from "@/components/features/principalManagement/CreateEditDp";
import { getUpdatedFields } from "@/utils/getUpdatedFields";
import { isValidObjectId } from "@/utils/helperFunctions";

export default function Page({ params }) {
  const { dp_id } = use(params);
  const router = useRouter();
  const isEdit = isValidObjectId(dp_id);
  const [tagOptions, setTagOptions] = useState([]);
  const [missingFields, setMissingFields] = useState([]);
  const [wrongFields, setWrongFields] = useState([]);
  const [mobile, setMobile] = useState("");
  const [allEmails, setAllEmails] = useState([]);
  const [allMobile, setAllMobile] = useState([]);
  const [allDataElements, setAllDataElements] = useState([]);

  const [formData, setFormData] = useState({
    systemId: "",
    identifiers: [],
    email: [],
    mobile: [],
    dp_other_identifier: [],
    preferredLanguage: "",
    country: "",
    state: null,
    activeDevices: [],
    is_active: false,
    is_legacy: true,
    dp_tags: [],
  });
  const [oldData, setOldData] = useState();

  useEffect(() => {
    if (isEdit) {
      getOneDataPrincipal();
    }
  }, [isEdit]);

  const getOneDataPrincipal = async () => {
    try {
      const response = await apiCall(
        `/data-principal/view-data-principal/${dp_id}`
      );
      if (response) {
        setFormData((prev) => ({
          ...prev,
          preferredLanguage: response.dp_preferred_lang || "english",
          country: response.dp_country?.toLowerCase() || "india",
          state: response.dp_state?.toLowerCase() || null,
          persona: response.dp_persona || [],
          is_legacy: Boolean(response.is_legacy),
          is_active: Boolean(response.is_active),
          dp_tags: response.dp_tags || [],
          identifiers: response.dp_identifiers || [],
          email: response.dp_email?.[0] || "",
          mobile: response.dp_mobile?.[0] || "",
          dp_other_identifier: response.dp_other_identifier || [],
          systemId: response.dp_system_id || "",
        }));
      }

      setOldData({
        ...response,
        dp_email: [],
        dp_mobile: [],
      });
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const validateForm = () => {
    let missing = [];
    const checks = [
      { value: formData.systemId, label: "System ID" },
      { value: formData.identifiers, label: "identifiers" },
    ];
    if (formData.identifiers.includes("email")) {
      checks.push({ value: formData.email, label: "Email" });
    }
    if (formData.identifiers.includes("mobile")) {
      checks.push({ value: mobile, label: "Mobile" });
    }
    if (formData.identifiers.includes("mobile")) {
      checks.push({ value: mobile, label: "Mobile" });
    }

    checks.forEach(({ value, label }) => {
      const isEmpty =
        (typeof value === "string" && !value.trim()) ||
        (Array.isArray(value) && value.length === 0) ||
        value === 0 ||
        value === null ||
        value === undefined ||
        value === false;

      if (isEmpty) missing.push(label);
    });

    if (missing.length > 0) {
      setMissingFields(missing);
      toast.error(`Please fill required fields: ${missing.join(", ")}`);
      return false;
    }

    return true;
  };

  const handleSubmit = async () => {
    setMissingFields([]);
    setWrongFields([]);

    const isValid = validateForm();
    if (!isValid) return;

    if (isEdit) {
      await updateDataPrincipal();
    } else {
      await addDataPrincipal();
    }
  };

  const addDataPrincipal = async () => {
    const requestBody = [
      {
        dp_system_id: formData.systemId,
        dp_identifiers: formData.identifiers || [],
        ...(formData?.identifiers?.includes("email") && {
          dp_email: formData.email ? [formData.email] : [],
        }),
        ...(formData?.identifiers?.includes("mobile") && {
          dp_mobile: mobile ? [mobile] : [],
        }),
        dp_other_identifier: formData?.dp_other_identifier || [],
        dp_preferred_lang: formData.preferredLanguage,
        dp_country: formData.country,
        dp_state: formData.state,
        dp_active_devices: formData.activeDevices,
        dp_tags: formData.dp_tags || [],
        is_legacy: formData.is_legacy,
        is_active: formData.is_active,
        created_at_df: new Date().toISOString(),
        last_activity: new Date().toISOString(),
      },
    ];

    try {
      const response = await apiCall("/data-principal/add-data-principal", {
        method: "POST",
        data: requestBody,
      });
      toast.success(response.message || "Data Principal Added successfully");
      router.push("/apps/principal-management");
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const updateDataPrincipal = async () => {
    const data = {
      dp_identifiers: formData.identifiers || [],
      ...(formData?.identifiers?.includes("email") && {
        dp_email: [formData.email],
      }),
      ...(formData?.identifiers?.includes("mobile") && {
        dp_mobile: [formData.mobile],
      }),
      dp_other_identifier: formData?.dp_other_identifier || [],
      dp_preferred_lang: formData.preferredLanguage,
      dp_country: formData.country,
      dp_tags: formData.dp_tags || [],
      dp_state: formData.state,
      is_legacy: formData.is_legacy,
      is_active: formData.is_active,
    };

    if (!isValidObjectId(dp_id)) {
      toast.error("Internal Server Error: Invalid Data Principal ID");
      return;
    }

    try {
      let updatedData = getUpdatedFields(oldData, data);

      const updateResponse = await apiCall(
        `/data-principal/update-data-principal/${dp_id}`,
        {
          method: "PUT",
          data: updatedData,
        }
      );

      toast.success(
        updateResponse.message || "Data Principal Updated successfully"
      );
      router.push("/apps/principal-management");
    } catch (error) {
      toast.error(getErrorMessage(error));
      router.push("/apps/principal-management");
    }
  };
  return (
    <div className="flex">
      <div className="mb-4 w-full">
        <div className="border-b border-borderheader">
          <Header
            title={isEdit ? "Edit Data Principal" : "Add Data Principal"}
            breadcrumbsProps={{
              path: isEdit
                ? `/apps/principal-management/Edit Data Principal`
                : `/apps/principal-management/Add Data Principal`,
              skip: "/apps",
            }}
          />
        </div>
        <div className="custom-nav-scrollbar h-[calc(100vh-172px)] overflow-auto pb-8">
          <div className="mx-auto mt-6 w-[480px] rounded-lg">
            <h2 className="text-2xl font-semibold">General Information</h2>
            <p className="mb-6 text-sm text-gray-500">
              Please provide the necessary details to complete your profile
              setup
            </p>

            <CreateEditDp
              isEdit={isEdit}
              missingFields={missingFields}
              wrongFields={wrongFields}
              formData={formData}
              setFormData={setFormData}
              tagOptions={tagOptions}
              setTagOptions={setTagOptions}
              mobile={mobile}
              setMobile={setMobile}
              allEmails={allEmails}
              allMobile={allMobile}
              allDataElements={allDataElements}
              setAllDataElements={setAllDataElements}
            />
          </div>
        </div>

        <StickyFooterActions
          onCancelHref="/apps/principal-management"
          onSubmit={() => {
            setMissingFields([]);
            setWrongFields([]);
            handleSubmit();
          }}
          submitLabel={isEdit ? "Save Changes" : "Submit"}
        />
      </div>
    </div>
  );
}
