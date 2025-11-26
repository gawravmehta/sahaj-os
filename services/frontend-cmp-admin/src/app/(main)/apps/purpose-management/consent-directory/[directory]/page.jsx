"use client";

import { use, useEffect, useState } from "react";
import { apiCall } from "@/hooks/apiCall";
import Header from "@/components/ui/Header";
import { MdOutlineTranslate } from "react-icons/md";
import Skeleton from "@/components/ui/Skeleton";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";
import { useSearchParams } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import Tag from "@/components/ui/Tag";
import { getLanguageLabel } from "@/utils/helperFunctions";
import { SelectInput } from "@/components/ui/Inputs";

const tabs = [{ id: "general", label: "General" }];

const Page = ({ params }) => {
  const { directory: ConsentDi } = use(params);
  const [directory, setDirectory] = useState(null);
  const [selectedLang, setSelectedLang] = useState("en");
  const [description, setDescription] = useState("");
  const [tempDataPrinciple, setTempDataPrinciple] = useState([]);
  const searchParams = useSearchParams();
  const [formattedLanguageOptions, setFormattedLanguageOptions] =
    useState(null);

  const currentPage = searchParams.get("page");
  const searchable = searchParams.get("query");

  const breadcrumbsProps = {
    path: `/apps/purpose-management/consent-directory/Details`,
    skip: "/apps",
  };
  useEffect(() => {
    getAllDataPrincipals();
  }, [ConsentDi]);

  const getAllDataPrincipals = async () => {
    try {
      const response = await apiCall(
        `/purposes/templates?purpose_id=${ConsentDi}`
      );

      const filteredData = response.purposes.filter(
        (item) => item?.purpose_id === ConsentDi
      );

      const data = filteredData[0];
      setTempDataPrinciple(data);

      const formattedOptions = Object.entries(data.translations).map(
        ([langCode, desc]) => ({
          value: langCode,
          label: getLanguageLabel(langCode, true),
          description: desc,
        })
      );

      setFormattedLanguageOptions(formattedOptions);

      if (formattedOptions.length > 0) {
        setSelectedLang(formattedOptions[0].value);
        setDescription(formattedOptions[0].description);
      }
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
      console.error("Error fetching data principals:", error);
    }
  };

  const handleLangChange = (e) => {
    const selectedLangCode = e.value;
    setSelectedLang(selectedLangCode);

    const selectedOption = formattedLanguageOptions.find(
      (opt) => opt.value === selectedLangCode
    );

    if (selectedOption) {
      setDescription(selectedOption.description);
    }
  };

  return (
    <div className="flex">
      <div className="w-full">
        <div className="border-b border-borderSecondary">
          <Header
            title="Biotechnology"
            breadcrumbsProps={breadcrumbsProps}
            subtitle="Set up your sub-organization, customize branding, and configure communication channels for unified operations."
          />
        </div>

        <div className="">
          <Tabs defaultValue="general">
            <div className="flex w-full items-center justify-center border-b border-borderheader">
              <TabsList className="gap-36">
                {tabs.map((tab) => (
                  <TabsTrigger
                    key={tab?.id}
                    value={tab?.id}
                    variant="secondary"
                  >
                    {tab?.label}
                  </TabsTrigger>
                ))}
              </TabsList>
            </div>

            <TabsContent value={"general"}>
              <div className="mt-5 flex items-center justify-end gap-2 pr-10">
                <label htmlFor="language-select ">
                  <MdOutlineTranslate size={20} className="text-primary" />
                </label>
              
                <SelectInput
                  className="w-36"
                  id="language-select"
                  value={formattedLanguageOptions?.filter(
                    (item) => item?.value == selectedLang
                  )}
                  onChange={handleLangChange}
                  options={formattedLanguageOptions}
                  isClearable={false}
                />
              </div>
              <div className="m-auto -mt-16 flex h-full w-200 justify-center px-5 py-10">
                <div>
                  <div className="flex flex-col gap-1">
                    <span className="text-sm text-gray-400">Purpose ID:</span>
                    <span className="text-base text-gray-600">{ConsentDi}</span>
                  </div>
                  <div className="mt-2 flex gap-20">
                    <div className="flex flex-col gap-1">
                      <span className="text-sm text-gray-400">
                        Industry Name:
                      </span>

                      {!tempDataPrinciple?.industry ? (
                        <Skeleton variant="single" className="h-4 w-full" />
                      ) : (
                        <span className="text-base text-gray-600">
                          {tempDataPrinciple?.industry}
                        </span>
                      )}
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-sm text-gray-400">
                        Sub-Category:
                      </span>

                      {!tempDataPrinciple?.sub_category ? (
                        <Skeleton variant="single" className="h-4 w-full" />
                      ) : (
                        <span className="text-base text-gray-600">
                          {tempDataPrinciple?.sub_category}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="mt-2 flex flex-col gap-1">
                    <span className="text-sm text-gray-400">Description:</span>
                    {!description ? (
                      <Skeleton variant="single" className="h-4 w-full" />
                    ) : (
                      <span className="text-base text-gray-600">
                        {description}
                      </span>
                    )}
                  </div>
                  <div className="mt-2">
                    <span>Data Element</span>
                    <div className="mt-1.5 flex flex-wrap gap-2">
                      {tempDataPrinciple?.data_elements?.length > 0 ? (
                        tempDataPrinciple?.data_elements.map((item, i) => (
                          <Tag key={i} variant="outlineBlue" label={item} />
                        ))
                      ) : (
                        <>
                          <Skeleton variant="single" className="h-8 w-36" />
                          <Skeleton variant="single" className="h-8 w-36" />
                          <Skeleton variant="single" className="h-8 w-36" />
                          <Skeleton variant="single" className="h-8 w-36" />
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default Page;
