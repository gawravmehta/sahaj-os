import React, { useEffect, useState } from "react";
import { RxCross2 } from "react-icons/rx";
import toast from "react-hot-toast";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import SearchBar from "@/components/shared/data-table/SearchBar";
import Button from "@/components/ui/Button";
import DataTable from "@/components/shared/data-table/DataTable";
import Loader from "@/components/ui/Loader";

const AddAdminMember = ({
  modalType,
  closeModal,
  setModalType,
  addDepartmentUser,
  selectedUsers,
  setSelectedUsers,
}) => {
  const [selectedUser, setSelectedUser] = useState([]);
  const [rowsPerPageState, setRowsPerPageState] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [searchable, setSearchable] = useState("");

  useEffect(() => {
    getallDepartmentUser();
  }, [searchable, currentPage, rowsPerPageState]);

  const getallDepartmentUser = async () => {
    setLoading(true);
    try {
      const searchQuery = searchable && `&search=${searchable}`;
      const response = await apiCall(
        `/auth/get-df-users?page=${currentPage}&page_size=${rowsPerPageState}${searchQuery}`
      );

      setSelectedUser(response.data);

      setTotalPages(response.total_pages);
      setLoading(false);
    } catch (error) {
      const message = getErrorMessage(error);
      console.error("Failed to fetch department details:", error);
      setLoading(false);
      toast.error(message);
    }
  };

  const handlePageChange = (newPage) => {
    if (newPage !== currentPage) {
      setCurrentPage(newPage);
    }
  };

  const handleRowsPerPageChange = (newRowsPerPage) => {
    setRowsPerPageState(newRowsPerPage);
    setCurrentPage(1);
  };

  const handleSearch = (value) => {
    setSearchable(value);
    setCurrentPage(1);
  };

  return (
    <div
      onClick={() => closeModal(null)}
      className="fixed inset-0 z-50 flex items-center justify-center overflow-auto bg-[#f2f9ff]/50 px-4 py-8"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative h-120 w-full max-w-4xl border bg-white p-6"
      >
        <>
          <div className="mb-6">
            <div className="flex items-center justify-between">
              {modalType?.type === "Users" ? (
                <h3 className="mb-2 text-lg font-semibold">
                  Department{" "}
                  <span className="capitalize">{modalType?.type}</span>{" "}
                </h3>
              ) : (
                <h3 className="mb-2 text-lg font-semibold">Role User</h3>
              )}
              <div className="flex items-center gap-5">
                <SearchBar searchQuery={searchable} onSearch={handleSearch} />
                <Button variant="close" onClick={() => closeModal(null)}>
                  <RxCross2 size={20} />
                </Button>
              </div>
            </div>
            {selectedUser.length > 0 ? (
              <DataTable
                columns={[
                  {
                    header: "Name",
                    accessor: "first_name",
                    headerClassName: "w-32  text-start",
                    render: (name, row) => (
                      <span>
                        {name} {row?.last_name || ""}
                      </span>
                    ),
                  },
                  {
                    header: "Email",
                    accessor: "email",
                    headerClassName: " text-start",
                    render: (element) => {
                      return (
                        <div className="flex">
                          <span className="">{element}</span>
                        </div>
                      );
                    },
                  },
                  {
                    header: "",
                    accessor: "_id",
                    render: (element) => (
                      <input
                        type="checkbox"
                        className="h-4 w-4 accent-primary cursor-pointer rounded border-gray-300 text-primary focus:ring-primary"
                        checked={selectedUsers.includes(element)}
                        onChange={() => {
                          if (selectedUsers.includes(element)) {
                            setSelectedUsers(
                              selectedUsers.filter(
                                (userId) => userId !== element
                              )
                            );
                          } else {
                            setSelectedUsers([...selectedUsers, element]);
                          }
                        }}
                      />
                    ),
                  },
                ]}
                loading={loading}
                fixedHeight={"294px"}
                tableWidth={"800px"}
                PaginationView={true}
                data={selectedUser}
                totalPages={totalPages}
                currentPage={currentPage}
                setCurrentPage={handlePageChange}
                rowsPerPageState={rowsPerPageState}
                setRowsPerPageState={handleRowsPerPageChange}
                hasSerialNumber
                searchable={false}
                hasFilterOption={false}
                getRowFunction={(row) => () => {
                  if (selectedUsers.includes(row._id)) {
                    setSelectedUsers(
                      selectedUsers.filter((userId) => userId !== row._id)
                    );
                  } else {
                    setSelectedUsers([...selectedUsers, row._id]);
                  }
                }}
              />
            ) : (
              <div className="flex h-[400px] items-center justify-center lg:px-8">
                <Loader />
              </div>
            )}
          </div>

          <div className="absolute bottom-4 right-5">
            <Button variant={"secondary"} onClick={() => addDepartmentUser()}>
              Add
            </Button>
          </div>
        </>
      </div>
    </div>
  );
};

export default AddAdminMember;
