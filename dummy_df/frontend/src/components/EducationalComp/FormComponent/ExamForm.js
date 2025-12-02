"use client";
import React, { useState } from "react";
import Loader from "../Loader";

const ExamForm = ({ handleShowNotice, disabled, formData, setFormData }) => {
  const handleInputChange = (e) => {
    const { name, value } = e.target;

    if (name === "contactNumber") {
      const numericValue = value.replace(/\D/g, "").slice(0, 10);
      setFormData((prevData) => ({
        ...prevData,
        [name]: numericValue,
      }));
    } else {
      setFormData((prevData) => ({
        ...prevData,
        [name]: value,
      }));
    }
  };

  const isFormValid = Object.values(formData).every(
    (value) => value.trim() !== ""
  );

  return (
    <div className="my-5 ">
      <form className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-2xl">
        <div className="mb-2">
          <label htmlFor="name" className="block text-gray-700 font-bold mb-2">
            Full Name
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-900"
            required
          />
        </div>

        <div className="mb-2">
          <label
            htmlFor="studentId"
            className="block text-gray-700 font-bold mb-2"
          >
            Student ID
          </label>
          <input
            type="text"
            id="studentId"
            name="studentId"
            value={formData.studentId}
            onChange={handleInputChange}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-900"
            required
          />
        </div>

        <div className="mb-2">
          <label htmlFor="email" className="block text-gray-700 font-bold mb-2">
            Email Address
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-900"
            required
          />
        </div>

        <div className="mb-2">
          <label
            htmlFor="course"
            className="block text-gray-700 font-bold mb-2"
          >
            Course
          </label>
          <input
            type="text"
            id="course"
            name="course"
            value={formData.course}
            onChange={handleInputChange}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-900"
            required
          />
        </div>

        <div className="mb-2">
          <label
            htmlFor="semester"
            className="block text-gray-700 font-bold mb-2"
          >
            Semester
          </label>
          <input
            type="text"
            id="semester"
            name="semester"
            value={formData.semester}
            onChange={handleInputChange}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-900"
            required
          />
        </div>

        <div className="mb-2">
          <label
            htmlFor="subject"
            className="block text-gray-700 font-bold mb-2"
          >
            Branch
          </label>
          <input
            type="text"
            id="subject"
            name="subject"
            value={formData.subject}
            onChange={handleInputChange}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-900"
            required
          />
        </div>

        <div className="mb-2">
          <label
            htmlFor="contactNumber"
            className="block text-gray-700 font-bold mb-2"
          >
            Contact Number
          </label>
          <input
            type="tel"
            id="contactNumber"
            name="contactNumber"
            value={formData.contactNumber}
            onChange={handleInputChange}
            maxLength={10}
            className="w-full px-3 py-1.5 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-900"
            required
          />
        </div>

        <div className="flex justify-center">
          <button
            type="button"
            className={`bg-[#071C55] text-white text-lg px-5 py-1.5 rounded-md focus:outline-none focus:ring-1 focus:ring-opacity-50 ${
              !isFormValid || disabled ? "opacity-50 cursor-not-allowed" : ""
            }`}
            disabled={disabled || !isFormValid}
            onClick={handleShowNotice}
          >
            {disabled ? <Loader /> : " Submit"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ExamForm;
