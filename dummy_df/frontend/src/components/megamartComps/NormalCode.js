import React from "react";

const NormalCode = () => {
  return (
    <div className="p-5 bg-black text-white border rounded-md">
      <h2>Normal Code</h2>
      <pre className="rounded-lg shadow-lg p-4">
        {`
import React, { useState } from "react";

const RegisterForm = () => {
   
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
      <button type="submit" className="text-green-500">Submit</button>
    </form>
  );
};
export default RegisterForm;
        `}
      </pre>
    </div>
  );
};

export default NormalCode;
