import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Skeleton from "@/components/ui/Skeleton";

import Link from "next/link";
import React, { useState } from "react";
import toast from "react-hot-toast";
import { FaCopy, FaEye, FaEyeSlash } from "react-icons/fa6";
import { LuArrowUpRight } from "react-icons/lu";

const SecurityAudit = ({ vendorData, loading }) => {
  return (
    <div className="mx-auto mt-4 w-full max-w-2xl space-y-4">
      <div className="mb-6">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">
          Consent Validation APIs
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <SecretField label="API Key" value={vendorData.api_key} />
          <SecretField
            label="API Secret"
            value={vendorData.api_secret}
            isSecret={true}
          />
        </div>
      </div>
      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1> Security Measures: </h1>
        </span>
        {vendorData?.security_measures?.map((processors, i) =>
          !loading ? (
            <p key={i} className="capitalize">
              {" "}
              {i + 1}. {processors?.measure_name}
            </p>
          ) : (
            <div key={i}>
              <Skeleton variant="single" className={"h-4 w-64"} />
            </div>
          )
        )}
      </div>
      <div className="flex items-center justify-between">
        <div>
          <span className="flex items-center justify-between  text-subHeading">
            <h1> Last Audit: </h1>
          </span>
          {!loading ? (
            <DateTimeFormatter
              date={vendorData?.audit_status?.last_audit_date}
              format="dd MMM yyyy"
            />
          ) : (
            <Skeleton variant="single" className={"h-4 w-28"} />
          )}
        </div>
        <div>
          <span className="flex items-center justify-between  text-subHeading">
            <h1>Next Due: </h1>
          </span>
          {!loading ? (
            <DateTimeFormatter
              date={vendorData?.audit_status?.next_audit_due}
              format="dd MMM yyyy"
            />
          ) : (
            <Skeleton variant="single" className={"h-4 w-28"} />
          )}
        </div>
        <div>
          <span className="flex items-center justify-between  text-subHeading">
            <h1>Result: </h1>
          </span>
          {!loading ? (
            <p className="capitalize">
              {vendorData?.audit_status?.audit_result.replace(/_/g, " ")}
            </p>
          ) : (
            <Skeleton variant="single" className={"h-4 w-28"} />
          )}
        </div>
      </div>
      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1>Contact Person: </h1>
        </span>
        {!loading ? (
          <p className="capitalize">{vendorData?.contact_person?.name}</p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-28"} />
        )}
      </div>
      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1>Contact Email: </h1>
        </span>
        {!loading ? (
          <p>{vendorData?.contact_person?.email}</p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-28"} />
        )}
      </div>
      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1>Contact Phone: </h1>
        </span>
        {!loading ? (
          <p>{vendorData?.contact_person?.phone}</p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-28"} />
        )}
      </div>

      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1>Sub-processors: </h1>
        </span>
        {vendorData?.contract_documents?.map((documents, i) =>
          !loading ? (
            <div key={i} className="mb-1 flex items-center justify-between">
              {" "}
              <span>
                {i + 1}. {documents?.document_name}
              </span>
              <Link
                href={documents?.document_url}
                target="_blank"
                className="flex items-center gap-2  font-normal text-primary"
              >
                View Link <LuArrowUpRight className="size-4" />
              </Link>
            </div>
          ) : (
            <div key={i}>
              <Skeleton variant="single" className={"h-4 w-64"} />
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default SecurityAudit;

const SecretField = ({ label, value, isSecret = false }) => {
  const [show, setShow] = useState(!isSecret);

  const handleCopy = () => {
    if (value) {
      navigator.clipboard.writeText(value);
      toast.success("Copied to clipboard!");
    }
  };

  return (
    <div className="mb-4">
      <label className="mb-1 block text-sm font-medium text-gray-700">
        {label}
      </label>
      <div className="flex items-center gap-2">
        <div className="relative w-full">
          <input
            type={show ? "text" : "password"}
            value={value || ""}
            readOnly
            className="w-full rounded border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none"
          />
          {isSecret && (
            <button
              type="button"
              onClick={() => setShow(!show)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              {show ? <FaEyeSlash /> : <FaEye />}
            </button>
          )}
        </div>
        <button
          type="button"
          onClick={handleCopy}
          className="rounded border border-gray-300 bg-white p-2 text-gray-500 hover:bg-gray-50 hover:text-gray-700"
          title="Copy"
        >
          <FaCopy />
        </button>
      </div>
    </div>
  );
};
