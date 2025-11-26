"use client";

import DataTable from "@/components/shared/data-table/DataTable";
import Button from "@/components/ui/Button";
import Loader from "@/components/ui/Loader";
import { usePermissions } from "@/contexts/PermissionContext";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { GoPlus } from "react-icons/go";

const RoleDetail = ({ closeModal, setShowAddUserModal, roleId }) => {
  const [selectedRole, setSelectedRole] = useState(null);
  const { canWrite } = usePermissions();

  useEffect(() => {
    RoLeOne();
  }, [roleId]);

  const RoLeOne = async () => {
    try {
      const response = await apiCall(`/roles/get-one-role/${roleId}`);

      setSelectedRole(response);
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error("Failed to fetch department details:", error);
    }
  };

  return (
    <div
      onClick={closeModal}
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50 w-full"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="border bg-white p-6 w-full max-w-2xl"
      >
        {selectedRole ? (
          <div className="flex h-full flex-col justify-between">
            <div>
              <div className="flex justify-between">
                <h2 className="mb-4 text-xl font-semibold">Role Details</h2>

                <Button
                  variant="secondary"
                  onClick={() => setShowAddUserModal(true)}
                  disabled={!canWrite("/apps/organization-management")}
                >
                  Add User
                </Button>
              </div>
              <p>
                <strong>Name:</strong> {selectedRole.role_name}
              </p>
              <p className="mt-2 text-sm text-gray-600 mb-2">
                <strong>Description:</strong> {selectedRole.role_description}
              </p>

              <div className="">
                <DataTable
                  tableHeight="550px"
                  tableWidth="500px"
                  columns={[
                    {
                      header: "Name",
                      headerClassName: "text-left",
                      accessor: "first_name",
                      render: (name, row) => (
                        <span>
                          {name} {row.last_name || ""}
                        </span>
                      ),
                    },
                    {
                      header: "Email",
                      headerClassName: "text-left w-36",
                      accessor: "email",
                      render: (name) => <span className="w-36">{name}</span>,
                    },
                    {
                      header: "Designation",
                      headerClassName: "text-left",
                      accessor: "designation",
                      render: (designation) => designation || "N/A",
                    },
                  ]}
                  data={selectedRole?.role_users_data}
                  PaginationView={true}
                  totalPages={1}
                  currentPage={1}
                  rowsPerPageState={5}
                  setRowsPerPageState={() => {}}
                  setCurrentPage={() => {}}
                  hasSerialNumber
                  searchable={false}
                  hasFilterOption={false}
                />
              </div>
            </div>
            <div className="mt-3 flex justify-end">
              <Button variant="cancel" onClick={closeModal}>
                Close
              </Button>
            </div>
          </div>
        ) : (
          <Loader height="700px" />
        )}
      </div>
    </div>
  );
};

export default RoleDetail;
