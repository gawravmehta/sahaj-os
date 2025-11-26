"use client";

import { useRouter } from "next/navigation";
import { FaRegUser } from "react-icons/fa";
import { MdOutlineEmail } from "react-icons/md";
import { IoCallOutline } from "react-icons/io5";
import Image from "next/image";
import { useState, useEffect } from "react";
import { dashboardCardDetails } from "@/constants/dashboardCardDetails";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";

export default function Home() {
  const router = useRouter();
  const [currentState, setCurrentState] = useState("My Consent");
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dashboardCounts, setDashboardCounts] = useState({});

  const fetchUserData = async () => {
    try {
      const response = await apiCall(`/api/v1/auth/me`);

      const data = response;
      setUserData(data.user);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const fetchDashboardCounts = async () => {
    try {
      const response = await apiCall(
        `/api/v1/preferences/preference-counts/by-dp`
      );
      setDashboardCounts(response);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchUserData();
    fetchDashboardCounts();
  }, []);

  const handleCardClick = (title) => {
    if (title === "Data Principal Access Request") {
      router.push("/data-rights");
      return;
    } else {
      router.push("/manage-preference");
      return;
    }
  };

  return (
    <div className=" h-screen">
      <div className="max-w-[1200px] mx-auto px-6 pt-20">
        <div className="grid lg:grid-cols-3 gap-3">
          <div className="lg:col-span-2">
            <div className="grid sm:grid-cols-2 gap-3">
              {dashboardCardDetails.map((card) => (
                <div
                  key={card.title}
                  onClick={() => handleCardClick(card.title)}
                  className={`group cursor-pointer border border-transparent bg-white px-3 py-5 hover:border hover:border-primary shadow-sm hover:border-opacity-0 hover:shadow-none ${
                    currentState === card.title ? "bg-white" : "bg-white"
                  }`}
                >
                  <div className="flex flex-col ">
                    <div className="">
                      <Image
                        src={card.image}
                        alt="icon"
                        width={100}
                        height={100}
                        className="size-10  object-fill"
                      />
                    </div>

                    <div className="text-[16px] text-heading mt-2">
                      {card.title}
                    </div>

                    <div className="text-[12px] text-subHeading mt-1">
                      {card.description}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-6 flex gap-4 text-center shadow-md border border-transparent transition hover:border hover:border-blue-950 bg-white">
            {loading ? (
              <div className="flex justify-center items-center w-full h-full">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
              </div>
            ) : (
              <div className="flex flex-col items-center w-full gap-2">
                <div className="flex  items-center w-full gap-3">
                  <div className="w-16 h-16 rounded-full border flex items-center justify-center border-gray-200 mb-4 flex-shrink-0">
                    <Image
                      src="/dashboard/user.png"
                      alt="icon"
                      width={100}
                      height={100}
                      className="size-10  object-fill"
                    />
                  </div>
                  <div className="text-left ">
                    <span className="text-[12px] text-[#000000]">
                      Data Principal ID:{" "}
                      {userData?.dp_id?.length > 22
                        ? `${userData.dp_id.slice(0, 22)}...`
                        : userData?.dp_id ?? "N/A"}
                    </span>

                    {userData?.email ? (
                      <div className="flex items-center gap-2 text-xs mb-2 mt-1 text-subText">
                        <MdOutlineEmail className="" />
                        <span className="">{userData?.email}</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 text-xs mb-2 text-subText">
                        <IoCallOutline className="" />
                        <span>{userData?.mobile}</span>
                      </div>
                    )}

                    <div className="text-green-600 text-sm">
                      {userData?.is_existing ? "Active" : "Inactive"}
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-2 grid-rows-2  px-4 py-2 w-full h-full">
                  <div className=" border-r-3 border-b-3  border-[#F0F0F0] py-2">
                    <h1 className="text-[36px] text-primary">
                      {dashboardCounts?.consent_count}
                    </h1>
                    <p className="text-[#3D3D3D] text-[12px]">Total Consents</p>
                  </div>
                  <div className=" border-b-3 border-[#F0F0F0] py-2">
                    <h1 className="text-[36px] text-primary">
                      {dashboardCounts?.cp_count}
                    </h1>
                    <p className="text-[#3D3D3D] text-[12px]">
                      {" "}
                      Total Collection Points
                    </p>
                  </div>
                  <div className=" border-r-3 border-[#F0F0F0] py-2">
                    <h1 className="text-[36px] text-primary">
                      {dashboardCounts?.dpar_count}
                    </h1>
                    <p className="text-[#3D3D3D] text-[12px]">
                      Total DPAR Requests
                    </p>
                  </div>
                  <div className=" py-2">
                    {" "}
                    <h1 className="text-[36px] text-primary">
                      {dashboardCounts?.grievance_count}
                    </h1>
                    <p className="text-[#3D3D3D] text-[12px]">
                      Total Raised Grievances
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
