"use client";
import DataTable from "@/components/shared/data-table/DataTable";
import Button from "@/components/ui/Button";
import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Header from "@/components/ui/Header";
import Tag from "@/components/ui/Tag";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { FiPlus } from "react-icons/fi";

const Page = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [grievances, setGrievances] = useState([]);
  const [rowsPerPageState, setRowsPerPageState] = useState(10);
  const [loading, setLoading] = useState(false);

  const router = useRouter();

  useEffect(() => {
    getGrievances();
  }, [currentPage, rowsPerPageState]);

  const getGrievances = async () => {
    setLoading(true);
    try {
      const response = await apiCall(
        `/grievances/view-all-grievances?page=${currentPage}&page_size=${rowsPerPageState}`
      );

      setGrievances(response?.data || []);
      setCurrentPage(response?.pagination?.page || 1);
      setTotalPages(response?.pagination?.pages || 0);

      setLoading(false);
    } catch (error) {
      toast.error(getErrorMessage(error));
      setLoading(false);
    }
  };

  const grievanceColumns = [
    {
      header: "Subject",
      accessor: "subject",
      headerClassName: "text-left w-60",
      render: (element) =>
        element ? (
          <div className="text-ellipsis">{element}</div>
        ) : (
          <div>- - -</div>
        ),
    },
    {
      header: "Email",
      accessor: "email",
      headerClassName: "text-left",
      render: (element) => element || "- - -",
    },
    {
      header: "Mobile",
      accessor: "mobile_number",
      headerClassName: "text-left",
      render: (element) => element || "- - -",
    },
    {
      header: "Data Principal Type",
      accessor: "dp_type",
      headerClassName: "text-left",
      render: (element) => (
        <div className="flex flex-wrap gap-1">
          {element?.map((item, i) => (
            <Tag key={i} variant="outlineBlue" label={item} />
          ))}
        </div>
      ),
    },
    {
      header: "Status",
      accessor: "request_status",
      headerClassName: "text-center",
      render: (element) => (
        <Tag
          variant={element === "open" ? "active" : "outlineBlue"}
          label={element}
          className="mx-auto w-20 capitalize"
        />
      ),
    },
    {
      header: "Created At",
      accessor: "created_at",
      headerClassName: "text-left",
      render: (element) =>
        element ? <DateTimeFormatter dateTime={element} /> : "- - -",
    },
  ];

  return (
    <>
      <div className="flex justify-between border-b border-gray-200">
        <Header
          title="Grievances"
          subtitle="Manage, track, and resolve employee or customer grievances to ensure fairness, trust, and compliance."
        />
      </div>

      <DataTable
        tableHeight="213px"
        columns={grievanceColumns}
        data={grievances}
        loading={loading}
        totalPages={totalPages}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        rowsPerPageState={rowsPerPageState}
        setRowsPerPageState={setRowsPerPageState}
        getRowRoute={(row) => (row?._id ? `/apps/grievances/${row._id}` : null)}
        illustrationText="No Grievances Available"
        illustrationImage="/assets/illustrations/no-data-find.png"
        noDataText="No Grievance Found"
        noDataImage="/assets/illustrations/no-data-find.png"
      />
    </>
  );
};

export default Page;
