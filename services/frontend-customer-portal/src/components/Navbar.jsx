"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { FaBars } from "react-icons/fa";
import { LuBell } from "react-icons/lu";
import { PiChecks } from "react-icons/pi";
import { MdLogout, MdOutlineEmail } from "react-icons/md";
import Image from "next/image";
import toast from "react-hot-toast";
import CustomGoogleTranslate from "./CustomGoogleTranslate";
import { getErrorMessage } from "@/utils/errorHandler";
import { apiCall } from "@/hooks/apiCall";
import TimeAgo from "./ui/TimeAgo";
import { CiClock1 } from "react-icons/ci";

function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const sidebarRef = useRef(null);
  const notificationRef = useRef(null);

  const [navbar, setNavbar] = useState(false);
  const [activeTab, setActiveTab] = useState("");
  const [notificationModal, setNotificationModal] = useState(false);
  const [notificationData, setNotificationData] = useState([]);
  const [notificationCount, setNotificationCount] = useState(0);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const handleNavbar = () => setNavbar(!navbar);

  const handleLogOut = () => {
    document.cookie.split(";").forEach((cookie) => {
      const name = cookie.split("=")[0].trim();
      document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/`;
    });
    localStorage.clear();
    sessionStorage.clear();
    toast.success("Logged Out Successfully");
    router.push("/login");
    window.location.reload();
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  useEffect(() => {
    const routeToTab = {
      "/data-rights": "data-rights",
      "/past-request": "past-request",
      "/manage-preference": "manage-preference",
      "/manage-preference/update-preference": "manage-preference",
      "/raise-grievance": "raise-grievance",
    };
    setActiveTab(routeToTab[pathname] || "");
  }, [pathname]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        sidebarRef.current &&
        !sidebarRef.current.contains(event.target) &&
        !notificationRef.current?.contains(event.target)
      ) {
        setNavbar(false);
        setNotificationModal(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const fetchNotifications = async (currentPage = 1) => {
    try {
      setLoading(true);
      const res = await apiCall(
        `/api/v1/notifications/get-all-notifications?page=${currentPage}&limit=10`
      );

      const newItems = res?.items || [];

      if (newItems.length > 0) {
        setNotificationData((prev) =>
          currentPage === 1 ? newItems : [...prev, ...newItems]
        );
      }

      if (newItems.length < 10) {
        setHasMore(false);
      }

      const unreadCount = newItems.filter((n) => n.status === "unread").length;
      if (currentPage === 1) {
        setNotificationCount(unreadCount);
      }
    } catch (error) {
      console.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationClick = async (id, agreement_id, type) => {
    try {
      const res = await apiCall(
        `/api/v1/notifications/notifications/${id}/read`,
        {
          method: "POST",
        }
      );

      if (res) {
        fetchNotifications();

        if (type === "CONSENT_RENEWAL") {
          router.push(
            `/manage-preference/renew-consent?agreement_id=${agreement_id}`
          );
        } else {
          router.push(`/notification-information/${id}`);
        }
      } else {
        console.error("Failed to mark as read");
      }
    } catch (error) {
      console.error("Error marking as read:", error);
    }
  };

  const handleBellClick = () => {
    setNotificationModal((prev) => {
      const newState = !prev;
      if (newState) {
        setPage(1);
        setNotificationData([]);
        fetchNotifications(1);
      }
      return newState;
    });
  };

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    if (scrollHeight - scrollTop <= clientHeight + 10 && hasMore && !loading) {
      const nextPage = page + 1;
      fetchNotifications(nextPage);
      setPage(nextPage);
    }
  };

  const getNotificationStyle = (notification) =>
    notification.status ? "bg-gray-300" : "bg-blue-500";

  return (
    <header className="fixed top-0 left-0 z-10 bg-white w-full">
      <div className="max-w-[1800px] mx-auto w-full shadow-sm flex justify-between px-4 py-2 items-center">
        <Link href="/">
          <Image
            src="/concur-logo/logo-first.png"
            alt="logo"
            width={150}
            height={150}
            className="h-5 object-contain"
          />
        </Link>

        <div className="flex items-center">
          <div className="hidden md:flex space-x-2 text-sm font-medium">
            {[
              { href: "/raise-grievance", label: "Raise Grievance" },
              { href: "/past-request", label: "Past Request" },
              { href: "/data-rights", label: "Data Rights" },
              { href: "/manage-preference", label: "Preference Center" },
            ].map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                className={`py-2 px-3 ${
                  activeTab === href.slice(1)
                    ? "text-primary "
                    : "text-[#797878] hover:text-hover "
                }`}
              >
                {label}
              </Link>
            ))}
          </div>

          <div className="mx-3 ">
            <CustomGoogleTranslate />
          </div>

          <div className="relative  flex items-center">
            <button
              onClick={handleBellClick}
              className="relative pr-2 cursor-pointer"
            >
              <LuBell
                size={24}
                className={`${
                  notificationModal ? "text-[#5A5A5A]" : "text-gray-400"
                }`}
              />
              {notificationCount > 0 && (
                <span className="absolute -top-1 -right-1 flex items-center justify-center h-5 w-5 rounded-full bg-red-500 text-white text-[10px]">
                  {notificationCount > 9 ? "9+" : notificationCount}
                </span>
              )}
            </button>

            {notificationModal && (
              <div className="absolute right-5 z-50 top-10 flex w-80 flex-col items-start border border-[#C7CFE2] bg-[#f9fcff] shadow-lg">
                <div className="flex w-full flex-col text-start text-sm text-[#242424]">
                  <div
                    ref={notificationRef}
                    className="flex items-center justify-between border-b border-[#D2E1FB66] p-2 px-3"
                  >
                    <p className="text-lg font-semibold">Notifications</p>
                  </div>

                  <div
                    onScroll={handleScroll}
                    className="custom-scrollbar h-96 overflow-y-auto overflow-x-hidden"
                  >
                    <ul className="w-full ">
                      {notificationData.map((notification) => (
                        <li
                          key={notification._id}
                          onClick={() => {
                            if (notification.status === "unread") {
                              handleNotificationClick(
                                notification._id,
                                notification.agreement_id,
                                notification.type
                              );
                            }
                          }}
                          className={`group relative flex cursor-pointer gap-3 border-b border-[#D2E1FB66] p-2 px-3 ${
                            notification.status === "unread"
                              ? "bg-[#ECF6FF] hover:bg-[#cee7fe]"
                              : "bg-white hover:bg-gray-100"
                          }`}
                        >
                          <span
                            className={`flex h-8 w-8 items-center bg-gray-300 justify-center rounded-full p-1 text-xl ${getNotificationStyle(
                              notification
                            )}`}
                          >
                            {notification.type === "CONSENT_RENEWAL" ? (
                              <CiClock1 />
                            ) : (
                              <MdOutlineEmail />
                            )}
                          </span>

                          <div className="flex flex-col gap-0.5 pr-5 pb-3">
                            <span className="font-medium text-sm">
                              {notification.title}
                            </span>
                            <p className="text-xs text-subHeading line-clamp-2">
                              {notification.message}
                            </p>
                          </div>

                          {notification.status === "unread" && (
                            <span className="absolute right-2 top-4 size-2 rounded-full bg-primary" />
                          )}

                          <TimeAgo
                            timestamp={notification?.created_at}
                            className="absolute bottom-1  right-2 text-[10px] italic text-gray-500"
                          />
                        </li>
                      ))}
                    </ul>

                    {loading && (
                      <div className="w-full py-2 text-center text-xs">
                        Loading more...
                      </div>
                    )}
                    {!hasMore && (
                      <div className="w-full py-2 text-center text-xs text-gray-400">
                        No more notifications
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          <div onClick={handleNavbar} className="md:hidden pl-3 ">
            <FaBars className="text-xl cursor-pointer bg-[#5A5A5A]" />
          </div>

          <button
            onClick={handleLogOut}
            className="ml-3 flex items-center text-sm text-gray-600 cursor-pointer"
          >
            <MdLogout size={18} className="mr-1" />
          </button>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
