"use client"
import React from "react";
import { FaFacebookSquare } from "react-icons/fa";
import { FaSquareInstagram } from "react-icons/fa6";
import { FaLinkedin } from "react-icons/fa";
import { FaXTwitter } from "react-icons/fa6";
import Image from "next/image";



const Footer = () => {
  
  const removeLocalStorage = () => {
    if (typeof window !== "undefined") {
    
      localStorage.clear();
    }
  };
  return (
    <div>
      <div className="bg-[#071C55]">
        <div className="flex">
          <div className="w-1/2 pt-16">
            <div className="w-[25%] rounded-lg  py-2 ml-14">
              <Image
                src="https://img.freepik.com/premium-vector/university-logo-vector-illustration_659631-5994.jpg?size=626&ext=jpg&ga=GA1.1.105260808.1701925756&semt=ais_hybrid"
                alt="logo"
                width={150}
                height={150}
              />
            </div>
            <h1 className="text-white text-xl font-medium ml-14 mt-14">
              About:
            </h1>
            <p className="text-white ml-14 mt-5">
              Hogwarts University Raipur is a research driven university
              established under the aegis of Hogwarts Group of Institutions
              catering to the nation building through higher education since
              more than 32 years.
            </p>
          </div>
          <div className="w-1/4 text-white pt-16 pl-6">
            <h1 className="text-xl font-medium">Under Graduate</h1>
            <ul className="mt-3 space-y-2 font-light">
              <li>BBA</li>
              <li>B.Com</li>
              <li>BCA</li>
              <li>B.Sc. Microbiology (Hons)</li>
              <li>B. Arch.</li>
              <li>BBA.LL.B</li>
            </ul>
          </div>
          <div className="w-1/4 text-white pt-16 pl-5">
            <h1 className="text-xl font-medium">Post Graduate</h1>
            <ul className="mt-3 space-y-2 font-light">
              <li>MBA</li>
              <li>LL.M</li>
              <li>M.Sc Microbiology</li>
              <li>M.Com</li>
              <li>MCA</li>
              <li>Ph.D.</li>
            </ul>
          </div>
        </div>
        <div className=" mt-10 flex">
          <div className="w-1/4  text-white ml-14 pl-6">
            <h1 className="text-xl font-medium"> University</h1>

            <ul className="mt-3 space-y-2 font-light ">
              <li>About University</li>
              <li>Chancellor&apos;s Message</li>
              <li>Registrar&apos;s Message</li>
              <li>Mission & Vision</li>
              <li>Approvals & Recognition</li>
              <li>University Management Team</li>
              <li>Committee Member</li>
            </ul>
          </div>
          <div className="w-1/4  text-white">
            <h1 className="text-xl font-medium">News and Events</h1>

            <ul className="mt-3 space-y-2 font-light ">
              <li>News and Events</li>
              <li>Media Coverage</li>
              <li>Gallery</li>
            </ul>
          </div>
          <div className="w-1/4  text-white">
            <h1 className="text-xl font-medium">Quick Links</h1>

            <ul className="mt-3 space-y-2 font-light ">
              <li>About</li>
              <li>Blogs</li>
              <li>Contact Us</li>
              <li>Careers</li>
              <li>Sitemap</li>
              <li>Privacy Policy</li>
            </ul>
          </div>
          <div className="w-1/4  text-white">
            <h1 className="text-xl font-medium">Research & Development</h1>

            <ul className="mt-3 space-y-2 font-light ">
              <li>Research & Development</li>
              <li>Expert Committee</li>
              <li>Publications</li>
              <li onClick={removeLocalStorage}>
              <a href="/educational-Institute" className="hover:text-white text-blue-600">
                Clear Cookie
              </a>
            </li>
            </ul>
            


            <h1 className="text-xl font-medium mt-3">Connect with us on:</h1>
            <div className="flex mt-2 gap-2">
              <FaFacebookSquare className="w-8 h-8" />
              <FaSquareInstagram className="w-8 h-8" />
              <FaLinkedin className="w-8 h-8" />
              <FaXTwitter className="w-8 h-8" />
            </div>
          </div>
        </div>
      </div>
      <div className="bg-[#1e273f] text-white flex justify-center items-center py-5 text-xl">
        <h1>Copyright © 2024 Hogwarts University All Rights Rese jurved</h1>
      </div>
    </div>
  );
};

export default Footer;
