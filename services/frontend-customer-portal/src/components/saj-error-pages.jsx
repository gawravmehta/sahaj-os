import React from "react";
import Link from "next/link";
import { GoArrowLeft } from "react-icons/go";
import Button from "@/components/ui/Button";
import { getErrorMessage } from "@/utils/errorHandler";
import { BiSolidError } from "react-icons/bi";

export function Error404({ projectName = "Sahaj" }) {
  return (
    <main
      style={{
        backgroundImage: "url('/assets/bg-images/Squar BG 100 Opacity.png')",
      }}
      className="min-h-screen flex items-center justify-center p-6 
               bg-no-repeat bg-cover bg-center"
    >
      <div className="max-w-3xl w-full text-center p-10 shadow-lg bg-white">
        <div className="text-9xl font-extrabold tracking-tight text-gray-200">
          404
        </div>
        <h1 className="mt-4 text-3xl font-bold text-primary">Page Not Found</h1>
        <p className="mt-2 text-gray-600">
          We couldn’t find the page you’re looking for in{" "}
          <span className="font-medium text-primary">{projectName}</span>.
        </p>

        <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/"
            className=" flex items-center gap-2 justify-center w-[20rem] px-5 py-2  bg-primary text-white font-medium hover:opacity-95"
          >
            <GoArrowLeft size={20} />
            Go to Dashboard
          </Link>
        </div>

        <div className="mt-8 text-xs text-gray-400">
          If you typed the address manually, make sure it is correct.
        </div>
      </div>
    </main>
  );
}

export function Error500({ error, reset }) {
  const message = getErrorMessage(error);
  return (
    <main className="relative min-h-screen flex items-center justify-center p-6">
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{
          backgroundImage: "url('/assets/bg-images/Squar BG 100 Opacity.png')",
        }}
      ></div>

      <div className="absolute inset-0 bg-white/70"></div>

      <div className="relative w-full max-w-xl border border-gray-200 bg-white shadow-md p-10 text-center">
        <div className="flex justify-center text-yellow-500 ">
          <BiSolidError size={80} />
        </div>

        <h1 className="mt-4 text-2xl font-semibold text-primary">
          Internal Server Error
        </h1>

        <p className="mt-2 text-gray-700">
          Something went wrong on our end. Please try again or go back to the
          homepage.
        </p>

        <div className="mt-6 flex flex-col sm:flex-row justify-center gap-3">
          <Button
            onClick={() => reset?.()}
            className="px-6 py-2 bg-primary text-white shadow hover:bg-primary/90"
          >
            Try Again
          </Button>

          <Link href="/" passHref>
            <Button className="px-6 py-2 border border-primary text-primary bg-transparent hover:bg-primary hover:text-white shadow transition">
              Go Dashboard
            </Button>
          </Link>
        </div>

        {error && (
          <details className="mt-6 bg-gray-100 p-4 border border-gray-200 text-left">
            <summary className="cursor-pointer font-medium text-primary">
              Technical Details
            </summary>
            <pre className="mt-3 text-sm text-red-600 whitespace-pre-wrap">
              {message}
            </pre>
          </details>
        )}
      </div>
    </main>
  );
}
export default function DefaultErrorPage(props) {
  return <Error404 {...props} />;
}
