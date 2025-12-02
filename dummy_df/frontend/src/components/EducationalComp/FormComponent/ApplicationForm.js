"use client";
import React, { useState } from "react";
import Loader from "../Loader";

const ApplicationForm = ({
  handleShowNotice,
  disabled,
  formData,
  setFormData,
}) => {
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Form Data:", formData);
  };
  return (
    <div>
      <form
        className="max-w-4xl mx-auto p-8 bg-white shadow-lg rounded-lg"
        onSubmit={handleSubmit}
      >
        <h2 className="text-2xl font-bold mb-6">Application Form</h2>

        <h3 className="text-xl font-semibold text-[#071C55] mb-4 ">
          Program & Course
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block mb-2">Select Program</label>
            <select
              name="program"
              value={formData.program}
              onChange={handleChange}
              className="w-full border px-3 py-2 outline-none rounded-lg"
            >
              <option value="">Select Program</option>
              <option value="graduate">Graduate</option>
              <option value="postgraduate">Post Graduate</option>
            </select>
          </div>
          <div>
            <label className="block mb-2">Course</label>
            {formData.program === "postgraduate" ? (
              <select
                name="course"
                value={formData.course}
                onChange={handleChange}
                className="w-full border px-3 py-2 outline-none rounded-lg"
              >
                <option value="">Select Course</option>
                <option value="LLM">LLM</option>
                <option value="MCA">MCA</option>
                <option value="MSC">MSC</option>
                <option value="MBA">MBA</option>
                <option value="M.com">M.com</option>
              </select>
            ) : (
              <>
                <select
                  name="course"
                  value={formData.course}
                  onChange={handleChange}
                  className="w-full border px-3 py-2 outline-none rounded-lg"
                >
                  <option value="">Select Course</option>
                  <option value="B.A">B.A</option>
                  <option value="BSC">BSC</option>
                  <option value="B.Tech">B.Tech</option>
                  <option value="BBA">BBA</option>
                  <option value="B.COM">B.COM</option>
                  <option value="BCA">BCA</option>
                </select>
              </>
            )}
          </div>
        </div>

        <h3 className="text-xl text-[#071C55] font-bold mb-4">
          Personal Details
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block mb-2">Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="w-full border px-3 py-2 outline-none rounded-lg"
            />
          </div>
          <div>
            <label className="block mb-2">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full border px-3 outline-none py-2 rounded-lg"
            />
          </div>
          <div>
            <label className="block mb-2">Mobile Number</label>
            <input
              type="text"
              name="mobile"
              value={formData.mobile}
              onChange={handleChange}
              className="w-full border px-3 py-2 outline-none rounded-lg"
            />
          </div>
          <div>
            <label className="block mb-2">Date of Birth</label>
            <input
              type="date"
              name="dob"
              value={formData.dob}
              onChange={handleChange}
              className="w-full border px-3 py-2 outline-none rounded-lg"
            />
          </div>
          <div>
            <label className="block mb-2">Gender</label>
            <select
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              className="w-full border px-3 py-2 outline-none rounded-lg"
            >
              <option value="">Select Gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="block mb-2">Category</label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full border px-3 py-2 outline-none rounded-lg"
            >
              <option value="">Select Category</option>
              <option value="general">General</option>
              <option value="obc">OBC</option>
              <option value="sc">SC</option>
              <option value="st">ST</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block mb-2">Country</label>
            <input
              type="text"
              name="country"
              value={formData.country}
              onChange={handleChange}
              className="w-full border px-3 py-2 outline-none rounded-lg"
            />
          </div>
          <div>
            <label className="block mb-2">State</label>
            <input
              type="text"
              name="state"
              value={formData.state}
              onChange={handleChange}
              className="w-full border px-3 py-2 outline-none rounded-lg"
            />
          </div>
          <div>
            <label className="block mb-2">City</label>
            <input
              type="text"
              name="city"
              value={formData.city}
              onChange={handleChange}
              className="w-full border px-3 py-2 outline-none rounded-lg"
            />
          </div>
        </div>

        <div className="mb-6">
          <h3 className="text-xl text-[#071C55] font-bold mb-4">
            Education Qualification
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block mb-2">12th Marks</label>
              <input
                type="text"
                name="marks12th"
                value={formData.marks12th}
                onChange={handleChange}
                className="w-full border px-3 py-2 outline-none rounded-lg"
              />
            </div>
            <div>
              <label className="block mb-2">University Name</label>
              <input
                type="text"
                name="universityName"
                value={formData.universityName}
                onChange={handleChange}
                className="w-full border px-3 py-2 outline-none rounded-lg"
              />
            </div>
            <div>
              <label className="block mb-2">School Name</label>
              <input
                type="text"
                name="schoolName"
                value={formData.schoolName}
                onChange={handleChange}
                className="w-full border px-3 py-2  outline-none rounded-lg"
              />
            </div>
            <div>
              <label className="block mb-2">Passing Year</label>
              <input
                type="text"
                name="passingYear"
                value={formData.passingYear}
                onChange={handleChange}
                className="w-full border px-3 py-2 outline-none rounded-lg"
              />
            </div>
            <div>
              <label className="block mb-2">Percentage</label>
              <input
                type="text"
                name="percentage"
                value={formData.percentage}
                onChange={handleChange}
                className="w-full border px-3 py-2 outline-none  rounded-lg"
              />
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="w-full bg-[#071C55] text-white py-2 px-4 rounded-lg  transition"
          disabled={disabled}
          onClick={handleShowNotice}
        >
          {disabled ? "Loading...": " Submit Application"}
        </button>
      </form>
    </div>
  );
};

export default ApplicationForm;
