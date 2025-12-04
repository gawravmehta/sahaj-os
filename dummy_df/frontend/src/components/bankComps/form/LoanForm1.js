"use client";

import { useRouter } from "next/navigation";
import React, { useState } from "react";
import Link from "next/link";
import Loader from "@/components/EducationalComp/Loader";

// Remove static import
// import { morajNoticeCenter } from "concur-consent/morajNoticeCenter";

const LoanForm1 = () => {
  const [disabled1, setDisabled1] = useState(false);
  const [formData, setFormData] = useState({
    fullName: "",
    address: "",
    phoneNumber: "",
    email: "",
    annualIncome: "",
    employmentStatus: "",
    loanAmountRequested: "",
    propertyAddress: "",
    panCard: "",
  });
  const router = useRouter();

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
        cp_id: "692ffd0df2c04cbd82d38087",
        dp_e: "abhishekkhare583@gmail.com",
      });
      setTimeout(() => {
        setDisabled1(false);
      }, 2000);
    } catch (err) {
      console.error("Failed to load notice script:", err);
      setDisabled1(false);
    }
  };


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
      fullName: "Gaurav Mehta",
      address: "Raipur. Chhattishgarh",
      phoneNumber: "8770467824",
      email: "gewgawrav@gmail.com",
      annualIncome: "100000",
      employmentStatus: "Employed",
      loanAmountRequested: "50000",
      propertyAddress: "1234 Elm Street",
      panCard: "ADFSAD21231",
    });
  };

  return (
    <div className="flex flex-row">
      <form
        onSubmit={handleSubmit}
        className="w-full sm:w-1/2 mx-auto mt-5 mb-5 p-4 sm:p-8 hover:shadow-2xl"
      >
        <h2 className="text-2xl font-semibold text-center text-[#003366] mb-6">
          Apply For Home Loan
        </h2>
        {/* Form Fields */}
        {[
          { id: "fullName", label: "Full Name*", type: "text" },
          { id: "address", label: "Address*", type: "text" },
          { id: "phoneNumber", label: "Phone Number*", type: "text" },
          { id: "email", label: "Email Address*", type: "email" },
          { id: "panCard", label: "Pan No*", type: "text" },
          { id: "annualIncome", label: "Annual Income*", type: "text" },
          { id: "employmentStatus", label: "Employment Status*", type: "text" },
          {
            id: "loanAmountRequested",
            label: "Loan Amount Requested*",
            type: "text",
          },
          { id: "propertyAddress", label: "Property Address*", type: "text" },
        ].map(({ id, label, type }) => (
          <div key={id} className="relative z-0 w-full mb-5 group">
            <input
              type={type}
              id={id}
              name={id}
              value={formData[id]}
              onChange={handleChange}
              className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
              placeholder=" "
              required
              maxLength={type === "text" ? 50 : undefined}
              style={
                id === "fullName" ? { textTransform: "capitalize" } : undefined
              }
            />
            <label
              htmlFor={id}
              className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:left-0 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
            >
              {label}
            </label>
          </div>
        ))}

        <div className="flex justify-center items-center mb-5 mt-10">
          <button
            disabled={disabled1}
            type="submit"
            className="text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center"
          >
            {disabled1 ? <Loader /> : "Submit"}

          </button>
        </div>
      </form>
      <button
        onClick={updateFormData}
        className=" absolute top-24 right-10 text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center"
      >
        Fill Data
      </button>
    </div>
  );
};

export default LoanForm1;
