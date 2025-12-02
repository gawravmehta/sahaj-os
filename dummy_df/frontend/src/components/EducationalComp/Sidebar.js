"use client";
import React, { useState } from "react";
import { GiHamburgerMenu } from "react-icons/gi";
import Link from "next/link";
import { RxDashboard } from "react-icons/rx";
import { RxCross2 } from "react-icons/rx";
import { IoPersonOutline } from "react-icons/io5";
import { MdPayments } from "react-icons/md";
import { FiLogOut } from "react-icons/fi";
import { FaWpforms } from "react-icons/fa6";
import { MdOutlineEventNote } from "react-icons/md";

const Sidebar = ({ children }) => {
  const [showHamburger, setShowHamburger] = useState(false);

  const handleMenu = () => {
    setShowHamburger(!showHamburger);
  };

  return (
    <>
      <div className={`fixed`}>
        <div
          className={`custom-scrollbar min-h-screen flex flex-col justify-between text-white bg-[#1e273f] ${
            showHamburger ? "pt-[20px]" : "min-w-[240px] pt-[10px]"
          } bg-primary p-3`}
        >
          <div
            className={`flex flex-col mb-4 justify-between h-[80vh] ${
              showHamburger ? "gap-y-5 items-center" : "gap-y-4"
            }`}
          >
            <div className="flex flex-col gap-5">
              <div className="w-full h-12 relative">
                <button
                  onClick={handleMenu}
                  className={`${showHamburger ? "" : "absolute right-2 top-2"}`}
                >
                  {showHamburger ? (
                    <GiHamburgerMenu size={20} />
                  ) : (
                    <RxCross2 size={20} />
                  )}
                </button>
              </div>

              <Link href="/educational-Institute/dashboard">
                <div className="flex items-center gap-3">
                  <span>
                    <RxDashboard size={20} />
                  </span>
                  <span className={`${showHamburger ? "hidden" : ""} text-sm`}>
                    Dashboard
                  </span>
                </div>
              </Link>
              <Link href="/educational-Institute/application-form">
                <div className="flex items-center gap-3">
                  <span>
                    <MdOutlineEventNote size={20} />
                  </span>
                  <span className={`${showHamburger ? "hidden" : ""} text-sm`}>
                    Application Form
                  </span>
                </div>
              </Link>
              <Link href="/educational-Institute/exam-form">
                <div className="flex items-center gap-3">
                  <span>
                    <FaWpforms size={20} />
                  </span>
                  <span className={`${showHamburger ? "hidden" : ""} text-sm`}>
                    Exam Form
                  </span>
                </div>
              </Link>
              <Link href="/educational-Institute/profile">
                <div className="flex items-center gap-3">
                  <span>
                    <IoPersonOutline size={20} />
                  </span>
                  <span className={`${showHamburger ? "hidden" : ""} text-sm`}>
                    Profile
                  </span>
                </div>
              </Link>

              <Link href="/educational-Institute/payment">
                <div className="flex items-center gap-3">
                  <span>
                    <MdPayments size={20} />
                  </span>
                  <span className={`${showHamburger ? "hidden" : ""} text-sm`}>
                    Payment
                  </span>
                </div>
              </Link>
            </div>
            <div className="">
              <Link href="/educational-Institute">
                <div
                  className="flex items-center gap-3"
                  onClick={() => localStorage.clear()}
                >
                  <span>
                    <FiLogOut size={20} />
                  </span>
                  <span className={`${showHamburger ? "hidden" : ""} text-sm`}>
                    Logout
                  </span>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
      <div className={`${showHamburger ? "ml-12" : ""}`}>{children}</div>
    </>
  );
};

export default Sidebar;
