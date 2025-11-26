"use client";

import { useEffect, useState } from "react";

import { LuCopy } from "react-icons/lu";

import { FaLongArrowAltDown, FaLongArrowAltUp } from "react-icons/fa";
import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Tag from "@/components/ui/Tag";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";
import Header from "@/components/ui/Header";
import DataTable from "@/components/shared/data-table/DataTable";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tab";
import ExpiringConsents from "@/components/features/consentManagement/expiring/ExpiringConsents";

const Page = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState("");
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");

  const [artificatData, setArtifactData] = useState([]);
  const [filterOption, setFilterOption] = useState({});
  const [sortOrder, setSortOrder] = useState("desc");

  const [currentAppliedFilters, setCurrentAppliedFilters] = useState({});

  useEffect(() => {
    getAllConsentArtifacts();
  }, [rowsPerPageState, currentPage, searchQuery, sortOrder]);

  const dataColumn = [
    {
      header: "Agreement Id",
      accessor: "artifact",
      headerClassName: " text-left",
      render: (element) => {
        return (
          <div className="mr-2 flex min-w-32">{element?.agreement_id}</div>
        );
      },
    },
    {
      header: (
        <div
          className="flex cursor-pointer items-center gap-1"
          onClick={() => handleSortChange()}
        >
          <span>Agreement Date</span>
          {sortOrder === "asc" ? <FaLongArrowAltUp /> : <FaLongArrowAltDown />}
        </div>
      ),
      accessor: "artifact",
      render: (element) => {
        return (
          <div className="flex w-36 items-center">
            <DateTimeFormatter
              className="flex gap-1 text-xs"
              dateTime={element?.data_fiduciary?.agreement_date}
            />
          </div>
        );
      },
    },

    {
      header: "Collection Point",
      accessor: "artifact",
      headerClassName: "text-left",
      render: (element, row) => {
        const formattedName = element.cp_name
          ?.replace(/_/g, " ")
          ?.replace(/\b\w/g, (c) => c.toUpperCase());

        return (
          <div className="mr-2 flex truncate text-capitalize">
            {formattedName}
          </div>
        );
      },
    },

    {
      header: "Data Elements",
      accessor: "artifact",
      headerClassName: "text-left",
      render: (element) => {
        return (
          <div className="flex min-w-64 flex-wrap items-center gap-2 py-2 capitalize">
            {element?.consent_scope?.data_elements.length > 3 ? (
              <>
                {element?.consent_scope?.data_elements
                  ?.slice(0, 3)
                  ?.map((dataElement) => (
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
      header: "DP ID",
      accessor: "artifact",
      headerClassName: "text-left",
      render: (element) => {
        if (!element?.data_principal?.dp_id) return null;
        const truncatedId =
          element?.data_principal?.dp_id.length > 25
            ? `${element?.data_principal?.dp_id.slice(0, 10)}...`
            : element?.data_principal?.dp_id;
        const handleCopy = (e) => {
          e.stopPropagation();
          navigator.clipboard.writeText(element?.data_principal?.dp_id);
        };

        if (element?.data_principal?.dp_id.length <= 5) {
          return (
            <div className="flex min-w-32 items-center">
              {element?.data_principal?.dp_id}
            </div>
          );
        }

        return (
          <div className="group flex w-20 items-center space-x-2">
            <span className="truncate">{truncatedId}</span>
            <button
              onClick={handleCopy}
              className="text-blue-500 opacity-0 transition-opacity duration-200 hover:underline focus:outline-none group-hover:opacity-100"
              title="Copy to clipboard"
            >
              <LuCopy />
            </button>
          </div>
        );
      },
    },
    {
      header: "DP email",
      accessor: "artifact",
      headerClassName: "text-left",
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
      headerClassName: "text-left",
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
  ];

  const handleSortChange = () => {
    const newSortOrder = sortOrder === "asc" ? "desc" : "asc";
    setSortOrder(newSortOrder);
    setCurrentPage(1);
  };

  const getAllConsentArtifacts = async (filters) => {
    setLoading(true);
    const page = currentPage === 0 ? 1 : currentPage;

    const {
      cp_names = [],
      purposes = [],
      data_elements = [],
      start_date,
      end_date,
      sort_order,
    } = filters || {};

    const queryParams = new URLSearchParams({
      page: page.toString(),
      limit: rowsPerPageState.toString(),
      search: searchQuery,
      sort_order: sort_order || sortOrder,
    });

    cp_names?.forEach((name) => queryParams.append("cp_names_query", name));
    purposes?.forEach((purpose) =>
      queryParams.append("purposes_query", purpose)
    );
    data_elements?.forEach((element) =>
      queryParams.append("data_elements_query", element)
    );

    if (start_date) queryParams.append("start_date", start_date);
    if (end_date) queryParams.append("end_date", end_date);

    const URL = `/consent-artifact/get-all-consent-artifact?${queryParams.toString()}`;

    try {
      const response = await apiCall(URL);
      setArtifactData(response.consent_data);
      setTotalPages(response.total_pages);
      setCurrentPage(response.current_page);
      setFilterOption(response.filter_options);
      setLoading(false);
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
      setLoading(false);
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const handleApplyFilters = (selectedFilters) => {
    setLoading(true);
    setCurrentPage(1);
    setCurrentAppliedFilters(selectedFilters);
    getAllConsentArtifacts(selectedFilters);
  };

  const filterDetails = [
    {
      name: "cp_names",
      label: "Collection Points",
      options: filterOption?.cp_names?.map((item) => ({
        value: item,
        label: item,
      })),
      isMultiSelect: true,
    },
    {
      name: "purpose_titles",
      label: "Purposes",
      options: filterOption?.purpose_titles?.map((item) => ({
        value: item,
        label: item,
      })),
      isMultiSelect: true,
    },
    {
      name: "data_elements",
      label: "Data Elements",
      options: filterOption?.data_elements?.map((item) => ({
        value: item,
        label: item,
      })),
      isMultiSelect: true,
    },
  ];

  const clearFilter = () => {
    const resetFilters = {};
    filterDetails.forEach((item) => {
      resetFilters[item.name] = item.isMultiSelect ? [] : null;
    });
    getAllConsentArtifacts(resetFilters);
  };

  const handleDownloadCSV = async () => {
    setLoading(true);
    const page = currentPage === 0 ? 1 : currentPage;

    const {
      cp_names = [],
      purposes = [],
      data_elements = [],
      start_date,
      end_date,
      sort_order,
    } = currentAppliedFilters || {};

    const queryParams = new URLSearchParams({
      page: page.toString(),
      limit: rowsPerPageState.toString(),
      search: searchQuery,
      sort_order: sort_order || sortOrder,
    });

    (cp_names || []).forEach((name) =>
      queryParams.append("cp_names_query", name)
    );
    (purposes || []).forEach((purpose) =>
      queryParams.append("purposes_query", purpose)
    );
    (data_elements || []).forEach((element) =>
      queryParams.append("data_elements_query", element)
    );

    if (start_date) queryParams.append("start_date", start_date);
    if (end_date) queryParams.append("end_date", end_date);

    try {
      const response = await apiCall(
        `/consent-artifact/export-csv?${queryParams.toString()}`
      );

      const respText = await response;

      const blob = new Blob([respText], { type: "text/csv" });

      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = "consent_artifacts.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      toast.error(getErrorMessage(error) || "Error downloading CSV");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex">
      <div className="w-full">
        <div className="flex flex-col justify-between gap-4 pr-6 sm:flex-row sm:border-b sm:border-borderheader">
          <Header
            title="Manage your consents"
            subtitle="Manage your consents."
          />
        </div>

        <Tabs defaultValue="consents">
          <div className="flex w-full items-center justify-start border-y border-borderSecondary sm:justify-center">
            <div className="flex flex-wrap gap-4 sm:flex sm:flex-row">
              <TabsList className="w-full space-x-12">
                <TabsTrigger value="consents" variant="secondary">
                  All Consents
                </TabsTrigger>
                <TabsTrigger value="expiring" variant="secondary">
                  Expiring Consents
                </TabsTrigger>
              </TabsList>
            </div>
          </div>

          <TabsContent value="consents">
            <DataTable
              apiSearch={true}
              search={searchQuery}
              setSearch={setSearchQuery}
              onSearch={handleSearch}
              tableHeight={"260px"}
              hasFilterOption={true}
              columns={dataColumn}
              data={artificatData}
              totalPages={totalPages}
              currentPage={currentPage}
              rowsPerPageState={rowsPerPageState}
              setRowsPerPageState={setRowsPerPageState}
              setCurrentPage={setCurrentPage}
              onApplyFilters={handleApplyFilters}
              filterWithDateRange={true}
              clearFilter={clearFilter}
              isFilter={true}
              filterDetails={filterDetails}
              searchable={true}
              hasSerialNumber={true}
              loading={loading}
              getRowRoute={(row) =>
                row?._id ? `/apps/consent-management/${row?._id}` : null
              }
              downloadCSV={true}
              handleDownloadCSV={handleDownloadCSV}
            />
          </TabsContent>
          <TabsContent value="expiring">
            <ExpiringConsents />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Page;
