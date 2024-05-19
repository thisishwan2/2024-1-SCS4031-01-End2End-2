/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: config => {
    config.module.rules.push({
      test: /\.svg$/,
      use: ["@svgr/webpack"],
    });

    return config;
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'static.cdn.soomgo.com',
        
      },
      {
        protocol: 'https',
        hostname: 'endtwoend.s3.ap-northeast-2.amazonaws.com',
        
      },
    ],
  },
};

export default nextConfig;
