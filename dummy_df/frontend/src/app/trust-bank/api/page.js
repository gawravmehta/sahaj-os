// https://www.npmjs.com/package/swagger-ui-react
// install it using `npm i swagger-ui-react`

"use client";
import React, { useState } from "react";
import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";

import apijson from "@/app/trust-bank/api-endpoints.json"; //static file with json data from /openapi.json

//Add this in your static open.json file after info
// "servers": [
//    {
//      "url": "https://api.cumulate.live/"
//    }
//  ],

const Page = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showModal, setShowModal] = useState(true);

  const handleSubmit = () => {
    if (email === "demo@concur.live" && password === "concurlive") {
      setShowModal(false);
    } else {
      alert("Invalid credentials!");
    }
  };

  return (
    <div>
      {showModal && (
        <div className="fixed top-0">
          <div className="w-screen h-screen absolute bg-black/50 backdrop-blur-[2px]"></div>
          <div className="flex items-center justify-center w-screen h-screen">
            <div className="h-[350px] flex items-center justify-center z-50  w-[600px] bg-white  m-auto  shadow-xl border-2 border-green-500 px-10 py-5">
              <div className="">
                <h1 className="text-xl font-semibold text-center mb-5">
                  Authentication
                </h1>
                <label htmlFor="" className="">Email</label>
                <input
                  type="email"
                  className="w-full  p-2 outline-none border-2 mb-4"
                  placeholder="Enter Email"
                  onChange={(e) => setEmail(e.target.value)}
                />
              <label  htmlFor="">Password</label>
                <input
                  type="password"
                  className="w-full  p-2  outline-none border-2"
                  placeholder="Enter Password"
                  onChange={(e) => setPassword(e.target.value)}
                />
                <div className="flex items-center justify-center mt-5">
                  <button
                    onClick={() => handleSubmit()}
                    className=" py-2 px-4 border-2 border-green-500 text-green-500 rounded"
                  >
                    Submit
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      <div className="-z-20">
        <SwaggerUI spec={JSON.stringify(apijson)} />
      </div>
    </div>
  );
};

export default Page;
