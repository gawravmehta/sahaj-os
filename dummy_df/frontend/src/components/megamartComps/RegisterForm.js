"use client";
import { useRouter } from "next/navigation";
import React, { useState } from "react";

const RegisterPage = ({ handleShowNotice, disabled1, setDisabled1 }) => {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    mobile: "",
    // password: "",
  });

  const router = useRouter();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
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

  const updateFormData = () => {
    setFormData({
      firstName: "Gaurav ",
      lastName: "Mehta",
      email: "gewgawrav@gmail.com",
      mobile: "8770467824", // Example CRN
    });
  };

  // const handleSubmit = (e) => {
  //   e.preventDefault();
  //   // Save form data to local storage
  //   localStorage.setItem("registerFormData", JSON.stringify(formData));
  //   console.log("Form data saved to local storage:", formData);

  //   // Show notice or redirect
  //   handleShowNotice();
  //   // Uncomment if you want to redirect after submission
  //   // router.push('/dashboard');
  // };

  return (
    <>
      <button
        onClick={updateFormData}
        className=" absolute top-12 right-10 text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center"
      >
        Fill Data
      </button>

      <form
        onSubmit={handleSubmit}
        className="shadow-md  w-96  p-8 bg-white border border-gray-300 rounded-lg"
      >
        <div className="text-2xl font-bold mb-6 w-full text-center">
          Register
        </div>
        <div className="mb-5">
          <label
            htmlFor="firstName"
            className="block mb-2 text-sm font-semibold"
          >
            First Name
          </label>
          <input
            type="text"
            id="firstName"
            name="firstName"
            value={formData.firstName}
            onChange={handleChange}
            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            placeholder="Enter your first name"
            required
          />
        </div>
        <div className="mb-5">
          <label
            htmlFor="lastName"
            className="block mb-2 text-sm font-semibold"
          >
            Last Name
          </label>
          <input
            type="text"
            id="lastName"
            name="lastName"
            value={formData.lastName}
            onChange={handleChange}
            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            placeholder="Enter your last name"
            required
          />
        </div>
        <div className="mb-5">
          <label htmlFor="email" className="block mb-2 text-sm font-semibold">
            Your Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            placeholder="name@flowbite.com"
            required
          />
        </div>
        <div className="mb-5">
          <label htmlFor="mobile" className="block mb-2 text-sm font-semibold">
            Mobile No.
          </label>
          <input
            type="text"
            id="mobile"
            name="mobile"
            value={formData.mobile}
            onChange={handleChange}
            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
            placeholder="Enter your mobile number"
            required
          />
        </div>
        {/* <div className="mb-5">
        <label htmlFor="password" className="block mb-2 text-sm font-semibold">
          Password
        </label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
          placeholder="Enter your password"
          required
        />
      </div> */}
        <button
          disabled={disabled1}
          type="submit"
          className="w-full bg-black text-white py-2 rounded-md  focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium text-sm transition duration-300"
        >
          Register
        </button>
      </form>
    </>
  );
};

export default RegisterPage;
