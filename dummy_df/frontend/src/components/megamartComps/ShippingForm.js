// import { useRouter } from "next/navigation";
// import React, { useState } from "react";

// const ShippingForm = ({ handleShowNotice }) => {
//   const [formData, setFormData] = useState({
//     house: "",
//     street: "",
//     city: "",
//     state: "",
//     country: "",
//   });

//   const router = useRouter();
//   const handleChange = (e) => {
//     const { name, value } = e.target;
//     setFormData({
//       ...formData,
//       [name]: value,
//     });
//   };

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     // Handle form submission
//     console.log(formData);
//     handleShowNotice();
//     // handleShowNotice();
//   };

//   return (
//     <div>
//       <form
//         onSubmit={handleSubmit}
//         className="max-w-lg  py-10 px-20 bg-white border shadow-md rounded-md"
//       >
//         <div className="mb-4">
//           <label htmlFor="house" className="block text-gray-700">
//             House No
//           </label>
//           <input
//             type="text"
//             id="house"
//             name="house"
//             value={formData.house}
//             onChange={handleChange}
//             className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
//           />
//         </div>
//         <div className="mb-4">
//           <label htmlFor="street" className="block text-gray-700">
//             Street
//           </label>
//           <input
//             type="text"
//             id="street"
//             name="street"
//             value={formData.street}
//             onChange={handleChange}
//             className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
//           />
//         </div>
//         <div className="mb-4">
//           <label htmlFor="city" className="block text-gray-700">
//             City
//           </label>
//           <input
//             type="city"
//             id="city"
//             name="city"
//             value={formData.city}
//             onChange={handleChange}
//             className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
//           />
//         </div>
//         <div className="mb-4">
//           <label htmlFor="state" className="block text-gray-700">
//             State
//           </label>
//           <input
//             type="state"
//             id="state"
//             name="state"
//             value={formData.state}
//             onChange={handleChange}
//             className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
//           />
//         </div>
//         <div className="mb-4">
//           <label htmlFor="state" className="block text-gray-700">
//             Country
//           </label>
//           <input
//             type="country"
//             id="country"
//             name="country"
//             value={formData.country}
//             onChange={handleChange}
//             className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
//           />
//         </div>
//         <button
//           type="submit"
//           className="w-full bg-indigo-500 text-white py-2 rounded-md hover:bg-indigo-600 transition duration-300"
//         >
//           Submit
//         </button>
//       </form>
//     </div>
//   );
// };

// export default ShippingForm;

"use client";

import { useRouter } from "next/navigation";
import React, { useState } from "react";
import Link from "next/link";

const ShippingPage = ({ handleShowNotice, disabled1, setDisabled1 }) => {
  const [formData, setFormData] = useState({
    houseNo: "",
    country: "",
    fullName: "",
    streetAddress: "",
    postalCode: "",
    city: "",
  });

  const router = useRouter();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  // const handleSubmit = (e) => {
  //   e.preventDefault();
  //   // Handle form submission
  //   console.log("formData");
  //   setDisabled1(true);
  //   handleShowNotice();
  //   // handleShowNotice();
  // };
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
      houseNo: "House No.123 ",
      country: "CountryName",
      fullName: "Gaurav Mehta",
      streetAddress: "Raipur. Chhattishgarh",
      postalCode: "123456",
      city: "Raipur",
    });
  };

  // const handleSubmit = (e) => {
  //   e.preventDefault();
  //   console.log(formData);
  //   // Redirect to payment page or handle form submission
  //   router.push('/payment');
  // };

  return (
    <>
      {/* <NavBar2 /> */}
      <div className="min-h-screen bg-white text-black flex items-center justify-center">
        <button
          onClick={updateFormData}
          className=" absolute top-20 right-10 text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center"
        >
          Fill Data
        </button>
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-lg p-6 border border-gray-300 rounded-lg shadow-md bg-white"
        >
          <h2 className="text-2xl font-bold mb-6">Shipping Information</h2>

          <div className="mb-4">
            <label
              className="block text-sm font-medium mb-2"
              htmlFor="house-no"
            >
              House No
            </label>
            <input
              id="house-no"
              name="houseNo"
              type="text"
              value={formData.houseNo}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              placeholder="Enter your house number"
            />
          </div>

          <div className="mb-4">
            <label
              className="block text-sm font-medium mb-2"
              htmlFor="street-address"
            >
              Street Address
            </label>
            <input
              id="street-address"
              name="streetAddress"
              type="text"
              value={formData.streetAddress}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              placeholder="Enter your street address"
            />
          </div>

          <div className="mb-4">
            <label
              className="block text-sm font-medium mb-2"
              htmlFor="postal-code"
            >
              Postal Code
            </label>
            <input
              id="postal-code"
              name="postalCode"
              type="text"
              value={formData.postalCode}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              placeholder="Enter your postal code"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2" htmlFor="city">
              City
            </label>
            <input
              id="city"
              name="city"
              type="text"
              value={formData.city}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              placeholder="Enter your city"
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2" htmlFor="country">
              Country
            </label>
            <input
              id="country"
              name="country"
              type="text"
              value={formData.country}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-black"
              placeholder="Enter your country"
            />
          </div>

          <button
            disabled={disabled1}
            type="submit"
            className="w-full bg-black text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
          >
            Submit
          </button>
        </form>
      </div>
    </>
  );
};

export default ShippingPage;
