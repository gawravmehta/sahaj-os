import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Skeleton from "@/components/ui/Skeleton";
import Tag from "@/components/ui/Tag";

import React from "react";

const General = ({ vendorData, loading }) => {
  return (
    <div className="mx-auto mt-4 w-full max-w-2xl space-y-4">
      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1> Name:</h1>
          <span className="">
            {" "}
            <Tag
              variant={
                vendorData?.status === "published"
                  ? "active"
                  : vendorData?.status === "archived"
                  ? "inactive"
                  : "draft"
              }
              label={vendorData.status}
              className=" capitalize text-xs"
            />
          </span>{" "}
        </span>
        {!loading ? (
          <p className="capitalize -mt-1">{vendorData?.dpr_name}</p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-28"} />
        )}
      </div>
      <div>
        <span className="flex items-center justify-between  text-subHeading">
          <h1> Legal Name: </h1>
        </span>
        {!loading ? (
          <p className="capitalize">{vendorData?.dpr_legal_name}</p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-28"} />
        )}
      </div>
      <div>
        <span className="flex items-center justify-between text-subHeading">
          <h1>Description: </h1>
        </span>
        {!loading ? (
          <p className="capitalize">{vendorData?.description}</p>
        ) : (
          <Skeleton variant="multiple" />
        )}
      </div>
      <div>
        <span className="flex items-center justify-between text-subHeading">
          <h1>Address: </h1>
        </span>
        {!loading ? (
          <p className="capitalize">{vendorData?.dpr_address}</p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-64"} />
        )}
      </div>
      <div className="flex items-center justify-between">
        <div>
          <span className="flex items-center justify-between text-subHeading">
            <h1> Country: </h1>
          </span>
          {!loading ? (
            <p className="capitalize">{vendorData?.dpr_country}</p>
          ) : (
            <Skeleton variant="single" className={"h-4 w-28"} />
          )}
        </div>
        <div>
          <span className="flex items-center justify-between text-subHeading">
            <h1> Country Risk: </h1>
          </span>
          {!loading ? (
            <p className="capitalize">{vendorData?.dpr_country_risk}</p>
          ) : (
            <Skeleton variant="single" className={"h-4 w-28"} />
          )}
        </div>
        <div>
          <span className="flex items-center justify-between text-subHeading">
            <h1>Industry: </h1>
          </span>
          {!loading ? (
            <p className="capitalize">{vendorData?.industry}</p>
          ) : (
            <Skeleton variant="single" className={"h-4 w-28"} />
          )}
        </div>
      </div>
      <div>
        <span className="flex items-center justify-between text-subHeading">
          <h1>Created By: </h1>
        </span>
        {!loading ? (
          <p className="capitalize">{vendorData?.created_by}</p>
        ) : (
          <Skeleton variant="single" className={"h-4 w-28"} />
        )}
      </div>
      <div className="flex items-center justify-between">
        <div>
          <span className="flex items-center justify-between  text-subHeading">
            <h1> Created At: </h1>
          </span>{" "}
          {!loading ? (
            <DateTimeFormatter
              className="flex flex-row gap-2"
              timeClass=""
              dateTime={vendorData?.created_at}
            />
          ) : (
            <Skeleton variant="single" className={"h-4 w-full"} />
          )}
        </div>
        <div>
          <span className="flex items-center justify-between  text-subHeading">
            <h1>Updated At: </h1>
          </span>{" "}
          {!loading ? (
            <DateTimeFormatter
              className="flex flex-row gap-2"
              timeClass=""
              dateTime={vendorData?.updated_at}
            />
          ) : (
            <Skeleton variant="single" className={"h-4 w-full"} />
          )}
        </div>
      </div>
    </div>
  );
};

export default General;
