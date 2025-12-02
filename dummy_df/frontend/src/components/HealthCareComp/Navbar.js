"use client";

import Link from "next/link";
import React, { useState } from "react";
import LoginRegisterModal from "./LoginRegisterModal"; // Import the LoginRegisterModal component
import { usePathname } from "next/navigation";
import { FaBell, FaUserCircle } from "react-icons/fa";

const Navbar = () => {
  const [showModal, setShowModal] = useState(false);

  const pathname = usePathname();
  const [isDropdownOpen, setDropdownOpen] = useState(false);

  const toggleDropdown = () => {
    setDropdownOpen((prevState) => !prevState); // Toggle dropdown visibility
  };

  return (
    <div className="fixed top-0 left-0 right-0 z-20  ">
      <nav className="bg-white border-gray-200 shadow-sm">
        <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
          <a
            href="/health_care"
            className="flex items-center space-x-3 rtl:space-x-reverse"
          >
            <span className="self-center text-2xl font-semibold whitespace-nowrap">
              <span className="text-blue-600">Health</span>Care
            </span>
          </a>
          <button
            data-collapse-toggle="navbar-default"
            type="button"
            className="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200"
            aria-controls="navbar-default"
            aria-expanded="false"
          >
            <svg
              className="w-5 h-5"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 17 14"
            >
              <path
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M1 1h15M1 7h15M1 13h15"
              />
            </svg>
          </button>
          <div className="hidden w-full md:block md:w-auto" id="navbar-default">
            <ul className="font-medium flex flex-col p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-white">
              <li>
                <Link href="/health_care">Home</Link>
              </li>
              <li>
                <Link href="/health_care/services">Services</Link>
              </li>

              <li>
                <Link href="/health_care/preference_center">
                  Preference Center{" "}
                </Link>
              </li>
              <li>
                <Link
                  href="/health_care/book_appointment"
                  className="px-3 py-2 rounded-lg bg-blue-700 text-white"
                >
                  Book Appointment
                </Link>
              </li>
              <li>
                <button
                  onClick={() => setShowModal(true)}
                  className={`${showModal ? "text-blue-600 " : ""}`}
                >
                  Login
                </button>
              </li>
              <div className={`flex items-center gap-4 `}>
                {/* <div className="">
              <FaBell size={22} />
            </div> */}
                <div className="relative">
                  <div className="relative">
                    <div className="cursor-pointer" onClick={toggleDropdown}>
                      <FaBell size={22} />
                    </div>

                    {isDropdownOpen && (
                      <div className="absolute right-0 mt-2 w-96 z-50 bg-white shadow-2xl rounded-lg px-4 py-4">
                        <Link
                          href="/health_care/preference_center"
                          onClick={toggleDropdown}
                        >
                          <div className="p-2 border-b border-gray-400 cursor-pointer">
                            <h1 className="text-gray-500 font-normal text-xs">
                              22, August, 2024
                            </h1>
                            <h1 className="text-[#FF0000] font-semibold text-sm">
                              Your consent for medical records access has
                              expired. Please reconsent to continue receiving
                              health services.
                            </h1>
                          </div>
                        </Link>
                        <Link
                          href="/health_care/preference_center"
                          onClick={toggleDropdown}
                        >
                          <div className="p-2 border-b border-gray-400 cursor-pointer">
                            <h1 className="text-gray-500 font-normal text-xs">
                              22, August, 2024
                            </h1>
                            <h1 className="text-gray-600 font-semibold text-sm">
                              Your lab test results for blood sugar are now
                              available. Log in to your health portal to view.
                            </h1>
                          </div>
                        </Link>
                        <Link
                          href="/health_care/preference_center"
                          onClick={toggleDropdown}
                        >
                          <div className="p-2 border-b border-gray-400 cursor-pointer">
                            <h1 className="text-gray-500 font-normal text-xs">
                              23, August, 2024
                            </h1>
                            <h1 className="text-[#FF0000] font-semibold text-sm">
                              Your consent for health record sharing has
                              expired. Reconsent to continue with your ongoing
                              care plan.
                            </h1>
                          </div>
                        </Link>
                        <Link
                          href="/health_care/preference_center"
                          onClick={toggleDropdown}
                        >
                          <div className="p-2 border-b border-gray-400 cursor-pointer">
                            <h1 className="text-gray-500 font-normal text-xs">
                              23, August, 2024
                            </h1>
                            <h1 className="text-gray-600 font-semibold text-sm">
                              Reminder: Your follow-up appointment with Dr.
                              Smith is scheduled for tomorrow at 10:00 AM.
                            </h1>
                          </div>
                        </Link>
                        <Link
                          href="/health_care/preference_center"
                          onClick={toggleDropdown}
                        >
                          <div className="p-2 border-b border-gray-400 cursor-pointer">
                            <h1 className="text-gray-500 font-normal text-xs">
                              23, August, 2024
                            </h1>
                            <h1 className="text-[#FF0000] font-semibold text-sm">
                              Your consent for health insurance information
                              sharing has expired. Reconsent to continue
                              receiving health coverage.
                            </h1>
                          </div>
                        </Link>
                        <Link
                          href="/health_care/preference_center"
                          onClick={toggleDropdown}
                        >
                          <div className="p-2 border-gray-400 cursor-pointer">
                            <h1 className="text-gray-500 font-normal text-xs">
                              24, August, 2024
                            </h1>
                            <h1 className="text-gray-600 font-semibold text-sm">
                              Your prescription for blood pressure medication is
                              ready for refill.
                            </h1>
                          </div>
                        </Link>
                      </div>
                    )}
                  </div>
                </div>
                <Link href="/health_care/preference_center">
                  <FaUserCircle size={25} />
                </Link>
              </div>
            </ul>
          </div>
        </div>
      </nav>

      {/* Modal for Login */}
      {showModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white p-5 max-w-4xl relative">
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-2 text-3xl  right-3 text-gray-500 hover:text-gray-700"
            >
              &times;
            </button>
            <LoginRegisterModal setShowModal={setShowModal} />
          </div>
        </div>
      )}
    </div>
  );
};

export default Navbar;
