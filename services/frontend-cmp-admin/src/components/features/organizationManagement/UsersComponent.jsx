"use client";
import React, { useState } from "react";
import DataTable from "@/components/shared/data-table/DataTable";
import Tag from "@/components/ui/Tag";
import Button from "@/components/ui/Button";
import { FiPlus } from "react-icons/fi";
import { MdOutlineModeEdit } from "react-icons/md";
import Link from "next/link";
import { apiCall } from "@/hooks/apiCall";
import { useEffect } from "react";

const UsersComponent = ({ GetDashboardCard }) => {
  const [dpData, setDpData] = useState([]);

  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [rowsPerPageState, setRowsPerPageState] = useState(10);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  const fetchUsers = () => {
    setLoading(true);
    apiCall(
      `/auth/get-df-users?page=${currentPage}&page_size=${rowsPerPageState}&search=${searchQuery}`
    )
      .then((response) => {
        setDpData(response?.data);
        setTotalPages(response.total_pages || 0);
        if (currentPage > response.total_pages) {
          setCurrentPage(currentPage - 1);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchUsers();
  }, [currentPage, rowsPerPageState, searchQuery, debouncedSearch]);
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [searchQuery]);

  const userColumns = [
    {
      header: "User Name",
      accessor: "first_name",
      headerClassName: "text-left",
      render: (element, row) => {
        return (
          <div>
            <div className="font-medium text-gray-900 capitalize">
              {element}
            </div>
          </div>
        );
      },
    },
    {
      header: "Email",
      accessor: "email",
      headerClassName: "text-left",
      render: (element) => {
        return <div className="text-gray-700">{element}</div>;
      },
    },
    {
      header: "Designation",
      accessor: "designation",
      headerClassName: "text-left",
      render: (element) => {
        return (
          <div className="text-gray-700  pl-7 capitalize">
            {element || "--"}
          </div>
        );
      },
    },

    {
      header: "Contact",
      accessor: "contact",
      headerClassName: "text-center",
      render: (element) => {
        return (
          <div className="text-center text-gray-700">{element || "--"}</div>
        );
      },
    },
  ];

  return (
    <div className=" bg-white  shadow">
      <div className="">
        <DataTable
          tableHeight="410px"
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
          apiSearch={false}
          searchable={true}
        />
      </div>
    </div>
  );
};

export default UsersComponent;
