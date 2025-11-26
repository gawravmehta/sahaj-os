import React from "react";

import { AiOutlineDelete } from "react-icons/ai";
import { FiEdit2 } from "react-icons/fi";
import Link from "next/link";
import Skeleton from "@/components/ui/Skeleton";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";

const GeneralTab = ({
  breachData,
  loading,
  handlePublish,
  id,
  showPublishButton,
}) => {
  return (
    <div>
      <div className="w-full space-y-3 p-6 text-[14px] mx-auto max-w-2xl text-gray-800">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Incident Name:
            </h1>

            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.incident_name}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>
          <div className="flex items-center gap-2 px-3 py-1 text-[14px] capitalize">
            <div className="flex cursor-pointer gap-3">
              {breachData?.status === "draft" && (
                <Button variant="secondary">
                  <Link href={`/apps/breach-management/${id}`}>
                    <FiEdit2 size={18} />
                  </Link>
                </Button>
              )}
            </div>
            {showPublishButton && (
              <div className="px-3 py-1 text-[14px] capitalize">
                <Button
                  variant="secondary"
                  onClick={handlePublish}
                  loading={loading}
                >
                  Mark as Published
                </Button>
              </div>
            )}
          
          </div>
        </div>

        <div>
          <h1 className="mb-1 font-lato text-sm text-subHeading">
            Description:
          </h1>

          {!loading ? (
            <p className="font-lato capitalize">{breachData?.description}</p>
          ) : (
            <Skeleton variant="single" className={"h-4 w-56"} />
          )}
        </div>
        <div className="mt-4 grid grid-cols-2 gap-x-6 gap-y-4 md:grid-cols-2">
          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">Type:</h1>

            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.incident_type}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Sensitivity:
            </h1>
            
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.incident_sensitivity}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-x-6 gap-y-4 md:grid-cols-2">
          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Current Stage:
            </h1>
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.current_stage}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>
          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">Status:</h1>

            {!loading ? (
              <Tag
                label={
                  breachData?.status === "in_progress"
                    ? "in progress"
                    : breachData?.status || ""
                }
                variant={
                  breachData?.status === "published"
                    ? "active"
                    : breachData?.status === "draft"
                    ? "draft"
                    : breachData?.status === "in_progress"
                    ? "suspended"
                    : breachData?.status === "closed"
                    ? "inactive"
                    : "suspended"
                }
                className="h- mt-2 w-24 font-lato text-[14px] capitalize"
              />
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-x-6 gap-y-4 md:grid-cols-3">
          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Date Occurred:
            </h1>
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.date_occurred}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Date Discovered:
            </h1>
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.date_discovered}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Deadline:
            </h1>
            {!loading ? (
              <p className="font-lato capitalize">{breachData?.deadline}</p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Date Closed:
            </h1>
          
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.date_closed && breachData.date_closed}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">Assign:</h1>
            {!loading ? (
              <p className="font-lato capitalize">{breachData?.assignee}</p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Compliance Standard:
            </h1>
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.compliance_standard}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Regulatory Authority:
            </h1>
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.regulatory_authority}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Regulatory Reported Date:
            </h1>
          
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.regulatory_reported &&
                  breachData?.regulatory_reported_date}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Notification Needed:
            </h1>
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.notification_needed ? "Yes" : "No"}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Notification Sent:
            </h1>
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.notification_sent ? "Yes" : "No"}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Notification Sent Date:
            </h1>
        
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.notification_sent_date &&
                  breachData?.notification_sent_date}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>

          <div>
            <h1 className="mb-1 font-lato text-sm text-subHeading">
              Affected Population:
            </h1>
            {!loading ? (
              <p className="font-lato capitalize">
                {breachData?.affected_population}
              </p>
            ) : (
              <Skeleton variant="single" className={"h-4 w-28"} />
            )}
          </div>
        </div>
        {breachData?.status !== "closed" && (
          <div className="flex justify-end">
            <Button
              variant="delete"
              onClick={() =>
                setDeleteModalData({
                  show: true,
                  id: breachData?._id,
                })
              }
            >
              <AiOutlineDelete size={20} /> Incident
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default GeneralTab;
