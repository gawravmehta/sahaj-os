import { useRouter } from "next/navigation";
import React, { useState } from "react";

// const PaymentForm = ({ handleShowNotice }) => {
//   const [formData, setFormData] = useState({
//     card: "",
//     cvv: "",
//     expiry: "",
//     type: "",
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

const PaymentForm = ({ handleShowNotice, disabled1, setDisabled1 }) => {
  const [formData, setFormData] = useState({
    card: "",
    cvv: "",
    expiry: "",
    type: "",
    upiId: "",
    paypalEmail: "",
  });

  const [paymentMethod, setPaymentMethod] = useState("upi");
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
    console.log(formData);
    setDisabled1(true); // Disable form submission until payment is successful
    handleShowNotice();
    // router.push("/confirm"); // Redirect after form submission
  };
  const updateFormData = () => {
    setFormData({
      card: "1234567812345678",
      cvv: "123",
      expiry: "12/25",
      type: "credit",
      upiId: "yourname@bankname",
      paypalEmail: "name@example.com",
    });
  };
  // const [paymentMethod, setPaymentMethod] = useState('upi');

  return (
    <div className="min-h-screen bg-gray-100 text-gray-800 flex items-center justify-center">
        <button
          onClick={updateFormData}
          className=" absolute top-12 right-10 text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center"
        >
          Fill Data
        </button>
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-lg p-10 border border-gray-200 rounded-lg shadow-2xl bg-white"
      >
        <h2 className="text-4xl font-bold mb-10 text-center text-gray-900">
          Payment Information
        </h2>

        <div className="mb-8">
          <label className="block text-xl font-semibold mb-4 text-gray-700">
            Select Payment Method
          </label>
          <div className="flex items-center space-x-8">
            {["upi", "debit-card", "paypal"].map((method) => (
              <label key={method} className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="paymentMethod"
                  value={method}
                  checked={paymentMethod === method}
                  onChange={() => setPaymentMethod(method)}
                  className="hidden"
                />
                <div
                  className={`w-5 h-5 rounded-full border-2 ${
                    paymentMethod === method
                      ? "bg-indigo-600 border-indigo-600"
                      : "border-gray-400"
                  }`}
                />
                <span className="ml-3 text-lg capitalize">
                  {method.replace("-", " ")}
                </span>
              </label>
            ))}
          </div>
        </div>

        {paymentMethod === "upi" && (
          <div className="mb-6">
            <label
              className="block text-lg font-medium mb-2 text-gray-700"
              htmlFor="upiId"
            >
              UPI ID
            </label>
            <input
              id="upiId"
              name="upiId"
              type="text"
              value={formData.upiId}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-600"
              placeholder="Enter your UPI ID"
            />
            <p className="mt-2 text-sm text-gray-500">
              Example: yourname@bankname
            </p>
          </div>
        )}

        {paymentMethod === "debit-card" && (
          <>
            <div className="mb-6">
              <label
                className="block text-lg font-medium mb-2 text-gray-700"
                htmlFor="card"
              >
                Card Number
              </label>
              <input
                id="card"
                name="card"
                type="text"
                value={formData.card}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-600"
                placeholder="Enter your card number"
              />
              <p className="mt-2 text-sm text-gray-500">
                16-digit number on your card
              </p>
            </div>

            <div className="flex space-x-4 mb-6">
              <div className="w-1/2">
                <label
                  className="block text-lg font-medium mb-2 text-gray-700"
                  htmlFor="expiry"
                >
                  Expiry Date
                </label>
                <input
                  id="expiry"
                  name="expiry"
                  type="text"
                  value={formData.expiry}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-600"
                  placeholder="MM/YY"
                />
                <p className="mt-2 text-sm text-gray-500">Example: 12/25</p>
              </div>
              <div className="w-1/2">
                <label
                  className="block text-lg font-medium mb-2 text-gray-700"
                  htmlFor="cvv"
                >
                  CVV
                </label>
                <input
                  id="cvv"
                  name="cvv"
                  type="text"
                  value={formData.cvv}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-600"
                  placeholder="CVV"
                />
                <p className="mt-2 text-sm text-gray-500">
                  3-digit code on back of your card
                </p>
              </div>
            </div>
          </>
        )}

        {paymentMethod === "paypal" && (
          <div className="mb-6">
            <label
              className="block text-lg font-medium mb-2 text-gray-700"
              htmlFor="paypalEmail"
            >
              PayPal Email
            </label>
            <input
              id="paypalEmail"
              name="paypalEmail"
              type="email"
              value={formData.paypalEmail}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-600"
              placeholder="Enter your PayPal email"
            />
            <p className="mt-2 text-sm text-gray-500">
              Example: name@example.com
            </p>
          </div>
        )}

        <div className="mt-8">
          <button
            disabled={disabled1}
            type="submit"
            className="w-full bg-black text-white px-5 py-3 rounded-md font-semibold text-lg shadow-lg hover:bg-gray-900 transition-colors duration-300"
          >
            Pay
          </button>
        </div>
      </form>
    </div>

    //-------
    // <div>
    //   <form
    //     onSubmit={handleSubmit}
    //     className="max-w-lg  py-10 px-20 bg-white border shadow-md rounded-md"
    //   >
    //     <div className="mb-4">
    //       <label htmlFor="house" className="block text-gray-700">
    //         Card No
    //       </label>
    //       <input
    //         type="number"
    //         id="card"
    //         name="card"
    //         value={formData.card}
    //         onChange={handleChange}
    //         className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
    //       />
    //     </div>
    //     <div className="mb-4">
    //       <label htmlFor="street" className="block text-gray-700">
    //         CVV
    //       </label>
    //       <input
    //         type="number"
    //         id="cvv"
    //         name="cvv"
    //         value={formData.cvv}
    //         onChange={handleChange}
    //         className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
    //       />
    //     </div>
    //     <div className="mb-4">
    //       <label htmlFor="city" className="block text-gray-700">
    //         Card expiry
    //       </label>
    //       <input
    //         type="date"
    //         id="expiry"
    //         name="expiry"
    //         value={formData.expiry}
    //         onChange={handleChange}
    //         className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
    //       />
    //     </div>
    //     <div className="mb-4">
    //       <label htmlFor="state" className="block text-gray-700">
    //         Type
    //       </label>
    //       <input
    //         type="text"
    //         id="type"
    //         name="type"
    //         value={formData.type}
    //         onChange={handleChange}
    //         className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-indigo-500"
    //       />
    //     </div>

    //     <button
    //       type="submit"
    //       className="w-full bg-indigo-500 text-white py-2 rounded-md hover:bg-indigo-600 transition duration-300"
    //     >
    //       Pay
    //     </button>
    //   </form>
    // </div>
  );
};

export default PaymentForm;
