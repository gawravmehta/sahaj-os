 "use client"
 
import Image from 'next/image';
 import Link from 'next/link';
import { usePathname } from 'next/navigation';
import React, { useState } from 'react'
import { FaBell, FaUserCircle } from 'react-icons/fa';

const Navbar = () => {
  const pathname = usePathname();
  const [isDropdownOpen, setDropdownOpen] = useState(false); 

   const toggleDropdown = () => {
     setDropdownOpen((prevState) => !prevState); // Toggle dropdown visibility
   };
  return (
    <header className="bg-gray-800 text-white ">
      <div className="container mx-auto flex justify-between items-center py-2 px-6 w-[80%] m-auto">
        <Link href="/real_state" className="text-2xl font-bold">
          <Image
            src="/logo.webp"
            className="rounded-full"
            height={70}
            width={60}
          />
        </Link>
        <nav
          className="flex
         gap-4"
        >
          <ul className="flex space-x-7">
            <li>
              <Link
                href="/real_state/application"
                className="hover:text-yellow-300"
              >
                Application
              </Link>
            </li>
            {/* <li>
              <Link href="/feedback" className="hover:text-yellow-300">
                Feedback
              </Link>
            </li> */}
            <li>
              <Link
                href="/real_state/reservation"
                className="hover:text-yellow-300"
              >
                Reservation
              </Link>
            </li>
            <li>
              <Link
                href="/real_state/register"
                className="hover:text-yellow-300"
              >
                Register
              </Link>
            </li>
            <li>
              <Link
                href="/real_state/preference-center"
                className="hover:text-yellow-300"
              >
                Preference Center
              </Link>
            </li>
          </ul>
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
                  <Link href="/real_state/preference-center"
                  onClick={toggleDropdown}>
                      <div className="p-2 border-b border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                              {" "}
                              22, August, 2024
                          </h1>
                          <h1 className="text-[#FF0000] font-semibold text-sm">
                              Your listing for &quot;Luxury Apartment in Downtown&quot; is about to expire. Renew to keep it active.
                          </h1>
                      </div>
                  </Link>
                  <Link href="/real_state/preference-center"
                  onClick={toggleDropdown}>
                      <div className="p-2 border-b border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                              {" "}
                              22, August, 2024
                          </h1>
                          <h1 className="text-gray-600 font-semibold text-sm">
                              Price Update: The price of &quot;Modern Family Home in Suburbia&quot; has changed to ₹ 15,250,000.00.
                          </h1>
                      </div>
                  </Link>
                  <Link href="/real_state/preference-center"
                  onClick={toggleDropdown}>
                      <div className="p-2 border-b border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                              {" "}
                              23, August, 2024
                          </h1>
                          <h1 className="text-[#FF0000] font-semibold text-sm">
                              Your consent for property photoshoot has expired. Reauthorize to continue marketing your listing.
                          </h1>
                      </div>
                  </Link>
                  <Link href="/real_state/preference-center"
                  onClick={toggleDropdown}>
                      <div className="p-2 border-b border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                              {" "}
                              23, August, 2024
                          </h1>
                          <h1 className="text-gray-600 font-semibold text-sm">
                              Viewing Alert: A client has scheduled a viewing for &quot;Seaside Villa&quot; on 24, August, 2024.
                          </h1>
                      </div>
                  </Link>
                  <Link href="/real_state/preference-center"
                  onClick={toggleDropdown}>
                      <div className="p-2 border-b border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                              {" "}
                              23, August, 2024
                          </h1>
                          <h1 className="text-[#FF0000] font-semibold text-sm">
                              Your consent for virtual tour service has expired. Reauthorize to keep your virtual tours available.
                          </h1>
                      </div>
                  </Link>
                  <Link href="/real_state/preference-center"
                  onClick={toggleDropdown}>
                      <div className="p-2 border-gray-400 cursor-pointer">
                          <h1 className="text-gray-500 font-normal text-xs">
                              24, August, 2024
                          </h1>
                          <h1 className="text-gray-600 font-semibold text-sm">
                              Offer Received: You&apos;ve received a new offer of ₹ 10,250,000.00 for &quot;Downtown Loft&quot;.
                          </h1>
                      </div>
                  </Link>
              </div>
              
                )}
              </div>
            </div>
            <Link href="/real_state/preference-center">
              <FaUserCircle size={25} />
            </Link>
          </div>
        </nav>
      </div>
    </header>
  );
}

export default Navbar