import Breadcrumbs from "@/components/ui/BreadCrumb";
import Button from "@/components/ui/Button";
import { timelineData } from "@/constants/timelineData";
import Link from "next/link";
import React from "react";

function Page() {
  return (
    <div className=" flex justify-center">
      <div className="w-[622px] pt-12">
        <div className="flex items-center justify-start mt-10 mb-5">
          <div>
            <Breadcrumbs
              path="/manage-preference/time-line"
              labels={{
                "/manage-preference/time-line": "Time Line",
              }}
            />
          </div>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex flex-col gap-1 max-w-3xl">
            <div className="text-xl font-semibold">Collection Point Name</div>
            <div className="text-sm">
              Lorem ipsum dolor sit amet consectetur. Feugiat nisl orci netus
              sit bibendum adipiscing dui cursus. Lorem venenatis ac eget eu id
              ac magna. Id augue tempus iaculis aliquam sed ut urna etiam.
              Aliquam tortor orci nunc a aliquet.
            </div>
          </div>
        </div>
        <div className="mt-10 ">
          {timelineData.map((item, index) => (
            <div key={index} className={`relative mb-8`}>
              <div className="absolute -left-3 top-0">
                <div className="size-16 bg-gray-300 rounded-full"></div>
                {index !== timelineData.length - 1 && (
                  <div className="w-2 h-24 bg-gray-300 absolute top-14 left-[43%]"></div>
                )}
              </div>
              <div className="ml-20">
                <div className="flex items-center justify-between">
                  <div className="pb-5">
                    <h3 className="text-lg font-semibold text-gray-800">
                      {item.title}
                    </h3>
                    <p className="text-gray-600 max-w-3xl">
                      {item.description}
                    </p>
                    <div className="flex items-center justify-start gap-x-5">
                      <p className="text-sm text-gray-600">
                        Agreement: 234-23423-234234{" "}
                      </p>
                      <p className="text-sm text-gray-600">
                        Attestation ID : 2jhhhhhgdsfhdsgdfg
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Page;
