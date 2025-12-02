"use client";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import Link from "next/link";

const LoanForm = ({ handleShowNotice }) => {
  const [formData, setFormData] = useState({
    fullName: "",
    address: "",
    phoneNumber: "",
    email: "",
    annualIncome: "",
    employmentStatus: "",
    loanAmountRequested: "",
    propertyAddress: "",
  });
  const router = useRouter();

  // const handleChange = (e) => {
  //   const { name, value } = e.target;
  //   setFormData({
  //     ...formData,
  //     [name]: value,
  //   });
  // };
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

    // Show notice or redirect

    // Uncomment if you want to redirect after submission
    // router.push('/dashboard');
  };

  

  return (
    <div className="flex flex-row">
      
    <form className=" w-full sm:w-1/2 mx-auto mt-5 p-4 sm:p-8 hover:shadow-2xl mb-5">
      
      <h2 className="text-2xl font-semibold text-center text-[#003366] mb-6">
        Apply For Home Loan
      </h2>
      <div className="relative z-0 w-full mb-5 group">
        <input
          type="text"
          id="fullName"
          name="fullName"
          value={formData.fullName}
          onChange={handleChange}
          className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none  dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
          placeholder=" "
          style={{ textTransform: "capitalize" }} // Capitalizes the first letter
          required
        />
        <label
          htmlFor="fullName"
          className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:left-0 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
        >
          Full Name*
        </label>
      </div>

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

      <div className="relative z-0 w-full mb-5 group">
        <input
          type="text"
          id="annualIncome"
          name="annualIncome"
          value={formData.annualIncome}
          onChange={handleChange}
          className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none  dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
          placeholder=" "
          required
        />
        <label
          htmlFor="annualIncome"
          className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:left-0 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
        >
          Annual Income*
        </label>
      </div>

      <div className="relative z-0 w-full mb-5 group">
        <input
          type="text"
          id="employmentStatus"
          name="employmentStatus"
          value={formData.employmentStatus}
          onChange={handleChange}
          className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none  dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
          placeholder=" "
          required
        />
        <label
          htmlFor="employmentStatus"
          className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:left-0 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
        >
          Employment Status*
        </label>
      </div>

      <div className="relative z-0 w-full mb-5 group">
        <input
          type="text"
          id="loanAmountRequested"
          name="loanAmountRequested"
          value={formData.loanAmountRequested}
          onChange={handleChange}
          className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none  dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
          placeholder=" "
          required
        />
        <label
          htmlFor="loanAmountRequested"
          className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:left-0 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
        >
          Loan Amount Requested*
        </label>
      </div>

      <div className="relative z-0 w-full mb-5 group">
        <input
          type="text"
          id="propertyAddress"
          name="propertyAddress"
          value={formData.propertyAddress}
          onChange={handleChange}
          className="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b border-gray-300 appearance-none  dark:border-gray-600 dark:focus:border-[#9F9F9F] focus:outline-none focus:ring-0 focus:border-[#9F9F9F] peer"
          placeholder=" "
          required
        />
        <label
          htmlFor="propertyAddress"
          className="peer-focus:font-normal absolute text-base text-[#CCCCCC] dark:text-[#9F9F9F] duration-300 transform -translate-y-6 scale-75 top-1 -z-10 origin-[0] peer-focus:left-0 peer-focus:text-[#9F9F9F] peer-focus:dark:text-[#9F9F9F] peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-6"
        >
          Property Address*
        </label>
      </div>

      <div className="flex justify-center items-center  mt-5">
        <Link href="/trust-bank/home">
          <button
            type="submit"
            className="text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center focus:outline-none "
          >
            Submit
          </button>
        </Link>
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

export default LoanForm;
