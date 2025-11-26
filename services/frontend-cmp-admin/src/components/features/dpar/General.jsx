import NoDataFound from "@/components/ui/NoDataFound";
import { capitalizeFirstLetter } from "@/utils/capitalizeFirstLetter";

const General = ({ data }) => {
  if (!data)
    return (
      <div>
        <NoDataFound />
      </div>
    );

  return (
    <div className="p-8 text-sm">
      <div className="m-auto grid w-[53%] grid-cols-2 gap-y-4">
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">First Name:</span>{" "}
          {capitalizeFirstLetter(data?.first_name) || "—"}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">Last Name:</span>{" "}
          {capitalizeFirstLetter(data?.last_name) || "—"}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">Core Identifier:</span>{" "}
          {data?.core_identifier || "—"}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">
            Secondary Identifier :
          </span>{" "}
          {data?.secondary_identifier || "—"}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">Country:</span>{" "}
          {capitalizeFirstLetter(data?.country || "—")}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">Category:</span>{" "}
          {capitalizeFirstLetter(data?.dp_type || "Not Yet")}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">Type:</span>{" "}
          {capitalizeFirstLetter(data?.request_type || "Not Yet")}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">Priority:</span>{" "}
          {capitalizeFirstLetter(data?.request_priority || "Not Yet")}
        </div>
        <div className="flex flex-col">
          <span className="font-medium text-subHeading">KYC Type:</span>{" "}
          {capitalizeFirstLetter(data?.kyc_document || "—")}
        </div>
      </div>
    </div>
  );
};

export default General;
