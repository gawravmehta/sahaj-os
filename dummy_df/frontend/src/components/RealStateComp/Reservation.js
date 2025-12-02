"use client";

import React, { useState } from "react";
import Loader from "../EducationalComp/Loader";

const Reservation = ({ handleShowNotice, disabled, setDisabled }) => {
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    phoneNumber: "",
    propertyAddress: "",
    preferredDateTime: "",
    specialRequests: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    setDisabled(true);
    e.preventDefault();
    // Handle form submission
    handleShowNotice();
  };

  const updateFormData = () => {
    setFormData({
      fullName: "Gaurav Mehta",
      email: "gewgawrav@gmail.com",
      phoneNumber: "8770467824",
      propertyAddress: "123 Main Street, Mumbai",
      preferredDateTime: "2024-09-15", // Example in 'YYYY-MM-DDTHH:MM' format
      specialRequests: "Need parking space",
    });
  };

  return (
    <div className=" h-screen flex items-center justify-center my-4">
      <button
        onClick={updateFormData}
        className=" absolute top-24 right-10 text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center"
      >
        Fill Data
      </button>

      <div className="max-w-lg mx-auto p-8 border rounded-lg shadow-lg w-[50%] bg-white">
        <h2 className="text-2xl font-bold mb-6 text-gray-800 text-center">
          Property Viewing Booking Form
        </h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-2">
            <label
              htmlFor="fullName"
              className="block text-gray-700 font-medium mb-1"
            >
              Full Name
            </label>
            <input
              type="text"
              id="fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="mb-2">
            <label
              htmlFor="email"
              className="block text-gray-700 font-medium mb-1"
            >
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="mb-2">
            <label
              htmlFor="phoneNumber"
              className="block text-gray-700 font-medium mb-1"
            >
              Phone Number
            </label>
            <input
              type="text"
              id="phoneNumber"
              name="phoneNumber"
              value={formData.phoneNumber}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="mb-2">
            <label
              htmlFor="propertyAddress"
              className="block text-gray-700 font-medium mb-1"
            >
              Property Address
            </label>
            <input
              type="text"
              id="propertyAddress"
              name="propertyAddress"
              value={formData.propertyAddress}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="mb-2">
            <label
              htmlFor="preferredDateTime"
              className="block text-gray-700 font-medium mb-1"
            >
              Preferred Date and Time
            </label>
            <input
              type="date"
              id="preferredDateTime"
              name="preferredDateTime"
              value={formData.preferredDateTime}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="mb-2">
            <label
              htmlFor="specialRequests"
              className="block text-gray-700 font-medium mb-1"
            >
              Special Requests or Notes
            </label>
            <textarea
              id="specialRequests"
              name="specialRequests"
              value={formData.specialRequests}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>
          <button
            type="submit"
            disabled={disabled}
            className="w-full bg-blue-500 text-white font-medium py-2 px-4 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
             {disabled? <Loader /> : " Submit"}
            
          </button>
        </form>
      </div>
    </div>
  );
};

export default Reservation;
