import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import React from "react";
import Button from "./Button";

const NoDataFound = ({
  height = "160px",
  label = "No Data Available",
  imageUrl = "/assets/illustrations/no-data-find.png",
}) => {
  const url = usePathname();

  return (
    <div
      className="flex items-center justify-center"
      style={{ height: `calc(100vh - ${height})` }}
    >
      <div className="flex flex-col items-center justify-center">
        <div className="w-[250px]">
          <Image
            height={200}
            width={200}
            src={imageUrl}
            alt="Circle Image"
            className="h-full w-full object-cover"
          />
        </div>
        <div className="mt-5">
          <h1 className="text-xl">{label}</h1>
        </div>
        {url == "/user/consent-governance/consent-gov/purpose-management" && (
          <div className="mt-3 flex items-center gap-4">
            <Link href="#">
              <Button variant="secondary" className="flex gap-5">
                Start Process Inventory
              </Button>
            </Link>
            <Link href="#">
              <Button variant="secondary">Review Data Inventory</Button>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default NoDataFound;
