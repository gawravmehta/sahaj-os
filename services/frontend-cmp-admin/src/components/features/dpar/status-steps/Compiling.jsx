import { apiCall } from "@/hooks/apiCall";
import React, { useEffect, useState } from "react";
import PastReqCard from "../PastReqCard";

const Compiling = ({ data }) => {
  const [relatedRequestData, setRelatedRequestData] = useState({});

  const fetchData = async () => {
    try {
      const pastreqData = await apiCall(
        `/dpar/get-one/${data?.related_request_id}`
      );
      setRelatedRequestData(pastreqData?.data);
    } catch (err) {
      console.error("Error fetching data:", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div>
      {Object.keys(relatedRequestData).length === 0 ? (
        <div className="text-xl text-gray-500 text-center h-72 flex items-center justify-center">
          No Past Requests Available
        </div>
      ) : (
        <PastReqCard relatedRequestData={relatedRequestData} />
      )}
    </div>
  );
};

export default Compiling;
