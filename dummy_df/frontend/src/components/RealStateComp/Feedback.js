"use client"
import React, { useState } from 'react'

const Feedback = () => {

 const [formData, setFormData] = useState({
   name: "",
   email: "",
   agentName: "",
   rating: "",
   comments: "",
 });

 const handleChange = (e) => {
   setFormData({ ...formData, [e.target.name]: e.target.value });
 };

 const handleSubmit = (e) => {
   e.preventDefault();
   console.log(formData);
 };


  return (
    <div className=" h-screen flex items-center justify-center">
      <div className="max-w-lg mx-auto p-8 border rounded-lg shadow-lg w-[50%] bg-white">
        <h2 className="text-2xl font-bold mb-6 text-center">
          Property Review Form
        </h2>
        <form>
          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">
              Name
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300"
              placeholder="Enter your name"
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">
              Email Address
            </label>
            <input
              type="email"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300"
              placeholder="Enter your email"
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">
              Property Address
            </label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300"
              placeholder="Enter the property address"
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">
              Rating (1-5 Stars)
            </label>
            <select className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300">
              <option value="1">1 Star</option>
              <option value="2">2 Stars</option>
              <option value="3">3 Stars</option>
              <option value="4">4 Stars</option>
              <option value="5">5 Stars</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 font-semibold mb-2">
              Review/Comments
            </label>
            <textarea
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300"
              placeholder="Enter your review or comments"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            Submit Review
          </button>
        </form>
      </div>
    </div>
  );
}

export default Feedback