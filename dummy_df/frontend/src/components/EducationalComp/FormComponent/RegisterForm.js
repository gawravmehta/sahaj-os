
"use client";
import React, { useState } from "react";
import Loader from "../Loader"; // Ensure this path is correct

const RegisterForm = ({
  handleShowNotice,
  disabled,
  formData,
  setFormData,
}) => {
  // Function to check if all required fields are filled
  const isFormValid = () => {
    return (
      formData.name.trim() !== "" &&
      formData.email.trim() !== "" &&
      formData.mobile.trim() !== "" &&
      formData.state.trim() !== "" &&
      formData.city.trim() !== "" &&
      formData.level.trim() !== "" &&
      formData.stream.trim() !== "" &&
      formData.program.trim() !== ""
    );
  };

  const handleSubmit = () => {
    if (isFormValid()) {
      handleShowNotice();
    }
  };

  return (
    <div
      className="relative bg-cover rounded-lg p-5 h-[500px]"
      style={{
        backgroundImage:
          'url("https://admission.matsuniversity.ac.in/wp-content/uploads/2024/02/MATS-School-of-Information-Technology.jpg")',
      }}
    >
      <div className="absolute inset-0 bg-blue-900 opacity-80 rounded-lg"></div>

      <div className="relative">
        <input
          type="text"
          placeholder="Enter Name*"
          className="w-full mb-3 rounded-md border outline-none border-gray-600 py-2 px-2"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        />
        <input
          type="email"
          placeholder="Enter Email Address*"
          className="w-full mb-3 rounded-md border mt-2 outline-none border-gray-600 py-2 px-2"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        />

        <div className="w-full mb-3 flex items-center mt-2">
          <span className="inline-flex items-center py-2 px-2 text-sm text-gray-900 bg-gray-200 border border-gray-300 rounded-l-md">
            +91
          </span>
          <input
            type="text"
            name="phoneNumber"
            className="w-full bg-gray-50 border outline-none text-gray-900 text-sm border-gray-300 rounded-r-md py-2 px-2"
            placeholder="Enter Mobile Number*"
            value={formData.mobile}
            onChange={(e) => {
              const numericValue = e.target.value.replace(/\D/g, ""); // Removes non-numeric characters
              setFormData({ ...formData, mobile: numericValue });
            }}
            maxLength={10}
          />
        </div>

        <div className="flex gap-8 mt-5">
          <input
            type="text"
            placeholder="Enter State*"
            className="w-1/2 mb-3 rounded-md border outline-none border-gray-600 py-2 px-2"
            value={formData.state}
            onChange={(e) =>
              setFormData({ ...formData, state: e.target.value })
            }
          />
          <input
            type="text"
            placeholder="Enter City*"
            className="w-1/2 mb-3 rounded-md border outline-none border-gray-600 py-2 px-2"
            value={formData.city}
            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
          />
        </div>

        <select
          className="w-full mb-3 mt-2 rounded-md border outline-none border-gray-600 py-2 px-2"
          placeholder="Select Level Applying For*"
          value={formData.level}
          onChange={(e) => setFormData({ ...formData, level: e.target.value })}
        >
          <option className="text-gray-500" value="">
            Select Level Applying For*
          </option>
          <option value="undergraduate">Graduate</option>
          <option value="postgraduate">Post Graduate</option>
        </select>

        <select
          className="w-full mb-3 mt-2 rounded-md border outline-none border-gray-600 py-2 px-2"
          value={formData.stream}
          onChange={(e) => setFormData({ ...formData, stream: e.target.value })}
        >
          <option className="text-gray-500" value="">
            Select Stream*
          </option>
          <option value="IT">I.T</option>
          <option value="Arts and Humanities">Arts and Humanities</option>
          <option value="Law">Law</option>
          <option value="Science">Science</option>
          <option value="Management">Management</option>
        </select>

        <select
          className="w-full mb-3 mt-2 rounded-md border outline-none border-gray-600 py-2 px-2"
          value={formData.program}
          onChange={(e) => setFormData({ ...formData, program: e.target.value })}
        >
          <option className="text-gray-500" value="">
            Select Course Name*
          </option>
          {formData.level === "postgraduate" ? (
            <>
              <option value="MBA">MBA</option>
              <option value="MCA">MCA</option>
              <option value="M.Sc">M.Sc</option>
            </>
          ) : (
            <>
              <option value="BBA">BBA</option>
              <option value="BCA">BCA</option>
              <option value="B.Sc">B.Sc</option>
            </>
          )}
        </select>

        <div className="mt-4">
          <button
            type="button"
            className={`w-full py-2 px-2 text-lg font-medium bg-[#071C55] text-white rounded-md flex items-center justify-center ${
              !isFormValid() ? "opacity-50 cursor-not-allowed" : ""
            }`}
            disabled={disabled || !isFormValid()} // Update here
            onClick={handleSubmit}
          >
            {disabled ? "Loading..." : "Submit"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RegisterForm;

