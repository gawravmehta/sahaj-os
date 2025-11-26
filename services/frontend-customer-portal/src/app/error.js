
"use client";

import { Error500 } from "@/components/saj-error-pages";





export default function GlobalError({ error, reset }) {
  console.error(error);

  return <Error500 error={error} projectName = "Sahaj"/>;
}
