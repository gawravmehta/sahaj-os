"use client";
import Link from "next/link";
import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import { useEffect, useState } from "react";
import { FiPlus } from "react-icons/fi";
import toast from "react-hot-toast";
import Tag from "@/components/ui/Tag";
import { apiCall } from "@/hooks/apiCall";
import Header from "@/components/ui/Header";
import Button from "@/components/ui/Button";
import { getErrorMessage } from "@/utils/errorHandler";
import DataTable from "@/components/shared/data-table/DataTable";
import { usePermissions } from "@/contexts/PermissionContext";
import { useRouter } from "next/navigation";

const Page = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [rowsPerPageState, setRowsPerPageState] = useState(10);
  const [incomingData, setIncomingData] = useState([]);
  const [filterOptions, setFilterOptions] = useState({ type: [], status: [] });
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [isFilter, setIsFilter] = useState(false);
  const [activeFilters, setActiveFilters] = useState({});

  const { canWrite } = usePermissions();
  const router = useRouter();

  useEffect(() => {
    const timeout = setTimeout(() => setDebouncedSearch(searchQuery), 500);
    return () => clearTimeout(timeout);
  }, [searchQuery]);

  const userColumns = [
    {
      header: "Core Identifier",
      accessor: "core_identifier",
      headerClassName: "text-start",
      render: (element) => <div className="w-40">{element}</div>,
    },
    {
      header: "Secondary Identifier",
      accessor: "secondary_identifier",
      headerClassName: "text-start",
      render: (element) => <div>{element}</div>,
    },

    {
      header: "Request Type",
      accessor: "dp_type",
      headerClassName: " text-start",
      render: (element) => <div className="capitalize">{element}</div>,
    },
    {
      header: "Created At",
      accessor: "created_timestamp",
      headerClassName: " text-start",
      render: (element) => (
        <div className="flex w-24">
          <DateTimeFormatter dateTime={element} className="text-gray-50" />
        </div>
      ),
    },
    {
      header: "Last Updated",
      accessor: "last_updated",
      headerClassName: "text-start",
      render: (element) => (
        <div className="flex w-24">
          <DateTimeFormatter dateTime={element} />
        </div>
      ),
    },
    {
      header: "Deadline",
      accessor: "deadline",
      headerClassName: "text-start",
      render: (element) => (
        <div className="flex w-24">
          <DateTimeFormatter dateTime={element} />
        </div>
      ),
    },

    {
      header: "Status",
      accessor: "status",
      headerClassName: " ",
      render: (val) => (
        <div className=" ">
          <div className="flex items-center justify-center">
            <Tag
              label={val === "in_progress" ? "in progress" : val}
              variant={
                val === "completed"
                  ? "active"
                  : val === "new"
                    ? "active"
                    : val === "in_progress"
                      ? "suspended"
                      : val === "rejected"
                        ? "inactive"
                        : "suspended"
              }
              className="text-xs capitalize"
            />
          </div>
        </div>
      ),
    },
  ];

  const filterDetails = [
    {
      name: "dp_type",
      label: "DP Type",
      options: [
        { label: "consumer", value: "consumer" },
        { label: "employee", value: "employee" },
        { label: "vendor", value: "vendor" },
      ],
    },
  ];

  const fetchIncoming = async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      params.append("page", currentPage);
      params.append("page_size", rowsPerPageState);

      const activeFiltersToUse = Object.keys(filters).length
        ? filters
        : activeFilters;

      if (activeFiltersToUse?.status)
        params.append("status", activeFiltersToUse.status);
      if (activeFiltersToUse?.dp_type)
        params.append("dp_type", activeFiltersToUse.dp_type);
      if (activeFiltersToUse?.created_from)
        params.append("created_from", activeFiltersToUse.created_from);
      if (activeFiltersToUse?.created_to)
        params.append("created_to", activeFiltersToUse.created_to);

      const response = await apiCall(`/dpar/get_all?${params.toString()}`);

      setIncomingData(response?.data || []);
      setTotalPages(response?.pagination?.total_pages || 1);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleApplyFilters = (selected) => {
    setActiveFilters(selected);
    setIsFilter(true);
    setCurrentPage(1);
    fetchIncoming(selected);
  };

  const clearFilter = () => {
    setActiveFilters({});
    setIsFilter(false);
    fetchIncoming({});
  };

  useEffect(() => {
    fetchIncoming();
  }, [currentPage, rowsPerPageState, debouncedSearch]);

  return (
    <div className="w-full">
      <div className="flex items-center justify-between border-b border-borderheader pr-6">
        <Header
          title="Incoming"
          subtitle="List of incoming Data Principal Access Requests"
        />

      </div>

      <DataTable
        tableHeight="213px"
        columns={userColumns}
        data={incomingData}
        totalPages={totalPages}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        rowsPerPageState={rowsPerPageState}
        setRowsPerPageState={setRowsPerPageState}
        isFilter={true}
        clearFilter={clearFilter}
        filterDetails={filterDetails}
        onApplyFilters={handleApplyFilters}
        getRowRoute={(row) => `/apps/dpar/${row._id}`}
        illustrationText="No Incoming Request Available"
        illustrationImage="/assets/illustrations/no-data-find.png"
        noDataText="No Data Found"
        noDataImage="/assets/illustrations/no-data-find.png"
      />
    </div>
  );
};

export default Page;
