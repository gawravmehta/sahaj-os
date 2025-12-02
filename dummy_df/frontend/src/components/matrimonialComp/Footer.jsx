"use client"

import React from "react";
import {
  FaAndroid,
  FaApple,
  FaFacebook,
  FaTwitter,
  FaInstagram,
} from "react-icons/fa";

const Footer = () => {
  return (
    <footer>
      <div id="js-footer">
        <div className="bg-[#34495E] pb-8 flex w-full  items-center justify-center">
          <div className=" px-4">
            <div className="w-full flex   gap-56  pt-5 text-gray-400">
              <div className="w-full">
                <ul className="text-sm space-y-2">
                  <li className="text-lg font-semibold text-white">Explore</li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Home
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Advanced search
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Success stories
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Sitemap
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Create Horoscope
                    </a>
                  </li>
                </ul>
              </div>

              <div className="w-full">
                <ul className="text-sm space-y-2">
                  <li className="text-lg font-semibold text-white">Services</li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Membership Options
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Soul Match Careers
                    </a>
                  </li>
                </ul>
              </div>

              <div className="w-full">
                <ul className="text-sm space-y-2">
                  <li className="text-lg font-semibold text-white">Help</li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Contact us
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Soul Match centers (32)
                    </a>
                  </li>
                  <li onClick={() => localStorage.clear()} className="p-1">
                    <a href="/matrimonial" className="hover:text-white">
                      Clear Cookie
                    </a>
                  </li>
                </ul>
              </div>

              <div className="w-full">
                <ul className="text-sm space-y-2">
                  <li className="text-lg font-semibold text-white">Legal</li>
                  <li>
                    <a href="#" className="hover:text-white">
                      About Us
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Fraud Alert
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Terms of use
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      3rd party terms of use
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Privacy policy
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Cookie policy
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Privacy Features
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Summons/Notices
                    </a>
                  </li>
                  <li>
                    <a href="#" className="hover:text-white">
                      Grievances
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-5 pb-6 bg-[#2E4154] text-white">
          <div className="container mx-auto px-4 flex justify-between">
            <div>
              <div className="text-sm font-semibold pb-2">App available on</div>
              <a href="#" className="inline-block mr-2">
                <FaAndroid className="h-6 w-6" />
              </a>
              <a href="#" className="inline-block">
                <FaApple className="h-6 w-6" />
              </a>
            </div>

            <div className="ml-8">
              <div className="text-sm font-semibold pb-2">Follow us on</div>
              <a href="#" className="inline-block mr-2">
                <FaFacebook className="h-6 w-6" />
              </a>
              <a href="#" className="inline-block mr-2">
                <FaTwitter className="h-6 w-6" />
              </a>
              <a href="#" className="inline-block">
                <FaInstagram className="h-6 w-6" />
              </a>
            </div>
          </div>
        </div>

        <div className="bg-gray-200 text-center py-2 text-xs text-gray-400">
          All rights reserved © 2023 Durgesh Chaudhary.
        </div>
      </div>
    </footer>
  );
};

export default Footer;
