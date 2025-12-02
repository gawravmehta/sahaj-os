// "use client";
// import React, { useState } from "react";
// import Loader from "../Loader";

// const Payment = ({ handleShowNotice, disabled, formData, setFormData }) => {
//   const handleChange = (e) => {
//     const { name, value, type, checked } = e.target;
//     setFormData((prevData) => ({
//       ...prevData,
//       [name]: type === "checkbox" ? checked : value,
//     }));
//   };

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     if (formData.agree) {
//       console.log("Payment Form Data:", formData);
//     } else {
//       alert("Please agree to the terms and conditions.");
//     }
//   };

//   return (
//     <div className="max-w-md mx-auto p-6 bg-white shadow-lg rounded-lg mt-5">
//       <h2 className="text-2xl font-bold mb-6 text-center">Payment Form</h2>
//       <form onSubmit={handleSubmit}>
//         <div className="mb-4">
//           <label className="block text-sm font-semibold mb-2">
//             Card Number
//           </label>
//           <input
//             type="text"
//             name="cardNumber"
//             value={formData.cardNumber}
//             onChange={handleChange}
//             placeholder="1234 5678 9101 1121"
//             className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#071C55]"
//             maxLength="16"
//           />
//         </div>

//         <div className="grid grid-cols-2 gap-4 mb-4">
//           <div>
//             <label className="block text-sm font-semibold mb-2">
//               Expiry Month
//             </label>
//             <select
//               name="expiryMonth"
//               value={formData.expiryMonth}
//               onChange={handleChange}
//               className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#071C55]"
//             >
//               <option value="">MM</option>
//               {Array.from({ length: 12 }, (_, i) => (
//                 <option key={i} value={String(i + 1).padStart(2, "0")}>
//                   {String(i + 1).padStart(2, "0")}
//                 </option>
//               ))}
//             </select>
//           </div>
//           <div>
//             <label className="block text-sm font-semibold mb-2">
//               Expiry Year
//             </label>
//             <select
//               name="expiryYear"
//               value={formData.expiryYear}
//               onChange={handleChange}
//               className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#071C55]"
//             >
//               <option value="">YYYY</option>
//               {Array.from({ length: 10 }, (_, i) => (
//                 <option key={i} value={new Date().getFullYear() + i}>
//                   {new Date().getFullYear() + i}
//                 </option>
//               ))}
//             </select>
//           </div>
//         </div>

//         <div className="mb-4">
//           <label className="block text-sm font-semibold mb-2">CVV</label>
//           <input
//             type="text"
//             name="cvv"
//             value={formData.cvv}
//             onChange={handleChange}
//             placeholder="123"
//             className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#071C55]"
//             maxLength="3"
//           />
//         </div>

//         <div className="mb-6 flex items-center">
//           <input
//             type="checkbox"
//             name="agree"
//             checked={formData.agree}
//             onChange={handleChange}
//             className="mr-2"
//           />
//           <label className="text-sm">
//             I agree to with{" "}
//             <span className="text-blue-700">Privacy Policy</span>by proceeding
//             with this payment.
//           </label>
//         </div>
//         <h1 className="text-blue-700 text-lg font-semibold">
//           INR 1000.00{" "}
//           <span className="text-black text-xs">(Total Amount Payable)</span>
//         </h1>

//         <button
//           type="submit"
//           className="w-full bg-[#071C55] text-white py-2 px-4 rounded-lg transition "
//           disabled={disabled}
//           onClick={handleShowNotice}
//         >
//           {disabled ? <Loader /> : "Make Payment"}
//         </button>
//       </form>
//     </div>
//   );
// };

// export default Payment;
"use client";
import React from "react";
import Loader from "../Loader";

const Payment = ({ handleShowNotice, disabled, formData, setFormData }) => {
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.agree) {
      console.log("Payment Form Data:", formData);
    } else {
      alert("Please agree to the terms and conditions.");
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white shadow-lg rounded-lg mt-5">
      <h2 className="text-2xl font-bold mb-6 text-center">Payment Form</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-semibold mb-2">
            Card Number
          </label>
          <input
            type="text"
            name="cardNumber"
            value={formData.cardNumber}
            onChange={handleChange}
            placeholder="1234 5678 9101 1121"
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#071C55]"
            maxLength="16"
          />
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-semibold mb-2">
              Expiry Month
            </label>
            <select
              name="expiryMonth"
              value={formData.expiryMonth}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#071C55]"
            >
              <option value="">MM</option>
              {Array.from({ length: 12 }, (_, i) => (
                <option key={i} value={String(i + 1).padStart(2, "0")}>
                  {String(i + 1).padStart(2, "0")}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-semibold mb-2">
              Expiry Year
            </label>
            <select
              name="expiryYear"
              value={formData.expiryYear}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#071C55]"
            >
              <option value="">YYYY</option>
              {Array.from({ length: 10 }, (_, i) => (
                <option key={i} value={new Date().getFullYear() + i}>
                  {new Date().getFullYear() + i}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-semibold mb-2">CVV</label>
          <input
            type="text"
            name="cvv"
            value={formData.cvv}
            onChange={handleChange}
            placeholder="123"
            className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#071C55]"
            maxLength="3"
          />
        </div>

        <div className="mb-6 flex items-center">
          <input
            type="checkbox"
            name="agree"
            checked={formData.agree}
            onChange={handleChange}
            className="mr-2"
          />
          <label className="text-sm">
            I agree to with{" "}
            <span className="text-blue-700">Privacy Policy</span> by proceeding
            with this payment.
          </label>
        </div>
        <h1 className="text-blue-700 text-lg font-semibold">
          INR 1000.00{" "}
          <span className="text-black text-xs">(Total Amount Payable)</span>
        </h1>

        <div className="mt-4">
          <button
            type="submit"
            className={`w-full py-2 px-4 rounded-lg transition flex items-center justify-center ${
              disabled ? "bg-gray-400 cursor-not-allowed" : "bg-[#071C55] text-white"
            }`}
            disabled={disabled}
            onClick={handleShowNotice}
          >
            {disabled ? "Loading..." : "Make Payment"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Payment;

