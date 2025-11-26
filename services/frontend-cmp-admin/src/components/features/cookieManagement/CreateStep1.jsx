"use client";

import {
  InputField,
  RetentionPeriodField,
  SelectInput,
  TextareaField,
} from "@/components/ui/Inputs";
import YesNoToggle from "@/components/ui/YesNoToggle";
import { categoryOptions, sameSiteOptions } from "@/constants/cookieManagement";

const CreateStep1 = ({ formData, setFormData, missingFields, wrongFields }) => {
  return (
    <div className="flex w-full max-w-lg flex-col space-y-4 pt-4 pb-4">
      <h1 className="text-[28px] ">General Information</h1>
      <p className="text-xs text-subHeading">
        Provide the required details to configure and classify this cookie.
      </p>

      <InputField
        name="cookie_name"
        label="Cookie Name"
        placeholder="Enter Cookie Name"
        tooltipText="Unique identifier of the cookie set by the website or application."
        value={formData.cookie_name}
        onChange={(e) =>
          setFormData({ ...formData, cookie_name: e.target.value })
        }
        required
        missingFields={missingFields}
      />

      <TextareaField
        label="Description"
        placeholder="Write a Brief Description"
        tooltipText="Brief explanation of the cookie's purpose and functionality."
        value={formData.description}
        onChange={(e) =>
          setFormData({ ...formData, description: e.target.value })
        }
      />

      <SelectInput
        label="Category"
        name="category"
        placeholder="Select Category"
        tooltipText="Select the cookie type: essential, analytics, marketing, functional, etc."
        options={categoryOptions}
        value={categoryOptions.find((opt) => opt.value === formData.category)}
        onChange={(selected) =>
          setFormData({ ...formData, category: selected?.value || "" })
        }
        required
        missingFields={missingFields}
      />

      <div className="flex justify-between">
        <YesNoToggle
          name="http_only"
          label="Http Only"
          value={formData.http_only ?? false}
          onChange={(field, value) =>
            setFormData({ ...formData, http_only: value })
          }
          tooltipText="Prevents client-side scripts from accessing the cookie. Recommended for security."
        />

        <YesNoToggle
          name="secure"
          label="Secure"
          value={formData.secure ?? false}
          onChange={(field, value) =>
            setFormData({ ...formData, secure: value })
          }
          tooltipText="Ensures the cookie is sent only over HTTPS connections."
        />

        <YesNoToggle
          name="is_third_party"
          label="Third Party"
          value={formData.is_third_party ?? false}
          onChange={(field, value) =>
            setFormData({ ...formData, is_third_party: value })
          }
          tooltipText="Specifies if this cookie is set by a domain other than the one you are visiting."
        />
      </div>

      <RetentionPeriodField
        name="de_retention_period"
        label="Expiry"
        tooltipText="Date or duration after which the cookie expires."
        placeholder="Enter Purpose Expiry Period"
        valueInDays={formData.lifespan}
        onChange={(days) =>
          setFormData({ ...formData, lifespan: String(days) })
        }
      />

      <InputField
        label="Hostname"
        name="hostname"
        placeholder="e.g. www.example.com"
        tooltipText="Domain name where the cookie is valid."
        value={formData.hostname}
        onChange={(e) => setFormData({ ...formData, hostname: e.target.value })}
        required
        missingFields={missingFields}
        wrongFields={wrongFields}
      />

      <InputField
        label="Path"
        placeholder="Enter Path"
        tooltipText="URL path for which the cookie is valid. Defaults to root /."
        value={formData.path}
        onChange={(e) => setFormData({ ...formData, path: e.target.value })}
      />

      <SelectInput
        className="mb-4"
        label="Same Site"
        tooltipText="Restricts cookie access across sites."
        options={sameSiteOptions}
        value={sameSiteOptions.find((opt) => opt.value === formData.same_site)}
        onChange={(selected) =>
          setFormData({ ...formData, same_site: selected?.value || "Lax" })
        }
        isClearable={false}
      />
    </div>
  );
};

export default CreateStep1;
