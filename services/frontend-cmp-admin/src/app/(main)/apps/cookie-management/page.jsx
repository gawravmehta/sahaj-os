"use client";

import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import NoDataFound from "@/components/ui/NoDataFound";
import Skeleton from "@/components/ui/Skeleton";
import Tag from "@/components/ui/Tag";
import { usePermissions } from "@/contexts/PermissionContext";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { useRouter } from "next/navigation";
import { useEffect, useState, useRef, useCallback } from "react";
import toast from "react-hot-toast";
import { FiPlus } from "react-icons/fi";

const Page = () => {
  const router = useRouter();
  const [websiteAssets, setWebsiteAssets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isFetchingMore, setIsFetchingMore] = useState(false);

  const observer = useRef();
  const { canWrite } = usePermissions();

  useEffect(() => {
    getWebsiteAssets(1);
  }, []);

  const getWebsiteAssets = async (pageToFetch) => {
    if (pageToFetch === 1) {
      setLoading(true);
    } else {
      setIsFetchingMore(true);
    }

    try {
      const response = await apiCall(
        `/cookie/get-all-website-assets?current_page=${pageToFetch}&data_per_page=20`
      );

      const newAssets = response.assets || [];

      setWebsiteAssets((prev) => {
        if (pageToFetch === 1) return newAssets;
        return [...prev, ...newAssets];
      });

      setHasMore(newAssets.length === 20);
      setPage(pageToFetch);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
      setIsFetchingMore(false);
    }
  };

  const lastAssetElementRef = useCallback(
    (node) => {
      if (loading || isFetchingMore) return;
      if (observer.current) observer.current.disconnect();
      observer.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasMore) {
          getWebsiteAssets(page + 1);
        }
      });
      if (node) observer.current.observe(node);
    },
    [loading, isFetchingMore, hasMore, page]
  );

  const handleRoute = (id) => {
    router.push(`/apps/cookie-management/${id}`);
  };

  return (
    <div className="flex">
      <div className="h-full w-full">
        <div className="flex flex-col justify-between gap-4 border-b border-borderheader pr-6 sm:flex-row">
          <Header
            title="Websites"
            subtitle="Manage your website assets used for cookies and tracking"
          />

          <div className="mt-0 flex items-center gap-3.5 sm:mt-2">
            <Button
              variant="secondary"
              className="flex gap-1"
              disabled={!canWrite("/apps/asset-sku")}
              onClick={() => router.push("/apps/asset-sku/create")}
            >
              <FiPlus /> Add Website Asset
            </Button>
          </div>
        </div>

        <div className="flex h-[calc(100vh-160px)] w-full">
          <div className="custom-scrollbar flex h-[calc(100vh-152px)] flex-col overflow-auto w-full">
            <div className="mt-5 px-6 pb-6">
              {loading && page === 1 ? (
                <div className="flex gap-4">
                  {Array.from({ length: 4 }).map((_, index) => (
                    <Skeleton
                      key={index}
                      variant="Box"
                      className="h-60 w-full"
                    />
                  ))}
                </div>
              ) : websiteAssets?.length === 0 ? (
                <NoDataFound />
              ) : (
                <>
                  <div className="grid gap-5 grid-cols-1 sm:grid-cols-2 md:grid-cols-4">
                    {websiteAssets.map((asset, index) => {
                      if (websiteAssets.length === index + 1) {
                        return (
                          <div
                            ref={lastAssetElementRef}
                            key={asset?._id}
                            onClick={() => handleRoute(asset?._id)}
                            className="flex cursor-pointer flex-col justify-center gap-2 border border-[#CBD5E1] px-4 py-3 shadow-md transition-all hover:border-primary hover:shadow-none"
                          >
                            <div className="flex w-full justify-between">
                              <div className="h-10">
                                <img
                                  src={
                                    asset.image ||
                                    "/assets/assets_icon/Website.png"
                                  }
                                  alt="asset-img"
                                  className="h-full w-full object-contain opacity-85"
                                />
                              </div>

                              <Tag
                                variant={
                                  asset?.meta_cookies?.scan_status ===
                                  "completed"
                                    ? "active"
                                    : "inactive"
                                }
                                label={
                                  asset?.meta_cookies?.scan_status ===
                                  "completed"
                                    ? "Scaned"
                                    : "Not Scaned"
                                }
                                className="h-6 text-xs capitalize"
                              />
                            </div>
                            <span className="">
                              <div className="mt-1 font-normal capitalize text-primary">
                                {asset.asset_name}
                              </div>
                            </span>
                            <p className="line-clamp-2 h-10 text-xs text-subHeading">
                              {asset.description}
                            </p>
                            <div className="text-xs">
                              Scanned Cookies :{" "}
                              {asset?.meta_cookies?.cookies_count ?? 0}
                            </div>
                          </div>
                        );
                      } else {
                        return (
                          <div
                            key={asset?._id}
                            onClick={() => handleRoute(asset?._id)}
                            className="flex cursor-pointer flex-col justify-center gap-2 border border-[#CBD5E1] px-4 py-3 shadow-md transition-all hover:border-primary hover:shadow-none"
                          >
                            <div className="flex w-full justify-between">
                              <div className="h-10">
                                <img
                                  src={
                                    asset.image ||
                                    "/assets/assets_icon/Website.png"
                                  }
                                  alt="asset-img"
                                  className="h-full w-full object-contain opacity-85"
                                />
                              </div>

                              <Tag
                                variant={
                                  asset?.meta_cookies?.scan_status ===
                                  "completed"
                                    ? "active"
                                    : "inactive"
                                }
                                label={
                                  asset?.meta_cookies?.scan_status ===
                                  "completed"
                                    ? "Scaned"
                                    : "Not Scaned"
                                }
                                className="h-6 text-xs capitalize"
                              />
                            </div>
                            <span className="">
                              <div className="mt-1 font-normal capitalize text-primary">
                                {asset.asset_name}
                              </div>
                            </span>
                            <p className="line-clamp-2 h-10 text-xs text-subHeading">
                              {asset.description}
                            </p>
                            <div className="text-xs">
                              Scanned Cookies :{" "}
                              {asset?.meta_cookies?.cookies_count ?? 0}
                            </div>
                          </div>
                        );
                      }
                    })}
                  </div>
                  {isFetchingMore && (
                    <div className="mt-4 flex justify-center">
                      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Page;
