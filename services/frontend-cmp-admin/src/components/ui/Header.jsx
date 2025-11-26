import React from "react";
import Breadcrumbs from "./BreadCrumb";
import { cn } from "@/utils/twMerge";

const Header = ({
  title,
  subtitle,
  titleClassName,
  subtitleClassName,
  breadcrumbsProps,
  subtitleMT = false,
}) => {
  const baseTitleStyles =
    " text-2xl  font-semibold text-heading leading-7 capitalize";
  const baseSubtitleStyles = "mt-[2px] text-sm font-normal text-subHeading";

  const titleClasses = cn(baseTitleStyles, titleClassName);
  const subtitleClasses = cn(baseSubtitleStyles, subtitleClassName);

  return (
    <div className="header-container pb-3.5 pl-6 pt-3 ">
      {breadcrumbsProps && <Breadcrumbs {...breadcrumbsProps} />}
      <div className="">
        {title && <h1 className={titleClasses}>{title}</h1>}
        {subtitle && <p className={subtitleClasses}>{subtitle}</p>}
        {subtitleMT && <p className="h-5"></p>}
      </div>
    </div>
  );
};

export default Header;
