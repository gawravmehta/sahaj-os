/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: [
      "thumbs.dreamstime.com",
      "davidsummertonconsulting.co.uk",
      "c8.alamy.com",
      "www.sony.co.in",
      "assets.ajio.com",
      "d57avc95tvxyg.cloudfront.net",
      "www.reliancedigital.in",
      "pyxis.nymag.com",
      "5.imimg.com",
      "www.kotak.com",
      "stgaccinwbsdevlrs01.blob.core.windows.net",
      "img.freepik.com",
      "www.itmuniversity.org",
    ], // Add your external domain here
    remotePatterns: [
      {
        protocol: "https",
        hostname: "allat.one",
      },
      {
        protocol: "https",
        hostname: "c8.alamy.com",
      },
      {
        protocol: "https",
        hostname: "i.pinimg.com",
      },
      {
        protocol: "https",
        hostname: "thumbs.dreamstime.com",
      },
      {
        protocol: "https",
        hostname: "cdn.pixabay.com",
      },
      {
        protocol: "https",
        hostname: "www.shutterstock.com",
      },
      {
        protocol: "https",
        hostname: "encrypted-tbn0.gstatic.com",
      },
      {
        protocol: "https",
        hostname: "imagecdn.jeevansathi.com",
      },
    ],
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
