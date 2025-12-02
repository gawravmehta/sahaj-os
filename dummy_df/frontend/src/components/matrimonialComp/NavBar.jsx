"use client";
import { useState } from "react";
import { IoIosArrowDown } from "react-icons/io";
import { HiOutlineUserGroup } from "react-icons/hi";
import Link from "next/link";
import RegisterForm from "./RegisterForm";
import PersonIcon1 from "./PersonIcon1";
import ShieldIcon from "./ShieldIcon";
import SinglePersonIcon from "./PrivacyControlIcon";
import PrivacyControlIcon from "./PrivacyControlIcon";
import LoginForm from "./LoginForm";

const NavBar = () => {
  const [profileFor, setProfileFor] = useState("");
  const [emailAddress, setEmailAddress] = useState("");
  const [mobileNum, setMobileNum] = useState("");
  const [password, setPassword] = useState("");

  const updateFormData = () => {
    console.log(profileFor);

    setProfileFor("son");
    setEmailAddress("gewgawrav@gmail.com");
    setMobileNum("8770467824");
    setPassword(123456789);
  };

  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
  const [isSearchDropdownOpen, setIsSearchDropdownOpen] = useState(false);
  const [showLoginForm, setShowLoginForm] = useState(false);

  return (
    <>
      <button
        onClick={updateFormData}
        className="px-6 py-3 absolute top-2 text-pink-600 hover:text-white  cursor-pointer right-10 border border-pink-600 hover:bg-pink-700 rounded-lg z-50"
      >
        Fill Data
      </button>
      <header className="bg-slate-700 shadow fixed top-0 left-0 right-0 z-50 mx-64 ">
        <div className="flex justify-between items-center  h-16   mx-auto ">
          <div className="bg-white text-center h-16 w-32 flex items-center justify-center">
            <span className="text-xl font-bold text-pink-600 text-center">
              Soul Match
            </span>
          </div>
          <div className="flex items-center space-x-8 px-4">
            <div
              onMouseLeave={() => setIsProfileDropdownOpen(false)}
              onMouseEnter={() => setIsProfileDropdownOpen(true)}
              className="relative"
            >
              <span className="cursor-pointer flex items-center text-white">
                BROWSE PROFILES BY <IoIosArrowDown className="ml-1" />
              </span>
              {isProfileDropdownOpen && (
                <div
                  id="profileOption"
                  className="absolute left-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden transition-all duration-300 z-10"
                >
                  <ul className="py-2">
                    <li>
                      <Link href="/profiledetails">
                        <div className="block px-4 py-2 hover:bg-gray-100">
                          Soul Match
                        </div>
                      </Link>
                    </li>
                    <li>
                      <Link href="/help">
                        <div className="block px-4 py-2 hover:bg-gray-100">
                          Soul Match
                        </div>
                      </Link>
                    </li>
                    <li>
                      <div className="block px-4 py-2 hover:bg-gray-100 cursor-pointer">
                        Soul Match
                      </div>
                    </li>
                  </ul>
                </div>
              )}
            </div>

            <div
              className="relative"
              onMouseLeave={() => setIsSearchDropdownOpen(false)}
              onMouseEnter={() => setIsSearchDropdownOpen(true)}
            >
              <span className="cursor-pointer flex items-center text-white">
                SEARCH <IoIosArrowDown className="ml-1" />
              </span>
              {isSearchDropdownOpen && (
                <div
                  id="SearchOption"
                  className="absolute left-0 mt-2 bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden transition-all duration-300 z-10"
                >
                  <ul className="py-2">
                    <li>
                      <Link href="/profiledetails">
                        <div className="block px-4 py-2 hover:bg-gray-100">
                          Soul Match
                        </div>
                      </Link>
                    </li>
                    <li>
                      <Link href="/help">
                        <div className="block px-4 py-2 hover:bg-gray-100">
                          Soul Match
                        </div>
                      </Link>
                    </li>
                    <li>
                      <div className="block px-4 py-2 hover:bg-gray-100 cursor-pointer">
                        Soul Match
                      </div>
                    </li>
                  </ul>
                </div>
              )}
            </div>

            <div className="cursor-pointer text-white">
              <span>HELP</span>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              className="cursor-pointer px-4 py-2 bg-slate-800 text-white hover:bg-slate-600"
              onClick={() => setShowLoginForm(true)}
            >
              <span>Login</span>
            </button>
            <button
              className="cursor-pointer px-4 py-2 bg-slate-800 text-white hover:bg-slate-600 mx-4"
              onClick={() => setShowLoginForm(false)}
            >
              <span>REGISTER</span>
            </button>
          </div>
        </div>
      </header>

      <div className="text-center py-6 flex justify-between  mt-10 px-64 ">
        <div className="flex flex-col items-start justify-end text-white ">
          <h1 className="text-5xl font-bold mb-4">Now, chat for free!</h1>
          <span className="text-lg ">
            Finding your perfect match just became easier
          </span>
        </div>
        <div className="mb-14">
          {showLoginForm ? (
            <LoginForm
              profileFor1={profileFor}
              emailAddress={emailAddress}
              mobileNum={mobileNum}
              password1={password}
            />
          ) : (
            <RegisterForm
              profileFor1={profileFor}
              emailAddress={emailAddress}
              mobileNum={mobileNum}
              password1={password}
            />
          )}
        </div>
      </div>

      <div className="bg-gray-100    px-16 mx-64  ">
        <div className="pt-6">
          <div className="">
            <span className="text-base text-gray-700 ">
              MORE THAN 20 YEARS OF
            </span>
          </div>
          <h4 className="text-2xl font-bold mb-8">
            Bringing People <span className="text-pink-500">Together</span>
          </h4>
        </div>

        <div className="flex justify-center space-x-12">
          <div className="    ">
            <div className=" mb-4 flex ">
              <PersonIcon1 />
            </div>
            <h6 className="text-base font-semibold mb-2">
              100% Manually Screened Profiles
            </h6>
            <div className="w-16 h-1 bg-pink-500 mb-1"></div>
            <div className="text-gray-700">
              <span>
                Search by location, community, profession & more from lakhs of
                active profiles
              </span>
            </div>
          </div>

          <div className="">
            <div className="text-pink-500 text-4xl mb-4">
              <ShieldIcon />
            </div>
            <h6 className="text-base font-semibold mb-2">
              Verification by Personal Visit
            </h6>
            <div className="w-16 h-1 bg-pink-500  mb-1"></div>
            <div className="text-gray-700">
              <span>
                Special listing of profiles verified by our agents through
                personal visits
              </span>
            </div>
          </div>

          <div className="">
            <div className="text-pink-500 text-4xl mb-4">
              <PrivacyControlIcon />
            </div>
            <h6 className="text-base font-semibold mb-2">
              Control over Privacy
            </h6>
            <div className="w-16 h-1 bg-pink-500  mb-1"></div>
            <div className="text-gray-700">
              <span>
                Restrict unwanted access to contact details & photos/videos
              </span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default NavBar;
