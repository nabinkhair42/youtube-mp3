import { axiosInstance } from '@/config/axios';
import { API_ROUTES } from '@/config/routes';
import { 
  VideoInfo, 
  StreamUrlResponse, 
  AudioExtractionForm,
  
} from '@/types';

// YouTube related services
export const youtubeServices = {
  // Get video information
  async getVideoInfo(url: string): Promise<VideoInfo> {
    // Validate URL before making request
    if (!url || url.trim() === '') {
      throw new Error('YouTube URL cannot be empty');
    }
    
    const response = await axiosInstance.get<VideoInfo>(
      `${API_ROUTES.YOUTUBE_INFO}?url=${encodeURIComponent(url)}`
    );
    return response.data;
  },

  // Extract audio from a YouTube video
  async extractAudio(params: AudioExtractionForm): Promise<Blob | StreamUrlResponse> {
    const { url, maxDuration = 600 } = params;
    
    // Validate URL before making request
    if (!url || url.trim() === '') {
      throw new Error('YouTube URL cannot be empty');
    }
    
    try {
      // First try to get the direct file download
      const response = await axiosInstance.get(
        `${API_ROUTES.YOUTUBE_EXTRACT_AUDIO}?url=${encodeURIComponent(url)}&max_duration=${maxDuration}`,
        {
          responseType: 'blob',
        }
      );
      
      // Check if response is JSON (stream URL) or blob (direct download)
      const contentType = response.headers['content-type'];
      
      if (contentType && contentType.includes('application/json')) {
        // It's a stream URL response
        const reader = new FileReader();
        return new Promise((resolve, reject) => {
          reader.onload = () => {
            try {
              const jsonResponse = JSON.parse(reader.result as string) as StreamUrlResponse;
              resolve(jsonResponse);
            } catch (error) {
              reject(error);
            }
          };
          reader.onerror = () => reject(reader.error);
          reader.readAsText(response.data);
        });
      }
      
      // It's a direct file download
      return response.data as Blob;
    } catch (error) {
      // If direct download fails, try to get stream URL
      console.error('Direct download failed, falling back to stream URL', error);
      const response = await axiosInstance.get<StreamUrlResponse>(
        `${API_ROUTES.YOUTUBE_STREAM_URL}?url=${encodeURIComponent(url)}`
      );
      return response.data;
    }
  },

  // Get stream URL directly
  async getStreamUrl(url: string): Promise<StreamUrlResponse> {
    // Validate URL before making request
    if (!url || url.trim() === '') {
      throw new Error('YouTube URL cannot be empty');
    }
    
    const response = await axiosInstance.get<StreamUrlResponse>(
      `${API_ROUTES.YOUTUBE_STREAM_URL}?url=${encodeURIComponent(url)}`
    );
    return response.data;
  }
};
