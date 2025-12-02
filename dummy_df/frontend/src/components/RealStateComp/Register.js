"use client";
import React, { useState } from "react";
import Loader from "../EducationalComp/Loader";

const Register = ({ handleShowNotice, disabled, setDisabled }) => {
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    phoneNumber: "",
    // password: "",
    // confirmPassword: "",
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
    // Add form submission logic here
    console.log("Form Data:", formData);
    handleShowNotice();
  };

  const updateFormData = () => {
    setFormData({
      fullName: "Gaurav Mehta",
      email: "gewgawrav@gmail.com",
      phoneNumber: "8770467824",
      // password: "securePassword123", // Add your desired password
      // confirmPassword: "securePassword123", // Should match the password
    });
  };

  return (
    <div className=" h-screen flex items-center justify-center">
      <button
        onClick={updateFormData}
        className=" absolute top-24 right-10 text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center"
      >
        Fill Data
      </button>
      <div className=" max-w-lg mx-auto p-8 border rounded-lg shadow-lg w-[50%] bg-white">
        <h2 className="text-2xl font-bold mb-6 text-center">
          User Registration
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700">Full Name</label>
            <input
              type="text"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              placeholder="Enter your full name"
              required
            />
          </div>
          <div>
            <label className="block text-gray-700">Email Address</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              placeholder="Enter your email"
              required
            />
          </div>
          <div>
            <label className="block text-gray-700">Phone Number</label>
            <input
              type="tel"
              name="phoneNumber"
              value={formData.phoneNumber}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              placeholder="Enter your phone number"
              required
            />
          </div>
          {/* <div>
            <label className="block text-gray-700">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              placeholder="Enter your password"
              required
            />
          </div>
          <div>
            <label className="block text-gray-700">Confirm Password</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
              placeholder="Confirm your password"
              required
            />
          </div> */}
          <button
            type="submit"
            disabled={disabled}
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            {disabled? <Loader /> : " Register"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Register;
