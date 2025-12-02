// components/Navbar.js
"use client";
import Link from "next/link";
import { FaBell } from "react-icons/fa";
import React, { useState } from "react";
import { FiLogOut } from "react-icons/fi";

const Navbar = () => {
  const [isDropdownOpen, setDropdownOpen] = useState(false); // State for dropdown visibility

  const toggleDropdown = () => {
    setDropdownOpen((prevState) => !prevState);
    // Toggle dropdown visibility
  };

  return (
    <nav>
      <nav className="border-gray-200 bg-gray-50 shadow-sm ">
        <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
          <a
            href="/megamart"
            className="flex items-center space-x-3 rtl:space-x-reverse"
          >
            <span className="self-center text-2xl font-semibold whitespace-nowrap ">
              MegaMart
            </span>
          </a>
          <button
            data-collapse-toggle="navbar-solid-bg"
            type="button"
            className="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 "
            aria-controls="navbar-solid-bg"
            aria-expanded="false"
          >
            <span className="sr-only">Open main menu</span>
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
          <div
            className="hidden w-full  md:block md:w-auto"
            id="navbar-solid-bg"
          >
            <div className="flex gap-5">
              <ul className="flex flex-col font-medium mt-4 rounded-lg bg-gray-50 md:space-x-8 rtl:space-x-reverse md:flex-row md:mt-0 md:border-0 md:bg-transparent ">
                <Link href="/megamart/landing/shopping">
                  <li
                    className="block py-2 px-3 md:p-0   rounded hover:text-gray-600  "
                    aria-current="page"
                  >
                    Shopping
                  </li>
                </Link>

                <Link href="/megamart/landing/profile">
                  <li className="block py-2 px-3 md:p-0  rounded hover:text-gray-600 ">
                    Profile
                  </li>
                </Link>

                <Link href="/megamart/landing/progressive">
                  <li className="block py-2 px-3 md:p-0  rounded hover:text-gray-600 ">
                    Progressive
                  </li>
                </Link>

                <Link href="/megamart/landing/preference">
                  <li className="block py-2 px-3 md:p-0  rounded hover:text-gray-600 ">
                    Preference
                  </li>
                </Link>
              </ul>
              <div className="relative">
                <div className="relative">
                  <div className="cursor-pointer" onClick={toggleDropdown}>
                    <FaBell size={22} />
                  </div>

                  {isDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-96 z-50 bg-white shadow-2xl rounded-lg px-4 py-4">
                      <Link
                        href="/megamart/landing/preference"
                        onClick={toggleDropdown}
                      >
                        <div className="p-2 border-b border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                            {" "}
                            22, August, 2024
                          </h1>
                          <h1 className="text-[#FF0000] font-semibold text-sm">
                            Your consent to participate in the MegaMart loyalty
                            program needs renewal. Please update to keep
                            enjoying member benefits.
                          </h1>
                        </div>
                      </Link>
                      <Link
                        href="/megamart/landing/preferencer"
                        onClick={toggleDropdown}
                      >
                        <div className="p-2 border-b border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                            {" "}
                            22, August, 2024
                          </h1>
                          <h1 className="text-gray-600 font-semibold text-sm">
                            New arrivals in the Electronics section! Check out
                            the latest gadgets and devices now available at
                            MegaMart.
                          </h1>
                        </div>
                      </Link>
                      <Link
                        href="/megamart/landing/preference"
                        onClick={toggleDropdown}
                      >
                        <div className="p-2 border-b border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                            {" "}
                            23, August, 2024
                          </h1>
                          <h1 className="text-[#FF0000] font-semibold text-sm">
                            Your consent for receiving promotional emails from
                            MegaMart has expired. Please update your preferences
                            to continue receiving the latest offers and
                            discounts.
                          </h1>
                        </div>
                      </Link>
                      <Link
                        href="/megamart/landing/preference"
                        onClick={toggleDropdown}
                      >
                        <div className="p-2 border-b border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                            {" "}
                            23, August, 2024
                          </h1>
                          <h1 className="text-gray-600 font-semibold text-sm">
                            Our customer support team is now available 24/7 to
                            assist you with any queries or concerns. Feel free
                            to reach out!
                          </h1>
                        </div>
                      </Link>
                      <Link
                        href="/megamart/landing/preference"
                        onClick={toggleDropdown}
                      >
                        <div className="p-2 border-b border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                            {" "}
                            23, August, 2024
                          </h1>
                          <h1 className="text-[#FF0000] font-semibold text-sm">
                            Confirm your consent to share purchase history with
                            MegaMart for better service and targeted offers.
                          </h1>
                        </div>
                      </Link>
                      <Link
                        href="/megamart/landing/preference"
                        onClick={toggleDropdown}
                      >
                        <div className="p-2 border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                            24, August, 2024
                          </h1>
                          <h1 className="text-gray-600 font-semibold text-sm">
                            MegaMart’s back-to-school sale starts tomorrow! Get
                            up to 30% off on school supplies and more.
                          </h1>
                        </div>
                      </Link>
                    </div>
                  )}
                </div>
              </div>
              <div className="">
                <Link href="/megamart">
                  <div className="flex items-center gap-3">
                    <span onClick={() => localStorage.clear()}>
                      <FiLogOut size={20} />
                    </span>
                  </div>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>
    </nav>

    // <nav classNameName="bg-gray-800 p-4 flex justify-end ">
    //   <div classNameName="mx-10 flex items-center justify-between">
    //     <div classNameName="flex items-center space-x-6">

    //       <Link href="/landing/shopping">
    //         <h classNameName="text-gray-300 hover:text-white transition duration-300">
    //           Shopping
    //         </h>
    //       </Link>

    //       <Link href="/landing/profile">
    //         <h classNameName="text-gray-300 hover:text-white transition duration-300">
    //           Profile
    //         </h>
    //       </Link>

    //       <Link href="/landing/progressive">
    //         <h classNameName="text-gray-300 hover:text-white transition duration-300">
    //           Progressive
    //         </h>
    //       </Link>

    //       <Link href="/landing/preference">
    //         <h classNameName="text-gray-300 hover:text-white transition duration-300">
    //           Preference
    //         </h>
    //       </Link>

    //     </div>
    //   </div>
    // </nav>
  );
};

export default Navbar;
