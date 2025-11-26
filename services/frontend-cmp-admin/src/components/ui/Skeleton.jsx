

import PropTypes from "prop-types";
import { cn } from "@/lib/utils";
import React from "react";

const Skeleton = ({ className, variant = "single" }) => {
  const validVariants = [
    "single",
    "multiple",
    "card",
    "Box",
    "CoursesBox",
    "personaCard",
    "personaDetails",
    "campaignDetails",
    "notice",
    "banner",
    "bannerTemplates",
    "incidentCard",
  ];
  const selectedVariant = validVariants.includes(variant) ? variant : "single";

  const renderSingleLine = () => (
    <div className="skeleton-line h-full w-full animate-pulse rounded bg-gray-300 dark:bg-gray-400"></div>
  );

  const renderMultipleLines = () => (
    <>
      <div className="skeleton-line mb-3 h-4 w-full animate-pulse rounded bg-gray-300 dark:bg-gray-400"></div>
      <div className="skeleton-line mb-3 h-4 w-full animate-pulse rounded bg-gray-300 dark:bg-gray-400"></div>
      <div className="skeleton-line h-4 w-3/4 animate-pulse rounded bg-gray-300 dark:bg-gray-400"></div>
    </>
  );

  const renderCard = () => (
    <div className="flex w-full gap-4 px-4 py-2">
      <div className="h-12 w-12 animate-pulse rounded-full bg-gray-300 dark:bg-gray-400"></div>
      <div className="mt-1 w-full pr-16">
        <div className="skeleton-line mb-3 h-4 w-3/4 animate-pulse rounded bg-gray-300 dark:bg-gray-400"></div>
        <div className="skeleton-line h-4 w-full animate-pulse rounded bg-gray-300 dark:bg-gray-400"></div>
      </div>
    </div>
  );

  const PersonaCard = () => (
    <div className="cursor-pointer border bg-white px-3 py-5">
      <div className="relative flex justify-between">
        <div className="skeleton-line h-4 w-32 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
        <div className="skeleton-icon h-10 w-10 animate-pulse rounded-full bg-gray-300 dark:bg-gray-400"></div>
      </div>
      <div className="skeleton-image mx-auto mt-3 h-20 w-20 animate-pulse rounded-full bg-gray-300 dark:bg-gray-400"></div>
      <div className="p-2">
        <div className="skeleton-line mx-auto mt-2 h-4 w-3/4 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
        <div className="skeleton-line mx-auto mt-1 h-4 w-2/4 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
        <div className="skeleton-line mx-auto mt-2 h-4 w-3/4 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
      </div>
    </div>
  );

  const IncidentCard = () => (
    <div className="cursor-pointer border bg-white px-3 py-5">
      <div className="skeleton-image mx-auto mt-3 h-20 w-20 animate-pulse rounded-full bg-gray-300 dark:bg-gray-400"></div>
      <div className="p-2">
        <div className="skeleton-line mx-auto mt-2 h-4 w-3/4 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
        <div className="skeleton-line mx-auto mt-1 h-4 w-2/4 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
        <div className="skeleton-line mx-auto mt-2 h-4 w-3/4 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
      </div>
    </div>
  );

  const renderBox = () => (
    <div className="h-full w-full animate-pulse bg-gray-300 dark:bg-gray-400"></div>
  );

  const renderCoursesBox = () => (
    <div className="h-full w-full">
      <div className="h-32 w-full animate-pulse bg-gray-300 dark:bg-gray-400"></div>
      <div className="my-2 h-2.5 w-32 animate-pulse rounded-full bg-gray-300 dark:bg-gray-400"></div>
      <div className="my-2 h-2.5 animate-pulse rounded-full bg-gray-300 dark:bg-gray-400"></div>
      <div className="h-2.5 animate-pulse rounded-full bg-gray-300 dark:bg-gray-400"></div>
    </div>
  );

  const renderPersonaDetails = () => (
    <div className="w-full space-y-4 p-4">
      <div className="skeleton-image mx-auto mt-3 h-40 w-40 animate-pulse rounded-full bg-gray-300 dark:bg-gray-400"></div>
      <div className="skeleton-line mx-auto mt-4 h-6 w-1/2 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
      <div className="skeleton-line mx-auto mt-2 h-4 w-3/4 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
      <div className="skeleton-line mx-auto mt-2 h-4 w-full animate-pulse bg-gray-300 dark:bg-gray-400"></div>
      <div className="skeleton-line mx-auto mt-2 h-4 w-3/4 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
    </div>
  );

  const notice = () => (
    <div className="h-[350px] w-[300px] animate-pulse border border-gray-300 bg-gray-100 p-4">
      <div className="relative flex justify-between">
        <div className="skeleton-line h-4 w-5 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
        <div className="skeleton-icon h-4 w-16 animate-pulse bg-gray-300 dark:bg-gray-400"></div>
      </div>
      <div className="mb-4 mt-4 h-[220px] w-full bg-gray-300"></div>
      <div className="mb-2 h-4 w-3/4 bg-gray-300"></div>
      <div className="h-3 w-1/2 bg-gray-200"></div>
    </div>
  );
  const banner = () => (
    <div className="h-[400px] w-[280px] animate-pulse border border-gray-300 bg-gray-100 p-5">
      <div className="mb-4 mt-2 h-[300px] w-full bg-gray-300"></div>
      <div className="relative flex justify-between">
        <div className="mb-2 h-4 w-3/4 bg-gray-300"></div>
        <div className="skeleton-icon size-5 animate-pulse rounded-full bg-gray-300 dark:bg-gray-400"></div>
      </div>
      <div>
        <div className="h-3 w-1/2 bg-gray-200"></div>
      </div>
    </div>
  );
  const bannerTemplates = () => (
    <div className="h-[400px] w-[280px] animate-pulse border border-gray-300 bg-gray-100 p-5">
      <div className="mb-4 mt-2 h-[300px] w-full bg-gray-300"></div>
      <div className="relative flex justify-between">
        <div className="mb-2 h-4 w-3/4 bg-gray-300"></div>
      </div>
      <div>
        <div className="h-3 w-1/2 bg-gray-200"></div>
      </div>
    </div>
  );
  const cookiePolicy = () => (
    <>
      <div className="skeleton-line mb-3 h-4 w-1/2 animate-pulse rounded bg-gray-300 dark:bg-gray-400"></div>
      <div className="skeleton-line mb-3 h-4 w-[20%] animate-pulse rounded bg-gray-300 dark:bg-gray-400"></div>
      <div className="skeleton-line h-20 w-full animate-pulse rounded bg-gray-300 dark:bg-gray-400"></div>
    </>
  );
  return (
    <div className={cn("w-full animate-pulse", className)}>
      {variant === "single" && renderSingleLine()}
      {variant === "multiple" && renderMultipleLines()}
      {variant === "card" && renderCard()}
      {variant === "Box" && renderBox()}
      {variant === "CoursesBox" && renderCoursesBox()}
      {variant === "personaCard" && PersonaCard()}
      {variant === "personaDetails" && renderPersonaDetails()}
      {variant === "notice" && notice()}
      {variant === "banner" && banner()}
      {variant === "bannerTemplates" && bannerTemplates()}
     
      {variant === "incidentCard" && IncidentCard()}
    </div>
  );
};

Skeleton.propTypes = {
  className: PropTypes.string,
  variant: PropTypes.oneOf([
    "single",
    "multiple",
    "card",
    "Box",
    "CoursesBox",
    "personaCard",
    "personaDetails",
    "notice",
  ]),
};

export default Skeleton;
