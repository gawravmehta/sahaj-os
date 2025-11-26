"use client";

import ResetPassword from "@/components/features/reset-password/ResetPassword";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import Cookies from "js-cookie";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import toast from "react-hot-toast";

const Page = () => {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [password, setPassword] = useState("");
  const [confirm_password, setConfirm_password] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();


  const handleReSetPassword = async () => {
    if (password !== confirm_password) {
      toast.error("Passwords do not match");
    } else {
      setLoading(true);

      try {
        const response = await apiCall(
          `/auth/reset-password?new_password=${password}`,
          {
            method: "POST",
          }
        );
        Cookies.remove("isNotPasswordSet");
        toast.success("Password set successfully");
        router.push("/org-setup");
      } catch (error) {
        const message = getErrorMessage(error);
        toast.error(message);
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="">
      <ResetPassword
        heading="Set Password"
        pword="Password"
        enterpw="Confirm Password"
        confirm="Set Password"
        onClick={handleReSetPassword}
        password={password}
        setPassword={setPassword}
        confirm_password={confirm_password}
        setConfirm_password={setConfirm_password}
        loading={loading}
      />
    </div>
  );
};

export default Page;
