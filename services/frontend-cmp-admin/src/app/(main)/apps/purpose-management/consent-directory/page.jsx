"use client";

import DataTable from "@/components/shared/data-table/DataTable";
import Header from "@/components/ui/Header";
import Tag from "@/components/ui/Tag";
import { apiCall } from "@/hooks/apiCall";
import { useDebounce } from "@/hooks/useDebounce";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { MdOutlineContentCopy } from "react-icons/md";
import IndustryModal from "@/components/features/purposeManagement/consentDirectory/IndustryModal";
import { industryOptions } from "@/constants/industryOptions";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";
import Button from "@/components/ui/Button";
import { usePermissions } from "@/contexts/PermissionContext";

const page = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState();
  const [directory, setDirectory] = useState([]);
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [loading, setLoading] = useState(false);
  const [selectedIndustry, setSelectedIndustry] = useState("");
  const [showModal, setShowModal] = useState(false);
  const searchParams = useSearchParams();

  const initialQuery = searchParams.get("query") || "";
  const [searchable, setSearchable] = useState(initialQuery);
  const debouncedSearchPurpose = useDebounce(searchable, 500);

  const { canWrite } = usePermissions();

  const breadcrumbsProps = {
    path: `/apps/purpose-management/consent-directory`,
    skip: "/apps",
  };

  useEffect(() => {
    getAllDataPrincipals();
  }, [rowsPerPageState, currentPage, debouncedSearchPurpose]);

  const getAllDataPrincipals = async (filters = {}) => {
    setLoading(true);

    const page = currentPage === 0 ? 1 : currentPage;
    let URL = `/purposes/templates?current_page=${page}&data_per_page=${rowsPerPageState}`;

    if (searchable?.length > 0) {
      URL += `&query=${encodeURIComponent(searchable)}`;
    }

    if (filters) {
      const filterQuery = Object.entries(filters)
        .filter(([key, value]) => value !== null && value !== "")
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join("&");

      if (filterQuery) {
        URL += `&${filterQuery}`;
      }
    }

    if (filters && Object.keys(filters).length > 0) {
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
      setTotalPages(response.total_pages);
      setDirectory(response.purposes);
      setCurrentPage(response.current_page);
    } catch (error) {
      console.error("Error fetching data principals:", error);
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const userColumns = [
    {
      header: "Industry",
      accessor: "industry",
      headerClassName: "w-32 text-left",
      render: (element) => (
        <div className="flex items-center">
          <span className="truncate max-w-[120px]">{element}</span>
        </div>
      ),
    },
    {
      header: "Category",
      accessor: "sub_category",
      headerClassName: "w-32 text-left",
      render: (element) => (
        <div className="flex items-center">
          <span className="truncate max-w-[120px]">{element}</span>
        </div>
      ),
    },
    {
      header: "Purpose",
      accessor: "translations",
      headerClassName: "w-56 text-left",
      render: (element) => (
        <div className="flex">
          <span className="line-clamp-2 items-center w-56 ">
            {element["eng"] || element["en"]}
          </span>
        </div>
      ),
    },
    {
      header: "Data Element",
      accessor: "data_elements",
      headerClassName: "w-52 text-left",
      render: (element) => (
        <div className="flex min-w-[200px] flex-wrap items-center gap-2 py-2 capitalize">
          {element?.length > 2 ? (
            <>
              {element?.slice(0, 3)?.map((dataElement, index) => (
                <div className="flex items-center gap-2" key={index}>
                  <Tag variant="outlineBlue" label={dataElement} />
                </div>
              ))}
              <span className="text-gray-500">...</span>
            </>
          ) : (
            element?.map((dataElement, index) => (
              <div className="flex items-center gap-2" key={index}>
                <Tag variant="outlineBlue" label={dataElement} />
              </div>
            ))
          )}
        </div>
      ),
    },
    {
      header: "Usage Count",
      accessor: "usage_count",
      headerClassName: "w-32 text-center",
      render: () => (
        <div className="flex items-center justify-center capitalize">
          {Math.floor(Math.random() * (10000 - 1000 + 1)) + 1000}
        </div>
      ),
    },
    {
      header: "",
      accessor: "purpose_id",
      headerClassName: "w-16 text-center",
      render: (element) => (
        <div onClick={(e) => e.stopPropagation()}>
          <Button
            variant="icon"
            onClick={() =>
              setShowModal(
                directory.filter((item) => item.purpose_id === element)
              )
            }
            disabled={!canWrite("/apps/purpose-management")}
          >
            <MdOutlineContentCopy size={16} />
          </Button>
        </div>
      ),
    },
  ];

  const industryDropdownOptions = useMemo(() => {
    return Object.keys(industryOptions).map((industry) => ({
      value: industry,
      label: industry,
    }));
  }, []);

  const subCategoryDropdownOptions = useMemo(() => {
    if (!selectedIndustry) return [];
    return industryOptions[selectedIndustry].map((sub) => ({
      value: sub,
      label: sub,
    }));
  }, [selectedIndustry]);

  const filterDefinitions = [
    {
      name: "industry",
      label: "Industry",
      options: industryDropdownOptions,
      onChange: (value) => {
        setSelectedIndustry(value);
      },
    },
    {
      name: "sub_category",
      label: "Sub Category",
      options: subCategoryDropdownOptions,
    },
  ];

  const handleApplyFilters = (selectedFilters) => {
    setLoading(true);
    setCurrentPage(1);
    getAllDataPrincipals(selectedFilters);
  };

  const clearFilter = () => {
    setLoading(true);
    setCurrentPage(1);
    getAllDataPrincipals({});
  };

  return (
    <div className="flex">
      <div className="w-full">
        <div className="flex flex-col justify-between gap-4 pr-6 sm:flex-row sm:border-b sm:border-borderheader">
          <Header
            title="Consent Directory"
            breadcrumbsProps={breadcrumbsProps}
            subtitle="Directory of consent purposes that can be copied to create new purposes."
          />
        </div>
        <div className="text-left">
          <DataTable
            tableHeight={"240px"}
            columns={userColumns}
            data={directory}
            loading={loading}
            totalPages={totalPages}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            rowsPerPageState={rowsPerPageState}
            setRowsPerPageState={setRowsPerPageState}
            setSearch={setSearchable}
            search={searchable}
            isFilter={true}
            clearFilter={clearFilter}
            filterDetails={filterDefinitions}
            onApplyFilters={handleApplyFilters}
            getRowRoute={(row) =>
              row?.purpose_id
                ? `/apps/purpose-management/consent-directory/${
                    row?.purpose_id
                  }?page=${currentPage}&query=${encodeURIComponent(searchable)}`
                : null
            }
          />
        </div>
        {showModal && (
          <IndustryModal showModal={showModal} setShowModal={setShowModal} />
        )}
      </div>
    </div>
  );
};

export default page;
