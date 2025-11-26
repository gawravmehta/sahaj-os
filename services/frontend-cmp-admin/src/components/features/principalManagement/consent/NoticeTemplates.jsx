import React, { useState, useEffect } from "react";
import Image from "next/image";
import { FaCircleCheck, FaChevronLeft, FaChevronRight } from "react-icons/fa6";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";
import Skeleton from "@/components/ui/Skeleton";

const NoticeTemplates = ({
  setCpId,
  cpId,
  setNoticeAvailable,
  setIsNoticeValid,
}) => {
  const [loading, setLoading] = useState(false);
  const [templatesData, setTemplatesData] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(cpId || null);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    fetchTemplates();
  }, []);

  useEffect(() => {
    if (cpId) {
      setSelectedTemplate(cpId);
    }
  }, [cpId]);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const response = await apiCall(
        `/cp/get-all-cps?current_page=1&data_per_page=20`
      );

      if (
        response &&
        response.collection_points &&
        Array.isArray(response.collection_points)
      ) {
        const mappedTemplates = response.collection_points.map((template) => ({
          cpId: template.cp_id || template.df_id,
          name: template.cp_name || "Unnamed Template",
          description: template.cp_description || "No description available",
          imageUrl: template.notice_url || "/assets/notice/Frame 1147 3.png",
        }));

        setTemplatesData(mappedTemplates);
        setNoticeAvailable(mappedTemplates.length > 0);
      } else {
        setTemplatesData([]);
        setNoticeAvailable(false);
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      setTemplatesData([]);
      setNoticeAvailable(false);
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateSelect = (templateId) => {
    const isAlreadySelected = selectedTemplate === templateId;
    const newSelected = isAlreadySelected ? null : templateId;

    setSelectedTemplate(newSelected);
    setCpId(newSelected);
    setIsNoticeValid(!!newSelected);
  };

  const nextSlide = () => {
    if (currentIndex < templatesData.length - 2) {
      setCurrentIndex((prevIndex) => prevIndex + 1);
    }
  };

  const prevSlide = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prevIndex) => prevIndex - 1);
    }
  };

  const goToSlide = (index) => {
    if (index <= templatesData.length - 2) {
      setCurrentIndex(index);
    }
  };

  const getVisibleTemplates = () => {
    if (templatesData.length <= 2) {
      return templatesData;
    }

    return templatesData.slice(currentIndex, currentIndex + 3);
  };

  const visibleTemplates = getVisibleTemplates();

  const canGoNext = currentIndex < templatesData.length - 3;
  const canGoPrev = currentIndex > 0;

  return (
    <div className="flex flex-col gap-2">
      {loading ? (
        <>
          <div className="">
            <h2 className="text-[15px] mt-5">Select Collection Point</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 flex-1 px-4 mt-2">
            {Array.from({ length: 3 }).map((_, idx) => (
              <div
                key={idx}
                className="relative w-full border border-[#C7CFE2] py-3 px-2 shadow-sm"
              >
                <div className="absolute right-2 top-2 z-10">
                  <Skeleton variant="Circle" className="h-6 w-6" />
                </div>

                <div className="p-2 space-y-2">
                  <Skeleton variant="Box" className="h-4 w-3/4" />

                  <Skeleton variant="Box" className="h-3 w-full" />
                  <Skeleton variant="Box" className="h-3 w-5/6" />
                </div>
              </div>
            ))}
          </div>
        </>
      ) : templatesData.length === 0 ? (
        <div className="flex items-center justify-center mt-3 w-full">
          <div className="flex flex-col items-center justify-center">
            <div className="mt-5 text-center">
              <h1 className="text-xl">
                No published collection point available
              </h1>
            </div>
          </div>
        </div>
      ) : (
        <div className="w-full max-w-3xl   mt-5">
          <div className="pb-3">
            <h2 className="text-[15px] mt-3">Select Collection Point</h2>
          </div>

          <div className="flex items-center justify-between w-full overflow-hidden">
            {templatesData.length > 3 && (
              <button
                onClick={prevSlide}
                disabled={!canGoPrev}
                className={`rounded-full p-2 shadow-lg transition-all ${
                  canGoPrev
                    ? "bg-white hover:bg-gray-100 cursor-pointer"
                    : "bg-gray-200 cursor-not-allowed opacity-50"
                }`}
                aria-label="Previous template"
              >
                <FaChevronLeft
                  className={canGoPrev ? "text-gray-600" : "text-gray-400"}
                  size={20}
                />
              </button>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 flex-1 px-4">
              {visibleTemplates.map((template) => (
                <div
                  key={template.cpId}
                  onClick={() => handleTemplateSelect(template.cpId)}
                  className={`relative w-full cursor-pointer border py-3 px-2 shadow-sm transition-all hover:shadow-md ${
                    selectedTemplate === template.cpId
                      ? "border-blue-900"
                      : "border-[#C7CFE2]"
                  }`}
                >
                  {selectedTemplate === template.cpId && (
                    <div className="absolute right-2 top-2 z-10">
                      <FaCircleCheck
                        size={20}
                        className="rounded-full bg-white text-[#06a42a]"
                      />
                    </div>
                  )}

                  <div className="p-2">
                    <h2 className="text-sm font-semibold line-clamp-1 capitalize">
                      {template.name}
                    </h2>
                    <p className="pt-1 text-xs text-subHeading line-clamp-2 capitalize">
                      {template.description.split(" ").length > 30
                        ? template.description
                            .split(" ")
                            .slice(0, 30)
                            .join(" ") + "..."
                        : template.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {templatesData.length > 3 && (
              <button
                onClick={nextSlide}
                disabled={!canGoNext}
                className={`rounded-full p-2  shadow-lg transition-all ${
                  canGoNext
                    ? "bg-white hover:bg-gray-100 cursor-pointer"
                    : "bg-gray-200 cursor-not-allowed opacity-50"
                }`}
                aria-label="Next template"
              >
                <FaChevronRight
                  className={canGoNext ? "text-gray-600" : "text-gray-400"}
                  size={20}
                />
              </button>
            )}
          </div>

          {templatesData.length > 3 && (
            <div className="mt-6 flex justify-center space-x-2">
              {Array.from({ length: templatesData.length - 2 }).map(
                (_, index) => (
                  <button
                    key={index}
                    onClick={() => goToSlide(index)}
                    className={`h-2 cursor-pointer rounded-full transition-all ${
                      index === currentIndex
                        ? "bg-primary w-6"
                        : "bg-gray-300 w-2"
                    }`}
                    aria-label={`Go to template ${index + 1}`}
                  />
                )
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NoticeTemplates;
