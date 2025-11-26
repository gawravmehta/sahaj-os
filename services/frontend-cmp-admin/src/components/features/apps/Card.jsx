"use client";
import { useOrg } from "@/components/shared/OrgContext";
import { usePermissions } from "@/contexts/PermissionContext";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { GoLock } from "react-icons/go";
import { RxCross2 } from "react-icons/rx";

const Card = ({ dashboardData }) => {
  const router = useRouter();
  const [showToast, setShowToast] = useState(true);
  const { orgDetails } = useOrg();
  const { canRead } = usePermissions();

  useEffect(() => {
    const logoUrl = orgDetails?.org_info?.df_logo_url;
    if ((orgDetails && !logoUrl) || logoUrl?.trim() === "") {
      setShowToast(true);
    } else {
      setShowToast(false);
    }
  }, [orgDetails]);

  useEffect(() => {
    if (showToast) {
      const timer = setTimeout(() => setShowToast(false), 10000);
      return () => clearTimeout(timer);
    }
  }, [showToast]);

  return (
    <div className="relative">
      {showToast && (
        <div className="fixed top-4 left-1/2 z-50 w-[90%] max-w-md -translate-x-1/2 bg-amber-50 border border-amber-300 text-amber-900 shadow-lg animate-fadeIn">
          <div
            onClick={() => router.push("/setting")}
            className="flex items-start justify-between p-4 cursor-pointer"
          >
            <div className="flex items-start space-x-3">
              <div className="mt-0.5 text-amber-500">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 9v2m0 4h.01M12 5a7 7 0 00-7 7v5a2 2 0 002 2h10a2 2 0 002-2v-5a7 7 0 00-7-7z"
                  />
                </svg>
              </div>
              <div>
                <p className="font-semibold text-amber-800">
                  Complete your organization setup
                </p>
                <p className="text-sm text-amber-700">
                  Please add your <span className="font-medium">logo</span>,
                  configure <span className="font-medium">SMTP</span> and{" "}
                  <span className="font-medium">SMS</span> settings before
                  continuing.
                </p>
              </div>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowToast(false);
              }}
              className="text-amber-500 hover:text-amber-700 p-1 rounded-full hover:bg-amber-100 transition"
            >
              <RxCross2 size={18} />
            </button>
          </div>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 ">
        {dashboardData?.map((data, i) => {
          const hasAccess = canRead(data.route);
          return (
            <div
              onClick={() => router.push(data.route)}
              key={i}
              className="group relative cursor-pointer border border-primary border-opacity-0 bg-white px-3 py-5 shadow-md hover:border-opacity-100 hover:shadow-none"
            >
              {!hasAccess && (
                <div className="absolute top-2 right-2 ">
                  <GoLock className="h-4 w-4 text-yellow-500" />
                </div>
              )}
              <div className="relative flex flex-col gap-1 pl-2">
                <div className="flex flex-col">
                  <div className="flex justify-between pt-1 text-3xl">
                    <Image
                      src={(data.image_logo || "").trim()}
                      alt="app image"
                      height={100}
                      width={100}
                      className="h-12 w-12"
                    />
                  </div>
                  <h2 className="mt-3 text-lg">{data.title}</h2>
                </div>
                <p className="text-xs text-subHeading">{data.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Card;
