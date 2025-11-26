"use client";

import PasswordSuccessfully from "@/components/features/reset-password/PasswordSuccessfully";
import ResetPassword from "@/components/features/reset-password/ResetPassword";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { useRouter } from "next/navigation";
import { use, useState } from "react";
import toast from "react-hot-toast";

const Page = ({ params }) => {
  const router = useRouter();

  const value = use(params);

  const resetPasswordToken = value["token"];
  const [password, setPassword] = useState("");
  const [confirm_password, setConfirm_password] = useState("");
  const [loading, setLoading] = useState(false);
  const [passwordResetSuccessFully, setPasswordResetSuccessFully] =
    useState(false);

  const handleReSetPassword = async () => {
    setLoading(true);

    if (password.trim() !== confirm_password.trim()) {
      toast.error("Passwords do not match");
      setLoading(false);
      return;
    }
    try {
      const response = await apiCall(`/auth/set-password`, {
        method: "PATCH",
        params: {
          token: resetPasswordToken,
          new_password: password.trim(),
        },
      });

      if (response?.message) {
        toast.success(response?.message);
        setPasswordResetSuccessFully(true);
        router.push("/login");
      } else {
        toast.error("Password reset failed. Please try again.");
      }
      setLoading(false);
    } catch (error) {
      setLoading(false);
      console.error("Error in adding data principal:", error);
      const message = getErrorMessage(error);
      toast.error(message);
    }
  };

  return (
    <div className="">
      {passwordResetSuccessFully ? (
        <PasswordSuccessfully
          title="Password Reset Successfully"
          desc="Log into your account with your new password  "
          type="new password"
          path="/auth/login"
          button="Back to login"
          arrowLeft={true}
        />
      ) : (
        <ResetPassword
          heading="Reset Password"
          pword="New Password"
          enterpw="Confirm Password"
          confirm="Set Password"
          onClick={handleReSetPassword}
          password={password}
          setPassword={setPassword}
          loading={loading}
          confirm_password={confirm_password}
          setConfirm_password={setConfirm_password}
          showLogin={true}
        />
      )}
    </div>
  );
};

export default Page;
