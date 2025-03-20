// API Response Types
export interface ApiResponse<T> {
  data: T;
  status: number;
  statusText: string;
  headers: any;
}

// YouTube Video Info Types
export interface VideoInfo {
  title: string;
  author: string;
  length_seconds: number;
  thumbnail_url: string;
  
  // Add the missing properties
  youtube_id?: string;  // The video ID (extracted from URL)
  youtube_url?: string; // The full YouTube URL
}

// Audio Extraction Response Types
export interface AudioDownloadResponse {
  // When direct download is successful, the response is a blob
  type: 'download';
  blob: Blob;
  filename: string;
  contentType: string;
}

export interface StreamUrlResponse {
  title: string;
  stream_url: string;
  thumbnail: string;
  duration: number;
  type: 'stream';
  format: string;
  youtube_url: string;
  note: string;
}

export type AudioResponse = AudioDownloadResponse | StreamUrlResponse;

// Form Input Types
export interface AudioExtractionForm {
  url: string;
  maxDuration?: number;
}

// UI Types
export interface AudioPlayerProps {
  streamData: StreamUrlResponse;
  onClose?: () => void;
}

export interface AudioCardProps {
  title: string;
  thumbnail: string;
  author?: string;
  duration?: number;
  onDownload?: () => void;
  onPlay?: () => void;
  isLoading?: boolean;
}
