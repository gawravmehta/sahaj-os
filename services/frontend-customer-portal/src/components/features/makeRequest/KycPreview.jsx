import { useState, useEffect } from "react";
import { FaTimesCircle, FaSpinner } from "react-icons/fa";
import { apiCall } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import Button from "@/components/ui/Button";

const KycPreview = ({
  kycFront,
  kycBack,
  fileFront,
  fileBack,
  attachments,
  onClose,
}) => {
  const [loading, setLoading] = useState({
    front: false,
    back: false,
    attachments: [],
  });
  const [fileUrls, setFileUrls] = useState({
    front: null,
    back: null,
    attachments: [],
  });

  const extractObjectName = (url) => {
    if (!url) return null;

    try {
      if (url.includes("/")) {
        const parts = url.split("/");
        return parts[parts.length - 1];
      }
      return url;
    } catch (error) {
      return url;
    }
  };

  const fetchFile = async (objectName, type, index = null) => {
    if (!objectName) return null;

    try {
      if (type === "front") setLoading((prev) => ({ ...prev, front: true }));
      if (type === "back") setLoading((prev) => ({ ...prev, back: true }));
      if (type === "attachment" && index !== null) {
        setLoading((prev) => ({
          ...prev,
          attachments: prev.attachments.map((item, i) =>
            i === index ? true : item
          ),
        }));
      }

      const baseURL = process.env.NEXT_PUBLIC_API_URL || "";
      const response = await fetch(
        `${baseURL}/api/v1/grievance/files/${objectName}`,
        {
          headers: {},
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch file: ${response.status}`);
      }

      const blob = await response.blob();
      const fileUrl = URL.createObjectURL(blob);
      if (type === "front") {
        setFileUrls((prev) => ({ ...prev, front: fileUrl }));
      } else if (type === "back") {
        setFileUrls((prev) => ({ ...prev, back: fileUrl }));
      } else if (type === "attachment" && index !== null) {
        setFileUrls((prev) => ({
          ...prev,
          attachments: prev.attachments.map((item, i) =>
            i === index ? fileUrl : item
          ),
        }));
      }
      return fileUrl;
    } catch (error) {
      console.error(`Error fetching ${type} file:`, error);
      toast.error(`Failed to load ${type} file`);
      return null;
    } finally {
      if (type === "front") setLoading((prev) => ({ ...prev, front: false }));
      if (type === "back") setLoading((prev) => ({ ...prev, back: false }));
      if (type === "attachment" && index !== null) {
        setLoading((prev) => ({
          ...prev,
          attachments: prev.attachments.map((item, i) =>
            i === index ? false : item
          ),
        }));
      }
    }
  };

  useEffect(() => {
    if (kycFront) {
      const frontObjectName = extractObjectName(kycFront);
      if (frontObjectName) {
        fetchFile(frontObjectName, "front");
      }
    }

    if (kycBack) {
      const backObjectName = extractObjectName(kycBack);
      if (backObjectName) {
        fetchFile(backObjectName, "back");
      }
    }

    if (attachments && attachments.length > 0) {
      setLoading((prev) => ({
        ...prev,
        attachments: Array(attachments.length).fill(true),
      }));

      setFileUrls((prev) => ({
        ...prev,
        attachments: Array(attachments.length).fill(null),
      }));

      attachments.forEach((attachment, index) => {
        const attachmentObjectName = extractObjectName(attachment);
        if (attachmentObjectName) {
          fetchFile(attachmentObjectName, "attachment", index);
        }
      });
    }

    return () => {
      if (fileUrls.front) URL.revokeObjectURL(fileUrls.front);
      if (fileUrls.back) URL.revokeObjectURL(fileUrls.back);
      fileUrls.attachments.forEach((url) => {
        if (url) URL.revokeObjectURL(url);
      });
    };
  }, [kycFront, kycBack, attachments]);

  if (
    !kycFront &&
    !kycBack &&
    !fileFront &&
    !fileBack &&
    (!attachments || attachments.length === 0)
  )
    return null;

  const renderFilePreview = (file, url, loadingState, type, index = null) => {
    if (loadingState) {
      return (
        <div className="aspect-video bg-gray-100 flex items-center justify-center">
          <FaSpinner className="animate-spin text-gray-500" size={24} />
        </div>
      );
    }

    if (file) {
      const isImage = file.type.startsWith("image/");
      const isPdf = file.type === "application/pdf";
      const objectUrl = URL.createObjectURL(file);

      if (isImage) {
        return (
          <div className="aspect-video bg-gray-100 flex items-center justify-center">
            <img
              src={objectUrl}
              alt={`Uploaded ${type}`}
              className="max-h-64 object-contain"
              onLoad={() => URL.revokeObjectURL(objectUrl)}
            />
          </div>
        );
      } else if (isPdf) {
        return (
          <div className="aspect-video bg-gray-100 flex flex-col items-center justify-center p-4">
            <div className="text-gray-500 mb-2">PDF Document</div>
            <a
              href={objectUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 underline"
              onClick={() => URL.revokeObjectURL(objectUrl)}
            >
              Download PDF
            </a>
            <div className="text-xs text-gray-400 mt-1">{file.name}</div>
          </div>
        );
      } else {
        return (
          <div className="aspect-video bg-gray-100 flex flex-col items-center justify-center p-4">
            <div className="text-gray-500 mb-2">Document File</div>
            <a
              href={objectUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 underline"
              onClick={() => URL.revokeObjectURL(objectUrl)}
            >
              Download File
            </a>
            <div className="text-xs text-gray-400 mt-1">{file.name}</div>
          </div>
        );
      }
    }

    if (url) {
      const isImage = url
        .toLowerCase()
        .match(/\.(jpeg|jpg|gif|png|svg|bmp|webp)$/i);
      const isPdf = url.toLowerCase().match(/\.(pdf)$/i);

      if (isImage) {
        return (
          <div className="aspect-video bg-gray-100 flex items-center justify-center">
            <img
              src={url}
              alt={`${type} file`}
              className="max-h-64 object-contain"
            />
          </div>
        );
      } else if (isPdf) {
        return (
          <div className="aspect-video bg-gray-100 flex flex-col items-center justify-center p-4">
            <div className="text-gray-500 mb-2">PDF Document</div>
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 underline"
            >
              Download PDF
            </a>
          </div>
        );
      } else {
        return (
          <div className="aspect-video bg-gray-100 flex flex-col items-center justify-center p-4">
            <div className="text-gray-500 mb-2">Document File</div>
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 underline"
            >
              Download File
            </a>
          </div>
        );
      }
    }

    return (
      <div className="aspect-video bg-gray-100 flex items-center justify-center">
        <span className="text-gray-500">No file available</span>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50">
      <div className="bg-white  shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-semibold">KYC Documents Preview</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <FaTimesCircle size={24} />
          </button>
        </div>

        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(kycFront || fileFront) && (
              <div className="border rounded-lg p-3">
                <h3 className="font-medium mb-2">Front Side</h3>
                {renderFilePreview(
                  fileFront,
                  fileUrls.front,
                  loading.front,
                  "front"
                )}
                {kycFront && (
                  <div className="mt-2 text-sm text-gray-600 break-all">
                    URL: {kycFront}
                  </div>
                )}
              </div>
            )}

            {(kycBack || fileBack) && (
              <div className="border rounded-lg p-3">
                <h3 className="font-medium mb-2">Back Side</h3>
                {renderFilePreview(
                  fileBack,
                  fileUrls.back,
                  loading.back,
                  "back"
                )}
                {kycBack && (
                  <div className="mt-2 text-sm text-gray-600 break-all">
                    URL: {kycBack}
                  </div>
                )}
              </div>
            )}

            {attachments && attachments.length > 0 && (
              <>
                {attachments.map((attachment, index) => (
                  <div key={index} className="border rounded-lg p-3">
                    <h3 className="font-medium mb-2">Attachment {index + 1}</h3>
                    {renderFilePreview(
                      null,
                      fileUrls.attachments[index],
                      loading.attachments[index],
                      "attachment",
                      index
                    )}
                    <div className="mt-2 text-sm text-gray-600 break-all">
                      URL: {attachment}
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>

          <div className="mt-6 flex justify-end">
            <Button variant="primary" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KycPreview;
