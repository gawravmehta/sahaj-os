"use client";

import DataTable from "@/components/shared/data-table/DataTable";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { getLanguageLabel } from "@/utils/helperFunctions";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import { LuCopy } from "react-icons/lu";
import { HiDownload } from "react-icons/hi";
import { MdAdd, MdDone, MdOutlineModeEdit, MdUploadFile } from "react-icons/md";
import { RxCross2 } from "react-icons/rx";
import ExportModal from "../../../../components/features/principalManagement/ExportModal";
import { IoMdAdd } from "react-icons/io";
import { AiOutlineDelete } from "react-icons/ai";
import { RiArrowDropDownLine } from "react-icons/ri";
import { usePermissions } from "@/contexts/PermissionContext";
import { useRouter } from "next/navigation";

const Page = () => {
  const router = useRouter();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState("");
  const [dpData, setDpData] = useState([]);
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [showExportModal, setShowExportModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [isIntroRunning, setIsIntroRunning] = useState(false);
  const [totalPrincipals, setTotalPrincipals] = useState(0);
  const [filterOption, setFilterOption] = useState({});
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [isFilter, setIsFilter] = useState(false);

  const { canWrite } = usePermissions();

  const handleCopy = (element, text) => {
    navigator.clipboard.writeText(element).then(() => {
      setCopied(element);
      toast.success(`${text} copied Successfully`);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  const toggleDropdown = () => setDropdownOpen(!dropdownOpen);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target) &&
        !event.target.closest(".user-toggle-button")
      ) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isIntroRunning]);

  useEffect(() => {
    getAllDataPrincipals();
  }, [currentPage, rowsPerPageState, debouncedSearch]);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [search]);

  const getAllDataPrincipals = async (filters) => {
    setLoading(true);
    try {
      let pageParam =
        Number.isInteger(Number(currentPage)) && Number(currentPage) >= 1
          ? Number(currentPage)
          : 1;

      let url = `/data-principal/get-all-data-principals?page=${pageParam}&limit=${rowsPerPageState}`;

      if (debouncedSearch) {
        url += `&search=${encodeURIComponent(debouncedSearch)}`;
      }

      if (filters) {
        const filterQuery = Object.entries(filters)
          .filter(([key, value]) => value !== null && value !== "")
          .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
          .join("&");

        if (filterQuery) {
          url += `&${filterQuery}`;
        }
      }

      const response = await apiCall(url, { method: "GET" });

      setTotalPages(response.totalPages);
      setDpData(response.dataPrincipals);
      setTotalPrincipals(response.totalPrincipals);
      setFilterOption(response.available_options);
    } catch (error) {
      console.error("Error in adding data principal:", error);
      const message = getErrorMessage(error);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };
  const capitalizeWords = (str) =>
    str.replace(/\b\w/g, (char) => char.toUpperCase());

  const closeModal = () => {
    setShowExportModal(false);
  };

  const userColumns = [
    {
      header: "DP ID",
      accessor: "dp_id",
      headerClassName: " text-left w-40 ",
      render: (element) => {
        return (
          <div
            className="group flex cursor-default items-center space-x-2"
            onClick={(e) => e.stopPropagation()}
          >
            <span>{element.slice(0, 8)}</span>
            <button
              onClick={() => handleCopy(element, "ID")}
              className="relative text-sm text-blue-500 opacity-0 hover:underline focus:outline-none group-hover:opacity-100"
            >
              <LuCopy />
            </button>
          </div>
        );
      },
    },

    {
      header: "Email",
      accessor: "dp_email",
      headerClassName: " text-left",
      render: (element) => {
        const hasData = Array.isArray(element) && element.length > 0;

        return (
          <div
            className="group mr-2 flex cursor-default"
            onClick={(e) => e.stopPropagation()}
          >
            <span className="flex flex-col">
              {[...(hasData ? element.slice(0, 2) : [])]
                .reverse()
                .map((item, index) => (
                  <span
                    key={index}
                    className={`${index === 0 && "font-semibold"}`}
                  >
                    {item}
                  </span>
                ))}
            </span>

            {hasData ? (
              <button
                onClick={() => handleCopy(element, "Email")}
                className="ml-1 text-sm text-blue-500 opacity-0 hover:underline focus:outline-none group-hover:opacity-100"
              >
                <LuCopy />
              </button>
            ) : (
              <span className="ml-2 text-sm text-gray-400">-</span>
            )}
          </div>
        );
      },
    },
    {
      header: "Mobile",
      accessor: "dp_mobile",
      headerClassName: "text-center",
      render: (element) => {
        const hasData = Array.isArray(element) && element.length > 0;

        return (
          <div className="mx-2 flex flex-col items-center justify-center gap-0.5">
            {hasData ? (
              [...element.slice(0, 2)].reverse().map((item, index) => (
                <span
                  key={index}
                  className={`${index === 0 && "font-semibold"}`}
                >
                  {item}
                </span>
              ))
            ) : (
              <span className="text-sm text-gray-400"> - </span>
            )}
          </div>
        );
      },
    },
    {
      header: "Country",
      accessor: "dp_country",
      headerClassName: "text-center w-40",
      render: (element) => {
        return (
          <div className="flex items-center justify-center capitalize">
            {element}
          </div>
        );
      },
    },
    {
      header: "State",
      accessor: "dp_state",
      headerClassName: "text-center w-40",
      render: (element) => {
        const formattedState = element ? element.replace(/-/g, " ") : "-";
        return (
          <div className="flex flex-nowrap items-center justify-center capitalize">
            {formattedState || <span className="text-sm text-gray-400">-</span>}
          </div>
        );
      },
    },
    {
      header: "Language",
      accessor: "dp_preferred_lang",
      headerClassName: "text-center w-44",
      render: (element) => {
        return (
          <div className="flex items-center justify-center">
            <span className="text-center capitalize">
              {getLanguageLabel(element)}
            </span>
          </div>
        );
      },
    },
    {
      header: "Legacy",
      accessor: "is_legacy",
      headerClassName: "text-center",
      render: (element) => {
        return (
          <div className="flex items-center justify-center">
            {element == 0 ? (
              <RxCross2 size={20} className="text-red-600" />
            ) : (
              <MdDone size={25} className="text-green-600" />
            )}
          </div>
        );
      },
    },
    {
      header: "Consents",
      accessor: "consent_count",
      headerClassName: "text-center w-36",
      render: (element) => {
        return (
          <div className="flex items-center justify-center">{element}</div>
        );
      },
    },
    {
      header: "",
      accessor: "dp_id",
      headerClassName: " text-center w-16",
      render: (element) => {
        return (
          <Button
            variant="icon"
            onClick={(e) => {
              e.stopPropagation();
              router.push(`/apps/principal-management/${element}`);
            }}
            disabled={!canWrite("/apps/principal-management")}
          >
            <MdOutlineModeEdit size={16} />
          </Button>
        );
      },
    },
  ];

  const filterDetails = [
    {
      name: "dp_country",
      label: "Country",
      options: filterOption?.dp_country?.map((item) => ({
        value: item,
        label: item,
      })),
    },
    {
      name: "consent_status",
      label: "Added Through",
      options: filterOption?.consent_status?.map((item) => ({
        value: item,
        label: item,
      })),
    },
    {
      name: "dp_preferred_lang",
      label: "Language",
      options: filterOption?.dp_preferred_lang?.map((item) => ({
        value: item,
        label: capitalizeWords(item),
      })),
    },
    {
      name: "added_with",
      label: "Added With",
      options: filterOption?.added_with?.map((item) => ({
        value: item,
        label: capitalizeWords(item),
      })),
    },
    {
      name: "is_legacy",
      label: "is legacy",
      type: "toggle",
      options: filterOption?.is_legacy?.map((item) => ({
        value: item,
        label: String(item),
      })),
    },
  ];

  const handleApplyFilters = (selectedFilters) => {
    setIsFilter(true);
    setLoading(true);
    setCurrentPage(1);
    getAllDataPrincipals(selectedFilters);
  };

  const clearFilter = (isFilter) => {
    setIsFilter(false);
    if (isFilter) {
      getAllDataPrincipals();
    }
  };

  return (
    <div className="flex max-h-[calc(100vh-53px)]">
      <div className="w-full">
        <div className="flex flex-col justify-between gap-4 pr-6 sm:flex-row sm:border-b sm:border-borderheader">
          <Header
            title={`Data Principal (${totalPrincipals})`}
            subtitle="Individuals whose personal data you collect, process, or store"
          />
          <div className="flex items-center gap-3.5">
            <Link href="/apps/principal-management/consent">
              <Button variant="secondary" className="flex items-center gap-1">
                Consent
              </Button>
            </Link>
            <div className="relative" ref={dropdownRef}>
              <Button
                variant="secondary"
                className="user-toggle-button px-[15.5px]"
                id="action-options"
                disabled={!canWrite("/apps/principal-management")}
                onClick={toggleDropdown}
              >
                Action{" "}
                <span
                  className={`-mr-2 ml-2 ${
                    dropdownOpen && "rotate-180"
                  } user-toggle-button`}
                >
                  <RiArrowDropDownLine size={25} />
                </span>
              </Button>

              {dropdownOpen && (
                <div
                  ref={dropdownRef}
                  className="absolute right-0 top-7 z-50 mt-2 w-[100px] border border-[#c7cfe2] bg-[#f9fcff]"
                >
                  <>
                    <Link
                      id="import-dp"
                      href="/apps/principal-management/import"
                      className="flex w-full items-center px-2 py-2 text-start text-sm text-[#525151] hover:bg-primary hover:text-white"
                    >
                      <span className="mr-1.5">
                        <MdUploadFile size={20} />
                      </span>{" "}
                      Import
                    </Link>
                    <button
                      id="export-dp"
                      onClick={() => setShowExportModal(true)}
                      className="flex w-full items-center px-2 py-2 text-start text-sm text-[#525151] hover:bg-primary hover:text-white"
                    >
                      <span className="mr-1.5">
                        <HiDownload size={20} />
                      </span>
                      Export
                    </button>
                    <Link
                      id="add-dp-manually"
                      href="/apps/principal-management/add-data-principal"
                      className="flex w-full items-center px-2 py-2 text-start text-sm text-[#525151] hover:bg-primary hover:text-white"
                    >
                      <span className="mr-1.5">
                        <IoMdAdd size={20} />
                      </span>
                      Manual
                    </Link>
                    <Link
                      id="delete-dp-bulk"
                      href="/apps/principal-management/bulk-dp-delete"
                      className="flex w-full items-center px-3 py-2 text-start text-sm text-[#525151] hover:bg-primary hover:text-white"
                    >
                      <span className="mr-1.5">
                        <AiOutlineDelete size={16} className="mb-1" />
                      </span>
                      Delete
                    </Link>
                  </>
                </div>
              )}
            </div>
          </div>
        </div>
        <DataTable
          tableHeight={"213.5px"}
          columns={userColumns}
          data={dpData}
          loading={loading}
          totalPages={totalPages}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          rowsPerPageState={rowsPerPageState}
          setRowsPerPageState={setRowsPerPageState}
          search={search}
          setSearch={setSearch}
          isFilter={true}
          clearFilter={clearFilter}
          filterDetails={filterDetails}
          isFilterQuery={debouncedSearch}
          onApplyFilters={handleApplyFilters}
          getRowRoute={(row) =>
            row?.dp_id
              ? `/apps/principal-management/detail/${row?.dp_id}`
              : null
          }
          illustrationText="No Data Element Available"
          illustrationImage="/assets/illustrations/no-data-find.png"
          noDataText="No Data Element Found"
          noDataImage="/assets/illustrations/no-data-find.png"
        />

        {showExportModal && <ExportModal closeModal={closeModal} />}
      </div>
    </div>
  );
};

export default Page;
