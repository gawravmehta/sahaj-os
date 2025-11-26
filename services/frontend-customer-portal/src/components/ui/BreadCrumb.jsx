"use client";

import Link from "next/link";

const Breadcrumbs = ({ path, skip = "", labels = {} }) => {
  const effectivePath = path.startsWith(skip) ? path.replace(skip, "") : path;

  const pathnames = effectivePath.split("/").filter(Boolean);

  return (
    <nav className="flex pb-1.5" aria-label="breadcrumb">
      <ol className="inline-flex items-center space-x-1 md:space-x-2 rtl:space-x-reverse">
        {pathnames.map((value, index) => {
          const href = `${skip}/${pathnames
            .slice(0, index + 1)
            .map((path) => path.replace(/\s+/g, ""))
            .join("/")}`;

          const isLast = index === pathnames.length - 1;
          const isSecondLast = index === pathnames.length - 2;
          const displayLabel =
            labels[href] || decodeURIComponent(value.replace(/-/g, " "));

          return isLast ? (
            <li key={index} aria-current="page">
              <div className="flex items-center">
                <span className="font-lato text-sm capitalize text-primary">
                  {displayLabel}
                </span>
              </div>
            </li>
          ) : (
            <li key={index}>
              <div className="flex items-center">
                <Link
                  href={href}
                  className="mr-2 font-lato text-sm capitalize text-subHeading hover:text-primary"
                >
                  {displayLabel}
                </Link>
                <svg
                  className={`h-3 w-3 rtl:rotate-180 ${
                    isSecondLast
                      ? "text-primary"
                      : "text-subHeading hover:text-primary"
                  }`}
                  aria-hidden="true"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 6 10"
                >
                  <path
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="1.5"
                    d="m1 9 4-4-4-4"
                  />
                </svg>
              </div>
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
