"use client";

import AddDataElement from "@/components/features/dataElement/AddDataElement";
import DataTable from "@/components/shared/data-table/DataTable";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import { usePermissions } from "@/contexts/PermissionContext";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import { FiPlus, FiSearch } from "react-icons/fi";
import { LuSearchX } from "react-icons/lu";
import { MdDone, MdOutlineModeEdit } from "react-icons/md";
import { RxCross2 } from "react-icons/rx";

const Page = () => {
  const addRef = useRef(null);
  const router = useRouter();

  const [visible, setVisible] = useState(true);
  const [deData, setDeData] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [totalPages, setTotalPages] = useState("");
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  const { canWrite } = usePermissions();

  const userColumns = [
    {
      header: "Name",
      accessor: "de_name",
      headerClassName: "text-left ",
      render: (element, row) => {
        return (
          <div className="flex max-w-64 flex-col">
            <span className="max-w-44 truncate text-ellipsis font-medium capitalize">
              {element}
            </span>
            <span className="max-w-40 truncate text-[10px] text-gray-500">
              {row.de_description}
            </span>
          </div>
        );
      },
    },
    {
      header: "Original Name",
      accessor: "de_original_name",
      headerClassName: "text-left ",
      render: (element) => {
        return (
          <div className="flex max-w-64 flex-col">
            <span className="max-w-44 truncate text-ellipsis font-medium capitalize">
              {element}
            </span>
          </div>
        );
      },
    },
    {
      header: "Type",
      accessor: "de_data_type",
      headerClassName: "text-left w-32",
      render: (element) => {
        return (
          <div className="flex max-w-64 flex-col">
            <span className="max-w-44 truncate text-ellipsis font-medium capitalize">
              {element}
            </span>
          </div>
        );
      },
    },
    {
      header: "Core Identifier",
      accessor: "is_core_identifier",
      headerClassName: "text-center w-32",
      render: (element) => {
        return (
          <div className="flex justify-center">
            {element === false ? (
              <RxCross2 size={20} className="text-red-600" />
            ) : (
              <MdDone size={20} className="text-green-600" />
            )}
          </div>
        );
      },
    },

    {
      header: "Sensitivity",
      accessor: "de_sensitivity",
      headerClassName: "text-center w-32",
      render: (element) => {
        return (
          <div className="flex items-center justify-center">
            {element && (
              <div
                className={`flex h-7 w-7 items-center justify-center rounded-full capitalize ${
                  element?.toLowerCase() === "medium"
                    ? "bg-[#FEF7DE] text-[#a18c00]"
                    : element?.toLowerCase() === "low"
                    ? "bg-[#E0FFE7] text-[#06a42a]"
                    : element?.toLowerCase() === "high"
                    ? "bg-[#FBEAEA] text-[#d94e4e]"
                    : ""
                }`}
              >
                {(element?.toLowerCase() === "medium" && "m") ||
                  (element?.toLowerCase() === "low" && "l") ||
                  (element?.toLowerCase() === "high" && "h")}
              </div>
            )}
          </div>
        );
      },
    },

    {
      header: "Status",
      accessor: "de_status",
      headerClassName: "text-center w-32",
      render: (element) => {
        let bgColor;

        if (element === "draft") {
          bgColor = "bg-gray-200 text-gray-500";
        } else if (element === "published") {
          bgColor = "bg-[#e1ffe7] text-[#06a42a]";
        } else if (element === "archived") {
          bgColor = "bg-[#fbeaea] text-[#d94e4e]";
        } else {
          bgColor = "bg-gray-100 text-white";
        }

        return (
          <div className="flex items-center justify-center">
            <div
              className={`w-20 rounded-full py-1 text-center capitalize ${bgColor}`}
            >
              {element}
            </div>
          </div>
        );
      },
    },
    {
      accessor: "de_id",
      headerClassName: "text-center w-20",
      render: (element, row) => {
        return (
          row.de_status !== "archived" &&
          row.de_status !== "published" && (
            <Button
              variant="icon"
              className="flex items-center justify-end gap-5 px-5"
              onClick={(e) => {
                e.stopPropagation();
                router.push(`/apps/data-element/${element}?type=edit`);
              }}
              disabled={!canWrite("/apps/data-element")}
            >
              <MdOutlineModeEdit size={16} />
            </Button>
          )
        );
      },
    },
  ];

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (addRef.current && !addRef.current.contains(event.target)) {
        handleSearchClick(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    getAllDataElement();
  }, [currentPage, rowsPerPageState, searchQuery, debouncedSearch]);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 500);
    return () => {
      clearTimeout(handler);
    };
  }, [searchQuery]);

  const getAllDataElement = async (filters) => {
    try {
      setLoading(true);

      let url = `/data-elements/get-all-data-element?current_page=${currentPage}&data_per_page=${rowsPerPageState}`;

      const response = await apiCall(url);
      if (response) {
        setDeData(response.data_elements);
        setTotalPages(response?.total_pages || 1);
      }
    } catch (error) {
      toast.error(getErrorMessage(error));

      console.error(
        "Error fetching data:",
        error?.response?.data || error.message
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSearchClick = () => {
    setVisible((prevVisible) => !prevVisible);
  };

  const handleNewDataElement = (newElement) => {
    setDeData((prev) => [newElement, ...prev]);
  };

  return (
    <>
      <div className="flex justify-between border-b border-borderheader">
        <Header
          title="Data Element"
          subtitle="Create and Explore all the data elements from here."
        />

        <div className="flex items-center justify-center gap-2 px-5">
          <Button
            variant={visible ? "secondary" : "primary"}
            onClick={handleSearchClick}
            className="flex w-28 items-center justify-center gap-2 py-2"
          >
            {visible ? (
              <FiSearch className="text-[16px]" />
            ) : (
              <LuSearchX className="text-[16px]" />
            )}
            <span className="text-sm">Data Veda</span>
          </Button>
          <Button
            disabled={!canWrite("/apps/data-element")}
            variant="secondary"
          >
            <Link
              href="/apps/data-element/create"
              className="flex w-[120px] gap-1 px-1"
            >
              <FiPlus className="text-base" />
              <p>Data Element</p>
            </Link>
          </Button>
        </div>
      </div>
      {!visible && (
        <div ref={addRef} className="absolute left-5 top-3 z-20 w-[250px]">
          <AddDataElement
            setVisible={setVisible}
            setDeData={setDeData}
            visible={visible}
            onCreate={handleNewDataElement}
            getAllDataElement={getAllDataElement}
          />
        </div>
      )}
      <div className="relative w-full">
        <DataTable
          tableHeight={"213.5px"}
          columns={userColumns}
          data={deData}
          loading={loading}
          totalPages={totalPages}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          rowsPerPageState={rowsPerPageState}
          setRowsPerPageState={setRowsPerPageState}
          getRowRoute={(row) =>
            row?.de_id ? `/apps/data-element/details/${row?.de_id}` : null
          }
          illustrationText="No Data Element Available"
          illustrationImage="/assets/illustrations/no-data-find.png"
          noDataText="No Data Element Found"
          noDataImage="/assets/illustrations/no-data-find.png"
        />
      </div>
    </>
  );
};
export default Page;
