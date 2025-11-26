"use client";
import DataTable from "@/components/shared/data-table/DataTable";
import Button from "@/components/ui/Button";
import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Header from "@/components/ui/Header";
import Tag from "@/components/ui/Tag";
import { apiCall } from "@/hooks/apiCall";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import { FiPlus } from "react-icons/fi";
import { MdOutlineModeEdit } from "react-icons/md";

const Page = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [breaches, setBreaches] = useState([]);
  const [rowsPerPageState, setRowsPerPageState] = useState(10);
  const [loading, setLoading] = useState(false);

  const router = useRouter();

  const getBreaches = async () => {
    setLoading(true);
    try {
      const response = await apiCall(
        `/incidents/get-all-incidents?page=${currentPage}&page_size=${rowsPerPageState}`
      );
      setBreaches(response.incidents || []);
      setTotalPages(response.pagination.totalPages);
    } catch (error) {
      console.error("Error fetching breaches:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    getBreaches();
  }, [currentPage, rowsPerPageState]);

  const breachColumns = [
    {
      header: "Breach Name",
      accessor: "incident_name",
      headerClassName: "text-left w-60",
      render: (element) =>
        element ? <div className="max-w-56">{element}</div> : <div>- - -</div>,
    },
    {
      header: "Breach Type",
      accessor: "incident_type",
      headerClassName: "text-left",
      render: (element) => element || "- - -",
    },
    {
      header: "Breach Severity",
      accessor: "incident_sensitivity",
      headerClassName: "text-left",
      render: (element) => element || "- - -",
    },
    {
      header: "Current Stage",
      accessor: "current_stage",
      headerClassName: "text-left",
      render: (element) => (
        <div className="flex flex-wrap gap-1">{element || "- - -"}</div>
      ),
    },
    {
      header: "Status",
      accessor: "status",
      headerClassName: "text-center",
      render: (element) => (
        <Tag
          label={element === "in_progress" ? "in progress" : element || ""}
          variant={
            element === "published"
              ? "active"
              : element === "draft"
              ? "draft"
              : element === "in_progress"
              ? "suspended"
              : element === "closed"
              ? "inactive"
              : "suspended"
          }
          className="h- mt-2 w-24 font-lato text-[14px] capitalize"
        />
      ),
    },
    {
      header: "Date Discovered",
      accessor: "date_discovered",
      headerClassName: "text-left",
      render: (element) =>
        element ? <DateTimeFormatter dateTime={element} /> : "- - -",
    },
    {
      header: "Deadline",
      accessor: "deadline",
      headerClassName: "text-left",
      render: (element) =>
        element ? <DateTimeFormatter dateTime={element} /> : "- - -",
    },
    {
      accessor: "_id",
      headerClassName: "text-center w-20",
      render: (element, row) => {
        return (
          row.status === "draft" && (
            <Button
              variant="icon"
              className="flex items-center justify-end gap-5 px-5"
              onClick={(e) => {
                e.stopPropagation();
                router.push(`/apps/breach-management/${element}`);
              }}
            >
              <MdOutlineModeEdit size={16} />
            </Button>
          )
        );
      },
    },
  ];

  return (
    <>
      <div className="flex flex-col justify-between gap-4 border-b border-borderheader pr-6 sm:flex-row">
        <Header
          title="Breach Management"
          subtitle="Identify, track, and resolve security breaches to ensure compliance and protect sensitive data."
        />
        <div className="mt-0 flex items-center gap-3.5 sm:mt-2">
          <Button
            variant="secondary"
            className="flex gap-1"
            onClick={() => {
              router.push("/apps/breach-management/create");
            }}
          >
            <FiPlus size={18} /> Breach
          </Button>
        </div>
      </div>
      <DataTable
        tableHeight="213px"
        columns={breachColumns}
        data={breaches}
        loading={loading}
        totalPages={totalPages}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        rowsPerPageState={rowsPerPageState}
        setRowsPerPageState={setRowsPerPageState}
        getRowRoute={(row) =>
          row?._id ? `/apps/breach-management/details/${row._id}` : null
        }
        illustrationText="No Breaches Available"
        illustrationImage="/assets/illustrations/no-data-find.png"
        noDataText="No Breach Found"
        noDataImage="/assets/illustrations/no-data-find.png"
      />
    </>
  );
};

export default Page;
