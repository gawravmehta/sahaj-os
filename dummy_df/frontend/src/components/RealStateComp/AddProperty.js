"use client"

import React, { useState } from 'react'

const AddProperty = () => {

 const [propertyType, setPropertyType] = useState("");
 const [propertyAddress, setPropertyAddress] = useState("");

 const handlePropertyTypeChange = (type) => {
   setPropertyType(type);
 };

 const handleSubmit = (e) => {
   e.preventDefault();
   // Handle form submission logic here
   console.log("Property Type:", propertyType);
   console.log("Property Address:", propertyAddress);
 };


  return (
    <div className="max-w-lg mx-auto mt-10 p-6 bg-white shadow-md rounded-md">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">
        Add your property
      </h2>
      <p className="text-gray-600 mb-6">
        First, we need some details about your property. That way, we can tailor
        the property management experience to you.
      </p>
      <form onSubmit={handleSubmit}>
        <div className="mb-6">
          <label className="block text-gray-700 font-medium mb-2">
            What kind of property is it?
          </label>
          <div className="grid grid-cols-2 gap-4">
            {["Single Family Home", "Condo", "Townhome", "Apartment"].map(
              (type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => handlePropertyTypeChange(type)}
                  className={`py-2 px-4 border rounded-md text-center ${
                    propertyType === type
                      ? "bg-blue-500 text-white"
                      : "bg-gray-100 text-gray-700"
                  }`}
                >
                  {type}
                </button>
              )
            )}
          </div>
        </div>

        <div className="mb-6">
          <label className="block text-gray-700 font-medium mb-2">
            What&apos;s the address of your property?
          </label>
          <input
            type="text"
            value={propertyAddress}
            onChange={(e) => setPropertyAddress(e.target.value)}
            className="w-full p-3 border rounded-md focus:outline-none focus:ring focus:border-blue-300"
            placeholder="Enter the address"
          />
        </div>

        <button
          type="submit"
          className="w-full py-3 bg-gray-500 text-white rounded-md hover:bg-gray-600 focus:outline-none focus:ring"
        >
          Add Your Property
        </button>

        <p className="text-gray-600 text-sm mt-4">
          By clicking Add Your Property above, I agree that I will provide
          accurate and non-discriminatory information and I will comply with the
          Apartments.com{" "}
          <a href="#" className="text-blue-500 underline">
            Terms and Conditions
          </a>{" "}
          and the{" "}
          <a href="#" className="text-blue-500 underline">
            Add a Property Terms of Service
          </a>
          . This site is protected by reCAPTCHA and the Google{" "}
          <a href="#" className="text-blue-500 underline">
            Privacy Policy
          </a>{" "}
          and{" "}
          <a href="#" className="text-blue-500 underline">
            Terms of Service
          </a>{" "}
          apply.
        </p>
      </form>
    </div>
  );
}

export default AddProperty