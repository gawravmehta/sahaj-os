import React from "react";
import { MdEmail, MdPhone, MdPublic } from "react-icons/md";
import { AiOutlineDelete } from "react-icons/ai";
import { MdOutlineModeEditOutline } from "react-icons/md";
import DpDeleteModal from "@/components/ui/DpDeleteModal";
import { useState } from "react";
import { apiCall } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";
import Link from "next/link";

const Card = ({ data, getDparData }) => {
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState(null);
  const statusStyles = {
    active: "bg-green-100 text-green-600",
    created: "bg-green-100 text-green-600",
    open: "bg-green-100 text-green-600",
    resolved: "bg-yellow-100 text-yellow-600",
    closed: "bg-yellow-100 text-yellow-600",
  };

  const handleDeleteClick = (item) => {
    setItemToDelete(item);
    setIsDeleteModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsDeleteModalOpen(false);
    setItemToDelete(null);
  };

  const handleConfirmDelete = async () => {
    try {
      const response = await apiCall(
        `/api/v1/dpar/dpa-requests/${data.dpar_id}`,
        {
          method: "DELETE",
        }
      );

      toast.success(`${data.dpar_id && "DPAR  deleted successfully"}`);
      getDparData();
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsDeleteModalOpen(false);
    }
  };

  const isDpar = !!data.dpar_id;
  const isGrievance = !!data._id;

  return (
    <div className="bg-white shadow-md p-4  border border-gray-200">
      {isDeleteModalOpen && (
        <DpDeleteModal
          closeModal={handleCloseModal}
          dpId={itemToDelete?.dpar_id}
          deleteDataPrincipal={handleConfirmDelete}
          title="Do you want to delete this"
          field={isDpar ? "DPAR request?" : "grievance?"}
          typeTitle={isDpar ? "DPAR Request" : "Grievance"}
        />
      )}
      {isDpar && (
        <>
          <div className="flex justify-between items-start">
            <h2 className="text-primary  text-[16px]">
              {data.first_name || ""} {data.last_name || ""}
            </h2>
            <div className="flex items-center gap-1">
              <span>
                <AiOutlineDelete
                  className="text-red-600 cursor-pointer"
                  onClick={() => handleDeleteClick(data)}
                />
              </span>
              <span className="text-xs italic text-[#7E7B7B]">
                {data.request_type || "DPAR Request"}
              </span>
            </div>
          </div>
          <p className="text-[#7E7B7B] text-sm mt-1">
            {data.request_message || "No message provided"}
          </p>

          <div className="flex items-center text-gray-500 text-sm mt-1 space-x-4">
            {data.secondary_identifier && (
              <div className="flex items-center space-x-1 text-[#7E7B7B] text-xs">
                <MdEmail /> <span>{data.secondary_identifier}</span>
              </div>
            )}
            {data.core_identifier && (
              <div className="flex items-center space-x-1 text-[#7E7B7B] text-xs">
                <MdPhone /> <span>{data.core_identifier}</span>
              </div>
            )}
            {data.country && (
              <div className="flex items-center space-x-1 text-[#7E7B7B] text-xs">
                <MdPublic /> <span>{data.country}</span>
              </div>
            )}
          </div>

          <div className="flex justify-between items-center mt-1">
            {data.last_updated && (
              <span className="text-xs italic text-gray-400">
                Last Updated: {new Date(data.last_updated).toLocaleDateString()}
              </span>
            )}
            {data.status && (
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  statusStyles[data.status.toLowerCase()] ||
                  "bg-gray-100 text-gray-600"
                }`}
              >
                {data.status}
              </span>
            )}
          </div>
        </>
      )}

      {isGrievance && (
        <div>
          <div className="flex justify-between items-start ">
            <div className="flex items-center text-[#7E7B7B] text-xs  space-x-4">
              {data.email && (
                <div className="flex items-center space-x-1">
                  <MdEmail /> <span>{data.email}</span>
                </div>
              )}
              {data.mobile_number && (
                <div className="flex items-center space-x-1">
                  <MdPhone /> <span>{data.mobile_number}</span>
                </div>
              )}
            </div>
            <span className="text-sm italic text-gray-500">
              {data.sub_category}
            </span>
          </div>
          <p className="text-[#7E7B7B] mt-1 text-sm">
            {data.message || "No message provided"}
          </p>

          <div className="flex justify-between items-center mt-3">
            {data.last_updated_at && (
              <span className="text-xs italic text-gray-400">
                Last Updated:{" "}
                {new Date(data.last_updated_at).toLocaleDateString()}
              </span>
            )}
            {data.request_status && (
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium ${
                  statusStyles[data.request_status.toLowerCase()] ||
                  "bg-gray-100 text-gray-600"
                }`}
              >
                {data.request_status}
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Card;
