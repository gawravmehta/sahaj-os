"use client";

import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Header from "@/components/ui/Header";
import Skeleton from "@/components/ui/Skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import Tag from "@/components/ui/Tag";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import InvalidIdWrapper, { isValidObjectId } from "@/utils/helperFunctions";
import { useParams, useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";

import toast from "react-hot-toast";

const Page = () => {
  const params = useParams();

  const [verification, setVerification] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (isValidObjectId(params.id)) {
      fetchVerification();
    }
  }, [params.id]);

  const fetchVerification = async () => {
    setLoading(true);
    try {
      const response = await apiCall(
        `/consent-validation/get-one-verification-log?request_id=${params.id}`
      );

      setLoading(false);
      setVerification(response);
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage || "Failed to fetch purposes");
    } finally {
      setLoading(false);
    }
  };

  const breadcrumbsProps = {
    path: `/apps/consent-validation/${verification?.request_id}`,
    skip: "/apps/",
  };

  const getDisplayValue = (value) => {
    if (value === null || value === undefined || value === "") return "N/A";
    return value;
  };

  return (
    <InvalidIdWrapper id={params.id}>
      <div className="border-border flex flex-col justify-between gap-4 border-b pr-6 sm:flex-row">
        <Header title={`Consent details`} breadcrumbsProps={breadcrumbsProps} />
      </div>

      <Tabs defaultValue="general">
        <div className="flex w-full items-center justify-center border-b border-t border-borderheader">
          <TabsList className={"gap-36"}>
            <TabsTrigger value="general" variant="secondary">
              General
            </TabsTrigger>
            <TabsTrigger value="scope" variant="secondary">
              Scope
            </TabsTrigger>
          </TabsList>
        </div>
        <TabsContent value="general">
          <div className="mx-auto mt-4 w-full max-w-2xl space-y-4">
            <div>
              <span className="flex items-center justify-between text-sm text-subHeading">
                request id:{" "}
                <span>
                  <Tag
                    variant={
                      verification?.status === "successful"
                        ? "active"
                        : "inactive"
                    }
                    label={getDisplayValue(verification?.status)}
                    className="w-24 capitalize"
                  />
                </span>
              </span>
              {!loading ? (
                <p>{getDisplayValue(verification?.request_id)}</p>
              ) : (
                <Skeleton variant="single" className={"h-4 w-28"} />
              )}
            </div>

            <div>
              <span className="flex items-center justify-between text-sm text-subHeading">
                df id:
              </span>
              {!loading ? (
                <p>{getDisplayValue(verification?.df_id)}</p>
              ) : (
                <Skeleton variant="single" className={"h-4 w-28"} />
              )}
            </div>

            <div>
              <span className="flex items-center justify-between text-sm text-subHeading">
                dp id:
              </span>
              {!loading ? (
                <p>{getDisplayValue(verification?.dp_id)}</p>
              ) : (
                <Skeleton variant="single" />
              )}
            </div>

            <div>
              <span className="flex items-center justify-between text-sm text-subHeading">
                dp system id:
              </span>
              {!loading ? (
                <p>{getDisplayValue(verification?.dp_system_id)}</p>
              ) : (
                <Skeleton variant="single" className={"h-4 w-64"} />
              )}
            </div>

            <div>
              <span className="flex items-center justify-between text-sm text-subHeading">
                dp_e:
              </span>
              {!loading ? (
                <p>{getDisplayValue(verification?.dp_e)}</p>
              ) : (
                <Skeleton variant="single" className={"h-4 w-28"} />
              )}
            </div>

            <div>
              <span className="flex items-center justify-between text-sm text-subHeading">
                dp_m:
              </span>
              {!loading ? (
                <p>{getDisplayValue(verification?.dp_m)}</p>
              ) : (
                <Skeleton variant="single" className={"h-4 w-28"} />
              )}
            </div>

            <div>
              <span className="flex items-center justify-between text-sm text-subHeading">
                internal_external:
              </span>
              {!loading ? (
                <p>{getDisplayValue(verification?.internal_external)}</p>
              ) : (
                <Skeleton variant="single" className={"h-4 w-28"} />
              )}
            </div>

            <div>
              <span className="flex items-center justify-between text-sm text-subHeading">
                Created At:
              </span>
              {!loading ? (
                <DateTimeFormatter
                  className="flex flex-row gap-2"
                  timeClass=""
                  dateTime={getDisplayValue(verification?.timestamp)}
                />
              ) : (
                <Skeleton variant="single" className={"h-4 w-full"} />
              )}
            </div>
          </div>
        </TabsContent>

        <TabsContent value="scope">
          <div className="mx-auto mt-4 w-full max-w-2xl space-y-4">
            <div>
              <span className="text-sm text-subHeading">Purpose Title:</span>
              <p>{getDisplayValue(verification?.scope?.purpose_title)}</p>
            </div>
            <div>
              <span className="text-sm text-subHeading">Purpose ID:</span>
              <p>{getDisplayValue(verification?.scope?.purpose_id)}</p>
            </div>
            <div>
              <span className="text-sm text-subHeading">Data Elements:</span>
              <div className="flex flex-wrap gap-2">
                {verification?.scope?.data_element_titles?.length > 0 ? (
                  verification.scope.data_element_titles.map((item, idx) => (
                    <Tag
                      key={idx}
                      variant="outlineBlue"
                      label={getDisplayValue(item)}
                    />
                  ))
                ) : (
                  <p>N/A</p>
                )}
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </InvalidIdWrapper>
  );
};

export default Page;
