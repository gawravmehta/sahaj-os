import React from "react";

const AddressCode = () => {
  return (
    <div className="p-5 bg-black text-white border rounded-md">
      <h2>Normal Code</h2>
      <pre className="rounded-lg shadow-lg p-4 overflow-x-auto">
        {`
import React, { useState } from "react";
const RegisterForm = () => {
   
  return (
    <form>
      <div><label>House No</label>
        <input type="text" name="house-no" value={formData.house-no} onChange={handleChange} />
      </div>
      <div><label>Street Name</label>
        <input type="text" name="street-name" value={formData.street-name} onChange={handleChange} />
      </div>
       <div><label>City </label>
        <input type="text" name="city" value={formData.city} onChange={handleChange} />
      </div>
      <div><label>Postal Code</label>
        <input type="number" name="postal-code" value={formData.postal-code} onChange={handleChange} />
      </div>
      <div><label>State</label>
        <input type="text" name="state" value={formData.state} onChange={handleChange} />
      </div>
       <div><label>Country</label>
        <input type="text" name="country" value={formData.country} onChange={handleChange} />
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

export default AddressCode;
