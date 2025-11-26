import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Skeleton from "@/components/ui/Skeleton";

import Link from "next/link";
import React from "react";
import { LuArrowUpRight } from "react-icons/lu";

const SecurityAudit = ({ vendorData, loading }) => {
  return (
    <div className="mx-auto mt-4 w-full max-w-2xl space-y-4">
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
