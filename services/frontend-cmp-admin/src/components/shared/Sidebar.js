"use client";
import { sidebarMenu } from "@/constants/sidebarMenu";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import React, { use, useEffect, useRef, useState } from "react";
import { FaRegUserCircle } from "react-icons/fa";
import { FaChevronDown, FaChevronRight } from "react-icons/fa6";
import { GiHamburgerMenu } from "react-icons/gi";
import { GoLock } from "react-icons/go";
import { RxCross2 } from "react-icons/rx";
import Navbar from "./Navbar";
import { useOrg } from "./OrgContext";
import { usePermissions } from "@/contexts/PermissionContext";
import { MdKeyboardArrowRight } from "react-icons/md";
import { MdKeyboardArrowLeft } from "react-icons/md";

const Sidebar = ({ children }) => {
  const pathname = usePathname();
  const [showSidebar, setShowSidebar] = useState(true);
  const [showHamburger, setShowHamburger] = useState(false);
  const [activeItem, setActiveItem] = useState("");
  const [dfName, setDfName] = useState([]);
  const [hoveredMenu, setHoveredMenu] = useState(null);
  const { orgName, loadingOrg, fetchOrgName } = useOrg();
  const { canRead } = usePermissions();

  useEffect(() => {
    fetchOrgName();
  }, []);

  useEffect(() => {
    const newState = Object.fromEntries(
      sidebarMenu.map((menu) => [menu.label, false])
    );

    const activeMenu = sidebarMenu.find(
      (menu) => menu.submenu && pathname.startsWith(menu.href)
    );

    if (activeMenu) {
      newState[activeMenu.label] = true;
    }

    setIsOpen(newState);
  }, [pathname]);

  const handleMenu = () => {
    setShowHamburger(!showHamburger);
    if (isOpen) {
      setIsOpen(false);
    }
  };

  const handleItemClick = (href) => {
    setActiveItem(href);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      sidebarMenu.forEach((menu) => {
        if (
          refs.current[menu.label].current &&
          !refs.current[menu.label].current.contains(event.target)
        ) {
          setIsOpen((prev) => ({ ...prev, [menu.label]: false }));
        }
      });
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showHamburger]);

  useEffect(() => {
    const handleResize = () => {
      const isLgScreen = window.innerWidth >= 1024;
      setShowSidebar(isLgScreen);
    };

    handleResize();

    window.addEventListener("resize", handleResize);

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const handleSidebar = () => {
    setShowSidebar(false);
  };

  const [isOpen, setIsOpen] = useState(
    Object.fromEntries(sidebarMenu.map((menu) => [menu.label, false]))
  );

  const toggleSubMenu = (menuLabel) => {
    setIsOpen((prev) => ({
      ...Object.fromEntries(Object.keys(prev).map((key) => [key, false])),
      [menuLabel]: !prev[menuLabel],
    }));
  };

  const refs = useRef(
    Object.fromEntries(
      sidebarMenu.map((menu) => [menu.label, React.createRef()])
    )
  );

  const getRefForMenu = (label) => refs.current[label];

  return (
    <>
      <div
        onClick={handleSidebar}
        className={` ${
          showSidebar ? "fixed" : "hidden"
        } inset-0 left-0 top-0 z-10 h-screen w-screen bg-black/20 opacity-75 blur-2xl lg:hidden`}
      ></div>
      <Navbar
        showSidebar={showSidebar}
        setShowSidebar={setShowSidebar}
        setDfName={setDfName}
      />

      <div className={`${showSidebar ? "fixed" : "hidden"} z-20 lg:fixed`}>
        <div
          className={`custom-scrollbar flex h-screen flex-col justify-between text-sm text-[#ccd5ed] ${
            showHamburger ? "pt-[60px]" : "w-60 pt-[60px]"
          } bg-[#13132A]`}
        >
          <div
            className={`mb-4 flex flex-col gap-y-1 ${
              showHamburger && "items-center"
            } ${showHamburger && "relative"} `}
          >
            <div className="absolute -right-7 hidden h-12 w-full lg:flex">
              <button
                onClick={handleMenu}
                className="absolute right-2 top-0.5 bg-[#13132A] border border-gray-500 p-1"
              >
                <MdKeyboardArrowLeft
                  size={20}
                  className={`transition-transform duration-300 ease-in-out ${
                    showHamburger ? "rotate-180" : "rotate-0"
                  }`}
                />
              </button>
            </div>
            {sidebarMenu.map((menu) => {
              const hasAccess = canRead(menu.href);

              return (
                <React.Fragment key={menu.label}>
                  {!menu.submenu ? (
                    <Link
                      onMouseEnter={() => setHoveredMenu(menu.label)}
                      onMouseLeave={() => setHoveredMenu(null)}
                      href={menu.href}
                      className={`w-full px-4 py-2 hover:bg-hover ${
                        pathname.includes(menu.href) && "bg-primary"
                      }`}
                    >
                      <div className="group relative flex items-center justify-between gap-3">
                        <div className="group relative flex items-center gap-3">
                          <span>
                            <Image
                              src={menu.icon}
                              alt="dashboard"
                              height={100}
                              width={100}
                              className="size-5 text-[#ccd5ed]"
                            />
                          </span>
                          <span
                            className={`text-[#ccd5ed] ${
                              showHamburger ? "hidden" : ""
                            }`}
                          >
                            {menu.label}
                          </span>

                          {showHamburger && hoveredMenu === menu.label && (
                            <div
                              id="tooltip-right"
                              role="tooltip"
                              className="absolute left-full top-1/2 z-10 ml-9 -translate-y-1/2 transform bg-primary px-3 py-2 text-sm font-medium text-[#ccd5ed] shadow-md transition-opacity duration-300 ease-in-out"
                            >
                              {menu.label}
                              <div className="tooltip-arrow absolute left-[-5px] top-1/2 h-3 w-3 -translate-y-1/2 rotate-45 transform bg-primary"></div>
                            </div>
                          )}
                        </div>
                        <span>
                          {!hasAccess && (
                            <div>
                              <GoLock className="h-4 w-4 text-yellow-500" />
                            </div>
                          )}
                        </span>
                      </div>
                    </Link>
                  ) : (
                    <div className="relative">
                      <button
                        onMouseEnter={() => {
                          setHoveredMenu(menu.label);
                        }}
                        onMouseLeave={() => {
                          setHoveredMenu(null);
                        }}
                        onClick={() => {
                          setHoveredMenu(null);
                          toggleSubMenu(menu.label);
                        }}
                        className={`group relative flex w-full items-center justify-between gap-2 py-2 pl-6 pr-5 hover:bg-hover ${
                          isOpen[menu.label] ? "bg-primary" : ""
                        } ${pathname.includes(menu.href) && "bg-primary"}`}
                      >
                        <div className="flex items-center gap-3">
                          <Image
                            src={menu.icon}
                            alt={menu.label}
                            width={100}
                            height={100}
                            className="size-5"
                          />
                          <span
                            className={`${
                              showHamburger
                                ? "hidden"
                                : `text-[#ccd5ed] group-hover:text-[#ccd5ed] ${
                                    isOpen[menu.label] && "text-[#ccd5ed]"
                                  }`
                            }`}
                          >
                            {menu.label}
                          </span>
                        </div>
                        {showHamburger && hoveredMenu === menu.label && (
                          <div
                            id="tooltip-right"
                            role="tooltip"
                            className="absolute left-full top-1/2 z-10 ml-3 -translate-y-1/2 transform text-nowrap bg-primary px-3 py-2 text-sm font-medium text-[#ccd5ed] transition-opacity duration-300 ease-in-out"
                          >
                            {menu.label}
                            <div className="tooltip-arrow absolute left-[-5px] top-1/2 h-3 w-3 -translate-y-1/2 rotate-45 transform bg-primary"></div>
                          </div>
                        )}

                        {!showHamburger ? (
                          <FaChevronDown
                            className={`text-[12px] font-bold transition-transform duration-300 ${
                              isOpen[menu.label] && "rotate-180"
                            } ${
                              pathname.includes(menu.href)
                                ? "text-[#ccd5ed]"
                                : "text-[#345594]"
                            } group-hover:text-[#ccd5ed]`}
                          />
                        ) : (
                          <FaChevronRight
                            className={`text-[12px] transition-transform duration-300 ${
                              isOpen[menu.label] || pathname.includes(menu.href)
                                ? "text-[#ccd5ed]"
                                : "text-[#345594]"
                            } group-hover:text-[#ccd5ed]`}
                          />
                        )}
                      </button>

                      <div>
                        {isOpen[menu.label] && (
                          <div
                            ref={
                              isOpen[menu.label] && showHamburger
                                ? getRefForMenu(menu.label)
                                : null
                            }
                            className={`${
                              isOpen[menu.label] && showHamburger
                                ? "absolute left-[92px] top-0 z-50 w-[220px] border border-[#345594] bg-white px-2 py-2 shadow-xl"
                                : ""
                            }`}
                          >
                            {menu.submenu.map((subItem, index) => (
                              <div
                                key={subItem.href}
                                className={`relative flex items-center py-1 ${
                                  showHamburger ? "ml-0" : "ml-4"
                                }`}
                              >
                                {!showHamburger && (
                                  <>
                                    {index !== 0 && (
                                      <span className="absolute -top-9 left-4 h-14 border-l-2 border-[#345594]" />
                                    )}

                                    <span className="absolute left-4 top-1/2 w-5 -translate-y-1/2 transform border-t-2 border-[#345594]" />
                                  </>
                                )}

                                <Link
                                  href={subItem.href}
                                  className={`block w-full py-1.5 pl-2 text-sm font-medium ${
                                    showHamburger
                                      ? "ml-0 text-gray-500"
                                      : "ml-10 text-[#ccd5ed]"
                                  } hover:bg-hover hover:text-[#ccd5ed] ${
                                    pathname.includes(subItem.href) ||
                                    activeItem === subItem.href
                                      ? "bg-[#3359b9] font-bold text-[#ccd5ed]"
                                      : ""
                                  }`}
                                  onClick={() => handleItemClick(subItem.href)}
                                >
                                  {subItem.label}
                                  {!subItem.isAccess && (
                                    <div className="absolute right-2 top-[0.7rem] flex justify-end">
                                      <GoLock className="h-4 w-4 text-yellow-500" />
                                    </div>
                                  )}
                                </Link>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
          <div
            className={` ${
              showHamburger ? "" : "-ml-2"
            } mb-2 flex items-center justify-between`}
          >
            <Link
              href="#"
              className={`${
                showHamburger ? "hidden" : ""
              } mr-2 w-full px-6 py-2 hover:bg-hover`}
            >
              <div className="flex items-center gap-2">
                <span className="px-2">
                  <FaRegUserCircle size={24} className={`text-gray-100`} />
                </span>
                <span
                  className={`text-[#ccd5ed] ${showHamburger ? "hidden" : ""}`}
                >
                  <div className="">
                    {loadingOrg ? (
                      <p className="text-sm text-gray-400">Loading...</p>
                    ) : (
                      <h2 className="">{orgName || "No Organization"}</h2>
                    )}
                  </div>
                </span>
              </div>
            </Link>
          </div>
        </div>
      </div>

      <div
        className={`${showHamburger ? "lg:ml-20" : "lg:ml-60"} h-screen`}
      >
        {children}
      </div>
    </>
  );
};

export default Sidebar;
