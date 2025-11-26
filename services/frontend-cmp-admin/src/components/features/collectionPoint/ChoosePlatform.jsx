"use client";
import React, { useEffect, useState } from "react";
import { FaCircleCheck } from "react-icons/fa6";
import { BiPlus } from "react-icons/bi";
import { useRouter } from "next/navigation";
import Link from "next/link";
import toast from "react-hot-toast";

import { apiCall } from "@/hooks/apiCall";
import Skeleton from "@/components/ui/Skeleton";
import { getErrorMessage } from "@/utils/errorHandler";
import { platform } from "@/constants/assets";

const ChoosePlatform = ({ formData, setFormData }) => {
  const [platforms, setPlatforms] = useState([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    fetchPlatforms();
  }, []);

  const fetchPlatforms = async () => {
    setLoading(true);
    try {
      const response = await apiCall(`/assets/get-all-assets`);
      setPlatforms(response.assets || []);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlatform = (platformId) => {
    setFormData({ ...formData, asset_id: platformId });
  };

  const truncateMiddle = (url, start = 10, end = 8) => {
    if (!url) return "";
    if (url.length <= start + end) return url;
    return `${url.slice(0, start)}...${url.slice(-end)}`;
  };

  const AddAssetCard = () => (
    <div
      onClick={() => router.push("/apps/asset-sku/create")}
      className="flex w-full h-full cursor-pointer flex-col items-center justify-center gap-5 border shadow-md transition-all hover:shadow-none"
    >
      <BiPlus className="size-14 text-primary" />
      <div className="-mt-4 text-lg text-subText">Add Assets</div>
    </div>
  );

  return (
    <div className=" flex flex-col gap-5">
      <div className="flex w-full max-w-2xl flex-col px-3 pb-12 pt-6">
        <h1 className="text-[28px] leading-9">Choose Platform</h1>
        <p className="mb-6 mt-0.5 text-xs font-light text-subHeading">
          Choose the platform where you want to integrate the collection point.
        </p>

        {loading && (
          <div className="grid grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="flex h-40 w-40 animate-pulse flex-col items-center justify-center gap-5 border border-[#CBD5E1] bg-white p-2 shadow-md"
              >
                <Skeleton variant="Box" className="h-14 w-12" />
                <Skeleton variant="single" />
                <Skeleton variant="single" />
              </div>
            ))}
          </div>
        )}

        {!loading && platforms.length === 0 && (
          <div className="flex h-56 w-56 items-center justify-center">
            <AddAssetCard />
          </div>
        )}

        {!loading && platforms.length > 0 && (
          <div className="grid grid-cols-3 gap-4">
            {platforms.map((p) => {
              const isSelected = formData.asset_id === p.asset_id;

              return (
                <div
                  key={p.asset_id}
                  onClick={() => handleSelectPlatform(p.asset_id)}
                  className={`relative flex py-5 cursor-pointer flex-col items-center justify-center gap-3 border shadow-md transition-all hover:shadow-none ${
                    isSelected
                      ? "border-primary shadow-none"
                      : "border-[#CBD5E1] hover:border-hover"
                  }`}
                >
                  {isSelected && (
                    <FaCircleCheck
                      size={25}
                      className="absolute right-2 top-2 rounded-full bg-white p-0.5 text-green-500"
                    />
                  )}

                  <img
                    src={
                      !p.image || p.image === "sampleurl.png"
                        ? "https://www.pngall.com/wp-content/uploads/11/World-Wide-Web-Address-PNG.png"
                        : p.image
                    }
                    alt={p.asset_name}
                    className="mt-2.5 h-16 w-16 object-contain"
                  />

                  <div className="text-center">
                    <p
                      className={`font-medium ${
                        isSelected ? "text-primary" : "text-heading"
                      }`}
                    >
                      {p.asset_name}
                    </p>
                    <div className="text-[10px] text-subHeading">
                      ({p.category})
                    </div>
                    <p className="mt-1 px-3 text-xs text-subText">
                      {p.description?.split(" ").slice(0, 5).join(" ")}
                      {p.description?.split(" ").length > 5 ? "..." : ""}
                    </p>
                    {p.usage_url && (
                      <div className="mt-2 flex items-center justify-center gap-2">
                        <Link
                          target="_blank"
                          href={p.usage_url}
                          className="text-xs text-primary"
                        >
                          {truncateMiddle(p.usage_url)}
                        </Link>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
            <div
              className={`${platforms.length % 3 === 0 ? "h-56" : "h-auto"}`}
            >
              <AddAssetCard />
            </div>
          </div>
        )}
      </div>
      <div className="flex w-full max-w-2xl flex-col px-3 pb-12">
        <h1 className="text-[28px] leading-9">Choose from other Platform</h1>
        <p className="mb-6 mt-0.5 text-xs text-subHeading">
          Choose the platform where you want to integrate the collection point.
        </p>
        <div>
          {loading ? (
            <div className="grid grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="flex h-40 w-40 animate-pulse flex-col items-center justify-center gap-5 border border-[#CBD5E1] bg-white p-2 shadow-md"
                >
                  <Skeleton variant="Box" className={"h-14 w-12"} />
                  <Skeleton variant="single" />
                  <Skeleton variant="single" />
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-4">
              {platform.map((p) => {
                const isSelected = formData.asset_id === p.asset_id;

                return (
                  <div
                    key={p.asset_id}
                    onClick={() => handleSelectPlatform(p.asset_id)}
                    className={`relative flex h-56 cursor-pointer flex-col items-center justify-center gap-3 border shadow-md transition-all hover:shadow-none ${
                      isSelected
                        ? "border-primary shadow-none"
                        : "border-[#CBD5E1] hover:border-hover"
                    }`}
                  >
                    {isSelected && (
                      <FaCircleCheck
                        size={25}
                        className="absolute right-2 top-2 rounded-full bg-white p-0.5 text-green-500"
                      />
                    )}

                    <img
                      src={
                        !p.image || p.image === "sampleurl.png"
                          ? "https://www.pngall.com/wp-content/uploads/11/World-Wide-Web-Address-PNG.png"
                          : p.image
                      }
                      alt={p.asset_name}
                      className="mt-2.5 h-16 w-16 object-contain"
                    />

                    <div className="text-center">
                      <p
                        className={`font-medium ${
                          isSelected ? "text-primary" : "text-heading"
                        }`}
                      >
                        {p.asset_name}
                      </p>
                      
                      <p className="mt-1 px-3 text-xs text-subText">
                        {p.description?.split(" ").slice(0, 5).join(" ")}
                        {p.description?.split(" ").length > 5 ? "..." : ""}
                      </p>
                      {p.usage_url && (
                        <div className="mt-2 flex items-center justify-center gap-2">
                          <Link
                            target="_blank"
                            href={p.usage_url}
                            className="text-xs text-primary"
                          >
                            {truncateMiddle(p.usage_url)}
                          </Link>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChoosePlatform;
