"use client";

import React, { use, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";

import Image from "next/image";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import Loader from "@/components/ui/Loader";
import Button from "@/components/ui/Button";
import { Error500 } from "@/components/shared/saj-error-pages";
import { BiSolidError } from "react-icons/bi";
import Link from "next/link";

const Page = ({ params }) => {
  const value = use(params);
  const inviteToken = value["invite-token"];
  const [acceptInvite, setAcceptInvite] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const router = useRouter();

  useEffect(() => {
    if (inviteToken) {
      handleAcceptInvite();
    }
  }, [inviteToken]);

  const handleAcceptInvite = async () => {
    try {
      const response = await apiCall(`/invite/accept/${inviteToken}`);
      toast.success("Invite accepted successfully!");
      setAcceptInvite(response.token);
    } catch (error) {
      const message = getErrorMessage(error);
      console.error("Error accepting invite:", message);
      setAcceptInvite(inviteToken);
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-50px)] w-full items-center justify-center px-4">
      {loading ? (
        <Loader />
      ) : error && error != "Invite has already been accepted" ? (
        <main className="relative min-h-screen flex items-center justify-center p-6">
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{
              backgroundImage:
                "url('/assets/bg-images/Squar BG 100 Opacity.png')",
            }}
          ></div>

          <div className="absolute inset-0 bg-white/70"></div>

          <div className="relative w-full max-w-xl border border-gray-200 bg-white shadow-md p-10 text-center">
            <div className="flex justify-center text-yellow-500 ">
              <BiSolidError size={80} />
            </div>

            <h1 className="mt-4 text-2xl font-semibold text-primary">
              Oops! Something went wrong.
            </h1>

            <p className="mt-2 text-gray-700">{error}</p>

            <div className="mt-6 flex flex-col sm:flex-row justify-center gap-3">
              <Button
                onClick={() => router.push("/login")}
                className="px-6 py-2 bg-primary text-white shadow hover:bg-primary/90"
              >
                Login
              </Button>
            </div>
          </div>
        </main>
      ) : acceptInvite ? (
        <div className="p-10 text-center shadow-md">
          <h2 className="mb-4 text-2xl font-bold text-primary">
            {error ? `${error}` : " Invite accepted successfully!"}
          </h2>
          <p className="mb-6 text-gray-700">You can now set your password.</p>

          <Button
            variant="primary"
            onClick={() => router.push(`/set-password/${acceptInvite}`)}
            className="w-full"
          >
            Set Password
          </Button>
        </div>
      ) : null}
    </div>
  );
};

export default Page;
