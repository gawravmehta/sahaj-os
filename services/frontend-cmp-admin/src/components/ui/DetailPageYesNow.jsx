import React from "react";

const DetailPageYesNow = ({ label, data }) => {
  return (
    <>
      <h1 className="pb-2 text-sm text-[#737c7c]">{label}</h1>
      <p>{data ? "Yes" : "No"}</p>
    </>
  );
};

export default DetailPageYesNow;
