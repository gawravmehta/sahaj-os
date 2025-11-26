"use client";

import DeleteModal from "@/components/shared/modals/DeleteModal";
import Header from "@/components/ui/Header";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";

import { LuTrash } from "react-icons/lu";
import Tag from "@/components/ui/Tag";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Button from "@/components/ui/Button";
import Loader from "@/components/ui/Loader";

const Page = () => {
  const params = useParams();
  const router = useRouter();
  const website_id = params?.website_id;
  const cookie_id = params?.cookie_id;

  const [loading, setLoading] = useState(false);
  const [cookieData, setCookieData] = useState(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);

  useEffect(() => {
    if (cookie_id) {
      getCookieById(cookie_id);
    }
  }, [cookie_id]);

  const getCookieById = async (cookieId) => {
    try {
      setLoading(true);
      const response = await apiCall(`/cookie/get-cookie/${cookieId}`);
      if (response) {
        setCookieData(response);
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error(
        "Error fetching cookie:",
        error?.response?.data || error.message
      );
    } finally {
      setLoading(false);
    }
  };

  const handlePublishCookie = async () => {
    try {
      setLoading(true);
      const response = await apiCall(`/cookie/publish-cookie/${cookie_id}`, {
        method: "PATCH",
      });
      if (response) {
        toast.success("Cookie published successfully");
        getCookieById(cookie_id);
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error(
        "Error publishing cookie:",
        error?.response?.data || error.message
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCookie = async () => {
    try {
      setLoading(true);
      await apiCall(`/cookie/delete-cookie/${cookie_id}`, {
        method: "DELETE",
      });
      toast.success("Cookie deleted successfully");
      setDeleteModalOpen(false);
      router.push(`/apps/cookie-management/${website_id}`);
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error(
        "Error deleting cookie:",
        error?.response?.data || error.message
      );
    } finally {
      setLoading(false);
    }
  };

  const breadcrumbsProps = {
    path: `/apps/cookie-management/${website_id}/${cookie_id}`,
    skip: `/apps`,
    labels: {
      [`/apps/cookie-management/${website_id}`]: "cookies",
    },
  };

  return (
    <>
      <div className="flex justify-between">
        <Header
          title={cookieData?.cookie_name || "Cookie Details"}
          breadcrumbsProps={breadcrumbsProps}
        />

        {cookieData && (
          <div className="flex items-center justify-center gap-2 pr-6">
            {cookieData.cookie_status === "draft" && (
              <Button
                onClick={handlePublishCookie}
                variant="secondary"
                className="gap-1"
                disabled={loading}
              >
                Publish
              </Button>
            )}
            <Button
              onClick={() => setDeleteModalOpen(true)}
              variant="delete"
              className="gap-1"
              disabled={loading}
            >
              <LuTrash />
              Delete Cookie
            </Button>
          </div>
        )}
      </div>

      <div>
        <Tabs defaultValue="general">
          <div className="flex w-full items-center  justify-start border-y border-borderSecondary sm:justify-center">
            <div className="flex flex-wrap gap-4 sm:flex sm:flex-row">
              <TabsList className="w-full space-x-2">
                <TabsTrigger value="general" variant="secondary">
                  General
                </TabsTrigger>
              </TabsList>
            </div>
          </div>

          <div className="h-[calc(100vh-175px)] overflow-y-auto custom-scrollbar pb-5">
            <TabsContent value="general">
              {cookieData ? (
                <div className="mx-auto mt-4 w-full max-w-2xl space-y-4 relative ">
                  <Tag
                    variant={
                      cookieData.cookie_status === "published"
                        ? "active"
                        : cookieData.cookie_status === "archived"
                        ? "inactive"
                        : "draft"
                    }
                    label={cookieData.cookie_status}
                    className="w-24 capitalize absolute right-0"
                  />

                  <div>
                    <span className="text-sm text-subHeading">
                      Cookie Name:
                    </span>
                    <p>{cookieData.cookie_name}</p>
                  </div>

                  <div>
                    <span className="text-sm text-subHeading">Website ID:</span>
                    <p>{cookieData.website_id}</p>
                  </div>
                  <div>
                    <span className="text-sm text-subHeading">Host Name:</span>
                    <p>{cookieData.hostname}</p>
                  </div>
                  <div>
                    <span className="text-sm text-subHeading">Path:</span>
                    <p>{cookieData.path}</p>
                  </div>
                  <div>
                    <span className="text-sm text-subHeading">
                      Description:
                    </span>
                    <p>{cookieData.description}</p>
                  </div>

                  <div className="grid grid-cols-3">
                    <div>
                      <span className="text-sm text-subHeading">Category:</span>
                      <p>{cookieData.category}</p>
                    </div>
                    <div>
                      <span className="text-sm text-subHeading">Source:</span>
                      <p>{cookieData.source}</p>
                    </div>

                    <div>
                      <span className="text-sm text-subHeading">Lifespan:</span>
                      <p>{cookieData.lifespan}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-3">
                    <div>
                      <span className="text-sm text-subHeading">
                        Http Only:
                      </span>
                      <p>{cookieData.http_only}</p>
                    </div>
                    <div>
                      <span className="text-sm text-subHeading">Secure:</span>
                      <p>{cookieData.secure}</p>
                    </div>

                    <div>
                      <span className="text-sm text-subHeading">
                        Is Third Party:
                      </span>
                      <p>{cookieData.is_third_party}</p>
                    </div>
                  </div>

                  <div>
                    <span className="text-sm text-subHeading">Created At:</span>
                    <DateTimeFormatter
                      className="flex flex-row gap-2"
                      dateTime={cookieData.created_at}
                    />
                  </div>

                  <div>
                    <span className="text-sm text-subHeading">Expiry At:</span>
                    <DateTimeFormatter
                      className="flex flex-row gap-2"
                      dateTime={cookieData.expiry}
                    />
                  </div>
                </div>
              ) : (
                <Loader height="h-[calc(100vh-195px)]" />
              )}
            </TabsContent>
          </div>
        </Tabs>
      </div>

      {deleteModalOpen && (
        <DeleteModal
          closeModal={() => setDeleteModalOpen(false)}
          onConfirm={handleDeleteCookie}
          title="Do you want to delete this"
          field="cookie?"
          typeTitle="Cookie"
        />
      )}
    </>
  );
};

export default Page;
