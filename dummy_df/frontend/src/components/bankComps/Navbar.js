// "use client";
// import Image from "next/image";
// import Link from "next/link";
// import React, { useState } from "react";
// import { usePathname } from "next/navigation";
// import { FaBell } from "react-icons/fa";
// import { FaUserCircle } from "react-icons/fa";

// const Navbar = () => {
//   const pathname = usePathname();
//   const [isDropdownOpen, setDropdownOpen] = useState(false); // State for dropdown visibility

//   const toggleDropdown = () => {
//     setDropdownOpen((prevState) => !prevState); // Toggle dropdown visibility
//   };

//   return (
//     <div className="h-16 flex items-center">
//       <div
//         className={`bg-[#FF0000] h-full ${
//           pathname != "/" ? "w-full" : "w-[70%]"
//         }  flex items-center  gap-5 text-white font-bold`}
//       >
//         <div className="w-[70%] m-auto flex justify-between">
//           <div className="flex items-center gap-4 ">
//             <div className="flex text-2xl items-center gap-2">
//               <a href="/" className="">
//                 <Image
//                   src="/image/trust-bank.png"
//                   height={100}
//                   width={130}
//                   className="rounded-full"
//                 />
//               </a>
//             </div>
//             <div
//               className={` flex gap-3 ml-5 ${
//                 pathname != "/trust-bank" ? "block" : "hidden"
//               }  `}
//             >
//               <Link
//                 href="/trust-bank/loan-auth"
//                 className="hover:text-blue-800"
//               >
//                 HomeLoan
//               </Link>
//               <Link href="/trust-bank/credit" className="hover:text-blue-800">
//                 Credit
//               </Link>
//               <Link
//                 href="/trust-bank/insurance"
//                 className="hover:text-blue-800"
//               >
//                 Insurance
//               </Link>
//               <Link href="/trust-bank/register" className="hover:text-blue-800">
//                 Register
//               </Link>
//               <Link
//                 href="/trust-bank/preference-center"
//                 className="hover:text-blue-800"
//               >
//                 PreferenceCenter
//               </Link>
//               {/* <Link href="#">Corporate</Link>
//             <Link href="#">Private Banking</Link> */}
//             </div>
//           </div>
//           <div
//             className={`flex items-center gap-4 ${
//               pathname != "/trust-bank" ? "" : "hidden"
//             }`}
//           >
//             {/* <div className="">
//               <FaBell size={22} />
//             </div> */}
//             <div className="relative">
//               <div className="relative">
//                 <div className="cursor-pointer" onClick={toggleDropdown}>
//                   <FaBell size={22} />
//                 </div>

//                 {isDropdownOpen && (
//                   <div className="absolute right-0 mt-2 w-96 z-50 text-[#003366] text-xs bg-white shadow-2xl rounded-lg  px-4 py-4">
//                     <Link href="/trust-bank/preference-center">
//                       <div className="p-2 border-b border-gray-200 ">
//                         <h1 className="cursor-pointer ">
//                           22, August, 2024
//                           <br /> Your consent for email address has expired.
//                           Reconsent to continue with service experience.
//                         </h1>
//                       </div>
//                     </Link>
//                     <Link href="/trust-bank/preference-center">
//                       <div className="p-2 border-b border-gray-200">
//                         <h1 className="cursor-pointer ">
//                           23,August,2024
//                           <br /> Your consent for CIBL report processing has
//                           expired. Reconsent to continue with service experience
//                         </h1>
//                       </div>
//                     </Link>
//                     <Link href="/trust-bank/preference-center">
//                       <div className="p-2  border-gray-200">
//                         <h1 className="cursor-pointer ">
//                           <br /> Your consent for mobile number has expired.
//                           Reconsent to continue wit service experience.
//                         </h1>
//                       </div>
//                     </Link>
//                   </div>
//                 )}
//               </div>
//             </div>

//             <a href="#" className="">
//               <FaUserCircle size={25} />
//             </a>
//           </div>
//         </div>
//       </div>
//       <div
//         className={`bg-[#003467] h-full w-[30%] flex items-center pl-20 gap-5  font-bold ${
//           pathname != "/trust-bank" && "hidden"
//         }`}
//       >
//         <Link
//           href="/trust-bank/register"
//           className="border text-white px-6 py-2 rounded-full "
//         >
//           <h1>Register</h1>
//         </Link>
//         <Link href="/" className="bg-white px-6 py-2 rounded-full ">
//           <h1>Login</h1>
//         </Link>
//       </div>
//     </div>
//   );
// };

// export default Navbar;

"use client";
import Image from "next/image";
import Link from "next/link";
import React, { useState } from "react";
import { usePathname } from "next/navigation";
import { FaBell } from "react-icons/fa";
import { FaUserCircle } from "react-icons/fa";

