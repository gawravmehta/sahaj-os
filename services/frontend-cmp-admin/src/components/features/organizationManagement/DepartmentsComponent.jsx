"use client";

import DataTable from "@/components/shared/data-table/DataTable";

import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import { AiOutlineDelete } from "react-icons/ai";
import { FiEye } from "react-icons/fi";
import { GoPlus } from "react-icons/go";
import { MdOutlineEdit } from "react-icons/md";
import { RxCross2 } from "react-icons/rx";

import toast from "react-hot-toast";

import DeleteModal from "@/components/shared/modals/DeleteModal";
import { InputField, TextareaField } from "@/components/ui/Inputs";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import Button from "@/components/ui/Button";
import { FaUserLock } from "react-icons/fa";
import { usePermissions } from "@/contexts/PermissionContext";
const DepartmentsComponent = ({
  setModalType,
  modalType,
  GetDashboardCard,
}) => {
  const [departments, setDepartments] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPageState, setRowsPerPageState] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedDept, setSelectedDept] = useState(null);
  const [editName, setEditName] = useState("");
  const [editDesc, setEditDesc] = useState("");
  const [missingFields, setMissingFields] = useState([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const [btnLoading, setBtnLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const { canWrite } = usePermissions();

  const fetchDepartments = () => {
    setLoading(true);
    apiCall(
      `/departments/get-all-departments?page=${currentPage}&limit=${rowsPerPageState}`
    )
      .then((response) => {
        setDepartments(response.data);
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
    const delayDebounceFn = setTimeout(() => {
      fetchDepartments();
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [currentPage, rowsPerPageState, searchTerm]);

  const openModal = async (type, dept = null) => {
    setModalType(type);

    if (type === "add") {
      setSelectedDept(null);
      setEditName("");
      setEditDesc("");
      return;
    }

    if (type === "edit") {
      setSelectedDept(dept);
      setEditName(dept.department_name);
      setEditDesc(dept.department_description);
      return;
    }

    if (type === "delete") {
      setSelectedDept(dept);
      return;
    }

    if (type === "view") {
      viewOneDepartment(dept);
    }
  };

  const closeModal = () => {
    setSelectedDept(null);
    setModalType(null);
    setMissingFields([]);
    setEditName("");
    setEditDesc("");
  };

  const viewOneDepartment = async (dept) => {
    try {
      const response = await apiCall(
        `/departments/get-one-department/${dept.id}`
      );
      setSelectedDept(response);
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error("Failed to fetch department details:", error);
    }
  };

  const handleDeleteConfirm = async () => {
    try {
      await apiCall(`/departments/delete-department/${selectedDept.id}`, {
        method: "DELETE",
      });
      fetchDepartments();

      closeModal();
      toast.success("Department deleted successfully");
      GetDashboardCard();
    } catch (err) {
      toast.error(getErrorMessage(err));
      console.error("Failed to delete:", err);
    }
  };

  const handleEditSubmit = async () => {
    const missing = [];
    const check = [
      {
        name: "Name",
        value: editName,
      },
      {
        name: "Description",
        value: editDesc,
      },
    ];
    check.forEach((item) => {
      if (!item.value) {
        missing.push(item.name);
      }
    });

    if (missing.length > 0) {
      setMissingFields(missing);
      toast.error(`Missing fields: ${missing.join(", ")}`);
      return;
    }

    try {
      await apiCall(`/departments/update-department/${selectedDept.id}`, {
        method: "PATCH",
        data: {
          department_name: editName,
          department_description: editDesc,
        },
      });
      fetchDepartments();
      closeModal();

      toast.success("Department updated successfully");
    } catch (err) {
      const message = getErrorMessage(err);
      toast.error(message);
    }
  };
  const handleCreate = async () => {
    const missing = [];
    const check = [
      {
        name: "Name",
        value: editName,
      },
      {
        name: "Description",
        value: editDesc,
      },
    ];
    check.forEach((item) => {
      if (!item.value) {
        missing.push(item.name);
      }
    });

    if (missing.length > 0) {
      setMissingFields(missing);
      toast.error(`Missing fields: ${missing.join(", ")}`);
      return;
    }

    const data = {
      department_name: editName,
      department_description: editDesc,
    };

    try {
      setBtnLoading(true);
      await apiCall("/departments/add-department", {
        method: "POST",
        data: data,
      });
      fetchDepartments();
      closeModal();

      setBtnLoading(false);
      toast.success("Department created successfully");
      GetDashboardCard();
    } catch (err) {
      const message = getErrorMessage(err);
      setBtnLoading(false);
      toast.error(message);
    }
  };

  const userColumns = [
    {
      header: "Name",
      accessor: "department_name",
      headerClassName: "w-44 text-start pl-6",
      render: (element) => (
        <div className="flex ">
          <div className="truncate text-ellipsis py-1.5 capitalize pl-6">
            {element}
          </div>
        </div>
      ),
    },
    {
      header: "Description",
      accessor: "department_description",
      headerClassName: "w-44  text-start px-4",
      render: (element) => (
        <div className="truncate text-ellipsis pl-5 capitalize ">
          {element.length > 40 ? element.slice(0, 40) + "..." : element}
        </div>
      ),
    },
    {
      header: "Actions",
      accessor: "id",
      headerClassName: "text-end pr-8  ",
      render: (id) => {
        const dept = departments.find((d) => d.id === id);
        return (
          <div
            onClick={(e) => e.stopPropagation()}
            className="flex items-center  gap-3  justify-end pr-8"
          >
            <Button
              onClick={(e) => {
                e.stopPropagation();
                openModal("edit", dept);
              }}
              variant="icon"
              disabled={!canWrite("/apps/organization-management")}
            >
              <MdOutlineEdit size={14} />
            </Button>
            <Button
              onClick={(e) => {
                e.stopPropagation();
                openModal("delete", dept);
              }}
              disabled={!canWrite("/apps/organization-management")}
              variant="icon"
              className={"hover:text-red-700"}
            >
              <AiOutlineDelete size={14} />
            </Button>
          </div>
        );
      },
    },
  ];

  return (
    <>
      {departments.length === 0 && !loading ? (
        <div className="h-full px-4 py-2 ">
          <div className="-mb-3 mt-2 flex items-center justify-between text-2xl">
            <span className="text-[16px] text-primary">Departments</span>
          </div>
          <div className="flex h-full w-full items-center justify-center">
            <div className="flex flex-col gap-4 text-center text-sm text-gray-400">
              <p>
                Organize teams by department to streamline workflows and
                permissions
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div>
          <div>
            <DataTable
              tableHeight={"365px"}
              loading={loading}
              hasFilterOption={true}
              columns={userColumns}
              data={departments}
              totalPages={totalPages}
              currentPage={currentPage}
              rowsPerPageState={rowsPerPageState}
              setRowsPerPageState={setRowsPerPageState}
              setCurrentPage={setCurrentPage}
              searchable={false}
              search={searchTerm}
              setSearch={setSearchTerm}
              hasSerialNumber={true}
              getRowRoute={(row) =>
                row?.id ? `/apps/organization-management/${row?.id}` : null
              }
            />

            {modalType === "delete" && selectedDept && (
              <DeleteModal
                closeModal={closeModal}
                onConfirm={handleDeleteConfirm}
                title=" Do you want to delete this"
                field="data Description?"
                typeTitle="Department"
              />
            )}
          </div>
        </div>
      )}

      {(modalType === "edit" || modalType === "add") && (
        <div
          onClick={closeModal}
          className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="flex w-[500px] flex-col justify-between border border-[#c7cfe2] bg-white p-6"
          >
            <div>
              <Button variant="close" className="flex w-full justify-end">
                <RxCross2 onClick={closeModal} size={20} />
              </Button>
              <h2 className="text-xl font-semibold">
                {modalType === "edit" ? "Edit Department" : "Add Department"}
              </h2>
              <p className="mb-4 mt-2 text-sm text-gray-400">
                Provide detailed information about the data element to ensure
                accurate categorization and usage.
              </p>
              <div className="space-y-4">
                <InputField
                  name={"Name"}
                  label="Name"
                  placeholder="Enter department name"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  required={true}
                  missingFields={missingFields}
                  tooltipText="Enter a unique department name (e.g., HR, Finance, IT) to identify this department."
                />
                <TextareaField
                  name={"Description"}
                  label="Description"
                  placeholder="Write description"
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                  required={true}
                  missingFields={missingFields}
                  tooltipText="Provide a brief summary of the department’s function or responsibilities."
                />
              </div>
            </div>
            <div className="mt-3 flex justify-end gap-3">
              <Button variant="cancel" onClick={closeModal}>
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={modalType === "edit" ? handleEditSubmit : handleCreate}
                className="px-3.5"
                btnLoading={btnLoading}
                disabled={btnLoading}
              >
                {modalType === "edit" ? "Save" : "Create"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default DepartmentsComponent;
