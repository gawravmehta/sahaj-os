"use client";

import React from "react";

const Footer = () => {
  const clearLocalStorage = () => {
    if (typeof window !== "undefined") {
      // Ensure localStorage is only accessed on the client
      localStorage.clear();
    }
  };

  return (
    <footer className="bg-gray-800 text-white py-10">
      <div className="container grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10 w-[90%] m-auto">
        <div>
          <h4 className="font-bold mb-2">Get Local Info</h4>
          <p className="text-gray-400">
            Does it have pet-friendly rentals? How are the schools? Get
            important local information on the areas you&apos;re most interested
            in.
          </p>
          <input
            type="text"
            className="mt-4 px-4 py-2 w-full rounded bg-gray-700 text-white"
            placeholder="75069, McKinney, TX"
          />
        </div>
        <div>
          <h4 className="font-bold mb-2">Need a home loan? Get pre-approved</h4>
          <p className="text-gray-400">
            Find a lender who can offer competitive mortgage rates and help you
            with pre-approval.
          </p>
          <button className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            Get pre-approved now
          </button>
        </div>
        <div>
          <h4 className="font-bold mb-2">Learn About NAR</h4>
          <ul className="text-gray-400">
            <li>
              <a href="#" className="hover:text-white">
                About NAR
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-white">
                Agent vs.REALSTATE®
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-white">
                Find an Appraiser
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-white">
                Commercial Services
              </a>
            </li>
            <li onClick={clearLocalStorage}>
              <a href="/real_state" className="hover:text-white">
                Clear Cookie
              </a>
            </li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold mb-2">For REALSTATE®</h4>
          <ul className="text-gray-400">
            <li>
              <a href="#" className="hover:text-white">
                Create personalized social media content with RPR® Mobile
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-white">
                How to Properly Price a Home
              </a>
            </li>
            <li>
              <a href="#" className="hover:text-white">
                RESPA Guidance Tips for REALSTATE®
              </a>
            </li>
          </ul>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
