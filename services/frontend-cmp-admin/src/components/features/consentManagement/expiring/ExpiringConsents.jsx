"use client";
import { InputField, SelectInput } from "@/components/ui/Inputs";
import Loader from "@/components/ui/Loader";
import { apiCall } from "@/hooks/apiCall";
import Link from "next/link";
import React, { useEffect, useState } from "react";
import { RxArrowTopRight } from "react-icons/rx";

export default function ExpiringConsents() {
  const [data, setData] = useState([]);
  const [dpId, setDpId] = useState("");
  const [daysToExpire, setDaysToExpire] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);

    try {
      const params = new URLSearchParams();

      if (dpId) params.append("dp_id", dpId);
      if (daysToExpire && daysToExpire !== "" && daysToExpire !== "All") {
        params.append("days_to_expire", daysToExpire);
      }

      const url = `/consent-artifact/get-expiring-consents${
        params.toString() ? `?${params.toString()}` : ""
      }`;

      const res = await apiCall(url);
      setData(res);
    } catch (error) {
      console.error("Error fetching expiring consents", error);
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [dpId, daysToExpire]);

  const expiryOptions = [
    { value: "All", label: "All" },
    { value: "7", label: "7 Days" },
    { value: "15", label: "15 Days" },
    { value: "30", label: "30 Days" },
  ];

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-4 mb-6">
        <div className="flex flex-col w-1/2">
          <InputField
            name="dp_id"
            label={"Filter by DP ID"}
            value={dpId}
            onChange={(e) => setDpId(e.target.value)}
            placeholder="Enter Data Principal ID"
          />
        </div>

        <div className="flex flex-col w-1/2">
          <SelectInput
            name={"expiry"}
            label={"Days to Expire"}
            value={expiryOptions.find((opt) => opt.value === daysToExpire)}
            onChange={(selectedOption) =>
              setDaysToExpire(selectedOption?.value || "")
            }
            options={expiryOptions}
            placeholder={"Select Days to Expire"}
          />
        </div>
      </div>

      {loading && <Loader height="h-96" />}

      <div className="space-y-4">
        {data.length === 0 && !loading && (
          <p className="text-gray-500 text-center">
            No expiring consents found.
          </p>
        )}

        {data.map((dp) => (
          <div
            key={dp.dp_id}
            className=" border  border-gray-300 p-4 shadow-sm bg-white"
          >
            <h2 className="text-lg  mb-3">DP ID: {dp.dp_id}</h2>

            <div className="space-y-3">
              {dp.expiring_purposes.map((p) => (
                <Link
                  href={`/apps/purpose-management/detail/${p.purpose_id}`}
                  key={p.purpose_id}
                >
                  <div className="relative border border-gray-300 hover:bg-gray-50 p-3">
                    <RxArrowTopRight
                      size={20}
                      className="absolute top-1 right-1"
                    />
                    <p className="font-medium text-gray-800">
                      {p.purpose_title}
                    </p>
                    <p className="text-sm  mt-2">
                      Expiry:{" "}
                      {new Date(p.consent_expiry_period).toLocaleString()}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
