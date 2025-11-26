import Loader from "@/components/ui/Loader";
import { apiCall } from "@/hooks/apiCall";
import Image from "next/image";
import React, { useEffect, useState, useCallback } from "react";

const Kyc = ({ data }) => {
  const [kycFront, setKycFront] = useState("");
  const [kycBack, setKycBack] = useState("");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalSrc, setModalSrc] = useState("");
  const [modalAlt, setModalAlt] = useState("");

  const openModal = useCallback((src, alt) => {
    setModalSrc(src);
    setModalAlt(alt);
    setIsModalOpen(true);

    document.documentElement.style.overflow = "hidden";
  }, []);

  const closeModal = useCallback(() => {
    setIsModalOpen(false);
    setModalSrc("");
    setModalAlt("");
    document.documentElement.style.overflow = "";
  }, []);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") closeModal();
    };
    if (isModalOpen) {
      window.addEventListener("keydown", onKey);
      return () => window.removeEventListener("keydown", onKey);
    }
  }, [isModalOpen, closeModal]);

  const getPresignedUrl = useCallback(async () => {
    try {
      const [response1, response2] = await Promise.all([
        data?.kyc_front
          ? apiCall(
              `/dpar/presigned-url?file_url=${encodeURIComponent(
                data.kyc_front
              )}`
            )
          : Promise.resolve(null),
        data?.kyc_back
          ? apiCall(
              `/dpar/presigned-url?file_url=${encodeURIComponent(
                data.kyc_back
              )}`
            )
          : Promise.resolve(null),
      ]);

      if (response1?.url) setKycFront(response1.url);
      if (response2?.url) setKycBack(response2.url);
    } catch (err) {
      console.error("Error fetching url data:", err);
    }
  }, [data?.kyc_front, data?.kyc_back]);

  useEffect(() => {
    getPresignedUrl();
  }, [getPresignedUrl]);

  if (!kycBack && !kycFront) return <Loader height={"h-96"} />;

  return (
    <div className="p-8 text-sm">
      <div className="flex flex-col">
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">KYC Document Type:</span>{" "}
          {data?.kyc_document || "—"}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 my-5">
          {kycFront ? (
            <div className="space-y-2">
              <div
                className="relative w-full aspect-4/3 overflow-hidden border border-gray-300 cursor-zoom-in"
                onClick={() => openModal(kycFront, "KYC front")}
                role="button"
                aria-label="Open KYC front image"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ")
                    openModal(kycFront, "KYC front");
                }}
              >
                <Image
                  src={kycFront}
                  alt="kyc front"
                  fill
                  className="object-contain bg-neutral-50"
                  sizes="(max-width: 768px) 100vw, 50vw"
                />
              </div>
            </div>
          ) : (
            <div className="text-neutral-500">Front image unavailable</div>
          )}

          {kycBack ? (
            <div className="space-y-2">
              <div
                className="relative w-full aspect-4/3  overflow-hidden border border-gray-300 cursor-zoom-in"
                onClick={() => openModal(kycBack, "KYC back")}
                role="button"
                aria-label="Open KYC back image"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ")
                    openModal(kycBack, "KYC back");
                }}
              >
                <Image
                  src={kycBack}
                  alt="kyc back"
                  fill
                  className="object-contain bg-neutral-50"
                  sizes="(max-width: 768px) 100vw, 50vw"
                />
              </div>
            </div>
          ) : (
            <div className="text-neutral-500">Back image unavailable</div>
          )}
        </div>
      </div>

      {isModalOpen && (
        <div
          className="fixed inset-0 z-100 flex items-center justify-center"
          aria-modal="true"
          role="dialog"
        >
          <div className="absolute inset-0 bg-black/70" onClick={closeModal} />
          <div className="relative z-101 max-w-[95vw] max-h-[90vh] w-auto">
            <div className="overflow-auto  p-2">
              <img
                src={modalSrc}
                alt={modalAlt}
                className="max-h-[80vh] max-w-[90vw] object-contain"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Kyc;
