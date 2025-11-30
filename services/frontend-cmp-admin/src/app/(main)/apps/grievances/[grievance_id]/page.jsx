"use client";

import Button from "@/components/ui/Button";
import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Header from "@/components/ui/Header";
import NoDataFound from "@/components/ui/NoDataFound";
import Tag from "@/components/ui/Tag";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { use, useEffect, useState } from "react";
import toast from "react-hot-toast";

const Page = ({ params }) => {
  const { grievance_id: grievanceId } = use(params);
  const [grievance, setGrievance] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (grievanceId) {
      getGrievanceDetail(grievanceId);
    }
  }, [grievanceId]);

  const getGrievanceDetail = async (id) => {
    setLoading(true);
    try {
      const response = await apiCall(`/grievances/view-grievance/${id}`);
      setGrievance(response.data);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const resolveGrievance = async (id) => {
    setLoading(true);
    try {
      const response = await apiCall(`/grievances/resolve-grievance/${id}`, {
        method: "PATCH",
      });
      toast.success("Grievance resolved successfully!");
      getGrievanceDetail(id);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const breadcrumbsProps = {
    path: `/apps/grievances/${grievance?.subject || "Details"}`,
    skip: "/apps",
  };

  return (
    <>
      <div className="flex justify-between border-b border-gray-200">
        <Header
          title={`Grievance: ${grievance?.subject || "Details"}`}
          subtitle="Grievance details and tracking"
          breadcrumbsProps={breadcrumbsProps}
        />
        <div className="flex items-center">
          {grievance?.request_status === "open" && (
            <Button
              onClick={() => resolveGrievance(grievance._id)}
              className="mx-2 my-auto"
              variant="secondary"
            >
              Resolve Grievance
            </Button>
          )}
        </div>
      </div>
      {grievance ? (
        <div className="mx-auto mt-6 w-full max-w-3xl space-y-6 p-4">
          <div className="flex items-center justify-between">
            <div></div>
            <Tag
              label={
                grievance?.request_status === "open"
                  ? "Open"
                  : grievance?.request_status === "resolved"
                  ? "Resolved"
                  : "Draft"
              }
              variant={
                grievance?.request_status === "open"
                  ? "active"
                  : grievance?.request_status === "resolved"
                  ? "outlineBlue"
                  : "draft"
              }
              className="mx-2 my-auto capitalize"
            />
          </div>
          <div>
            <p className="text-sm text-subHeading">Email:</p>
            <p className="font-medium">{grievance.email}</p>
          </div>

          <div>
            <p className="text-sm text-subHeading">Mobile Number:</p>
            <p className="font-medium">{grievance.mobile_number}</p>
          </div>

          <div>
            <p className="text-sm text-subHeading">Message:</p>
            <p className="font-medium">{grievance.message}</p>
          </div>

          <div>
            <p className="text-sm text-subHeading">Category / Sub-category:</p>
            <p className="font-medium">
              {grievance.category} / {grievance.sub_category}
            </p>
          </div>

          <div>
            <p className="text-sm text-subHeading">Data Principal Type:</p>
            <div className="flex flex-wrap gap-2">
              {grievance.dp_type?.map((type, idx) => (
                <Tag key={idx} label={type} variant="outlineBlue" />
              ))}
            </div>
          </div>

          <div className="flex justify-between text-sm text-subHeading">
            <span>
              Created At: <DateTimeFormatter dateTime={grievance.created_at} />
            </span>
            <span>
              Last Updated:{" "}
              <DateTimeFormatter dateTime={grievance.last_updated_at} />
            </span>
          </div>
        </div>
      ) : (
        <NoDataFound />
      )}
    </>
  );
};

export default Page;
