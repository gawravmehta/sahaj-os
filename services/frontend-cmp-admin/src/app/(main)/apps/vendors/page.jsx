"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { FiPlus } from "react-icons/fi";

import { MdDone } from "react-icons/md";
import { FiEdit2 } from "react-icons/fi";
import { RxCross2 } from "react-icons/rx";

import { getErrorMessage } from "@/utils/errorHandler";
import Tag from "@/components/ui/Tag";
import Header from "@/components/ui/Header";
import Button from "@/components/ui/Button";
import NoDataFound from "@/components/ui/NoDataFound";
import DataTable from "@/components/shared/data-table/DataTable";
import toast from "react-hot-toast";
import { apiCall } from "@/hooks/apiCall";
import { usePermissions } from "@/contexts/PermissionContext";
import { useRouter } from "next/navigation";

const Page = () => {
  const [totalPages, setTotalPages] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [search, setSearch] = useState("");
  const [tableDataRows, setTableDataRows] = useState([]);
  const [isFilter, setIsFilter] = useState(false);
  const [loading, setLoading] = useState(false);

  const { canWrite } = usePermissions();
  const router = useRouter();

  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [filterOptions, setFilterOptions] = useState({
    dpr_country: [],
    dpr_country_risk: [],
    industry: [],
    processing_category: [],
    cross_border: [],
    sub_processor: [],
    audit_result: [],
  });

  const filterDetails = [
    {
      name: "dpr_country",
      label: "Country",
      options: filterOptions?.dpr_country?.map((item) => ({
        value: item,
        label: item,
      })),
    },
    {
      name: "dpr_country_risk",
      label: "Dpr Country Risk",
      options: filterOptions?.dpr_country_risk?.map((item) => ({
        value: item,
        label: item,
      })),
    },
    {
      name: "industry",
      label: "Industry",
      options: filterOptions?.industry?.map((item) => ({
        value: item,
        label: item,
      })),
    },
    {
      name: "processing_category",
      label: "Processing Category",
      options: filterOptions?.processing_category?.map((item) => ({
        value: item,
        label: item,
      })),
    },
    {
      name: "sub_processor",
      label: "Sub Processor",
      options: filterOptions?.sub_processor?.map((item) => ({
        value: item ? "true" : "false",
        label: item ? "True" : "False",
      })),
    },
    {
      name: "audit_result",
      label: "Audit Result",
      options: filterOptions?.audit_result?.map((item) => ({
        value: item,
        label: item,
      })),
    },
    {
      name: "cross_border",
      label: "Cross Border",
      options: filterOptions?.cross_border?.map((item) => ({
        value: item ? "true" : "false",
        label: item ? "True" : "False",
      })),
    },
  ];

  const handleApplyFilters = (selectedFilters) => {
    setIsFilter(true);
    setCurrentPage(1);
    getAllVendors(selectedFilters);
  };
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(search);
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [search]);

  useEffect(() => {
    getAllVendors();
  }, [debouncedQuery, currentPage, rowsPerPageState]);

  const buildApiUrl = (filters = {}) => {
    const params = new URLSearchParams();

    if (filters.dpr_country) params.append("dpr_country", filters.dpr_country);
    if (filters.dpr_country_risk)
      params.append("dpr_country_risk", filters.dpr_country_risk);
    if (filters.industry) params.append("industry", filters.industry);
    if (filters.processing_category)
      params.append("processing_category", filters.processing_category);
    if (filters.audit_result)
      params.append("audit_result", filters.audit_result);

    if (filters.cross_border)
      params.append("cross_border", filters.cross_border);
    if (filters.sub_processor)
      params.append("sub_processor", filters.sub_processor);

    if (search) params.append("search", debouncedQuery);
    params.append("sort_order", "desc");
    params.append("page", currentPage);
    params.append("page_size", rowsPerPageState);

    return `/vendor/get-all-vendors?${params.toString()}`;
  };

  const getAllVendors = async (filters = {}) => {
    setLoading(true);
    try {
      const response = await apiCall(buildApiUrl(filters));

      setTotalPages(response?.pagination?.total_pages);
      setCurrentPage(response?.pagination?.current_page);
      setRowsPerPageState(response?.pagination?.page_size);
      setTableDataRows(response?.vendors);

      if (response?.filter_fields) {
        setFilterOptions({
          dpr_country: response.filter_fields.dpr_country || [],
          dpr_country_risk: response.filter_fields.dpr_country_risk || [],
          industry: response.filter_fields.industry || [],
          processing_category: response.filter_fields.processing_category || [],
          cross_border: response.filter_fields.cross_border || [],
          sub_processor: response.filter_fields.sub_processor || [],
          audit_result: response.filter_fields.audit_result || [],
        });
      }
      setLoading(false);
    } catch (error) {
      setLoading(false);
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  const clearFilter = () => {
    setIsFilter(false);
    getAllVendors();
  };

  const userColumns = [
    {
      header: "Vendor Name",
      accessor: "dpr_name",
      headerClassName: " text-start",
      render: (element, row) => {
        return (
          <div className="min-w-40">
            <div className="flex flex-wrap text-sm text-gray-800 sm:flex sm:flex-nowrap capitalize">
              {element}
            </div>
            <div className="flex flex-wrap text-xs sm:flex sm:flex-nowrap capitalize">
              {row.industry}
            </div>
          </div>
        );
      },
    },

    {
      header: "Country",
      accessor: "dpr_country",
      headerClassName: "text-start",
      render: (element, row) => {
        return (
          <div className="flex min-w-20 flex-wrap sm:flex sm:flex-nowrap capitalize">
            {element}
          </div>
        );
      },
    },

    {
      header: "Processing Category",
      accessor: "processing_category",
      headerClassName: " text-start",
      render: (element, row) => {
        return (
          <div className="flex gap-2">
            {element.map((data, index) => (
              <Tag
                key={index}
                label={data.replace(/_/g, " ")}
                variant="outlineBlue"
                className="capitalize"
              />
            ))}
          </div>
        );
      },
    },

    {
      header: "Cross Border",
      accessor: "cross_border",
      headerClassName: "text-center ",
      render: (element) => {
        return (
          <div className="flex items-center justify-center">
            {!element ? (
              <RxCross2 size={20} className="text-red-600" />
            ) : (
              <MdDone size={25} className="text-green-600" />
            )}
          </div>
        );
      },
    },
    {
      header: "Sub Processor",
      accessor: "sub_processor",
      headerClassName: " text-center",
      render: (element) => {
        return (
          <div className="flex items-center justify-center">
            {!element ? (
              <RxCross2 size={20} className="text-red-600" />
            ) : (
              <MdDone size={25} className="text-green-600" />
            )}
          </div>
        );
      },
    },
    {
      header: "DPA Signed",
      accessor: "dpdpa_compliance_status",
      headerClassName: "text-center ",
      render: (element, row) => {
        return (
          <div className="flex items-center justify-center">
            {!element.signed_dpa ? (
              <RxCross2 size={20} className="text-red-600" />
            ) : (
              <MdDone size={25} className="text-green-600" />
            )}
          </div>
        );
      },
    },
    {
      header: "Contact Person",
      accessor: "contact_person",
      headerClassName: "text-center ",

      render: (element, row) => {
        return (
          <div className="flex items-center justify-center capitalize">
            <p className="">{element.name}</p>
          </div>
        );
      },
    },
    {
      header: "Status",
      accessor: "status",
      headerClassName: "text-center ",

      render: (element, row) => {
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
              className="mx-auto w-24 capitalize"
            />
          </div>
        );
      },
    },
    {
      header: "",
      accessor: "_id",
      headerClassName: "pr-6",
      render: (element, row) =>
        row.status == "draft" && (
          <Button
            variant="icon"
            onClick={(e) => {
              e.stopPropagation();
              router.push(`/apps/vendors/${element}`);
            }}
          >
            <FiEdit2 size={14} className="text-[#8A8A8A]" />
          </Button>
        ),
    },
  ];

  return (
    <div className="flex">
      <div className="h-full w-full">
        <div className="flex flex-col justify-between gap-4 border-b border-borderheader pr-6 sm:flex-row">
          <Header
            title="Vendors"
            subtitle="View, manage, and audit third-party processors handling user data across various purposes."
          />
          <div className="mt-0 flex items-center gap-3.5 sm:mt-2">
            <Button
              variant="secondary"
              className="flex gap-1"
              disabled={!canWrite("/apps/vendors")}
              onClick={() => {
                router.push("/apps/vendors/create-vender");
              }}
            >
              <FiPlus size={18} /> Vendors
            </Button>
          </div>
        </div>
        <div className="">
          {tableDataRows.length === 0 && !loading && !search && !isFilter ? (
            <NoDataFound label="No Vendor Available" />
          ) : (
            <DataTable
              hasFilterOption={true}
              columns={userColumns}
              data={tableDataRows}
              totalPages={totalPages}
              currentPage={currentPage}
              rowsPerPageState={rowsPerPageState}
              setRowsPerPageState={setRowsPerPageState}
              setCurrentPage={setCurrentPage}
              setSearch={setSearch}
              search={search}
              apiSearch={true}
              hasSerialNumber={true}
              tableHeight={"215px"}
              getRowRoute={(row) =>
                row?._id ? `/apps/vendors/details/${row?._id}` : null
              }
              loading={loading}
              isFilter={true}
              clearFilter={clearFilter}
              filterDetails={filterDetails}
              onApplyFilters={handleApplyFilters}
              illustrationText="No Vendor Available"
              illustrationImage="/data-element/business.png"
              noDataText="No Vendor Found"
              noDataImage="/data-element/business.png"
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Page;
