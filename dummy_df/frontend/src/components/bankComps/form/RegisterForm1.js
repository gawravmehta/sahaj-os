"use client";

import Loader from "@/components/EducationalComp/Loader";
import React, { useEffect, useState } from "react";

const RegisterForm1 = ({
  // handleShowNotice,
  disabled1,
  setDisabled1,
  formData,
  setFormData,
}) => {
  const handleChange = (e) => {
    const { name, value } = e.target;

    // For phone number, filter out non-numeric characters and limit to 10 digits
    if (name === "phoneNumber") {
      const formattedValue = value.replace(/\D/g, "").slice(0, 10);
      setFormData({
        ...formData,
        [name]: formattedValue,
      });
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
  };

  const loadConcurNotice = async () => {
    return new Promise((resolve, reject) => {
      if (window.invokeNotice) return resolve();

      const script = document.createElement("script");
      script.src = "/concur-notice.js";
      script.type = "module";
      script.onload = () => resolve();
      script.onerror = (error) => reject(error);
      document.head.appendChild(script);
    });
  };

  const handleShowNotice = async () => {

    console.log("handleShowNotice function call");

    try {
      await loadConcurNotice();

      window.invokeNotice({
        cp_id: "69293269780a509f14ce1f8b",
        dp_e: formData.email,
        redirect_url: "https://www.google.com",
      });

      setTimeout(() => {
        setDisabled1(false);
      }, 2000);
    } catch (err) {
      console.error("Failed to load notice script:", err);
      setDisabled1(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Save form data to local storage
    localStorage.setItem("registerFormData", JSON.stringify(formData));

    console.log("Form data saved to local storage:", formData);
    setDisabled1(true);
    handleShowNotice();
    // Uncomment if you want to redirect after submission
    // router.push("/home1");
  };

  useEffect(() => {
    console.log(formData.dob);
  }, [formData]);

  return (
    <form onSubmit={handleSubmit} className="w-full mt-5">
      {/* Full Name */}
      <div className="relative z-0 w-full mb-5 group">
        <input
          type="text"
          id="fullName"
          name="fullName"
          value={formData.fullName}
          onChange={handleChange}
          className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none  dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
          placeholder=" "
          required
          style={{ textTransform: "capitalize" }}
        />
        <label
          htmlFor="fullName"
          className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:left-0 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
        >
          Full Name*
        </label>
      </div>

      {/* Email Address */}
      <div className="relative z-0 w-full mb-5 group">
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none  dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
          placeholder=" "
          required
        />
        <label
          htmlFor="email"
          className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:left-0 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
        >
          Email Address*
        </label>
      </div>

      {/* Phone Number */}
      <div className="relative z-0 w-full mb-5 group">
        <input
          type="text"
          id="phoneNumber"
          name="phoneNumber"
          value={formData.phoneNumber}
          onChange={handleChange}
          className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none  dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
          placeholder=" "
          required
          maxLength={10}
        />
        <label
          htmlFor="phoneNumber"
          className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:left-0 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
        >
          Phone Number*
        </label>
      </div>

      {/* Date of Birth */}
      <div className="relative z-0 w-full mb-5 group">
        <input
          type="date"
          id="dob"
          name="dob"
          value={formData.dob}
          onChange={handleChange}
          className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none  dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
          placeholder=" "
          required
        />
        <label
          htmlFor="dob"
          className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:left-0 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
        >
          Date of Birth*
        </label>
      </div>

      {/* Address */}
      <div className="relative z-0 w-full mb-5 group">
        <input
          type="text"
          id="address"
          name="address"
          value={formData.address}
          onChange={handleChange}
          className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none  dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
          placeholder=" "
          required
        />
        <label
          htmlFor="address"
          className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:left-0 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
        >
          Address*
        </label>
      </div>

      {/* Submit Button */}
      <div className="flex justify-center items-center  mt-5">
        <button
          disabled={disabled1}
          type="submit"
          className="text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center "
        >
          {disabled1 ? <Loader /> : "Register"}
        </button>
      </div>
    </form>
  );
};

export default RegisterForm1;
