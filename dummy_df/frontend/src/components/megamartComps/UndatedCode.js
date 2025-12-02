"use client"

import React from "react";

const UpdatedCode = () => {
  return (
    <div className="p-5 bg-black  text-white border rounded-md">
      <h2 className="">Updated Code</h2>
      <pre className="rounded-lg shadow-lg p-4 ">
        <code>
          {`
import React, { useState } from "react";
`}
          <span className="bg-yellow-700">{`
import { morajNoticeCenter } from "con-notice/morajNoticeCenter"; 
`}</span>
          {`
const RegisterForm = () => `}

          <span className="bg-yellow-700">{`
const handleShowNotice = () => {
 morajNoticeCenter(
    "66a34fb83b3523e0d76268d2",
    "a82867ce6edda37a",
    "66a34e793b3523e0d76268d0",
    "kYc3H3SHDN9d8ZQLNwDMbw",
    "C5xnyDbv8DRIHepgWpzx3m_G8Mnhyyb2Hv0BRLFu38M"
  );
};`}</span>
          {`
   
  return (
    <form>
      <div><label>First Name</label>
        <input type="text" name="firstName" value={formData.firstName} onChange={handleChange} />
      </div>
      <div><label>Last Name</label>
        <input type="text" name="lastName" value={formData.lastName} onChange={handleChange} />
      </div>
      <div><label>Email</label>
        <input type="email" name="email" value={formData.email} onChange={handleChange} />
      </div>
      <div><label>Mobile Number</label>
        <input type="tel" name="mobile" value={formData.mobile} onChange={handleChange} />
      </div>
       `}
          <span className="bg-yellow-700">{`
      <button onClick={handleShowNotice}>Notice center</button>
`}</span>
          {`
      <button type="submit" className="text-green-500">Submit</button>
    </form>
  );
};
export default RegisterForm;
          `}
        </code>
      </pre>
    </div>
  );
};

export default UpdatedCode;
