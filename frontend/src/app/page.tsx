'use client';

import { useState } from 'react';
import { VideoInfo, StreamUrlResponse } from '@/types';
import { UrlInput } from '@/components/youtube/url-input';
import { VideoCard } from '@/components/youtube/video-card';
import { AudioPlayer } from '@/components/youtube/audio-player';
import { Card, CardContent } from '@/components/ui/card';
import { toast } from 'sonner';

export default function HomePage() {
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [streamData, setStreamData] = useState<StreamUrlResponse | null>(null);

  const handleVideoInfoReceived = (info: VideoInfo) => {
    setVideoInfo(info);
    setStreamData(null); // Reset stream data when new video info is received
  };

  const handleAudioResponse = (blob: Blob, filename: string) => {
    // Create download link for the audio file
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    URL.revokeObjectURL(url);
    document.body.removeChild(a);
    toast.success('Download started!');
  };

  const handleStreamResponse = (data: StreamUrlResponse) => {
    setStreamData(data);
  };

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="flex flex-col items-center justify-center mb-8 text-center">
        <h1 className="text-4xl font-bold mb-2">YouTube Audio Extractor</h1>
        <p className="text-xl text-muted-foreground max-w-2xl">
          Extract audio from YouTube videos and download them as MP3 files or stream them directly.
        </p>
      </div>

      <div className="max-w-2xl mx-auto mb-8">
        <UrlInput onVideoInfoReceived={handleVideoInfoReceived} />
      </div>

      {videoInfo && videoInfo !== null && (
        <div className="max-w-2xl mx-auto mb-8">
          <VideoCard 
            videoInfo={videoInfo} 
            onAudioResponse={handleAudioResponse}
            onStreamResponse={handleStreamResponse}
          />
        </div>
      )}

      {streamData && streamData !== null && (
        <div className="max-w-2xl mx-auto">
          <AudioPlayer 
            streamData={streamData} 
            onClose={() => setStreamData(null)} 
          />
        </div>
      )}

      {!videoInfo && !streamData && (
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardContent className="p-6 text-center">
              <h2 className="text-xl font-semibold mb-2">How to use</h2>
              <ol className="text-left list-decimal pl-5 space-y-2">
                <li>Paste a YouTube video URL in the input field above</li>
                <li>Click the &quot;Extract Audio&quot; button to retrieve video information</li>
                <li>Click &quot;Download Audio&quot;  to extract and download the audio</li>
                <li>If direct download is not available, you&apos;ll get a player to stream the audio</li>
              </ol>
            </CardContent>
          </Card>
        </div>
      )}
    </main>
  );
}
