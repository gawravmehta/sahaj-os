"use client";
import DataTable from "@/components/shared/data-table/DataTable";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import NoDataFound from "@/components/ui/NoDataFound";
import Tag from "@/components/ui/Tag";
import { usePermissions } from "@/contexts/PermissionContext";
import { apiCall } from "@/hooks/apiCall";
import { useDebounce } from "@/hooks/useDebounce";
import { getErrorMessage } from "@/utils/errorHandler";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { FiPlus } from "react-icons/fi";
import { MdOutlineModeEdit } from "react-icons/md";

const Page = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState("");
  const [dpData, setDpData] = useState([]);
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [loading, setLoading] = useState(true);
  const [isFilter, setIsFilter] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const debouncedSearchPurpose = useDebounce(searchQuery, 500);

  const { canWrite } = usePermissions();
  const router = useRouter();

  useEffect(() => {
    getAllDataPurpose();
  }, [rowsPerPageState, currentPage, debouncedSearchPurpose]);

  const userColumns = [
    {
      header: "Statement",
      accessor: "purpose_title",
      headerClassName: " w-96 text-left",
      render: (element, row) => {
        return (
          <div className="mr-2 w-72 overflow-hidden truncate text-ellipsis whitespace-nowrap">
            {element}
          </div>
        );
      },
    },
    {
      header: "Data Element",
      accessor: "data_elements",
      headerClassName: "w-96 text-left",
      render: (element) => {
        return (
          <div className="flex min-w-64 flex-wrap items-center gap-2 py-2 capitalize">
            {element?.length < 1 ? (
              <p className="">- - - - - - - </p>
            ) : element?.length > 3 ? (
              <>
                {element.slice(0, 3).map((dataElement) => (
                  <div
                    className="flex items-center justify-center gap-2"
                    key={dataElement.de_id}
                  >
                    <Tag label={dataElement.de_name} variant="outlineBlue" />
                  </div>
                ))}
                <div className="flex items-center justify-center gap-2">
                  <span>...</span>
                </div>
              </>
            ) : (
              element?.map((dataElement) => (
                <div
                  className="flex items-center gap-2"
                  key={dataElement.de_id}
                >
                  <Tag label={dataElement.de_name} variant="outlineBlue" />
                </div>
              ))
            )}
          </div>
        );
      },
    },
    {
      header: "Category",
      accessor: "purpose_category",
      headerClassName: "w-72  text-center",
      render: (element) => {
        const formatted = element
          ?.replace(/_/g, " ")
          ?.replace(/\b\w/g, (char) => char?.toUpperCase());

        return formatted ? (
          <p className="text-center text-nowrap">{formatted}</p>
        ) : (
          <p className="text-center">- - - - - -</p>
        );
      },
    },

    {
      header: "Priority",
      accessor: "purpose_priority",
      headerClassName: "text-center w-20",
      render: (element) => {
        return (
          <div className="flex items-center justify-center">
            {element && (
              <div
                className={`flex h-7 w-7 items-center justify-center rounded-full capitalize ${
                  element.toLowerCase() === "medium"
                    ? "bg-[#FEF7DE] text-[#a18c00]"
                    : element.toLowerCase() === "low"
                    ? "bg-[#E0FFE7] text-[#06a42a]"
                    : element.toLowerCase() === "high"
                    ? "bg-[#FBEAEA] text-[#d94e4e]"
                    : ""
                }`}
              >
                {(element.toLowerCase() === "medium" && "m") ||
                  (element.toLowerCase() === "low" && "l") ||
                  (element.toLowerCase() === "high" && "h")}
              </div>
            )}
          </div>
        );
      },
    },
    {
      header: "Time Period",
      accessor: "consent_time_period",
      headerClassName: "w-56 text-center",
      render: (element) => {
        return <p className="text-center">{element}</p>;
      },
    },

    {
      header: "Status",
      accessor: "purpose_status",
      headerClassName: "text-center w-32",

      render: (element) => {
        return (
          <div className="flex items-center justify-center">
            <Tag
              variant={
                element == "published"
                  ? "active"
                  : element == "archived"
                  ? "inactive"
                  : "draft"
              }
              label={element}
              className="mx-auto w-20 capitalize tracking-wide"
            />
          </div>
        );
      },
    },

    {
      header: "",
      accessor: "purpose_id",
      headerClassName: "",
      tableDataClassName: "w-10",
      render: (element, row) => {
        return (
          row.purpose_status != "published" && (
            <Button
              variant="icon"
              onClick={(e) => {
                e.stopPropagation();
                router.push(`/apps/purpose-management/${element}`);
              }}
              disabled={!canWrite("/apps/purpose-management")}
              className={"gap-5 px-6"}
            >
              <MdOutlineModeEdit size={16} />
            </Button>
          )
        );
      },
    },
  ];

  const filterDefinitions = [
    {
      name: "status",
      label: "State",
      options: [
        { value: "draft", label: "Draft" },
        { value: "publish", label: "Publish" },
      ],
    },
    {
      name: "priority",
      label: "Priority",
      options: [
        { value: "high", label: "High" },
        { value: "low", label: "Low" },
        { value: "medium", label: "Medium" },
      ],
    },
  ];

  const getAllDataPurpose = async (filters = {}) => {
    const page = currentPage === 0 ? 1 : currentPage;
    let URL = `/purposes/get-all-purposes?current_page=${page}&data_per_page=${rowsPerPageState}`;

    if (filters) {
      const filterQuery = Object.entries(filters)
        .filter(([key, value]) => value !== null && value !== "")
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join("&");

      if (filterQuery) {
        URL += `&${filterQuery}`;
      }
    }

    try {
      const response = await apiCall(URL);
      setDpData(response.purposes);
      setTotalPages(response.total_pages);
      setCurrentPage(response.current_page);
      setLoading(false);
    } catch (error) {
      console.error("Error in get purpose:", error);
      const message = getErrorMessage(error);
      toast.error(message);
      setLoading(false);
    }
  };

  const handleApplyFilters = (selectedFilters) => {
    setIsFilter(true);
    setLoading(true);
    setCurrentPage(1);

    getAllDataPurpose(selectedFilters);
  };

  const clearFilter = (shouldReload = true) => {
    setIsFilter(false);
    if (shouldReload) {
      getAllDataPurpose();
    }
  };

  return (
    <div className="flex">
      <div className="w-full">
        <div className="flex flex-col justify-between gap-4 pr-6 sm:flex-row sm:border-b sm:border-borderheader">
          <Header
            title="Purpose Management"
            subtitle="Manage purposes for consent governance and data protection compliance."
          />

          <div className="mt-2 flex items-center gap-3.5">
            <Link href="/apps/purpose-management/consent-directory">
              <Button variant="secondary" className="text-nowrap">
                Consent Directory
              </Button>
            </Link>
            <Link href="/apps/purpose-management/create">
              <Button
                variant="secondary"
                disabled={!canWrite("/apps/purpose-management")}
                className="flex gap-1 text-nowrap"
              >
                <FiPlus className="text-lg" /> Purpose
              </Button>
            </Link>
          </div>
        </div>
        {dpData?.length === 0 && !loading && searchQuery?.length < 1 ? (
          <NoDataFound height={"145px"} label="No Purpose Available" />
        ) : (
          <DataTable
            tableHeight={"213px"}
            columns={userColumns}
            data={dpData}
            loading={loading}
            totalPages={totalPages}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            rowsPerPageState={rowsPerPageState}
            setRowsPerPageState={setRowsPerPageState}
            setSearch={setSearchQuery}
            search={searchQuery}
            isFilter={true}
            clearFilter={clearFilter}
            filterDetails={filterDefinitions}
            onApplyFilters={handleApplyFilters}
            searchable={true}
            getRowRoute={(row) =>
              row?.purpose_id
                ? `/apps/purpose-management/detail/${row?.purpose_id}`
                : null
            }
          />
        )}
      </div>
    </div>
  );
};

export default Page;
