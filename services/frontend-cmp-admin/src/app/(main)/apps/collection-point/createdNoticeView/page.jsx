"use client";

import ErrorPopup from "@/components/features/collectionPoint/ErrorPopup";
import Button from "@/components/ui/Button";
import Loader from "@/components/ui/Loader";
import { apiCall, uploadFile } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { FaArrowLeft, FaTrash } from "react-icons/fa";
import { languagesOptions } from "@/constants/countryOptions";

const Page = () => {
  const searchParams = useSearchParams();
  const [mounted, setMounted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [btnLoading, setBtnLoading] = useState(false);
  const [createdNoticeHtml, setCreateNoticeHtml] = useState(null);
  const [templatesAssets, setTemplatesAssets] = useState(null);
  const [errorPopup, setErrorPopup] = useState(null);
  const cpId = searchParams.get("cpId") || "";
  const router = useRouter();

  const [uploadedAudios, setUploadedAudios] = useState({});
  const [uploadingLang, setUploadingLang] = useState(null);
  const [deletingLang, setDeletingLang] = useState(null);

  useEffect(() => {
    if (cpId) {
      getCollectionPoint();
      setMounted(true);
    }
  }, [cpId]);

  const getCollectionPoint = async () => {
    try {
      const response = await apiCall(`/cp/get-cp/${cpId}`);
      setTemplatesAssets(response);
      setCreateNoticeHtml(response?.notice_html);

      if (response?.translated_audio) {
        const initialAudios = {};
        response.translated_audio.forEach((item) => {
          initialAudios[item.audio_language] = item.audio_url;
        });
        setUploadedAudios(initialAudios);
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleFileUpload = async (event, langCode) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadingLang(langCode);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await uploadFile("/cp/upload-audio", formData);

      const audioUrl = response?.url || response?.audio_url || response;

      setUploadedAudios((prev) => ({
        ...prev,
        [langCode]: audioUrl,
      }));
      toast.success(`Audio uploaded`);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setUploadingLang(null);
    }
  };

  const handleDeleteAudio = async (langCode, audioUrl) => {
    if (!audioUrl) return;

    const audioFileName = audioUrl.split("/").pop();

    setDeletingLang(langCode);
    try {
      await apiCall(`/cp/delete-audio/${audioFileName}`, {
        method: "DELETE",
      });

      setUploadedAudios((prev) => {
        const newState = { ...prev };
        delete newState[langCode];
        return newState;
      });

      toast.success(`Audio deleted`);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setDeletingLang(null);
    }
  };

  const saveCollectionPoint = async (isDraft = true) => {
    setBtnLoading(true);
    try {
      const translatedAudioArray = Object.entries(uploadedAudios).map(
        ([lang, url]) => ({
          audio_language: lang,
          audio_url: url,
        })
      );

      const payload = {
        translated_audio: translatedAudioArray,
      };

      await apiCall(`/cp/update-cp/${cpId}`, {
        method: "PUT",
        data: payload,
      });

      if (!isDraft) {
        await apiCall(`/cp/publish-cp/${cpId}`, {
          method: "PATCH",
        });
        toast.success("Collection point published successfully");
      } else {
        toast.success("Collection point saved as draft");
      }

      router.push(`/apps/collection-point/integration-guide?cp_id=${cpId}`);
    } catch (error) {
      const errData = error?.data?.detail;
      if (errData) {
        setErrorPopup(errData);
      } else {
        toast.error(getErrorMessage(error));
      }
    } finally {
      setBtnLoading(false);
    }
  };

  if (!mounted) return null;

  return (
    <>
      <div className="flex items-center justify-between border-b border-borderheader py-4 pl-6">
        <Link
          href={
            templatesAssets?.cp_status == "draft"
              ? `/apps/collection-point/${cpId}?type=edit&activeTab=4`
              : "/apps/collection-point"
          }
          className="left-5 top-7"
        >
          <Button variant="back">
            <FaArrowLeft />
            <p>Back</p>
          </Button>
        </Link>
        {templatesAssets?.cp_status == "draft" && (
          <div className="flex items-center justify-center gap-3.5 pr-6">
            <div className="right-32 top-7 bg-white">
              <Button
                variant="secondary"
                onClick={() => saveCollectionPoint(true)}
                disabled={btnLoading}
              >
                Save as Draft
              </Button>
            </div>
            <div className="right-6 top-7">
              <Button
                className={"px-4"}
                btnLoading={btnLoading && !uploadingLang}
                disabled={btnLoading || !!uploadingLang}
                variant="primary"
                onClick={() => saveCollectionPoint(false)}
              >
                Publish
              </Button>
            </div>
          </div>
        )}
      </div>

      <div className="relative flex h-[84vh] w-full flex-row items-start bg-[#F3F3F3]">
        <div className="custom-scrollbar h-full w-1/2 overflow-auto border-r border-borderheader bg-white p-5 shadow">
          {!loading ? (
            <div className="h-full w-full">
              <iframe
                srcDoc={createdNoticeHtml}
                className="h-full w-full border-none"
                title="Notice Preview"
              />
            </div>
          ) : (
            <Loader height="h-full" />
          )}
        </div>

        <div className="custom-scrollbar h-full w-1/2 overflow-auto bg-white p-5">
          <h2 className="mb-4 text-lg font-semibold text-[#4B5563]">
            Upload Audio for Languages
          </h2>
          <div className="flex flex-col gap-4">
            {languagesOptions.map((lang) => (
              <div
                key={lang.alt}
                className="flex items-center justify-between border border-gray-300 p-4 "
              >
                <span className="font-medium text-[#374151] capitalize">
                  {lang.label}{" "}
                  <span className="text-gray-500">({lang.nativeLabel})</span>
                </span>
                <div className="flex items-center gap-2">
                  {uploadedAudios[lang.alt] ? (
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-green-600">Uploaded</span>
                      <button
                        onClick={() =>
                          handleDeleteAudio(lang.alt, uploadedAudios[lang.alt])
                        }
                        disabled={deletingLang === lang.alt}
                        className="text-red-500 hover:text-red-700 transition-colors"
                        title="Delete Audio"
                      >
                        {deletingLang === lang.alt ? (
                          <span className="text-xs">Deleting...</span>
                        ) : (
                          <FaTrash size={16} />
                        )}
                      </button>
                    </div>
                  ) : (
                    <>
                      {uploadingLang === lang.alt ? (
                        <span className="text-sm text-gray-500">
                          Uploading...
                        </span>
                      ) : (
                        <input
                          type="file"
                          accept="audio/*"
                          onChange={(e) => handleFileUpload(e, lang.alt)}
                          className="block w-full text-sm text-slate-500
                            file:mr-4   file:border file:border-gray-300
                            file:bg-violet-50 file:px-4 file:py-2 file:text-sm
                            file:font-semibold file:text-primary
                            hover:file:bg-violet-100"
                        />
                      )}
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      {errorPopup && (
        <ErrorPopup
          errorData={errorPopup}
          onClose={() => setErrorPopup(null)}
          onSaveDraft={() => router.push("/apps/collection-point")}
        />
      )}
    </>
  );
};

export default Page;
