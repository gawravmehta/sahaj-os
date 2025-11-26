import { Field } from "@/components/ui/DetailPageFields";
import Tag from "@/components/ui/Tag";
import { languagesOptions } from "@/constants/countryOptions";
import Image from "next/image";

const General = ({ dpData }) => {
  if (dpData === null) {
    return (
      <div className="flex h-[calc(100vh-210px)] flex-col items-center justify-center overflow-auto">
        <div className="w-[200px]">
          <Image
            height={200}
            width={200}
            src="/assets/illustrations/no-data-find.png"
            alt="Loading..."
            className="h-full w-full object-cover"
          />
        </div>
        <div className="mt-5">
          <p>Loading data...</p>
        </div>
      </div>
    );
  }

  const isEmpty = !dpData || Object.keys(dpData).length === 0;

  const languageMap = languagesOptions.reduce((acc, option) => {
    acc[option.value] = option.label;
    return acc;
  }, {});

  const nameToCode = Object.fromEntries(
    Object.entries(languageMap).map(([code, name]) => [name, code])
  );

  const langValue = dpData?.dp_preferred_lang;

  return (
    <div className="">
      <div className="flex items-center justify-center">
        {isEmpty ? (
          <div className="flex h-[calc(100vh-210px)] flex-col items-center justify-center overflow-auto">
            <div className="w-[200px]">
              <Image
                height={200}
                width={200}
                src="/assets/illustrations/no-data-find.png"
                alt="No data"
                className="h-full w-full object-cover"
              />
            </div>
            <div className="mt-5">
              <p>No General Data Available</p>
            </div>
          </div>
        ) : (
          <div className="custom-scrollbar h-[calc(100vh-179px)] w-full overflow-auto pt-5">
            <div className="mx-auto h-full w-full max-w-[870px] rounded-sm px-3">
              <div className="space-y-3.5 text-sm">
                <Field label="DP ID:" value={dpData.dp_id} />
                <Field
                  label="System ID:"
                  value={dpData?.dp_system_id ?? "N/A"}
                />

                <div className="grid grid-cols-3 gap-4">
                  <Field
                    label="Email:"
                    value={
                      Array.isArray(dpData.dp_email)
                        ? dpData.dp_email.join("   ")
                        : "N/A"
                    }
                  />
                  <Field
                    label="Mobile:"
                    value={
                      Array.isArray(dpData.dp_mobile)
                        ? dpData.dp_mobile.join(" , ")
                        : "N/A"
                    }
                  />
                  <Field
                    label="Consent Count:"
                    value={
                      typeof dpData.consent_count === "number"
                        ? dpData.consent_count
                        : "N/A"
                    }
                  />
                </div>
                <div className="grid grid-cols-3 gap-4 capitalize">
                  <Field
                    label="Country:"
                    value={dpData?.dp_country ? dpData.dp_country : "N/A"}
                  />
                  <Field
                    label="State:"
                    value={
                      dpData?.dp_state
                        ? dpData.dp_state
                            .replace(/-/g, " ")
                            .replace(/\b\w/g, (c) => c.toUpperCase())
                        : "N/A"
                    }
                  />

                  <Field
                    label="Language:"
                    value={
                      langValue
                        ? languageMap[langValue]
                          ? `${languageMap[langValue]} [${langValue}]`
                          : nameToCode[langValue]
                          ? `${langValue} [${nameToCode[langValue]}]`
                          : ` ${langValue}`
                        : "N/A"
                    }
                  />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <Field
                    label="Added With:"
                    value={dpData?.added_with ?? "N/A"}
                    displayValueClassName="capitalize"
                  />
                  <span></span>
                  <div className="flex flex-col">
                    <h1 className="mb-1.5 text-[16px] text-subHeading">
                      Added By:
                    </h1>
                    {dpData?.added_by ? (
                      <p className="text-[16px]">{dpData.added_by}</p>
                    ) : (
                      "N/A"
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="flex flex-col">
                    <h1 className="mb-1.5 text-[16px] text-subHeading">
                      Active Devices:
                    </h1>
                    <p className="text-[16px] capitalize">
                      {Array.isArray(dpData?.dp_active_devices) &&
                      dpData.dp_active_devices.length > 0
                        ? dpData.dp_active_devices.join(", ")
                        : "No active devices"}
                    </p>
                  </div>
                  <Field
                    label="Is Active?"
                    value={
                      typeof dpData?.is_active === "number" ||
                      typeof dpData?.is_active === "boolean"
                        ? dpData.is_active
                          ? "Yes"
                          : "No"
                        : "N/A"
                    }
                  />
                  <Field
                    label="Is Legacy?"
                    value={
                      typeof dpData?.is_legacy === "number" ||
                      typeof dpData?.is_legacy === "boolean"
                        ? dpData.is_legacy
                          ? "Yes"
                          : "No"
                        : "N/A"
                    }
                  />
                </div>
                <div className="">
                  <h1 className="mb-1.5 text-[16px] text-subHeading">
                    Persona ID&apos;s:
                  </h1>
                  <p className="text-[16px]">
                    {dpData.dp_persona?.join(" , ") || "N/A"}
                  </p>
                </div>
                <div className="flex flex-col gap-2">
                  <h1 className="mb-1.5 text-[16px] text-subHeading">Tags:</h1>
                  <div className="mb-3 flex flex-wrap gap-2">
                    {Array.isArray(dpData?.dp_tags) &&
                    dpData.dp_tags.length > 0 ? (
                      dpData.dp_tags.map((tag, index) => (
                        <Tag
                          key={index}
                          className="text-sm"
                          variant="outlineBlue"
                          label={tag}
                        />
                      ))
                    ) : (
                      <span>No tags available</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default General;
