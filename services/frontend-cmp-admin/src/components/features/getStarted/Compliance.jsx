import React from "react";

import Link from "next/link";
import { getStartedComplianceData as data } from "@/constants/getStartedCompianceData";

const Compliance = () => {
  return (
    <div className="">
      <div className="custom-scrollbar h-[calc(100vh-149px)] overflow-auto bg-backgroundSecondary px-5 pt-5">
        <h1 className="text-2xl font-semibold text-heading">
          Compliance Made Easy!
        </h1>
        <p className="pt-5 text-justify text-sm text-subHeading">
          Starting the journey to comply with the Digital Personal Data
          Protection Act, 2023 can feel like a daunting task for any
          organization. There are so many questions to answer: What steps do we
          need to take to meet the regulations? In what order should they be
          completed to stay on track? Which rules specifically apply to us, and
          how do we figure that out? Who in our organization is responsible for
          what, and how long will each task take? Without a clear plan,
          It&apos;s... easy to get overwhelmed, leading to confusion and
          unnecessary delays.
        </p>
        <p className="pt-5 text-justify text-sm text-subHeading">
          We get it — That&apos;s why we&apos;ve... created a straightforward,
          step-by-step guide to take the guesswork out of compliance. Our guide
          is designed to help you tackle each task with confidence, breaking
          down the process into simple, actionable steps. From setting up
          sub-organizations and customizing your branding to automating data
          discovery and organizing key information — we’ve made it easy. Of
          course, some tasks might not apply depending on the size, industry, or
          specific needs of your organization, but this guide will provide you
          with a solid starting point to understand the full compliance journey.
          By following these steps, You&apos;ll... ensure that nothing important
          gets overlooked, while saving valuable time and resources.
        </p>
        <p className="pt-5 text-justify text-sm  text-subHeading">
          Let&apos;s... make the process smoother, together.
        </p>

        <div className="flex justify-between pt-8">
          <div className="grid w-full grid-cols-1 gap-5 pb-4 2xl:grid-cols-2">
            {data.map((item, index) => (
              <Link
                href={
                  item.url.startsWith("http") ? item.url : `mailto:${item.url}`
                }
                target="_blank"
                rel="noopener noreferrer"
                key={index}
                aria-label={`Navigate to ${item.title}`}
                className="flex items-center gap-2 bg-white px-2 py-3 shadow-md"
              >
                <div className="pl-2 text-subHeading">{item.icon}</div>
                <div>
                  <h2 className="text-[15px] font-semibold text-primary">
                    {item.title}
                  </h2>
                  <p className="text-[11px] leading-none text-gray-600">
                    {item.description}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Compliance;
