"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import {
  CreatableInputs,
  InputField,
  SelectInput,
} from "@/components/ui/Inputs";
import { countryOptions } from "@/constants/countryOptions";
import Image from "next/image";
import Cookies from "js-cookie";
import { designationOptions } from "@/constants/org";

const Page = () => {
  const router = useRouter();

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    designation: "",
    contactNumber: "",
    orgName: "",
    orgWebsite: "",
    orgCountry: null,
  });

  const [loading, setLoading] = useState(false);

  const createOptions = (options) => {
    return options.map((option) => ({
      value: option,
      label: option.charAt(0).toUpperCase() + option.slice(1),
    }));
  };

  const formattedDesignationOptions = createOptions(designationOptions);

  const handleChange = (nameOrEvent, value) => {
    if (nameOrEvent?.target) {
      const { name, value } = nameOrEvent.target;
      setFormData((prev) => ({ ...prev, [name]: value }));
    } else {
      const name = nameOrEvent;
      setFormData((prev) => ({
        ...prev,
        [name]: value ? value.value || value : "",
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        user_basic_info: {
          first_name: formData.firstName,
          last_name: formData.lastName,
          phone: formData.contactNumber,
          designation: formData.designation,
        },
        org_info: {
          name: formData.orgName,
          website_url: formData.orgWebsite,
          country: formData.orgCountry?.label || "",
        },
      };

      await apiCall("/data-fiduciary/setup-data-fiduciary", {
        method: "POST",
        data: payload,
      });
      Cookies.remove("isNotOrgSetup");
      toast.success("Organization setup completed!");
      router.push("/apps");
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-[url('/assets/bg-images/Bg-48-percent-opacity.png')] bg-cover bg-center">
      <div className="flex w-full flex-col items-center justify-center sm:w-[500px]">
        <Image
          src="/assets/sahaj-logos/sahaj.png"
          alt="logo"
          width={150}
          height={150}
          className="h-9 w-40 object-contain"
        />
        <form
          onSubmit={handleSubmit}
          className="mt-6 w-full bg-background p-6 shadow-[0_4px_16px_rgba(0,47,167,0.1)] "
        >
          <div className="mb-6">
            <h2 className="text-2xl font-semibold">
              Setup Organization And Profile
            </h2>
            <p className="text-xs text-subText">
              Complete your organization profile to continue
            </p>
          </div>

          <div className="flex flex-col space-y-4 mb-4 ">
            <div className="grid grid-cols-2 gap-4 ">
              <InputField
                name="firstName"
                label="First Name"
                placeholder="First Name"
                value={formData.firstName}
                onChange={handleChange}
                required
              />
              <InputField
                name="lastName"
                label="Last Name"
                placeholder="Last Name"
                value={formData.lastName}
                onChange={handleChange}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4  ">
              <CreatableInputs
                name="designation"
                label="Designation"
                placeholder="Designation"
                options={formattedDesignationOptions}
                value={
                  formattedDesignationOptions.find(
                    (opt) => opt.value === formData.designation
                  ) || null
                }
                onChange={(selected) => handleChange("designation", selected)}
                required
              />

              <InputField
                name="contactNumber"
                label="Contact Number"
                placeholder="Contact Number"
                type="tel"
                inputMode="numeric"
                maxLength={10}
                value={formData.contactNumber}
                onChange={handleChange}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4 ">
              <InputField
                name="orgName"
                label="Organization Name"
                placeholder="Organization Name"
                value={formData.orgName}
                onChange={handleChange}
                required
              />

              <InputField
                name="orgWebsite"
                label="Organization Website"
                placeholder="Organization Website URL"
                type="url"
                value={formData.orgWebsite}
                onChange={handleChange}
                required
              />
            </div>

            <div className="">
              <SelectInput
                name="orgCountry"
                label="Organization Country"
                options={countryOptions}
                value={
                  countryOptions.find((e) => e.value == formData.orgCountry) ||
                  null
                }
                onChange={(selected) => handleChange("orgCountry", selected)}
                placeholder="Select Country"
                required
              />
            </div>
          </div>


          <button
            type="submit"
            disabled={loading}
            className={`h-10 w-full text-base text-white transition ${
              loading
                ? "bg-gray-300 cursor-not-allowed"
                : "bg-primary hover:bg-hover"
            }`}
          >
            {loading ? "Submitting..." : "Complete Setup"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Page;
