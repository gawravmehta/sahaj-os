
import { languagesOptions } from "@/constants/countryOptions";
import Link from "next/link";

export function getLanguageLabel(value, useNative = false) {
  const language = languagesOptions.find(
    (option) => option.value === value || option.alt === value
  );

  if (!language) return value;

  if (useNative && language.nativeLabel) {
    return `${language.label} ( ${language.nativeLabel} )`;
  }

  return language.label;
}

export function isValidObjectId(id) {
  const objectIdRegex = /^[a-f\d]{24}$/i;
  const hex32Regex = /^[a-f\d]{32}$/i;
  const uuidRegex =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

  return objectIdRegex.test(id) || hex32Regex.test(id) || uuidRegex.test(id);
}

const InvalidIdWrapper = ({ id, children }) => {
  if (!isValidObjectId(id)) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-linear-to-br from-gray-50 to-gray-100">
        <h1 className="text-7xl font-extrabold text-red-500">404</h1>
        <p className="mt-4 text-2xl font-semibold text-gray-800">
          Page Not Found
        </p>
        <p className="mt-2 text-gray-600">
          Oops! The page you are looking for doesn&apos;t exist or has been
          moved.
        </p>

        <Link
          href="/"
          className="mt-6 rounded-xl bg-red-500 px-5 py-2 text-white shadow transition hover:bg-red-600"
        >
          ⬅ Back to Home
        </Link>
      </div>
    );
  }

  return <>{children}</>;
};

export default InvalidIdWrapper;
