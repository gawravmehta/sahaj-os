import React from "react";

const PersonalInfo = ({ userInfo }) => {
  return (
    <div className=" flex flex-col gap-3  py-10 px-20 bg-white border shadow-md rounded-md text-gray-700">
      <div>
        <div className=" flex  gap-2  ">
          <h1 className=""> First Name </h1> -
          <h1 className="text-black"> {userInfo?.firstName}</h1>
        </div>
        <div className=" flex gap-2">
          <h1> Last Name </h1> -{" "}
          <h1 className="text-black"> {userInfo?.lastName}</h1>
        </div>
        <div className=" flex gap-2">
          <h1> Email </h1> - <h1 className="text-black">{userInfo?.email}</h1>
        </div>
        <div className=" flex gap-2">
          <h1> Mobile </h1> -{" "}
          <h1 className="text-black"> {userInfo?.mobile}</h1>
        </div>
      </div>
    </div>
  );
};

export default PersonalInfo;
