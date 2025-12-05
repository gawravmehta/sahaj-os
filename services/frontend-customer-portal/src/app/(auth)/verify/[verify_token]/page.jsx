"use client";
import { useState, useEffect, use } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { apiCall } from "@/hooks/apiCall";

const Page = ({ params: paramsPromise }) => {
  const router = useRouter();
  const { verify_token: token } = use(paramsPromise);

  const [isLoading, setIsLoading] = useState(true);
  const [isCancelling, setIsCancelling] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState(null);

  useEffect(() => {
    const verifyEmail = async () => {
      try {
        const response = await apiCall(`/api/v1/grievance/verify`, {
          method: "POST",
          data: { token: token },
        });

        toast.success(response.message);
        setVerificationStatus("success");
      } catch (error) {
        console.error("Verification error:", error);
        toast.error(error.message || "Verification failed");
        setVerificationStatus("error");
      } finally {
        setIsLoading(false);
      }
    };

    if (token) {
      verifyEmail();
    }
  }, [token]);

  const handleCancel = async () => {
    try {
      setIsCancelling(true);
      await apiCall("/api/v1/grievance/cancel", {
        method: "DELETE",
        data: { token: token },
      });
      toast.success("Request cancelled successfully");
      router.push("/past-request");
    } catch (error) {
      console.error("Cancellation error:", error);
      toast.error(error.message || "Cancellation failed");
    } finally {
      setIsCancelling(false);
    }
  };

  const handleContinue = () => {
    router.push("/past-request");
  };

  const handleGoHome = () => {
    router.push("/");
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
        <div className="bg-white  shadow-xl p-8 max-w-md w-full text-center">
          <div className="flex flex-col items-center">
            <div className="w-16 h-16 border-4 border-t-transparent rounded-full animate-spin mb-6"></div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Verifying Your Email
            </h2>
            <p className="text-gray-600">
              Please wait while we verify your email address...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-gray-100 z-50 ">
      <div className="bg-white  shadow-xl p-8 max-w-md w-full">
        <div className="text-center mb-6">
          {verificationStatus === "success" ? (
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-12 h-12 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M5 13l4 4L19 7"
                ></path>
              </svg>
            </div>
          ) : (
            <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-10 h-10 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M6 18L18 6M6 6l12 12"
                ></path>
              </svg>
            </div>
          )}

          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            {verificationStatus === "success"
              ? "Grievance Request Verified"
              : "Verification Failed"}
          </h2>
          <p className="text-gray-600">
            {verificationStatus === "success"
              ? "Your Grievance Request Has been Verified."
              : "There was an error verifying your email. Please try again or contact support."}
          </p>
        </div>

        <div className="flex flex-col gap-4 mt-6">
          {verificationStatus === "success" ? (
            <>
              <button
                onClick={handleContinue}
                className="bg-primary hover:bg-hover text-white  py-2.5 px-4 transition duration-200 cursor-pointer"
              >
                Continue to Past Requests
              </button>
              <button
                onClick={handleCancel}
                disabled={isCancelling}
                className="flex items-center justify-center cursor-pointer gap-2 border border-red-500 text-red-600 hover:bg-red-50  py-2.5 px-4 transition duration-200 disabled:opacity-50"
              >
                {isCancelling ? (
                  <>
                    <div className="w-5 h-5 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
                    Cancelling...
                  </>
                ) : (
                  "Cancel Request"
                )}
              </button>
            </>
          ) : (
            <button
              onClick={handleGoHome}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4  transition duration-200"
            >
              Go to Homepage
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Page;
