"use client";
import React, { useEffect, useState } from "react";
import DataTable from "@/components/shared/data-table/DataTable";
import Tag from "@/components/ui/Tag";
import Button from "@/components/ui/Button";
import { FiPlus } from "react-icons/fi";
import { MdOutlineEdit, MdOutlineModeEdit } from "react-icons/md";
import Link from "next/link";
import { apiCall } from "@/hooks/apiCall";
import { AiOutlineDelete } from "react-icons/ai";
import { InputField, TextareaField } from "@/components/ui/Inputs";
import { GoPlus } from "react-icons/go";
import RoleDetail from "./RoleDetail";
import { RxCross2 } from "react-icons/rx";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";
import DeleteModal from "@/components/shared/modals/DeleteModal";
import AddAdminMember from "./AddAdminMember";
import { FaUserLock } from "react-icons/fa";
import PermissionsModal from "./PermissionsModal";
import { usePermissions } from "@/contexts/PermissionContext";

const RolesComponent = ({ setModalType, modalType, GetDashboardCard }) => {
  const [rolesData, setRolesData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRole, setSelectedRole] = useState(null);
  const [roleId, setRoleId] = useState(null);
  const [editName, setEditName] = useState("");
  const [editDesc, setEditDesc] = useState("");
  const [missingFields, setMissingFields] = useState([]);
  const [showRoleDetailModal, setShowRoleDetailModal] = useState(false);
  const [rolesUser, setRolesUser] = useState([]);

  const [showAddUserModal, setShowAddUserModal] = useState(false);

  const { canWrite } = usePermissions();

  const fetchRoles = () => {
    setLoading(true);
    apiCall(
      `/roles/get-all-roles?page=${currentPage}&limit=${rowsPerPageState}`
    )
      .then((response) => {
        setRolesData(response?.data);
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
    fetchRoles();
  }, [currentPage, rowsPerPageState]);

  const openModal = async (type, dept = null) => {
    setSelectedRole(dept);
    setRoleId(dept?.id);

    switch (type) {
      case "permission":
        setModalType("permission");
        break;
      case "add":
        setEditName("");
        setEditDesc("");
        setModalType("add");
        break;
      case "edit":
        setEditName(dept.role_name);
        setEditDesc(dept.role_description);
        setModalType("edit");
        break;
      case "delete":
        setModalType("delete");
        break;
      case "view":
        setShowRoleDetailModal(true);
        break;
      case "getUser":
        setShowAddUserModal(true);
        break;
    }
  };

  const closeModal = () => {
    setSelectedRole(null);
    setModalType(null);
    setEditName("");
    setEditDesc("");
    setMissingFields([]);
    setRoleId(null);
  };

  const addRolesUser = async () => {
    if (rolesUser.length === 0) {
      toast.error("Please select at least one user to assign.");
      return;
    }
    try {
      const response = await apiCall(`/roles/update-role-users/${roleId}`, {
        method: "PATCH",
        data: { users_list: rolesUser },
      });

      toast.success(response?.message);
      setModalType(null);
      fetchRoles();

      GetDashboardCard();
      setRolesUser([]);
      setShowAddUserModal(false);
      setShowRoleDetailModal(false);
    } catch (error) {
      console.error("Failed to fetch department details:", error);
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  const handleDeleteConfirm = async () => {
    try {
      await apiCall(`/roles/delete-role/${selectedRole.id}`, {
        method: "DELETE",
      });

      fetchRoles();
      closeModal();
      GetDashboardCard();
      toast.success("Role deleted successfully");
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
      await apiCall(`/roles/update-role/${selectedRole.id}`, {
        method: "PATCH",
        data: {
          role_name: editName,
          role_description: editDesc,
        },
      });
      fetchRoles();
      closeModal();
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

    try {
      await apiCall("/roles/add-role", {
        method: "POST",
        data: {
          role_name: editName,
          role_description: editDesc,
        },
      });
      fetchRoles();
      closeModal();
      GetDashboardCard();
    } catch (err) {
      const message = getErrorMessage(err);
      toast.error(message);
    }
  };

  const rolesColumns = [
    {
      header: "Name",
      accessor: "role_name",
      headerClassName: "w-44 text-start ",
      render: (element) => (
        <div className="flex ">
          <span className="truncate text-ellipsis py-1.5 capitalize">
            {element}
          </span>
        </div>
      ),
    },
    {
      header: "Description",
      accessor: "role_description",
      headerClassName: "w-44",
      render: (element) => (
        <div className="truncate text-ellipsis pl-14 capitalize">
          {element.length > 40 ? element.slice(0, 40) + "..." : element}
        </div>
      ),
    },
    {
      header: "Actions",
      accessor: "id",
      headerClassName: " text-end pr-8 ",
      render: (id) => {
        const dept = rolesData.find((d) => d.id === id);
        return (
          <div className="flex items-center  gap-3  justify-end pr-8">
            <Button
              onClick={(e) => {
                e.stopPropagation();
                openModal("permission", dept);
              }}
              variant="icon"
              disabled={!canWrite("/apps/organization-management")}
            >
              <FaUserLock size={14} />
            </Button>
            <Button
              variant="icon"
              disabled={!canWrite("/apps/organization-management")}
              onClick={(e) => {
                e.stopPropagation();
                openModal("edit", dept);
              }}
            >
              <MdOutlineEdit size={14} />
            </Button>
            <Button
              onClick={(e) => {
                e.stopPropagation();
                openModal("delete", dept);
              }}
              className={"hover:text-red-700"}
              disabled={!canWrite("/apps/organization-management")}
              variant="icon"
            >
              <AiOutlineDelete size={14} />
            </Button>
          </div>
        );
      },
    },
  ];

  return (
    <div className=" ">
      <div className="flex flex-col justify-end gap-4  sm:flex-row "></div>

      <div className="mt-6 w-full ">
        <DataTable
          tableHeight="390px"
          columns={rolesColumns}
          data={rolesData}
          loading={loading}
          totalPages={totalPages}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          rowsPerPageState={rowsPerPageState}
          setRowsPerPageState={setRowsPerPageState}
          setSearch={setSearchQuery}
          search={searchQuery}
          isFilter={false}
          clearFilter={() => fetchRoles(currentPage, rowsPerPageState)}
          filterDetails={[]}
          onApplyFilters={(filters) =>
            fetchRoles(currentPage, rowsPerPageState, filters)
          }
          searchable={false}
          getRowFunction={(row) => {
            const dept = rolesData.find((d) => d.id === row.id);
            return dept ? () => openModal("view", dept) : null;
          }}
        />
        {showRoleDetailModal && (
          <RoleDetail
            closeModal={() => setShowRoleDetailModal(false)}
            roleId={roleId}
            setShowAddUserModal={setShowAddUserModal}
          />
        )}

        {showAddUserModal && (
          <AddAdminMember
            closeModal={() => setShowAddUserModal(false)}
            addDepartmentUser={addRolesUser}
            setSelectedUsers={setRolesUser}
            selectedUsers={rolesUser}
            setModalType={setModalType}
            modalType={modalType}
          />
        )}
        {modalType === "delete" && selectedRole && (
          <DeleteModal
            closeModal={closeModal}
            onConfirm={handleDeleteConfirm}
            title=" Do you want to delete this"
            field={"data Role?"}
            typeTitle="Role"
          />
        )}
      </div>

      {(modalType === "edit" || modalType === "add") && (
        <div
          onClick={closeModal}
          className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50 px-4 py-8"
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
                {modalType === "edit" ? "Edit Role" : "Add Role"}
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
                  tooltipText="Enter the role title (e.g., Manager, Analyst, Intern). This defines user responsibilities within a department."
                />
                <TextareaField
                  name={"Description"}
                  label="Description"
                  placeholder="Write description"
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                  required={true}
                  missingFields={missingFields}
                  tooltipText="Add details about this role’s duties, permissions, or scope."
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
              >
                {modalType === "edit" ? "Save" : "Create"}
              </Button>
            </div>
          </div>
        </div>
      )}

      {modalType == "permission" && (
        <PermissionsModal roleId={roleId} onClose={() => setModalType("")} />
      )}
    </div>
  );
};

export default RolesComponent;
