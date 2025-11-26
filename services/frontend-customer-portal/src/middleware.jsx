import { NextResponse } from "next/server";
import { jwtDecode } from "jwt-decode";

function isTokenExpired(token) {
  if (!token) return true;
  try {
    const decoded = jwtDecode(token);
    return decoded.exp * 1000 < Date.now();
  } catch (error) {
    return true;
  }
}

const userProtectedPaths = [
  "/",
  "/manage-preference",
  "/past-request",
  "/data-rights",
  "/raise-grievance",
  "/time-line",
];
const authPaths = ["/login", "/verify-otp"];

export function middleware(req) {
  const { pathname } = req.nextUrl;
  const token = req.cookies.get("access_token")?.value;
  const tokenExpired = isTokenExpired(token);
  const isUserProtectedPath = userProtectedPaths.some(
    (path) => pathname === path || pathname.startsWith(path + "/")
  );
  const isAuthPath = authPaths.some(
    (path) => pathname === path || pathname.startsWith(path + "/")
  );

  if (isUserProtectedPath && (!token || tokenExpired)) {
    const url = req.nextUrl.clone();
    url.pathname = "/login";
    const res = NextResponse.redirect(url);
    res.cookies.delete("access_token");
    return res;
  }

  if (isAuthPath && token && !tokenExpired) {
    const url = req.nextUrl.clone();
    url.pathname = "/";
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}
