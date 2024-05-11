/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'static.cdn.soomgo.com',
        
      },
      {
        protocol: 'https',
        hostname: 'https://endtwoend.s3.ap-northeast-2.amazonaws.com',
        
      },
    ],
  },
};

export default nextConfig;
