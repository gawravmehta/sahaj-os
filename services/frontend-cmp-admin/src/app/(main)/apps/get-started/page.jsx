"use client";

import Skeleton from "@/components/ui/Skeleton";
import { apiCall } from "@/hooks/apiCall";
import { useLayoutEffect, useState } from "react";
import Card from "@/components/features/getStarted/Card";
import Compliance from "@/components/features/getStarted/Compliance";
import steps from "@/components/features/getStarted/getStartedjson/get-content"

const Page = () => {
  const [checkedSteps, setCheckedSteps] = useState([]);

  return (
    <>
      <div className="flex">
        <div className="flex w-full flex-col">
          <div className="w-full border-b border-borderheader py-5 lg:px-8">
            <h1 className="text-sm font-semibold text-primary sm:text-3xl">
              Lets get you started!
            </h1>
          </div>

          <div className="custom-scrollbar flex h-[calc(100vh-125px)] overflow-auto pt-6">
            <div className="custom-scrollbar flex h-[calc(100vh-149px)] w-full overflow-auto">
              {steps ? (
                <div className="w-full lg:px-8">
                  <div className="flex flex-col gap-3 pb-4">
                    {steps.length > 0 ? (
                      [...steps]
                        .sort((a, b) => a.step_number - b.step_number)
                        .map((step, index) => (
                          <Card
                            key={step.step_id}
                            step={step}
                            checkedSteps={checkedSteps}
                            index={index}
                          />
                        ))
                    ) : (
                      <div className="flex flex-col gap-10 px-4 pb-10 pt-6">
                        {Array(10)
                          .fill(null)
                          .map((_, index) => (
                            <Skeleton
                              key={index}
                              variant="card"
                              className="h-8"
                            />
                          ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="flex h-[100%] items-center justify-center lg:px-8">
                  <h1 className="text-2xl text-gray-600">Data Not Found</h1>
                </div>
              )}
            </div>
            <div className="w-[60%] pr-6">
              <Compliance />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Page;
