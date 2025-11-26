"use client";

import Skeleton from "@/components/ui/Skeleton";
import Card from "@/components/features/apps/Card";
import { appModules } from "@/constants/appModules";

const Page = () => {
  return (
    <>
      <div className="flex">
        <div className="mb-6 min-h-screen w-full px-8 pt-8">
          {appModules?.length < 1 ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {Array(21)
                .fill(null)
                .map((_, index) => (
                  <Skeleton key={index} variant="Box" className="h-52 pr-2" />
                ))}
            </div>
          ) : (
            <Card dashboardData={appModules} />
          )}
        </div>
      </div>
    </>
  );
};

export default Page;