const Navbar = () => {
  const pathname = usePathname();
  const [isDropdownOpen, setDropdownOpen] = useState(false); // State for dropdown visibility

  const toggleDropdown = () => {
    setDropdownOpen((prevState) => !prevState); // Toggle dropdown visibility
  };

  return (
    <div className="h-16 flex items-center">
      <div
        className={`bg-[#FF0000] h-full ${pathname != "/" ? "w-full" : "w-full"
          }  flex items-center  gap-5 text-white px-10 `}
      >
        <div className="w-full m-auto flex justify-between">
          <div className="flex items-center gap-4 w-full pr-10 font-normal ">
            <div className="flex justify-between w-full items-center gap-4 ">
              <div className="flex text-2xl items-center gap-2 text-white">
                <a href="/" className="">
                  <Image
                    src="/image/trust-bank.png"
                    height={100}
                    width={130}
                    className="rounded-full"
                    alt="Trust Bank Logo"
                  />
                </a>
              </div>
              <div className={` flex gap-3 ml-5`}>
                <Link href="/trust-bank/events" className="">
                  Admin Events
                </Link>
                <Link href="/trust-bank/register" className="">
                  New Account
                </Link>
                <Link href="/trust-bank/loan-auth" className="">
                  Home Loan
                </Link>
                <Link href="/trust-bank/credit" className="">
                  Credit
                </Link>
                <Link href="/trust-bank/insurance" className="">
                  Insurance
                </Link>
                <Link target="_blank" href="https://privacy-centre.sahaj.live" className="">
                  Preference Center
                </Link>
                {/* <Link href="#">Corporate</Link>
                  <Link href="#">Private Banking</Link> */}
              </div>
            </div>
          </div>
          <div
            className={`flex items-center gap-4 ${pathname != "/" ? "" : "hidden"
              }`}
          >
            {/* <div className="">
              <FaBell size={22} />
            </div> */}
            <div className="relative">
              <div className="relative">
                <div className="cursor-pointer" onClick={toggleDropdown}>
                  <FaBell size={22} />
                </div>

                {isDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-96 z-50   bg-white shadow-2xl rounded-lg  px-4 py-4">
                    <Link href="/trust-bank/preference-center"
                      onClick={toggleDropdown}>
                      <div className="p-2 border-b border-gray-400 cursor-pointer">
                        <h1 className="text-gray-500 font-normal text-xs">
                          {" "}
                          22, August, 2024
                        </h1>
                        <h1 className="text-[#FF0000] font-semibold text-sm">
                          Your consent for email address has expired. Reconsent
                          to continue with service experience.
                        </h1>
                      </div>
                    </Link>
                    <Link href="/trust-bank/preference-center"
                      onClick={toggleDropdown}>
                      <div className="p-2 border-b border-gray-400 cursor-pointer">
                        <h1 className="text-gray-500 font-normal text-xs">
                          {" "}
                          22, August, 2024
                        </h1>
                        <h1 className="text-gray-600 font-semibold text-sm ">
                          Your account balance is now ₹ 15,250.00.
                        </h1>
                      </div>
                    </Link>
                    <Link href="/trust-bank/preference-center"
                      onClick={toggleDropdown}>
                      <div className="p-2 border-b border-gray-400 cursor-pointer">
                        <h1 className="text-gray-500 font-normal text-xs">
                          {" "}
                          23,August,2024
                        </h1>
                        <h1 className="text-[#FF0000] font-semibold text-sm">
                          Your consent for CIBL report processing has expired.
                          Reconsent to continue with service experience
                        </h1>
                      </div>
                    </Link>
                    <Link href="/trust-bank/preference-center"
                      onClick={toggleDropdown}>
                      <div className="p-2 border-b border-gray-400 cursor-pointer">
                        <h1 className="text-gray-500 font-normal text-xs">
                          {" "}
                          23,August,2024
                        </h1>
                        <h1 className="text-gray-600 font-semibold text-sm">
                          Transaction Alert: ₹ 5000.00 has been withdrawn from
                          your account ending in 1234.
                        </h1>
                      </div>
                    </Link>
                    <Link href="/trust-bank/preference-center"
                      onClick={toggleDropdown}>
                      <div className="p-2 border-b border-gray-400 cursor-pointer">
                        <h1 className="text-gray-500 font-normal text-xs">
                          {" "}
                          23,August,2024
                        </h1>
                        <h1 className="text-[#FF0000] font-semibold text-sm">
                          Your consent for mobile number has expired. Reconsent
                          to continue wit service experience.
                        </h1>
                      </div>
                    </Link>
                    <Link href="/trust-bank/preference-center"
                      onClick={toggleDropdown}>
                      <div className="p-2  border-gray-400 cursor-pointer">
                        <h1 className="text-gray-500 font-normal text-xs">
                          24,August,2024
                        </h1>
                        <h1 className="text-gray-600 font-semibold text-sm">
                          Your account balance is now ₹ 10,250.00.
                        </h1>
                      </div>
                    </Link>
                  </div>
                )}
              </div>
            </div>
            <Link href="/trust-bank/preference-center">
              <FaUserCircle size={25} />
            </Link>
          </div>
        </div>
      </div>
      <div
        className={`bg-[#003467] h-full w-[30%] flex items-center pl-20 gap-5  font-bold ${pathname != "/landing" && "hidden"
          }`}
      >
        <Link
          href="/register"
          className="border text-white px-6 py-2 rounded-full "
        >
          <h1>Register</h1>
        </Link>
        <Link href="/" className="bg-white px-6 py-2 rounded-full ">
          <h1>Login</h1>
        </Link>
      </div>
    </div>
  );
};

export default Navbar;
