"use client";
import React, { Suspense } from "react";
import IntegrationGuide from "@/components/features/collectionPoint/IntegrationGuide";
import { useSearchParams } from "next/navigation";
import Loader from "@/components/ui/Loader";

const Page = () => {
  const cpId = useSearchParams().get("cp_id");

  return (
    <Suspense fallback={<Loader />}>
      <IntegrationGuide cpId={cpId} />
    </Suspense>
  );
};

export default Page;
