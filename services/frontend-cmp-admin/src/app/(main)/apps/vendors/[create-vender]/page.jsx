"use client";

import CreateStep1 from "@/components/features/vendor/CreateStep1";
import CreateStep2 from "@/components/features/vendor/CreateStep2";
import CreateStep3 from "@/components/features/vendor/CreateStep3";
import Header from "@/components/ui/Header";
import Stepper from "@/components/ui/Stepper";
import StickyFooterActions from "@/components/ui/StickyFooterActions";

import { getErrorMessage } from "@/utils/errorHandler";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { FaArrowRight } from "react-icons/fa";
import { use } from "react";
import { apiCall } from "@/hooks/apiCall";

const Page = ({ params }) => {
  const VendorsId = use(params)["create-vender"];

  const [dpr_name, setDpr_name] = useState("");
  const [dpr_legal_name, setDpr_legal_name] = useState("");
  const [dpr_logo_url, setDpr_logo_url] = useState("");
  const [description, setDescription] = useState("");
  const [dpr_address, setDpr_address] = useState("");
  const [dpr_country, setDpr_country] = useState("");
  const [dpr_country_risk, setDpr_country_risk] = useState("");
  const [dpr_privacy_policy, setDpr_privacy_policy] = useState("");
  const [dpr_data_policy, setDpr_data_policy] = useState("");
  const [dpr_security_policy, setDpr_security_policy] = useState("");
  const [industry, setIndustry] = useState("");
  const [data_retention_policy, setData_retention_policy] = useState("");
  const [legal_basis_of_processing, setLegal_basis_of_processing] =
    useState("");

  const [cross_border, setCross_border] = useState(false);
  const [sub_processor, setSub_processor] = useState(false);

  const [processing_category, setProcessing_category] = useState([]);
  const [data_categories, setData_categories] = useState([]);
  const [data_location, setData_location] = useState([]);

  const [data_processing_activity, setData_processing_activity] = useState([]);

  const [sub_processors, setSub_processors] = useState([]);

  const [security_measures, setSecurity_measures] = useState({
    compliance_reference: "",
    description: "",
    measure_name: "",
  });

  const [contract_documents, setContract_documents] = useState([]);

  const [dpdpa_compliance_status, setDpdpa_compliance_status] = useState({
    signed_dpa: false,
    transfer_outside_india: false,
    cross_border_mechanism: "",
    breach_notification_time: "",
  });

  const [audit_status, setAudit_status] = useState({
    last_audit_date: "",
    next_audit_due: "",
    audit_result: "",
  });

  const [contact_person, setContact_person] = useState({
    name: "",
    designation: "",
    email: "",
    phone: "",
  });

  const [missingFields, setMissingFields] = useState([]);
  const [wrongFields, setWrongFields] = useState([]);

  const searchParams = useSearchParams();
  const [activeStep, setActiveStep] = useState(
    parseInt(searchParams.get("activeTab")) || 1
  );
  const router = useRouter();

  const [loading, setLoading] = useState(false);

  const handlePrevStep = () => {
    if (activeStep > 1) {
      handleTabChange(activeStep - 1);
    }
  };

  const handleTabChange = (tabId) => {
    setActiveStep(tabId);
    const params = new URLSearchParams(searchParams.toString());
    params.set("activeTab", tabId);
    router.push(`?${params.toString()}`, undefined, { shallow: true });
  };

  const breadcrumbsProps = {
    path: "/apps/vendors/create-vender",
    skip: "/apps/",
  };

  useEffect(() => {
    if (VendorsId !== "create-vender") {
      fetchData();
    }
  }, []);

  const fetchData = async () => {
    try {
      const response = await apiCall(
        `/vendor/get-one-vendor?vendor_id=${VendorsId}`
      );

      if (response) {
        setAudit_status(response?.audit_status);
        setContact_person(response?.contact_person);
        setContract_documents(response?.contract_documents);
        setData_categories(response?.data_categories);
        setData_location(response?.data_location);
        setData_processing_activity(response?.data_processing_activity || []);
        setData_retention_policy(response?.data_retention_policy);
        setDescription(response?.description);
        setDpdpa_compliance_status(response?.dpdpa_compliance_status);
        setDpr_address(response?.dpr_address);
        setDpr_country(response?.dpr_country);
        setDpr_country_risk(response?.dpr_country_risk);
        setDpr_data_policy(response?.dpr_data_policy);
        setDpr_legal_name(response?.dpr_legal_name);
        setDpr_logo_url(response?.dpr_logo_url);
        setDpr_name(response?.dpr_name);
        setDpr_privacy_policy(response?.dpr_privacy_policy);
        setDpr_security_policy(response?.dpr_security_policy);
        setIndustry(response?.industry);
        setLegal_basis_of_processing(response?.legal_basis_of_processing);
        setProcessing_category(response?.processing_category || []);
        setSecurity_measures(response?.security_measures[0] || []);
        setSub_processor(response?.sub_processor);
        setSub_processors(response?.sub_processors || []);
      }
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
      console.error("Error fetching data:", error);
    }
  };

  const validateMissingFields = () => {
    const missing = [];

    if (!dpr_name || !dpr_name.trim()) {
      missing.push("dpr_name");
    }

    return missing;
  };

  const handleSubmit = async (status, clickStatus = false) => {
    try {
      setLoading(true);

      if (!clickStatus) {
        const missing = validateMissingFields();
        if (missing.length > 0) {
          toast.error(
            `Please fill all the required fields. ${missing.join(", ")}`
          );
          setMissingFields(missing);
          setLoading(false);
          return;
        }
      }

      const data = {
        dpr_name,
        dpr_legal_name,
        dpr_logo_url,
        description,
        dpr_address,
        dpr_country,
        dpr_country_risk,
        dpr_privacy_policy,
        dpr_data_policy,
        dpr_security_policy,
        industry,
        processing_category,
        data_categories,
        data_processing_activity,
        data_retention_policy,
        data_location,
        cross_border,
        sub_processor,
        sub_processors,
        legal_basis_of_processing,
        dpdpa_compliance_status,
        security_measures: [security_measures],
        audit_status,
        contact_person,
        contract_documents,
      };

      const endpoint =
        VendorsId === "create-vender"
          ? "/vendor/create-or-update-vendor"
          : `/vendor/create-or-update-vendor?vendor_id=${VendorsId}`;

      if (!dpr_name || !dpr_name.trim()) {
        toast.error("DPR Name is required");
        setMissingFields(["dpr_name"]);
        setLoading(false);
        return;
      }

      const response = await apiCall(endpoint, {
        method: "POST",
        data: data,
      });

      if (clickStatus === true) {
        toast.success("Saved as Draft successfully");
        router.push(`/apps/vendors`);
        return;
      }

      if (activeStep < 3) {
        handleTabChange(activeStep + 1);

        if (VendorsId === "create-vender" && response?.vendor_id) {
          router.push(
            `/apps/vendors/${response.vendor_id}?activeTab=${activeStep + 1}`
          );
        }
      } else if (activeStep === 3) {
        if (status === "publish") {
          await handlePublish(response?.vendor_id);
        } else {
          router.push(`/apps/vendors`);
        }
      }
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async (venderId) => {
    try {
      const response = await apiCall(`/vendor/make-it-publish/${venderId}`, {
        method: "POST",
      });
      if (response) {
        toast.success(response.message || "Vendor Published Successfully");
        router.push(`/apps/vendors`);
      }
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  return (
    <div className="relative flex h-full flex-col justify-between">
      <div className="w-full">
        <Header title="Create Vendor" breadcrumbsProps={breadcrumbsProps} />
      </div>

      <Stepper
        steps={["Step 1", "Step 2", "Step 3"]}
        activeStep={activeStep}
        onStepClick={setActiveStep}
      />
      <div
        className={`custom-scrollbar flex h-[calc(100vh-210px)] w-full justify-center overflow-auto`}
      >
        <div className="flex h-auto w-full justify-center">
          {activeStep == 1 && (
            <CreateStep1
              dpr_name={dpr_name}
              setDpr_name={setDpr_name}
              dpr_legal_name={dpr_legal_name}
              setDpr_legal_name={setDpr_legal_name}
              dpr_logo_url={dpr_logo_url}
              setDpr_logo_url={setDpr_logo_url}
              description={description}
              setDescription={setDescription}
              dpr_address={dpr_address}
              setDpr_address={setDpr_address}
              dpr_country={dpr_country}
              setDpr_country={setDpr_country}
              dpr_country_risk={dpr_country_risk}
              setDpr_country_risk={setDpr_country_risk}
              industry={industry}
              setIndustry={setIndustry}
              dpr_privacy_policy={dpr_privacy_policy}
              setDpr_privacy_policy={setDpr_privacy_policy}
              dpr_data_policy={dpr_data_policy}
              setDpr_data_policy={setDpr_data_policy}
              dpr_security_policy={dpr_security_policy}
              setDpr_security_policy={setDpr_security_policy}
              missingFields={missingFields}
              wrongFields={wrongFields}
            />
          )}
          {activeStep == 2 && (
            <CreateStep2
              processing_category={processing_category}
              setProcessing_category={setProcessing_category}
              data_categories={data_categories}
              setData_categories={setData_categories}
              data_location={data_location}
              setData_location={setData_location}
              data_processing_activity={data_processing_activity}
              setData_processing_activity={setData_processing_activity}
              sub_processors={sub_processors}
              setSub_processors={setSub_processors}
              sub_processor={sub_processor}
              setSub_processor={setSub_processor}
              legal_basis_of_processing={legal_basis_of_processing}
              setLegal_basis_of_processing={setLegal_basis_of_processing}
              dpdpa_compliance_status={dpdpa_compliance_status}
              setDpdpa_compliance_status={setDpdpa_compliance_status}
              data_retention_policy={data_retention_policy}
              setData_retention_policy={setData_retention_policy}
              cross_border={cross_border}
              setCross_border={setCross_border}
              missingFields={missingFields}
              wrongFields={wrongFields}
            />
          )}
          {activeStep == 3 && (
            <CreateStep3
              security_measures={security_measures}
              setSecurity_measures={setSecurity_measures}
              audit_status={audit_status}
              setAudit_status={setAudit_status}
              contact_person={contact_person}
              setContact_person={setContact_person}
              contract_documents={contract_documents}
              setContract_documents={setContract_documents}
              missingFields={missingFields}
              wrongFields={wrongFields}
            />
          )}
        </div>

        <StickyFooterActions
          showCancel={activeStep === 1}
          onCancelHref="/apps/vendors"
          showBack={activeStep > 1}
          onBack={handlePrevStep}
          showPublish={true}
          onPublish={() =>
            handleSubmit(activeStep === 3 ? "publish" : "draft", false)
          }
          onSaveAsDraft={() => {
            handleSubmit("draft", true);
          }}
          showSaveAsDraft={true}
          publishLabel={
            activeStep !== 3 ? (
              <>
                Next <FaArrowRight />
              </>
            ) : (
              "Publish"
            )
          }
          className="mt-10 py-4 shadow-xl"
        >
          {activeStep !== 4 && <FaArrowRight className="text-[12px]" />}
        </StickyFooterActions>
      </div>
    </div>
  );
};

export default Page;
