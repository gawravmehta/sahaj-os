import Header from "@/components/ui/Header";
import Link from "next/link";
import React from "react";
import { LuFileClock, LuFileUp } from "react-icons/lu";

const Page = () => {
  const cards = [
    {
      icon: <LuFileUp className="h-7 w-7" />,
      title: "New Upload",
      description:
        "Upload a new file for bulk verification. Ensure it meets the required format and validation rules.",
      link: "/apps/consent-validation/bulk-verification/bulk-upload",
    },
    {
      icon: <LuFileClock className="h-7 w-7" />,
      title: "Previously Uploaded",
      description:
        "Review your uploaded files with status indicators. Check upload time or download them anytime.",
      link: "/apps/consent-validation/bulk-verification/previously-uploaded",
    },
  ];

  const breadcrumbsProps = {
    path: "/apps/consent-validation/bulk-verification",
    skip: "/apps",
  };

  return (
    <div className="flex">
      <div className="w-full">
        <div className="w-full border-b sm:border-borderheader">
          <Header
            title="Import Bulk Verification"
            subtitle="Upload your customer's data here."
            breadcrumbsProps={breadcrumbsProps}
          />
        </div>
        <div className="flex flex-wrap justify-center gap-8 p-10">
          {cards.map((card, index) => (
            <Link
              href={card.link}
              key={index}
              className="w-80 border border-borderSecondary bg-white p-5 transition-all duration-500 hover:shadow-md"
            >
              <div className="mb-3 text-subHeading">{card.icon}</div>
              <h3 className="mb-1 font-medium">{card.title}</h3>
              <p className="text-sm font-normal text-subHeading">
                {card.description}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Page;
