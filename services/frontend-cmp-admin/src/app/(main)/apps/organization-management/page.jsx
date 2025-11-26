"use client";
import React, { useState, useEffect } from "react";
import Header from "@/components/ui/Header";
import DepartmentsComponent from "@/components/features/organizationManagement/DepartmentsComponent";
import UsersComponent from "@/components/features/organizationManagement/UsersComponent";
import RolesComponent from "@/components/features/organizationManagement/RolesComponent";
import InvitationsComponent from "@/components/features/organizationManagement/InvitationsComponent";
import CardItem from "@/components/features/organizationManagement/CardItem";
import { apiCall } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";
import Button from "@/components/ui/Button";
import { GoPlus } from "react-icons/go";
import { usePermissions } from "@/contexts/PermissionContext";

const Page = () => {
  const [activeCard, setActiveCard] = useState(0);
  const [cardCounts, setCardCounts] = useState({
    users: 0,
    departments: 0,
    roles: 0,
    invitations: 0,
  });
  const [modalType, setModalType] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { canWrite } = usePermissions();

  const handleCardClick = (index) => {
    setActiveCard(index);
  };

  const GetDashboardCard = async () => {
    try {
      const response = await apiCall("/departments/dashboard");
      const counts = {
        users: response?.user_count || 0,
        departments: response?.department_count || 0,
        roles: response?.role_count || 0,
        invitations:
          (response?.invitations?.accepted || 0) +
          (response?.invitations?.pending || 0),
      };

      setCardCounts(counts);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  useEffect(() => {
    GetDashboardCard();
  }, []);

  const cardData = [
    {
      title: "Departments",
      icon: "/assets/organization-icons/Departments.png",
      count: cardCounts.departments,
    },
    {
      title: "Users",
      icon: "/assets/organization-icons/Users.png",
      count: cardCounts.users,
    },
    {
      title: "Roles",
      icon: "/assets/organization-icons/Roles.png",
      count: cardCounts.roles,
    },
    {
      title: "Invitations",
      icon: "/assets/organization-icons/Invitations.png",
      count: cardCounts.invitations,
    },
  ];

  const openModal = async (type, dept = null) => {
    setModalType(type);
  };

  const renderComponent = (index) => {
    switch (index) {
      case 0:
        return (
          <DepartmentsComponent
            setModalType={setModalType}
            modalType={modalType}
            GetDashboardCard={GetDashboardCard}
          />
        );
      case 1:
        return <UsersComponent GetDashboardCard={GetDashboardCard} />;
      case 2:
        return (
          <RolesComponent
            GetDashboardCard={GetDashboardCard}
            setModalType={setModalType}
            modalType={modalType}
          />
        );
      case 3:
        return (
          <InvitationsComponent
            setIsModalOpen={setIsModalOpen}
            isModalOpen={isModalOpen}
            GetDashboardCard={GetDashboardCard}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex">
      <div className="h-full w-full">
        <div className="flex flex-col justify-between gap-4 border-b border-borderheader items-center pr-6 py-2 sm:flex-row">
          <Header
            title="Organization Management"
            subtitle="Set up your sub-organization, customize branding, and configure communication channels for unified operations."
          />
          <div className="">
            {(activeCard === 0 || activeCard === 2 || activeCard === 3) && (
              <div className="flex items-center gap-3">
                {activeCard === 0 && (
                  <div className="flex justify-center">
                    <Button
                      variant="secondary"
                      onClick={() => openModal("add")}
                      disabled={!canWrite("/apps/organization-management")}
                    >
                      <GoPlus size={20} />
                      Departments
                    </Button>
                  </div>
                )}

                {activeCard === 2 && (
                  <div className="flex items-center gap-3.5">
                    <Button
                      variant="secondary"
                      onClick={() => {
                        openModal("add");
                      }}
                      className="w-24"
                      disabled={!canWrite("/apps/organization-management")}
                    >
                      <GoPlus size={20} /> Roles
                    </Button>
                  </div>
                )}

                {(activeCard === 0 || activeCard === 3) && (
                  <div className="flex justify-center">
                    <Button
                      variant="secondary"
                      onClick={() => {
                        setActiveCard(3);
                        setIsModalOpen(true);
                      }}
                    >
                      <GoPlus size={20} /> Invite User
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-4 px-6 sm:grid-cols-2 lg:grid-cols-4 w-full  overflow-y-auto custom-scrollbar">
          {cardData.map((card, index) => (
            <CardItem
              key={index}
              index={index}
              title={card.title}
              icon={card.icon}
              count={card.count}
              activeCard={activeCard}
              onClick={handleCardClick}
            />
          ))}
        </div>

        {activeCard !== null && (
          <div className="  mt-4">{renderComponent(activeCard)}</div>
        )}
      </div>
    </div>
  );
};

export default Page;
