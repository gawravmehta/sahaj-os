"use client";

import DetailSidebar from "@/components/features/assetSku/DetailSidebar";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import NoDataFound from "@/components/ui/NoDataFound";
import Skeleton from "@/components/ui/Skeleton";
import Tag from "@/components/ui/Tag";
import { usePermissions } from "@/contexts/PermissionContext";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { FiPlus } from "react-icons/fi";

const Page = () => {
  const [assets, setAssets] = useState([]);
  const [oneAssets, setOneAssets] = useState([]);
  const [detailBar, setDetailBar] = useState(false);
  const [loading, setLoading] = useState(false);
  const [highlight, setHighlight] = useState(false);

  const { canWrite } = usePermissions();
  const router = useRouter();

  useEffect(() => {
    getAssets();
  }, []);

  const getAssets = async () => {
    setLoading(true);
    try {
      const response = await apiCall(`/assets/get-all-assets`);
      setAssets(response.assets);
      setLoading(false);
    } catch (error) {
      toast.error(getErrorMessage(error));
      setLoading(false);
    }
  };

  const handleOneAsset = async (id) => {
    try {
      const response = await apiCall(`/assets/get-asset/${id}`);
      if (id === response.asset_id) {
        setHighlight(response.asset_id);
      }
      setOneAssets(response);
      setDetailBar(true);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  return (
    <div className="flex">
      <div className="h-full w-full">
        <div className="flex flex-col justify-between gap-4 border-b border-borderheader pr-6 sm:flex-row">
          <Header
            title="Assets"
            subtitle="Create and manage your customer Assets here"
          />

          <div className="mt-0 flex items-center gap-3.5 sm:mt-2">
            <Button
              variant="secondary"
              disabled={!canWrite("/apps/asset-sku")}
              onClick={() => router.push("/apps/asset-sku/create")}
              className="flex gap-1"
            >
              <FiPlus /> Create
            </Button>
          </div>
        </div>

        <div className="flex h-[calc(100vh-160px)] w-full">
          <div
            className={`custom-scrollbar flex h-[calc(100vh-152px)] flex-col overflow-auto ${
              detailBar === true ? "w-[70%]" : "w-full"
            }`}
          >
            <div className="mt-5 px-6">
              {loading ? (
                <div className="flex gap-4">
                  {Array.from({ length: 4 }).map((_, index) => (
                    <Skeleton
                      key={index}
                      variant="Box"
                      className="h-60 w-full"
                    />
                  ))}
                </div>
              ) : assets?.length === 0 ? (
                <NoDataFound />
              ) : (
                <div
                  className={`grid gap-5 ${
                    detailBar
                      ? "grid-cols-1 sm:grid-cols-2 md:grid-cols-3"
                      : "grid-cols-1 sm:grid-cols-2 md:grid-cols-4"
                  }`}
                >
                  {assets.map((templatesAssets) => (
                    <div
                      key={templatesAssets.asset_id}
                      onClick={() => {
                        if (templatesAssets.asset_status !== "archived") {
                          handleOneAsset(templatesAssets.asset_id);
                        } else {
                          setDetailBar(false);
                        }
                      }}
                      className={`flex cursor-pointer flex-col justify-center gap-2 border border-primary border-opacity-0 ${
                        highlight === templatesAssets.asset_id
                          ? "border-primary border-opacity-100"
                          : "border-[#CBD5E1]"
                      } px-4 py-3 shadow-md transition-all hover:border-opacity-100 hover:shadow-none`}
                    >
                      <div className="flex w-full justify-between">
                        <div className="h-10">
                          <img
                            src={templatesAssets.image || ""}
                            alt="img"
                            height={1000}
                            width={1000}
                            quality={100}
                            className="h-full w-full object-contain opacity-85"
                          />
                        </div>

                        <Tag
                          variant={
                            templatesAssets.asset_status == "published"
                              ? "active"
                              : templatesAssets.asset_status == "archived"
                              ? "inactive"
                              : "draft"
                          }
                          label={templatesAssets.asset_status}
                          className="h-6 text-xs capitalize"
                        />
                      </div>
                      <span className="">
                        <div className="mt-1 font-normal capitalize text-primary">
                          {templatesAssets.asset_name
                            .split(" ")
                            .slice(0, 10)
                            .join(" ") +
                            (templatesAssets.description.split(" ").length > 14
                              ? "..."
                              : "")}
                        </div>
                      </span>
                      <p className="h-16 text-xs text-subHeading">
                        {templatesAssets.description
                          .split(" ")
                          .slice(0, 18)
                          .join(" ") +
                          (templatesAssets.description.split(" ").length > 10
                            ? "..."
                            : "")}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {detailBar && (
            <div>
              <div className="fixed right-0 h-[calc(100vh-125px)] w-88 border-l bg-white border-borderSecondary  ">
                <DetailSidebar
                  setHighlight={setHighlight}
                  setAssets={setAssets}
                  assets={assets}
                  asset={oneAssets}
                  setDetailBar={setDetailBar}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Page;
