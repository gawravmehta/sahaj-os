"use client";

import Actions from "@/components/features/getStarted/Actions";
import steps from "@/components/features/getStarted/getStartedjson/get-content";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import Skeleton from "@/components/ui/Skeleton";
import { getErrorMessage } from "@/utils/errorHandler";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { use, useLayoutEffect, useState } from "react";
import toast from "react-hot-toast";

const Page = ({ params }) => {
  const { id: id } = use(params);
  const router = useRouter();
  const [data, setData] = useState(null);
  const [isActive, setIsActive] = useState(false);
  const [allSteps, setAllSteps] = useState(steps);
  const [isLoading, setIsLoading] = useState(false);
  const token = Cookies.get("access_token");

  useLayoutEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    const filteredStep = allSteps.find((step) => step.step_id === id);
    setData(filteredStep);
  };

  useLayoutEffect(() => {
    const allActionsCompleted = data?.recommended_actions?.every(
      (action) => action.is_action_completed
    );
    setIsActive(allActionsCompleted);
  }, [data]);

  const updateStepsFile = async (updatedSteps) => {
    try {
      const response = await fetch("/api/update-step", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ steps: updatedSteps }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setAllSteps(updatedSteps);
      return true;
    } catch (error) {
      console.error("API failed, using localStorage fallback:", error);

      try {
        localStorage.setItem("getStartedSteps", JSON.stringify(updatedSteps));
        setAllSteps(updatedSteps);
        toast.success("Changes saved locally");
        return true;
      } catch (localError) {
        toast.error("Failed to save changes");
        console.error("Local storage error:", localError);
        return false;
      }
    } finally {
      setIsLoading(false);
    }
  };

  const markOrganizationCompleted = async () => {
    setIsLoading(true);
    try {
      const stepIndex = allSteps.findIndex((step) => step.step_id === id);

      if (stepIndex === -1) {
        toast.error("Step not found");
        return;
      }

      const updatedSteps = JSON.parse(JSON.stringify(allSteps));
      updatedSteps[stepIndex].is_section_completed = true;

      const success = await updateStepsFile(updatedSteps);

      if (success) {
        setData(updatedSteps[stepIndex]);
        toast.success("Step marked as completed");
        router.push("/apps/get-started");
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      setIsLoading(false);
    }
  };

  const updateActionStatus = async (action_number) => {
    const stepIndex = allSteps.findIndex((step) => step.step_id === id);

    if (stepIndex === -1) return;

    const updatedSteps = JSON.parse(JSON.stringify(allSteps));
    const actionIndex = updatedSteps[stepIndex].recommended_actions.findIndex(
      (action) => action.action_number === action_number
    );

    if (actionIndex === -1) return;

    const currentStatus =
      updatedSteps[stepIndex].recommended_actions[actionIndex]
        .is_action_completed;
    updatedSteps[stepIndex].recommended_actions[
      actionIndex
    ].is_action_completed = !currentStatus;

    if (!currentStatus) {
      updatedSteps[stepIndex].recommended_actions[actionIndex].completed_on =
        new Date().toISOString();
      updatedSteps[stepIndex].recommended_actions[actionIndex].completed_by =
        "current_user_id";

      updatedSteps[stepIndex].completed_action_count =
        (updatedSteps[stepIndex].completed_action_count || 0) + 1;
    }

    const success = await updateStepsFile(updatedSteps);

    if (success) {
      setData(updatedSteps[stepIndex]);
    }
  };
  const breadcrumbsProps = {
    path: `/apps/get-started/${data?.step_title}`,
    skip: "/apps/",
  };

  return (
    <>
      <div className="flex w-full items-center">
        <div className="w-full">
          <div className="border-b border-borderheader">
            <Header
              title="Concur Setup Guide"
              subtitle="Follow these steps to onboard your organization and ensure DPDPA compliance seamlessly."
              breadcrumbsProps={breadcrumbsProps}
            />
          </div>
          <div className="custom-scrollbar h-[calc(100vh-152px)] overflow-auto pb-4">
            <div className="mt-5 w-full bg-white px-6 py-4 pb-16 shadow-lg sm:mx-8 lg:ml-8 lg:w-[90%] xl:w-[70%]">
              <h1 className="mb-2 w-full text-2xl">
                <div className="w-full">
                  {data?.step_title ? (
                    <span>{data.step_title}</span>
                  ) : (
                    <Skeleton variant="single" className={"h-4 w-full"} />
                  )}
                </div>
              </h1>

              <div className="mb-6 w-full text-gray-800">
                {data?.step_description ? (
                  <p className="text-gray-800">{data.step_description}</p>
                ) : (
                  <Skeleton variant="multiple" className={"w-full"} />
                )}
              </div>

              <div className="mb-6">
                <h2 className="mb-2 text-xl">Why?</h2>
                <div className="text-gray-800">
                  {data?.step_why ? (
                    <p className="text-gray-800">{data.step_why}</p>
                  ) : (
                    <Skeleton variant="multiple" />
                  )}
                </div>
              </div>

              <div>
                <h2 className="mb-4 text-xl">Actions</h2>
                <div className="list-inside list-disc space-y-2 text-gray-700">
                  {data?.recommended_actions?.length > 0 ? (
                    <Actions
                      data={{
                        ...data,
                        recommended_actions: [...data.recommended_actions].sort(
                          (a, b) =>
                            Number(a.action_number) - Number(b.action_number)
                        ),
                      }}
                      setData={setData}
                      updateActionStatus={updateActionStatus}
                    />
                  ) : (
                    <Skeleton variant="multiple" />
                  )}
                </div>
              </div>

              <div className="mt-8 text-center">
                <Button
                  variant="primary"
                  className={`float-end ${
                    isActive && !isLoading ? "bg-primary" : "bg-gray-300"
                  }`}
                  disabled={
                    !isActive || isLoading || data?.is_section_completed
                  }
                  onClick={markOrganizationCompleted}
                >
                  {isLoading ? "Saving..." : "Completed"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Page;
