"use client";
import React, { useEffect, useState } from "react";

import { FiRepeat, FiTrash2 } from "react-icons/fi";

import { AiOutlineDelete } from "react-icons/ai";
import { RxCross2 } from "react-icons/rx";

import toast from "react-hot-toast";

import dayjs from "dayjs";
import Select, { components } from "react-select";
import { getErrorMessage } from "@/utils/errorHandler";
import { apiCall } from "@/hooks/apiCall";
import Button from "@/components/ui/Button";
import DataTable from "@/components/shared/data-table/DataTable";
import DeleteModal from "@/components/shared/modals/DeleteModal";
import { InputField, SelectInput } from "@/components/ui/Inputs";
import { GoPlus } from "react-icons/go";

const InvitationsComponent = ({ setIsModalOpen, isModalOpen }) => {
  const [roles, setRoles] = useState([]);
  const [selectedRoles, setSelectedRoles] = useState([]);
  const [invitation, setInvitation] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPageState, setRowsPerPageState] = useState(10);
  const totalPages = Math.ceil(invitation.length / rowsPerPageState);
  const [openModal, setOpenModal] = useState(null);
  const [disable, setDisable] = useState(false);
  const [hasMoreRoles, setHasMoreRoles] = useState(true);
  const [missingFields, setMissingFields] = useState([]);
  const [wrongField, setWrongField] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingSelect, setLoadingSelect] = useState(true);
  const [btnLoading, setBtnLoading] = useState(false);
  const [formData, setFormData] = useState({
    invited_user_email: "",
    invited_user_id: "",
    invited_user_name: "",
  });

  const rowsPerPage = 5;

  const fetchRoles = async (page = 1) => {
    setLoadingSelect(true);
    try {
      const response = await apiCall(
        `/roles/get-all-roles?page=${page}&limit=${rowsPerPage}`
      );
      const roleOptions = response?.data?.map((role) => ({
        label: role.role_name,
        value: role.id,
      }));

      setRoles((prev) =>
        page === 1 ? roleOptions : [...prev, ...roleOptions]
      );

      if (response?.total_pages <= page) {
        setHasMoreRoles(false);
      }
    } catch (error) {
      console.error("Error fetching roles:", error);
    } finally {
      setLoadingSelect(false);
    }
  };

  useEffect(() => {
    fetchRoles(currentPage);
  }, [currentPage]);

  const handleLoadMore = () => {
    setCurrentPage((prev) => prev + 1);
  };

  const fetchInvitations = async () => {
    setLoading(true);
    try {
      const res = await apiCall(
        `/invite/view-all-invites?page=${currentPage}&page_size=${rowsPerPageState}`
      );

      const allInvites = [...res.pending, ...res.accepted, ...res.expired].sort(
        (a, b) => new Date(b.invited_at) - new Date(a.invited_at)
      );

      setInvitation(allInvites);
    } catch (err) {
      console.error(err);
      const message = getErrorMessage(err);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvitations();
  }, [currentPage, rowsPerPageState]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  useEffect(() => {
    if (wrongField.length > 0) {
      toast.error(wrongField[0].message);
    }
  }, [wrongField]);

  const handleInvite = async () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (
      !emailRegex.test(formData.invited_user_email) &&
      formData.invited_user_email
    ) {
      const usernamePart =
        formData.invited_user_email.split("@")[0] || "example";
      setWrongField([
        {
          value: "invited_user_email",
          message: `Please enter a valid email address like ${usernamePart}@gmail.com`,
        },
      ]);
      return;
    }

    const missing = [];
    if (!formData.invited_user_email) missing.push("invited_user_email");
    if (!formData.invited_user_name) missing.push("invited_user_name");
    if (selectedRoles.length === 0) missing.push("invited_user_role");

    setMissingFields(missing);
    if (missing.length > 0) {
      toast.error("Please fill in the required fields");
      return;
    }

    const dataToSend = {
      ...formData,
      invited_user_roles: selectedRoles,
    };
    setBtnLoading(true);
    try {
      const res = await apiCall("/invite/new", {
        method: "POST",
        data: dataToSend,
      });

      toast.success("Invite sent!");
      setIsModalOpen(false);
      setFormData({
        invited_user_email: "",
        invited_user_id: "",
        invited_user_name: "",
      });
      setBtnLoading(false);
      setSelectedRoles([]);
      fetchInvitations();
    } catch (err) {
      console.error(err);
      const message = getErrorMessage(err);
      toast.error(message);
      setBtnLoading(false);
    }
  };

  const handleResend = async (inviteId) => {
    setDisable(true);
    try {
      await apiCall(`/invite/resend-invitation/${inviteId}`, {
        method: "PATCH",
      });
      toast.success("Invite resent!");
      fetchInvitations();
      setDisable(false);
    } catch (err) {
      console.error(err);
      toast.error(getErrorMessage(err));
      setDisable(false);
    }
  };

  const handleCancel = async (inviteId) => {
    try {
      await apiCall(`/invite/cancel-invite/${inviteId}`, {
        method: "DELETE",
      });
      toast.success("Invite cancelled!");
      fetchInvitations();
      closeModal();
    } catch (err) {
      console.error(err);
      toast.error(getErrorMessage(err));
    }
  };
  const closeModal = () => {
    setOpenModal(null);
  };

  const paginatedData = invitation.slice(
    (currentPage - 1) * rowsPerPageState,
    currentPage * rowsPerPageState
  );

  const userColumns = [
    {
      header: "Name",
      accessor: "invited_user_name",
      headerClassName: "w-48 px-4  text-start",
      render: (element) => (
        <div className="flex">
          <span className="max-w-48 truncate text-ellipsis px-4 py-1.5 capitalize">
            {element ? element : "------"}
          </span>
        </div>
      ),
    },
    {
      header: "Email",
      accessor: "invited_user_email",
      headerClassName: "w-60 text-start ",
      render: (element) => <div className="flex  py-1.5">{element}</div>,
    },
    {
      header: "Status",
      accessor: "invite_status",
      headerClassName: "text-center ",
      render: (element) => (
        <div className="flex items-center justify-center capitalize">
          {element}
        </div>
      ),
    },
    {
      header: "Invited By",
      accessor: "invited_by_name",
      headerClassName: " pr-14",
      render: (element) => (
        <div className="flex items-center justify-center">{element}</div>
      ),
    },
    {
      header: "Invited At",
      accessor: "invited_at",
      headerClassName: "text-center",
      render: (element) => (
        <div className="flex items-center justify-center">
          {dayjs(element).format("MMM D, YYYY")}
        </div>
      ),
    },
    {
      header: "Action",
      accessor: "action-buttons",
      headerClassName: "text-center",
      render: (_, row) => {
        if (row?.invite_status !== "pending") return null;

        return (
          <div className="flex items-center justify-center gap-3">
            <button
              disabled={disable}
              onClick={() => handleResend(row._id)}
              className={`hover:text-blue-800 cursor-pointer ${
                disable ? "cursor-not-allowed opacity-50" : ""
              }`}
              title="Resend Invite"
            >
              <FiRepeat size={16} />
            </button>
            <button
              onClick={() => setOpenModal(row._id)}
              className="hover:text-red-800 cursor-pointer"
              title="Cancel Invite"
            >
              <AiOutlineDelete size={16} />
            </button>
          </div>
        );
      },
    },
  ];

  return (
    <>
      {invitation.length === 0 && !loading ? (
        <div className="h-[40vh] px-4 py-2">
          <div className="-mb-3 mt-2 flex items-center justify-between text-2xl">
            <span className="text-[16px] text-primary">Invitations</span>
          </div>
          <div className="flex h-full w-full items-center justify-center">
            <div className="flex flex-col gap-4 text-center text-sm text-gray-400">
              <p>Invite team members for role assignments</p>
            </div>
          </div>
        </div>
      ) : (
        <div>
          <div className="flex w-full justify-end   pr-6 pb-5"></div>

          <DataTable
            hasFilterOption={true}
            loading={loading}
            tableHeight={"390px"}
            columns={userColumns}
            data={invitation}
            hidePagination={false}
            totalPages={totalPages}
            currentPage={currentPage}
            rowsPerPageState={rowsPerPageState}
            setRowsPerPageState={setRowsPerPageState}
            setCurrentPage={setCurrentPage}
            searchable={false}
            hasSerialNumber={true}
            filters={[]}
          />


          {openModal && (
            <DeleteModal
              closeModal={closeModal}
              onConfirm={() => handleCancel(openModal)}
              title="Do you want to delete this "
              field="invite?"
              dpId={openModal}
              typeTitle="Invite"
            />
          )}
        </div>
      )}
      {isModalOpen && (
        <div
          onClick={() => {
            setIsModalOpen(false);
            setMissingFields([]);
            setFormData({
              invited_user_email: "",
              invited_user_id: "",
              invited_user_name: "",
            });
            setSelectedRoles([]);
          }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50 px-4 py-8"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="flex w-[500px] flex-col justify-between border border-[#c7cfe2] bg-white p-6"
          >
            <div>
              <Button variant="close" className="flex w-full justify-end">
                <RxCross2
                  onClick={() => {
                    setIsModalOpen(false);
                    setMissingFields([]);
                    setFormData({
                      invited_user_email: "",
                      invited_user_id: "",
                      invited_user_name: "",
                    });
                    setSelectedRoles([]);
                  }}
                  size={20}
                />
              </Button>
              <h2 className="text-xl font-semibold">Invite User</h2>
              <p className="mb-4 mt-2 text-sm text-gray-400">
                Provide user details to send the invite.
              </p>
              <div className="space-y-4">
                <InputField
                  name="invited_user_name"
                  label="Full Name"
                  placeholder="Enter Name"
                  value={formData.invited_user_name}
                  onChange={(e) => {
                    setFormData((prev) => ({
                      ...prev,
                      ["invited_user_name"]: e.target.value,
                    }));
                  }}
                  missingFields={missingFields}
                  required={true}
                  tooltipText="Enter the user’s complete name as it should appear in the system."
                />
                <InputField
                  name="invited_user_email"
                  label="Email"
                  type="email"
                  placeholder="example123@gmail.com"
                  value={formData.invited_user_email}
                  onChange={(e) => {
                    setFormData((prev) => ({
                      ...prev,
                      ["invited_user_email"]: e.target.value,
                    }));
                  }}
                  onKeyDown={(e) => {
                    if (e.key === " ") {
                      e.preventDefault();
                    }
                  }}
                  required={true}
                  missingFields={missingFields}
                  wrongFields={wrongField}
                  tooltipText="Enter a valid email address. An invitation link will be sent here."
                />

                <SelectInput
                  label="Role"
                  name="invited_user_role"
                  options={roles}
                  value={roles.filter((role) =>
                    selectedRoles.includes(role.value)
                  )}
                  onChange={(selected) => {
                    const selectedIds = selected
                      ? selected.map((item) => item.value)
                      : [];
                    setSelectedRoles(selectedIds);
                  }}
                  placeholder="Select role"
                  isMulti={true}
                  required={true}
                  hasMore={hasMoreRoles}
                  loadingMore={loadingSelect}
                  onLoadMore={() => setCurrentPage((prev) => prev + 1)}
                  tooltipText="Select the appropriate role for this user. Roles determine permissions and access level."
                />
              </div>
            </div>
            <div className="mt-5 flex justify-end gap-3">
              <Button
                variant="cancel"
                onClick={() => {
                  setIsModalOpen(false);
                  setMissingFields([]);
                  setFormData({
                    invited_user_email: "",
                    invited_user_id: "",
                    invited_user_name: "",
                  });
                  setSelectedRoles([]);
                }}
              >
                Cancel
              </Button>
              <Button
                disabled={btnLoading}
                btnLoading={btnLoading}
                variant="primary"
                onClick={() => {
                  setMissingFields([]);
                  setWrongField([]);
                  handleInvite();
                }}
                className=""
              >
                Send Invite
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default InvitationsComponent;
