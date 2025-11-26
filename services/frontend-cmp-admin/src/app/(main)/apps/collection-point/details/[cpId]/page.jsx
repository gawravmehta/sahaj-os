"use client";

import ErrorPopup from "@/components/features/collectionPoint/ErrorPopup";
import DataTable from "@/components/shared/data-table/DataTable";
import DeleteModal from "@/components/shared/modals/DeleteModal";
import Button from "@/components/ui/Button";
import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Header from "@/components/ui/Header";
import Loader from "@/components/ui/Loader";
import NoDataFound from "@/components/ui/NoDataFound";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import Tag from "@/components/ui/Tag";
import { usePermissions } from "@/contexts/PermissionContext";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { use, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { BsArrowRight } from "react-icons/bs";
import { LuChevronDown, LuCopy, LuTrash } from "react-icons/lu";

const Page = ({ params }) => {
  const { cpId: cpId } = use(params);
  const [templatesAssets, setTemplatesAssets] = useState([]);
  const [openIndex, setOpenIndex] = useState(null);
  const [loading, setLoading] = useState(false);
  const [createdNoticeHtml, setCreateNoticeHtml] = useState(null);
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState("");
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [deleteCp, setDeleteDp] = useState("");
  const [artificatData, setArtifactData] = useState([]);
  const [cpName, setCpName] = useState("");
  const [errorPopup, setErrorPopup] = useState(null);

  const { canWrite } = usePermissions();

  const breadcrumbsProps = {
    path: `/apps/collection-point/${templatesAssets?.cp_name}`,
    skip: "/apps/",
  };

  const dataColumn = [
    {
      header: "DP System Id",
      accessor: "artifact",
      render: (element) => {
        return (
          <div className="mr-2 flex min-w-32">
            {element?.data_principal?.dp_df_id}
          </div>
        );
      },
    },
    {
      header: "Collection Point",
      accessor: "artifact",
      render: (element, row) => {
        return (
          <div className="mr-2 flex truncate text-ellipsis">
            {element?.cp_name}
          </div>
        );
      },
    },
    {
      header: "Data Elements",
      accessor: "artifact",
      render: (element) => {
        return (
          <div className="flex min-w-64 flex-wrap items-center gap-2 py-2 capitalize">
            {element?.consent_scope?.data_elements.length > 3 ? (
              <>
                {element?.data_elements?.slice(0, 3)?.map((dataElement) => (
                  <div
                    className="flex items-center justify-center gap-2"
                    key={dataElement?.title}
                  >
                    <Tag label={dataElement?.title} variant="lightBlue" />
                  </div>
                ))}
                <div className="flex items-center justify-center gap-2">
                  <span>...</span>
                </div>
              </>
            ) : (
              element?.consent_scope?.data_elements?.map((dataElement) => (
                <div
                  className="flex items-center gap-2"
                  key={dataElement?.title}
                >
                  <Tag label={dataElement?.title} variant="lightBlue" />
                </div>
              ))
            )}
          </div>
        );
      },
    },
    {
      header: "DP Residency",
      accessor: "artifact",
      render: (element) => {
        return (
          <div className="mr-2 flex min-w-32">
            {" "}
            {element?.data_principal?.dp_residency}
          </div>
        );
      },
    },
    {
      header: "DP email",
      accessor: "artifact",
      render: (element) => {
        const email = element?.data_principal?.dp_e ?? "";
        const truncated =
          email.length > 25 ? `${email.slice(0, 10)}...` : email;

        const handleCopy = (e) => {
          e.stopPropagation();
          navigator.clipboard.writeText(email);
        };

        return (
          <div className="group flex w-20 items-center space-x-2">
            <span className="truncate">{truncated}</span>
            {email && (
              <button
                onClick={handleCopy}
                className="text-blue-500 opacity-0 transition-opacity duration-200 hover:underline focus:outline-none group-hover:opacity-100"
                title="Copy to clipboard"
              >
                <LuCopy />
              </button>
            )}
          </div>
        );
      },
    },

    {
      header: "DP mobile",
      accessor: "artifact",
      render: (element) => {
        const mobile = element?.data_principal?.dp_m ?? "";
        const truncated =
          mobile.length > 25 ? `${mobile.slice(0, 10)}...` : mobile;

        const handleCopy = (e) => {
          e.stopPropagation();
          navigator.clipboard.writeText(mobile);
        };

        return (
          <div className="group flex w-20 items-center space-x-2">
            <span className="truncate">{truncated}</span>
            {mobile && (
              <button
                onClick={handleCopy}
                className="text-blue-500 opacity-0 transition-opacity duration-200 hover:underline focus:outline-none group-hover:opacity-100"
                title="Copy to clipboard"
              >
                <LuCopy />
              </button>
            )}
          </div>
        );
      },
    },

    {
      header: "Agreement Date",
      accessor: "artifact",
      render: (element) => {
        return (
          <div className="flex items-center">
            <DateTimeFormatter
              className="flex gap-1 text-xs"
              dateTime={element?.data_fiduciary?.agreement_date}
            />
          </div>
        );
      },
    },
  ];

  const toggle = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  useEffect(() => {
    if (cpId) {
      getCollectionPoint();
    }
  }, []);

  const handleCloseModal = () => {
    setDeleteDp("");
  };

  const getCollectionPoint = async () => {
    try {
      const response = await apiCall(`/cp/get-cp/${cpId}`);
      setCpName(response.cp_name);
      setTemplatesAssets(response);
      setCreateNoticeHtml(response?.notice_html);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleDeleteCP = async () => {
    try {
      await apiCall(`/cp/delete-cp/${cpId}`, {
        method: "DELETE",
      });
      toast.success("Collection point deleted successfully");
      router.push(`/apps/collection-point`);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handlePublishCP = async () => {
    try {
      await apiCall(`/cp/publish-cp/${cpId}`, {
        method: "PATCH",
      });
      setTemplatesAssets((prev) => ({
        ...prev,
        cp_status: "published",
      }));
      toast.success("Collection point published successfully");
    } catch (error) {
      const errData = error?.data?.detail;
      if (errData) {
        setErrorPopup(errData);
      } else {
        toast.error(getErrorMessage(error));
      }
    }
  };

  return (
    <>
      {" "}
      <div className="flex justify-between">
        <Header
          title={`${templatesAssets.cp_name}`}
          breadcrumbsProps={breadcrumbsProps}
        />
        {templatesAssets && (
          <div className="flex items-center justify-center gap-2 pr-6">
            {templatesAssets.cp_status === "draft" && (
              <Button
                onClick={() => handlePublishCP()}
                variant="secondary"
                disabled={!canWrite("/apps/collection-point")}
                className="hover:none gap-1"
              >
                Publish
              </Button>
            )}
            <Button
              onClick={() => setDeleteDp(cpId)}
              variant="delete"
              disabled={!canWrite("/apps/collection-point")}
              className="hover:none gap-1"
            >
              <LuTrash />
              Collection Point
            </Button>
          </div>
        )}
      </div>
      <div>
        <Tabs defaultValue="general">
          <div className="flex w-full items-center justify-start border-y border-borderSecondary sm:justify-center">
            <div className="flex flex-wrap gap-4 sm:flex sm:flex-row">
              <TabsList className="w-full space-x-2">
                <TabsTrigger value="general" variant="secondary">
                  General
                </TabsTrigger>
                <TabsTrigger value="data element" variant="secondary">
                  Data Element
                </TabsTrigger>
                <TabsTrigger value="purpose" variant="secondary">
                  Purpose
                </TabsTrigger>
                <TabsTrigger value="notice" variant="secondary">
                  Notice
                </TabsTrigger>

                <TabsTrigger value="consents" variant="secondary">
                  Consents
                </TabsTrigger>

                <TabsTrigger value="audit" variant="secondary">
                  Audit
                </TabsTrigger>
              </TabsList>
            </div>
          </div>
          <TabsContent value="general">
            <div className="mx-auto mt-4 w-full max-w-2xl space-y-4">
              <div>
                <span className="flex items-center justify-between text-sm text-subHeading">
                  Name:{" "}
                  <span>
                    {" "}
                    <Tag
                      variant={
                        templatesAssets.cp_status == "published"
                          ? "active"
                          : templatesAssets.cp_status == "archived"
                          ? "inactive"
                          : "draft"
                      }
                      label={templatesAssets.cp_status}
                      className="w-24 capitalize"
                    />
                  </span>{" "}
                </span>
                <p>{templatesAssets.cp_name}</p>
              </div>

              <div>
                <span className="flex items-center justify-between  text-sm text-subHeading">
                  Description:{" "}
                </span>
                <p>{templatesAssets.cp_description}</p>
              </div>
              <div>
                <span className="flex items-center justify-between  text-sm text-subHeading">
                  Redirection URL:{" "}
                </span>
                <p>{templatesAssets.redirection_url}</p>
              </div>
              <div>
                <span className="flex items-center justify-between  text-sm text-subHeading">
                  Fallback URL:{" "}
                </span>
                <p>{templatesAssets.fallback_url}</p>
              </div>
              <div>
                <span className="flex items-center justify-between  text-sm text-subHeading">
                  Is Verification Required:{" "}
                </span>
                <p>{templatesAssets.is_verification_required ? "Yes" : "No"}</p>
              </div>
              <div>
                <span className="flex items-center justify-between  text-sm text-subHeading">
                  Verification Done By:{" "}
                </span>
                <p>{templatesAssets.verification_done_by}</p>
              </div>
              <div>
                <span className="flex items-center justify-between  text-sm text-subHeading">
                  Prefered Verification Medium:{" "}
                </span>
                <p>{templatesAssets.prefered_verification_medium}</p>
              </div>
              <div>
                <span className="flex items-center justify-between  text-sm text-subHeading">
                  Notice Popup Window Timeout:{" "}
                </span>
                <p>{templatesAssets.notice_popup_window_timeout}</p>
              </div>

              <div>
                <span className="flex items-center justify-between text-sm text-subHeading">
                  Created At:{" "}
                </span>
                <p>
                  {" "}
                  <DateTimeFormatter
                    className="flex flex-row gap-2"
                    timeClass=""
                    dateTime={templatesAssets.created_at}
                  />{" "}
                </p>
              </div>
            </div>
          </TabsContent>
          <TabsContent value="data element">
            <div className="mx-auto w-full max-w-2xl p-4">
              {templatesAssets?.data_elements?.map((item, index) => (
                <Link
                  href={`/apps/data-element/details/${item.de_id}`}
                  key={item.de_id}
                  className="py-2"
                >
                  <button className="flex w-full items-center justify-between gap-8 border-b border-borderheader px-5 py-2 font-medium text-gray-700 focus:outline-none">
                    <span className="text-heading">{item.de_name}</span>
                    <BsArrowRight className="text-subHeading/60" />
                  </button>
                </Link>
              ))}
            </div>
          </TabsContent>
          <TabsContent value="purpose">
            <div className="mx-auto w-full max-w-2xl p-4">
              {templatesAssets?.data_elements?.map((item, index) => (
                <div key={item?.de_id} className="py-2">
                  <button
                    className="flex w-full items-center gap-8 border-b border-borderheader py-2 font-medium text-gray-700 focus:outline-none"
                    onClick={() => toggle(index)}
                  >
                    <LuChevronDown
                      className={`h-4 w-4 transform transition-transform duration-200 ${
                        openIndex === index ? "rotate-180" : ""
                      }`}
                    />
                    <span className="text-heading">{item.de_name}</span>
                  </button>
                  {openIndex === index && (
                    <div className="mt-2 w-full space-y-1 py-2 text-sm text-subHeading">
                      {item.purposes.map((purpose, i) => (
                        <Link
                          href={`/apps/purpose-management/detail/${purpose?.purpose_id}`}
                          key={purpose.purpose_id}
                          className="relative ml-12 flex items-center border-b border-[#DEDEDE] py-2"
                        >
                          <div>
                            <span>Purpose {1 + i}: </span>
                            <span className="w-full">
                              {" "}
                              {purpose.purpose_title}
                            </span>
                          </div>
                          <BsArrowRight className="absolute right-0 top-1/2 -translate-y-1/2 text-subHeading/60" />
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </TabsContent>
          <TabsContent value="notice">
            <div className="relative mx-auto flex h-[74vh] w-full flex-col items-center justify-center border-2 p-5 shadow-md">
              <div className="custom-scrollbar w-full flex-1 overflow-auto bg-[#F9FCFF]">
                {!loading ? (
                  <div className="h-full w-full">
                    <iframe
                      srcDoc={createdNoticeHtml}
                      className="h-full w-full border-none"
                    />
                  </div>
                ) : (
                  <Loader height="h-full" />
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="consents">
            <div className="-mt-7">
              <DataTable
                apiSearch={true}
                tableHeight={"190px"}
                hasFilterOption={true}
                columns={dataColumn}
                data={artificatData}
                totalPages={totalPages}
                currentPage={currentPage}
                rowsPerPageState={rowsPerPageState}
                setRowsPerPageState={setRowsPerPageState}
                setCurrentPage={setCurrentPage}
                searchable={true}
                hideSearchBar
                hasSerialNumber={true}
                loading={loading}
              />
            </div>
          </TabsContent>

          <TabsContent value="audit">
            <div className="mx-auto w-full max-w-2xl p-4 text-center">
              <NoDataFound height="338px" />
            </div>
          </TabsContent>
        </Tabs>
      </div>
      {errorPopup && (
        <ErrorPopup
          errorData={errorPopup}
          onClose={() => setErrorPopup(null)}
          onSaveDraft={() => setErrorPopup(null)}
        />
      )}
      {deleteCp && (
        <DeleteModal
          closeModal={handleCloseModal}
          onConfirm={handleDeleteCP}
          title=" Do you want to delete this"
          field=" Collection Point?"
          typeTitle="Collection Point"
        />
      )}
    </>
  );
};

export default Page;
