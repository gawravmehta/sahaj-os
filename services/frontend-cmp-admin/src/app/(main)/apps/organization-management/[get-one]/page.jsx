"use client";
import React from "react";

import AddAdminMember from "@/components/features/organizationManagement/AddAdminMember";
import DepartmentAdmin from "@/components/features/organizationManagement/DepartmentAdmin";
import DepartmentMember from "@/components/features/organizationManagement/DepartmentMember";
import Header from "@/components/ui/Header";
import Loader from "@/components/ui/Loader";

import { getErrorMessage } from "@/utils/errorHandler";

import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { apiCall } from "@/hooks/apiCall";

const Page = ({ params }) => {
  const paramsData = React.use(params);
  const id = paramsData["get-one"];

  const [selectedDept, setSelectedDept] = useState(null);
  const [modalType, setModalType] = useState(null);
  const [selectedUsers, setSelectedUsers] = useState([]);

  useEffect(() => {
    viewOneDepartment();
  }, [id]);

  const viewOneDepartment = async () => {
    try {
      const response = await apiCall(`/departments/get-one-department/${id}`);

      setSelectedDept(response);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const addDepartmentUser = async () => {
    try {
      if (selectedUsers.length === 0) {
        toast.error("Please select at least one user to assign.");
        return;
      }

      const response = await apiCall(
        `/departments/update-department-members/${modalType.id}`,

        {
          method: "PATCH",
          data: { department_users: selectedUsers },
        }
      );

      toast.success(response?.message);
      setModalType(null);
      viewOneDepartment();
      setSelectedUsers([]);
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message);
      setModalType(null);
    }
  };

  const breadcrumbsProps = {
    path: `/apps/organization-management/${selectedDept?.department_name}`,
    skip: "/apps",
  };

  return (
    <div>
      <div className=" ">
        <div className="w-full rounded-lg bg-white">
          {selectedDept ? (
            <>
              <div className="border-b pr-6">
                <Header
                  breadcrumbsProps={breadcrumbsProps}
                  title={selectedDept.department_name}
                  subtitle={selectedDept.department_description}
                />
              </div>

              <div className="custom-scrollbar mt-5 h-[calc(100vh-210px)] overflow-auto ">
                <div className="mt-4 bg-white shadow-md">
                  <DepartmentAdmin selectedDept={selectedDept} />
                </div>

                <div className="mt-10 bg-white shadow-md">
                  <DepartmentMember
                    viewOneDepartment={viewOneDepartment}
                    selectedDept={selectedDept}
                    setModalType={setModalType}
                  />
                </div>
              </div>
            </>
          ) : (
            <Loader />
          )}
        </div>
      </div>
      <div className="">
        {modalType && (
          <AddAdminMember
            modalType={modalType}
            setModalType={setModalType}
            addDepartmentUser={addDepartmentUser}
            setSelectedUsers={setSelectedUsers}
            selectedUsers={selectedUsers}
            closeModal={() => setModalType(null)}
          />
        )}
      </div>
    </div>
  );
};

export default Page;
