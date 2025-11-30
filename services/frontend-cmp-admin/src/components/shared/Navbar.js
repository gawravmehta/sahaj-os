"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import { FaRegUserCircle } from "react-icons/fa";
import { GiHamburgerMenu } from "react-icons/gi";
import { MdLogout, MdOutlineEmail } from "react-icons/md";
import { LuBell } from "react-icons/lu";
import { PiChecks } from "react-icons/pi";
import { BsFileEarmarkCheck, BsFileEarmarkX } from "react-icons/bs";
import { GoOrganization } from "react-icons/go";
import { HiOutlineSpeakerWave } from "react-icons/hi2";
import { menuItems } from "@/constants/navbarMenu";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import TimeAgo from "./TimeAgo";
import Cookies from "js-cookie";
import { EventSourcePolyfill } from "event-source-polyfill";

const baseURL = process.env.NEXT_PUBLIC_ADMIN_URL || "";
const Navbar = ({ showSidebar, setShowSidebar }) => {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);

  const [notificationData, setNotificationData] = useState([]);
  const [notificationCount, setNotificationCount] = useState(0);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [notificationModal, setNotificationModal] = useState(false);

  const userRef = useRef();
  const notificationRef = useRef();

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

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

  const fetchNotifications = async (currentPage = 1) => {
    try {
      setLoading(true);
      const response = await apiCall(
        `/notifications/notifications?page=${currentPage}&limit=10`
      );

      if (response?.data?.length > 0) {
        setNotificationData((prev) =>
          currentPage === 1 ? response.data : [...prev, ...response.data]
        );
        setNotificationCount(response?.unseen_notification_count);
      }

      if (response?.data?.length < 10) {
        setHasMore(false);
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error("Error fetching notifications:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleReadNotification = async (notificationId) => {
    try {
      const response = await apiCall(
        `/notifications/read-notification/${notificationId}`,
        {
          method: "PATCH",
        }
      );

      if (notificationCount > 0) {
        setNotificationCount(notificationCount - 1);
      }

      if (response) {
        setNotificationData((prev) =>
          prev.map((n) =>
            n._id === notificationId ? { ...n, is_read: true } : n
          )
        );
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleMarkAsRead = async () => {
    try {
      const response = await apiCall(`/notifications/mark-all-read`, {
        method: "GET",
      });
      if (response) {
        toast.success(response.message);
        fetchNotifications(1);
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error("Error marking notification as read:", error);
    }
  };

  const handleScroll = (e) => {
    const bottomReached =
      e.target.scrollTop + e.target.clientHeight >= e.target.scrollHeight - 50;

    if (bottomReached && hasMore && !loading) {
      const nextPage = page + 1;
      fetchNotifications(nextPage);
      setPage(nextPage);
    }
  };

  useEffect(() => {
    fetchNotifications(1);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        userRef.current &&
        !userRef.current.contains(event.target) &&
        !event.target.closest(".user-toggle-button")
      ) {
        setIsOpen(false);
      }
      if (
        notificationRef.current &&
        !notificationRef.current.contains(event.target) &&
        !event.target.closest(".notification-toggle-button")
      ) {
        setNotificationModal(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  useEffect(() => {
    const token = Cookies.get("access_token");
    if (!token) return;

    const evtSource = new EventSourcePolyfill(
      `${baseURL}/notifications/notifications/stream`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    evtSource.addEventListener("new_notification", (event) => {
      const notification = JSON.parse(event.data);

      setNotificationData((prev) => [notification, ...prev]);
      if (!notification.is_read) {
        setNotificationCount((prev) => prev + 1);
      }
      toast.success(notification.notification_title || "New notification!");
    });

    evtSource.onerror = (err) => {
      console.error("❌ SSE connection error:", err);
      evtSource.close();
    };

    return () => {
      evtSource.close();
    };
  }, [baseURL]);

  const getNotificationStyle = (notification) => {
    if (notification?.category === "user_invitation") {
      return "text-primary bg-[#E5EAF6]";
    } else if (
      notification?.category === "bulk_import" &&
      notification?.notification_title === "Bulk Import Failed"
    ) {
      return "bg-[#FBEAEA] text-[#FE4343]";
    } else {
      return "text-[#06A42A] bg-[#E0FFE7]";
    }
  };

  const getNotificationIcon = (notification) => {
    if (notification?.category === "user_invitation") {
      return <MdOutlineEmail />;
    } else if (
      notification?.category === "bulk_import" &&
      notification?.notification_title === "Bulk Import Failed"
    ) {
      return <BsFileEarmarkX />;
    } else if (notification?.category === "organization") {
      return <GoOrganization />;
    } else if (
      notification?.category === "registration" &&
      notification?.notification_title === "Welcome to Our Platform!"
    ) {
      return <HiOutlineSpeakerWave />;
    } else {
      return <BsFileEarmarkCheck />;
    }
  };

  return (
    <div className="fixed top-0 z-50 flex h-12 w-full items-center justify-between bg-white px-4 shadow-[0_5px_2px_-4px_rgba(0,0,0,0.1)]">
      <Link href="/apps">
        <h1 className="tracking-tight font-semibold text-3xl text-[#13132A]">
          SAHAJ
        </h1>
      </Link>

      <div className="flex gap-4">
        <Link
          href="/apps"
          className="w-full bg-primary hover:bg-hover px-1 text-white"
        >
          <div className="group relative flex h-7 items-center gap-2 rounded-sm px-2">
            <span>
              <Image
                src="/assets/sidebar-icons/app.png"
                height={100}
                width={100}
                className="size-3"
                alt="apps icon"
              />
            </span>
            <span className="text-xs">Apps</span>
          </div>
        </Link>

        <button
          onClick={() => setNotificationModal(!notificationModal)}
          className="notification-toggle-button relative flex items-center pr-1 text-lg cursor-pointer"
        >
          <LuBell
            size={24}
            className={`${notificationModal ? "text-black" : "text-[#9f9f9f]"
              } hover:text-hover`}
          />
          {notificationCount > 0 && (
            <span
              className={`absolute -right-0.5 -top-0.5 flex size-5 items-center justify-center rounded-full bg-red-500 ${notificationCount > 9 ? "p-2 tracking-tighter" : ""
                } text-[10px] text-white`}
            >
              {notificationCount > 9 ? "9+" : notificationCount}
            </span>
          )}
        </button>

        {notificationModal && (
          <div className="absolute right-16 z-50 mt-12 flex w-80 flex-col items-start border border-[#C7CFE2] bg-[#f9fcff] shadow-lg">
            <div
              ref={notificationRef}
              className="flex w-full flex-col text-start text-sm text-[#242424]"
            >
              <div className="flex items-center justify-between border-b border-[#D2E1FB66] p-2 px-3">
                <p className="text-lg">Notifications</p>
                <button
                  onClick={handleMarkAsRead}
                  className={`flex items-center cursor-pointer gap-2 ${notificationCount > 0 && "text-primary"
                    } `}
                >
                  <PiChecks size={20} />
                  Mark all as read
                </button>
              </div>
              <div
                onScroll={handleScroll}
                className="custom-scrollbar h-96 overflow-y-auto overflow-x-hidden"
              >
                <ul className="w-full">
                  {notificationData.map((notification) => (
                    <li
                      key={notification._id}
                      onClick={() => {
                        if (!notification.is_read) {
                          handleReadNotification(notification._id);
                        }
                      }}
                      className={`group relative flex cursor-pointer gap-3 border-b border-[#D2E1FB66] p-2 px-3 ${notification.is_read
                          ? "bg-white hover:bg-gray-100"
                          : "bg-[#ECF6FF] hover:bg-[#cee7fe]"
                        }`}
                    >
                      <span
                        className={`flex h-8 w-8 items-center justify-center rounded-full p-1 text-xl ${getNotificationStyle(
                          notification
                        )}`}
                      >
                        {getNotificationIcon(notification)}
                      </span>
                      <div className="flex items-start justify-between gap-2 pb-3">
                        <div className="flex flex-col">
                          <span>{notification.notification_title}</span>
                          <span
                            className={`text-xs ${notification.is_read
                                ? "text-subHeading group-hover:text-gray-600"
                                : "text-gray-600"
                              }`}
                          >
                            {notification.notification_message}
                          </span>
                        </div>
                        {!notification.is_read && (
                          <span className="absolute right-2 top-[31%] mt-1 size-2 rounded-full bg-primary" />
                        )}
                        <TimeAgo
                          timestamp={notification?.created_at}
                          className="absolute bottom-0 right-2"
                        />
                      </div>
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

        <div className="relative flex">
          <div onClick={toggleDropdown} className="flex cursor-pointer gap-2">
            <span className="user-toggle-button flex items-center pr-2 text-lg">
              <FaRegUserCircle
                size={24}
                className={`${isOpen ? "text-black" : "text-[#9f9f9f]"
                  } hover:text-hover`}
              />
            </span>
          </div>

          {isOpen && (
            <div
              ref={userRef}
              className="absolute right-2 z-50 mt-12 flex w-[195px] flex-col items-start border border-[#c7cfe2] bg-[#f9fcff] shadow-lg"
            >
              <>
                {menuItems.map(({ href, label, icon, external }) => (
                  <Link
                    key={href}
                    href={href}
                    target={external ? "_blank" : "_self"}
                    className="flex w-full items-center gap-2 px-3.5 py-2 text-start text-sm text-[#242424] hover:bg-primary hover:text-white"
                  >
                    {icon} {label}
                  </Link>
                ))}
              </>
              <button
                onClick={handleLogOut}
                className="flex w-full items-center gap-2 px-3.5 py-2 text-start text-sm text-[#242424] hover:bg-primary hover:text-white"
              >
                <MdLogout size={18} /> Logout
              </button>
            </div>
          )}
        </div>

        <div className="flex items-center lg:hidden">
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="text-[#132f5f]"
          >
            <GiHamburgerMenu size={25} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
