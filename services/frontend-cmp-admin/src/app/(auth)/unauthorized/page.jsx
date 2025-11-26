import Image from "next/image";
import Link from "next/link";
import { FaArrowLeftLong } from "react-icons/fa6";
import sahajIllustration from "@/../public/assets/illustrations/sahaj-illustration.png";

export default function ForbiddenPage() {
  return (
    <div className="flex h-[calc(100vh-3rem)] flex-col items-center justify-center bg-white px-4">
      <div className="w-full flex justify-center items-center flex-col text-center -mt-20 ">
        <div className="relative aspect-square h-[350px] ">
          <Image
            alt="rtr-pic"
            src={sahajIllustration}
            layout="fill"
            objectFit="cover"
            objectPosition="center"
            className="h-full w-full "
          />
        </div>
        <h2 className="mt-6 text-2xl font-semibold text-gray-800">
          Access Denied
        </h2>
        <p className="mb-6 text-gray-600">
          You do not have permission to access this page.
        </p>
        <Link
          href="/apps"
          className=" bg-primary px-6 py-2 text-white shadow flex items-center gap-2 transition hover:bg-primary/90"
        >
          <FaArrowLeftLong />
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
