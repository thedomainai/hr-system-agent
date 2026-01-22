/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React strict mode for development
  reactStrictMode: true,

  // Static export for GitHub Pages
  output: 'export',

  // Base path for GitHub Pages (repository name)
  basePath: process.env.NODE_ENV === 'production' ? '/hr-system-agent' : '',

  // Asset prefix for GitHub Pages
  assetPrefix: process.env.NODE_ENV === 'production' ? '/hr-system-agent/' : '',

  // Disable image optimization (requires server)
  images: {
    unoptimized: true,
  },

  // Trailing slash for static export
  trailingSlash: true,
};

module.exports = nextConfig;
