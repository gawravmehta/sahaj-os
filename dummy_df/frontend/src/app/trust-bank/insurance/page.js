"use client";

import Footer from "@/components/bankComps/Footer";
import Navbar from "@/components/bankComps/Navbar";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Loader from "@/components/EducationalComp/Loader";

const Page = () => {
  const [disabled1, setDisabled1] = useState(false);
  const [formData, setFormData] = useState({
    fullName: "",
    address: "",
    mobile: "",
    company: "",
    insuranceType: "",
    health: "",
  });

  const router = useRouter();

  const handleChange = (e) => {
    const { id, value } = e.target;
    if (id === "mobile") {
      const formattedValue = value.replace(/\D/g, "").slice(0, 10);
      setFormData({
        ...formData,
        [id]: formattedValue,
      });
    } else {
      setFormData({
        ...formData,
        [id]: value,
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
        cp_id: "692c333883050d035b147893",
        dp_e: formData.address,
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
    // Save form data to local storage or handle form submission
    localStorage.setItem("insuranceFormData", JSON.stringify(formData));
    console.log("Form data saved to local storage:", formData);
    handleShowNotice(); // Show notice center or redirect to the landing page after submission
    setDisabled1(true);

    // Uncomment if you want to redirect after submission
    // router.push("/trust-bank/home");
  };
  const updateFormData = () => {
    setFormData({
      fullName: "Gaurav Mehta",
      address: "gewgawrav@gmail.com",
      mobile: "8770467824",
      company: "Catax",
      insuranceType: "Life  ",
      health: "123",
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
      <div className="min-h-screen flex items-center justify-center">
        <div className="p-8 rounded-lg hover:shadow-lg w-full max-w-3xl">
          <h2 className="text-2xl font-semibold text-center text-gray-800 mb-6">
            Apply for Insurance
          </h2>
          <form onSubmit={handleSubmit}>
            {/* Full Name */}
            <div className="relative z-0 w-full mb-5 group">
              <input
                type="text"
                id="fullName"
                value={formData.fullName}
                onChange={handleChange}
                className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
                placeholder=" "
                required
              />
              <label
                htmlFor="fullName"
                className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
              >
                Name*
              </label>
            </div>

            {/* Address */}
            <div className="relative z-0 w-full mb-5 group">
              <input
                type="email"
                id="address"
                value={formData.address}
                onChange={handleChange}
                className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
                placeholder=" "
                required
              />
              <label
                htmlFor="address"
                className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
              >
                Email address*
              </label>
            </div>
            <div className="relative z-0 w-full mb-5 group">
              <input
                type="text"
                id="health"
                value={formData.health}
                onChange={handleChange}
                className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
                placeholder=" "
                required
              />
              <label
                htmlFor="health"
                className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
              >
                Abha health id*
              </label>
            </div>

            {/* Mobile */}
            <div className="relative z-0 w-full mb-5 group">
              <input
                type="number"
                id="mobile"
                value={formData.mobile}
                onChange={handleChange}
                className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
                placeholder=" "
                required
                maxLength={10}
              />
              <label
                htmlFor="mobile"
                className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
              >
                Mobile*
              </label>
            </div>

            {/* Occupation */}
            <div className="relative z-0 w-full mb-5 group">
              <input
                type="text"
                id="company"
                value={formData.company}
                onChange={handleChange}
                className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
                placeholder=" "
                required
              />
              <label
                htmlFor="company"
                className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:start-0 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
              >
                Company name*
              </label>
            </div>

            {/* Insurance Type */}
            <div className="relative z-0 w-full mb-5 group">
              <select
                id="insuranceType"
                value={formData.insuranceType}
                onChange={handleChange}
                className="block py-2.5 px-0 w-full text-md text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
                required
              >
                <option value="" disabled>
                  Select Insurance
                </option>
                <option value="Life">Life</option>
                <option value="Health">Health</option>
                <option value="Home">Home</option>
                <option value="Vehicle">Vehicle</option>
              </select>
            </div>

            {/* Submit Button */}
            <div className="flex justify-center items-center mb-5 mt-10">
              <button
                disabled={disabled1} // Enable the button only when all fields are filled and valid
                type="submit"
                className="text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center"
              >
                {disabled1 ? <Loader /> : "Apply Now"}
              </button>
            </div>
          </form>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Page;
