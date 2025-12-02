"use client";
import Loader from "@/components/EducationalComp/Loader";
import Footer from "@/components/bankComps/Footer";
import Navbar from "@/components/bankComps/Navbar";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

const Page = () => {
  const [disabled1, setDisabled1] = useState(false);

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    city: "",
    occupation: "",
    panCard: "",
    phoneNumber: "",
    email: "",
  });
  const router = useRouter();

  const handleChange = (e) => {
    const { name, value } = e.target;
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
    try {
      await loadConcurNotice();

      window.invokeNotice({
        collection_point_id: "68b152a05392f9da736070c5",
        notice_id: "68b123c1e6ef7bbc4b109051",
        dp_id: "a3e1bc2f-8d3e-4a9b-9c41-f6a2e8f3d123",
        dp_e: "gewgawrav@gmail.com",
        dp_m: "8770467824",
        redirect_url: "http://localhost:3000/trust-bank",
      });
      setTimeout(() => {
        setDisabled1(false);
      },2000);
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
  };
  const updateFormData = () => {
    setFormData({
      firstName: "Gaurav",
      lastName: " Mehta",
      city: "Raipur",
      occupation: "CEO",
      panCard: "ASSSD12SD",
      phoneNumber: "8770467824",
      email: "gewgawrav@gmail.com",
    });
  };

  return (
    <div>
      <Navbar />
      <button
        onClick={updateFormData}
        className=" absolute top-24 right-10 text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center"
      >
        Fill Data
      </button>
      <form
        className="w-full sm:w-1/2 hover:shadow-2xl mx-auto mt-5 p-4 sm:p-8 mb-5"
        onSubmit={handleSubmit}
      >
        <h2 className="text-2xl font-semibold text-center text-[#003366] mb-6">
          Apply for Credit Card
        </h2>

        {/* First Name */}
        <div className="relative z-0 w-full mb-5 group">
          <input
            type="text"
            id="firstName"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
            placeholder=" "
            required
            style={{ textTransform: "capitalize" }}
          />
          <label
            htmlFor="firstName"
            className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
          >
            First Name*
          </label>
        </div>

        {/* Last Name */}
        <div className="relative z-0 w-full mb-5 group">
          <input
            type="text"
            id="lastName"
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
            placeholder=" "
            required
            style={{ textTransform: "capitalize" }}
          />
          <label
            htmlFor="lastName"
            className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
          >
            Last Name*
          </label>
        </div>

        {/* City */}
        <div className="relative z-0 w-full mb-5 group">
          <input
            type="text"
            id="city"
            name="city"
            value={formData.city}
            onChange={handleChange}
            className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
            placeholder=" "
            required
          />
          <label
            htmlFor="city"
            className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
          >
            City*
          </label>
        </div>

        {/* Occupation */}
        <div className="relative z-0 w-full mb-5 group">
          <input
            type="text"
            id="occupation"
            name="occupation"
            value={formData.occupation}
            onChange={handleChange}
            className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
            placeholder=" "
            required
          />
          <label
            htmlFor="occupation"
            className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
          >
            Occupation*
          </label>
        </div>

        {/* PAN Card */}
        <div className="relative z-0 w-full mb-5 group">
          <input
            type="text"
            id="panCard"
            name="panCard"
            value={formData.panCard}
            onChange={handleChange}
            className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
            placeholder=" "
            required
          />
          <label
            htmlFor="panCard"
            className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
          >
            PAN Card*
          </label>
        </div>

        {/* Mobile Number */}
        <div className="relative z-0 w-full mb-5 group">
          <input
            type="text"
            id="phoneNumber"
            name="phoneNumber"
            value={formData.phoneNumber}
            onChange={handleChange}
            className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
            placeholder=" "
            required
            maxLength={10}
          />
          <label
            htmlFor="phoneNumber"
            className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
          >
            Mobile Number*
          </label>
        </div>

        {/* Email */}
        <div className="relative z-0 w-full mb-5 group">
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
            placeholder=" "
            required
          />
          <label
            htmlFor="email"
            className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
          >
            Email*
          </label>
        </div>

        {/* Submit Button */}
        <div className="flex justify-center items-center mb-5 mt-10">
          <button
            disabled={disabled1}
            type="submit"
            className="text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium cursor-pointer rounded-md text-base w-full sm:w-auto px-7 py-3 text-center"
          >
        {   disabled1? <Loader /> : "Apply Now"}
          </button>
        </div>
      </form>

      <Footer />
    </div>
  );
};

export default Page;
