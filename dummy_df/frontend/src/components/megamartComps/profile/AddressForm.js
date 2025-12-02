import { useRouter } from "next/navigation";
import React, { useState } from "react";

const AddressForm = () => {
  const [formData, setFormData] = useState({
    houseNo: "",
    street: "",
    city: "",
    state: "",
    postalCode: "",
    country: "",
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

    // Show confirmation alert
    const isConfirmed = window.confirm(
      "Are you sure you want to submit this information?"
    );
    if (isConfirmed) {
      // Handle form submission
      console.log(formData);

      // Optionally, show an alert after submission
      window.alert("Your address has been submitted successfully!");

      // Redirect to another page
      router.push("/landing/shopping");
    }
  };

  return (
    <div className="py-10 px-20 bg-white border shadow-md rounded-md">
      <form onSubmit={handleSubmit} className="">
        <div className="mb-4">
          <label htmlFor="houseNo" className="block text-gray-700">
            House No
          </label>
          <input
            type="text"
            id="houseNo"
            name="houseNo"
            value={formData.houseNo}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="mb-4">
          <label htmlFor="street" className="block text-gray-700">
            Street Name
          </label>
          <input
            type="text"
            id="street"
            name="street"
            value={formData.street}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="mb-4">
          <label htmlFor="city" className="block text-gray-700">
            City
          </label>
          <input
            type="text"
            id="city"
            name="city"
            value={formData.city}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="mb-4">
          <label htmlFor="state" className="block text-gray-700">
            State
          </label>
          <input
            type="text"
            id="state"
            name="state"
            value={formData.state}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="mb-4">
          <label htmlFor="postalCode" className="block text-gray-700">
            Postal Code
          </label>
          <input
            type="text"
            id="postalCode"
            name="postalCode"
            value={formData.postalCode}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
          />
        </div>
        <div className="mb-4">
          <label htmlFor="country" className="block text-gray-700">
            Country
          </label>
          <input
            type="text"
            id="country"
            name="country"
            value={formData.country}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
          />
        </div>
        <button
          type="submit"
          className="w-full bg-indigo-500 text-white py-2 rounded-md hover:bg-indigo-600 transition duration-300"
        >
          Submit
        </button>
      </form>
    </div>
  );
};

export default AddressForm;
