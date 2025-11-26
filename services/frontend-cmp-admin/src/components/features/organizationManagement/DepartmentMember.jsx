"use client";

import React, { useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import { HiOutlineDotsHorizontal } from "react-icons/hi";

import { GoPlus } from "react-icons/go";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import DataTable from "@/components/shared/data-table/DataTable";
import DeleteModal from "@/components/shared/modals/DeleteModal";
import Button from "@/components/ui/Button";

const DepartmentMember = ({
  selectedDept,
  setModalType,
  viewOneDepartment,
}) => {
  const [DepartmentActions, setDepartmentActions] = useState(null);
  const [addAdmin, setAddAdmin] = useState(false);
  const [removeAdmin, setRemoveAdmin] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [loading, setLoading] = useState(true);

  const handleButtonClick = (type, id) => {
    setModalType({ type, id });
  };
  const showOption = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showOption.current && !showOption.current.contains(event.target)) {
        setDepartmentActions(null);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const addDepartmentUser = async () => {
    try {
      const response = await apiCall(
        `/departments/update-department-members/${selectedDept._id}`,
        {
          method: "PATCH",
          data: { department_admins: [addAdmin] },
        }
      );
      toast.success(response?.message);
      setAddAdmin();
      viewOneDepartment();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const removeDepartmentUser = async (id) => {
    try {
      const response = await apiCall(
        `/departments/remove-members?department_id=${selectedDept._id}&user_ids=${id}`,
        {
          method: "DELETE",
        }
      );
      toast.success(response?.message);
      setRemoveAdmin(null);
      viewOneDepartment();
    } catch (error) {
      console.error("Failed to fetch department details:", error);
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  const close = () => {
    setAddAdmin(null);
    setRemoveAdmin(null);
  };

  const totalPages = Math.ceil(
    selectedDept.department_users_data.length / rowsPerPage
  );

  const indexOfLastRow = currentPage * rowsPerPage;
  const indexOfFirstRow = indexOfLastRow - rowsPerPage;

  const currentRows = selectedDept.department_users_data.slice(
    indexOfFirstRow,
    indexOfLastRow
  );

  useEffect(() => {
    setLoading(false);
  }, [currentRows, currentPage]);

  const handlePageChange = (page) => {
    if (page < 1 || page > totalPages) return;
    setLoading(true);
    setCurrentPage(page);
  };

  return (
    <div className="border-b">
      <div className="flex w-full items-center justify-between px-6 pb-5">
        <h3 className="text-base text-primary">Department Users</h3>

        <Button
          variant="secondary"
          onClick={() => handleButtonClick("Users", selectedDept._id)}
        >
          Add User
        </Button>
      </div>
      {selectedDept?.department_users_data?.length > 0 ? (
        <DataTable
          columns={[
            {
              header: "Name",
              accessor: "first_name",
              headerClassName: "w-78 text-start  ",
              render: (name, row) => (
                <span className="">
                  {name} {row.last_name || ""}
                </span>
              ),
            },
            {
              header: "Email",
              headerClassName: "w-70 text-start  ",
              accessor: "email",
            },
            {
              header: "Designation",
              accessor: "designation",
              headerClassName: "w-44 text-start  ",
              render: (designation) => designation || "N/A",
            },
            {
              header: "Actions",
              accessor: "_id",
              headerClassName: " text-end  pr-6 ",
              render: (element) => (
                <div className=" flex justify-end  gap-4  pr-10">
                  <div
                    onClick={() => setDepartmentActions(element)}
                    className="cursor-pointer text-gray-500 hover:text-gray-700"
                  >
                    <HiOutlineDotsHorizontal size={20} />
                  </div>
                  {DepartmentActions === element && (
                    <div
                      ref={showOption}
                      className=" -mb-10 flex flex-col gap-1 border bg-white p-2 text-sm"
                    >
                      <span
                        onClick={() => setAddAdmin(element)}
                        className="cursor-pointer hover:text-blue-600"
                      >
                        Promote to Admin
                      </span>
                      <span
                        onClick={() => setRemoveAdmin(element)}
                        className="cursor-pointer hover:text-red-500"
                      >
                        Remove User
                      </span>
                    </div>
                  )}
                </div>
              ),
            },
          ]}
          tableHeight="750px"
          data={currentRows}
          loading={loading}
          PaginationView={false}
          totalPages={totalPages}
          currentPage={currentPage}
          rowsPerPageState={rowsPerPage}
          setRowsPerPageState={setRowsPerPage}
          setCurrentPage={handlePageChange}
          hasSerialNumber
          searchable={false}
          hasFilterOption={false}
          fixedHeight={"18rem"}
        />
      ) : (
        <div className="flex items-center justify-center text-gray-500">
          <p>No Data Found</p>
        </div>
      )}

      <div>
        {addAdmin && (
          <DeleteModal
            title="Are you sure you want to promote this member to admin?"
            addAdmin={addAdmin}
            closeModal={close}
            dpId={addAdmin}
            onConfirm={addDepartmentUser}
            variant="primary"
            buttonClass="w-32 py-2"
            typeTitle="Department Admin"
          />
        )}
        {removeAdmin && (
          <DeleteModal
            title="Are you sure you want to remove this member from the department?"
            addAdmin={removeAdmin}
            closeModal={close}
            dpId={removeAdmin}
            onConfirm={removeDepartmentUser}
            buttonClass="w-32 py-2"
            typeTitle="Department User"
          />
        )}
      </div>
    </div>
  );
};

export default DepartmentMember;
