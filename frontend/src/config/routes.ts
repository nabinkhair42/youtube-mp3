export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const API_ROUTES = {
  // YouTube routes
  YOUTUBE_INFO: '/youtube/info',
  YOUTUBE_EXTRACT_AUDIO: '/youtube/extract-audio',
  YOUTUBE_STREAM_URL: '/youtube/stream-url',
  YOUTUBE_PROXY_AUDIO: '/youtube/proxy-audio',
};

export const APP_ROUTES = {
  HOME: '/',
  ABOUT: '/about',
};
