"use client";
import CookieIframe from "@/components/features/cookieManagement/CookieFrame";
import DataTable from "@/components/shared/data-table/DataTable";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import Tag from "@/components/ui/Tag";
import { usePermissions } from "@/contexts/PermissionContext";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { FiPlus } from "react-icons/fi";
import { MdOutlineModeEdit } from "react-icons/md";
import { PiWarningBold } from "react-icons/pi";

const Page = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState("");
  const [cookies, setCookies] = useState([]);
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [loading, setLoading] = useState(false);
  const [buildLoader, setBuildLoader] = useState(false);

  const router = useRouter();
  const params = useParams();
  const websiteId = params?.website_id;

  const [assetDetails, setAssetDetails] = useState({});

  const { canWrite } = usePermissions();

  useEffect(() => {
    if (websiteId) {
      getCookies();
      getOneAsset();
    }
  }, [websiteId, rowsPerPageState, currentPage]);

  const getCookies = async () => {
    setLoading(true);
    try {
      let url = `/cookie/get-all-cookies?website_id=${websiteId}&current_page=${currentPage}&data_per_page=${rowsPerPageState}`;
      const response = await apiCall(url);

      setCookies(response.cookies || []);
      setCurrentPage(response.current_page);
      setTotalPages(response.total_pages);
      setLoading(false);
    } catch (error) {
      toast.error(getErrorMessage(error));
      setLoading(false);
    }
  };

  const getOneAsset = async () => {
    try {
      const response = await apiCall(`/assets/get-asset/${websiteId}`);
      setAssetDetails(response);
    } catch (error) {}
  };

  const handleScanCookies = async () => {
    try {
      const response = await apiCall(
        `/cookie/scan-website-cookies?asset_id=${websiteId}`,
        {
          method: "POST",
        }
      );

      getCookies();

      setAssetDetails({
        ...assetDetails,
        meta_cookies: {
          ...assetDetails.meta_cookies,
          scan_status: "running",
        },
      });
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleBuildCookieBanner = async () => {
    try {
      setBuildLoader(true);
      const response = await apiCall(
        `/cookie/build-widget?asset_id=${websiteId}`,
        {
          method: "POST",
        }
      );

      setBuildLoader(false);
      getOneAsset();
    } catch (error) {
      setBuildLoader(false);
      toast.error(getErrorMessage(error));
    }
  };

  const cookieColumns = [
    {
      header: "Cookie Name",
      accessor: "cookie_name",
      headerClassName: "text-left w-60",
      render: (element) =>
        element ? (
          <div className="text-ellipsis">{element}</div>
        ) : (
          <div>- - -</div>
        ),
    },
    {
      header: "Description",
      accessor: "description",
      headerClassName: "text-left",
      render: (element) =>
        element ? (
          <div className="line-clamp-2 w-96 text-ellipsis">{element}</div>
        ) : (
          <div>- - -</div>
        ),
    },
    {
      header: "Category",
      accessor: "category",
      headerClassName: "text-center",
      render: (element) => (
        <div className="capitalize">{element || "- - -"}</div>
      ),
    },
    {
      header: "Lifespan",
      accessor: "lifespan",
      headerClassName: "text-center",
      render: (element) => <div>{element || "- - -"}</div>,
    },
    {
      header: "Status",
      accessor: "cookie_status",
      headerClassName: "text-center",
      render: (element) => (
        <Tag
          variant={
            element === "published"
              ? "active"
              : element === "archived"
              ? "inactive"
              : "draft"
          }
          label={element}
          className="mx-auto w-24 capitalize"
        />
      ),
    },
    {
      header: "",
      accessor: "cookie_id",
      headerClassName: "text-center",
      render: (element, row) => (
        <div
          className="flex items-center justify-end gap-5 pr-6"
          onClick={(e) => e.stopPropagation()}
        >
          {row?.cookie_status === "draft" && (
            <Button
              variant="icon"
              disabled={!canWrite("/apps/cookie-management")}
              onClick={() =>
                router.push(
                  `/apps/cookie-management/${websiteId}/create-cookie?id=${element}&type=edit`
                )
              }
            >
              <MdOutlineModeEdit size={16} />
            </Button>
          )}
        </div>
      ),
    },
  ];

  const breadcrumbsProps = {
    path: `/apps/cookie-management/cookies`,
    skip: `/apps/`,
  };

  return (
    <>
      <div className="flex justify-between border-b border-borderheader">
        <Header
          title="Cookies"
          subtitle="Manage cookies for this website"
          breadcrumbsProps={breadcrumbsProps}
        />

        <div className="flex items-center justify-center gap-2 pr-6">
          <Button
            onClick={() =>
              router.push(`/apps/cookie-management/${websiteId}/create-cookie`)
            }
            variant="secondary"
            className="hover:none gap-1"
            disabled={!canWrite("/apps/cookie-management")}
          >
            <FiPlus size={18} />
            Add Cookie
          </Button>
        </div>
      </div>
      <Tabs defaultValue="cookies">
        <div className="flex w-full items-center justify-start border-y border-borderSecondary sm:justify-center">
          <div className="flex flex-wrap gap-4 sm:flex sm:flex-row">
            <TabsList className="w-full space-x-12">
              <TabsTrigger value="cookies" variant="secondary">
                Cookies
              </TabsTrigger>
              <TabsTrigger value="banner" variant="secondary">
                Banner
              </TabsTrigger>
            </TabsList>
          </div>
        </div>

        <TabsContent value="cookies">
          {assetDetails?.meta_cookies?.scan_status === "completed" && (
            <DataTable
              tableHeight={"240px"}
              columns={cookieColumns}
              data={cookies}
              loading={loading}
              totalPages={totalPages}
              currentPage={currentPage}
              setCurrentPage={setCurrentPage}
              rowsPerPageState={rowsPerPageState}
              setRowsPerPageState={setRowsPerPageState}
              searchable={false}
              getRowRoute={(row) =>
                row?.cookie_id
                  ? `/apps/cookie-management/${websiteId}/${row.cookie_id}`
                  : null
              }
              illustrationText="No Cookies Available"
              illustrationImage="/assets/illustrations/no-data-find.png"
              noDataText="No Cookie Found"
              noDataImage="/assets/illustrations/no-data-find.png"
            />
          )}
          {!assetDetails?.meta_cookies?.scan_status && !loading && (
            <div className="flex flex-col items-center justify-center gap-4 h-[70vh]">
              <div className="flex flex-col items-center">
                <PiWarningBold size={150} className="text-yellow-500" />
                <div className="max-w-lg text-center">
                  You have not scanned any cookies for this website yet. Click
                  the below button to start scanning.
                </div>
              </div>
              <Button
                variant="secondary"
                onClick={() => {
                  handleScanCookies();
                }}
                disabled={!canWrite("/apps/cookie-management")}
              >
                Scan Cookies
              </Button>
            </div>
          )}
          {assetDetails?.meta_cookies?.scan_status === "running" &&
            !loading && (
              <div className="flex flex-col items-center justify-center gap-4 h-[70vh]">
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 border-4 border-t-transparent rounded-full animate-spin"></div>
                </div>
                <div>Scanning cookies...</div>
              </div>
            )}
        </TabsContent>
        <TabsContent value="banner">
          <div>
            {assetDetails?.meta_cookies?.script_url?.length > 0 ? (
              <div>
                {" "}
                <CookieIframe
                  scriptUrl={assetDetails?.meta_cookies?.script_url}
                />{" "}
              </div>
            ) : (
              <div>
                {!buildLoader ? (
                  <div className="flex flex-col items-center justify-center gap-4 h-[70vh]">
                    <div className="flex flex-col items-center">
                      <PiWarningBold size={150} className="text-yellow-500" />
                      <div className="max-w-lg text-center">
                        You have not build the banner yet. Click the below
                        button to build the banner.
                      </div>
                    </div>
                    <Button
                      variant="secondary"
                      onClick={() => {
                        handleBuildCookieBanner();
                      }}
                    >
                      Build Banner
                    </Button>
                  </div>
                ) : (
                  <div>
                    <div className="flex flex-col items-center justify-center gap-4 h-[70vh]">
                      <div className="flex flex-col items-center">
                        <div className="w-16 h-16 border-4 border-t-transparent rounded-full animate-spin"></div>
                      </div>
                      <div>Building...</div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </>
  );
};

export default Page;
