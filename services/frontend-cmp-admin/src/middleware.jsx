import { NextResponse } from "next/server";

function decodeJwt(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(base64));
  } catch {
    return null;
  }
}

function isTokenExpired(token) {
  if (!token) return true;
  const decoded = decodeJwt(token);
  if (!decoded?.exp) return true;
  return decoded.exp * 1000 < Date.now();
}

export async function middleware(request) {
  const { pathname } = request.nextUrl;

  const token = request.cookies.get("access_token")?.value;
  const tokenExpired = isTokenExpired(token);

  const isNotOrgSetup = request.cookies.get("isNotOrgSetup")?.value === "true";
  const isNotPasswordSet =
    request.cookies.get("isNotPasswordSet")?.value === "true";

  if (
    pathname.startsWith("/accept-invite") ||
    pathname.startsWith("/set-password")
  ) {
    return NextResponse.next();
  }

  if (!token || tokenExpired) {
    if (pathname !== "/login") {
      const url = request.nextUrl.clone();
      url.pathname = "/login";
      const response = NextResponse.redirect(url);
      response.cookies.delete("access_token");
      return response;
    }
    return NextResponse.next();
  }

  if (isNotOrgSetup && pathname.startsWith("/apps")) {
    const url = request.nextUrl.clone();
    url.pathname = "/org-setup";
    return NextResponse.redirect(url);
  }

  if (isNotPasswordSet && pathname.startsWith("/apps")) {
    const url = request.nextUrl.clone();
    url.pathname = "/reset-password";
    return NextResponse.redirect(url);
  }

  if (request.nextUrl.pathname.startsWith("/apps")) {
    try {
      const encodedPath = encodeURIComponent(request.nextUrl.pathname);
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_ADMIN_URL}/auth/check-access/${encodedPath}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await res.json();
      if (!data?.access) {
        return NextResponse.redirect(new URL("/unauthorized", request.url));
      }
    } catch (error) {
      console.error("Error checking access:", error);
      return NextResponse.redirect(new URL("/unauthorized", request.url));
    }
  }

  if (pathname === "/login") {
    const url = request.nextUrl.clone();
    url.pathname = "/apps";
    return NextResponse.redirect(url);
  }

  if (pathname === "/") {
    const url = request.nextUrl.clone();
    url.pathname = "/apps";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)",
  ],
};
