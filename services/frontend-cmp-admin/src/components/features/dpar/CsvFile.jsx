"use client";

import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import UploadFile from "@/components/UploadFile";
import React, { useState } from "react";
import { IoClose } from "react-icons/io5";
import Link from "next/link";

const CsvFile = () => {
  const [csvFile, setCsvFile] = useState(null);
  return (
    <div className="relative h-screen">
      <div className="h-[91vh] w-full pt-16">
        <div className="px-7">
          <Header title="Import File" />
        </div>
        <div className="mt-3 h-[62px] border bg-[#fafafa]"></div>
      </div>

      <div className="fixed bottom-0 right-0 z-0 mt-10 flex h-12 w-full items-center justify-end gap-3 border-t bg-[#fafafa] px-5 py-4 shadow-xl">
        <Link href="/user/dpar/incoming">
          <Button variant="cancel" className="py-1.5">
            Cancel
          </Button>
        </Link>
        <Link href="/user/dpar/incoming">
          <Button variant="primary" className="py-1.5">
            Upload
          </Button>
        </Link>
      </div>
    </div>
  );
};

export default CsvFile;
