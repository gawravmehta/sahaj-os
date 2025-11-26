import Button from "@/components/ui/Button";
import React from "react";
import { RxCross2 } from "react-icons/rx";

const ShowPreviewModal = ({ noticeHtml, setShowPreviewModal }) => {
  return (
    <div
      onClick={() => setShowPreviewModal(false)}
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50 bg-opacity-70"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative flex w-full max-w-2xl flex-col items-center justify-center border border-[#c7cfe2] bg-white p-2 pt-6"
      >
        <div className="absolute right-5 top-4">
          <Button variant="close" onClick={() => setShowPreviewModal(false)}>
            <RxCross2 size={20} />
          </Button>
        </div>
        <h2 className="mb-4 text-xl">Preview Notice</h2>
        <div
          className="medium-scrollbar w-full"
          style={{
            background: "#F9FCFF",
            height: "calc(100vh - 193px)",
            justifyContent: "center",
            overflow: "auto",
          }}
        >
          <iframe
            srcDoc={noticeHtml}
            style={{ width: "100%", height: "100%", border: "none" }}
          />
        </div>
      </div>
    </div>
  );
};

export default ShowPreviewModal;
