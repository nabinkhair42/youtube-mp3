"use client";

import { VideoInfo } from "@/types";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useMutation } from "@tanstack/react-query";
import { youtubeServices } from "@/services";
import { toast } from "sonner";
import { useState } from "react";

interface VideoCardProps {
  videoInfo: VideoInfo;
  onAudioResponse: (blob: Blob, filename: string) => void;
  onStreamResponse: (streamData: any) => void;
}

export function VideoCard({
  videoInfo,
  onAudioResponse,
  onStreamResponse,
}: VideoCardProps) {
  const [isDownloading, setIsDownloading] = useState(false);

  // Get YouTube URL from video info or construct it from the ID
  const getYoutubeUrl = (): string => {
    // If full URL is provided, use it
    if (
      videoInfo.youtube_url &&
      videoInfo.youtube_url.includes("youtube.com")
    ) {
      return videoInfo.youtube_url;
    }

    // If ID is provided, construct URL
    if (videoInfo.youtube_id) {
      return `https://www.youtube.com/watch?v=${videoInfo.youtube_id}`;
    }

    // Extract ID from URL if possible
    if (videoInfo.youtube_url) {
      const regExp = /^.*(youtu.be\/|v\/|e\/|u\/\w+\/|embed\/|v=)([^#\&\?]*).*/;
      const match = videoInfo.youtube_url.match(regExp);
      if (match && match[2].length === 11) {
        return `https://www.youtube.com/watch?v=${match[2]}`;
      }
    }

    // Fallback - return original URL or empty string
    return videoInfo.youtube_url || "";
  };

  // Get the YouTube URL
  const youtubeUrl = getYoutubeUrl();

  // Format video duration
  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  // Extract audio mutation
  const { mutate: extractAudio } = useMutation({
    mutationFn: youtubeServices.extractAudio,
    onMutate: () => {
      setIsDownloading(true);
      toast.loading("Extracting audio, please wait...");
    },
    onSuccess: (data) => {
      toast.dismiss();
      if ((data as any).type === "stream") {
        // It's a stream URL response
        toast.success("Audio stream ready!");
        onStreamResponse(data);
      } else {
        // It's a direct file download (blob)
        toast.success("Audio extracted successfully!");
        const filename = `${videoInfo.title.replace(/[^\w\s]/gi, "")}.mp3`;
        onAudioResponse(data as Blob, filename);
      }
    },
    onError: (error: any) => {
      toast.dismiss();
      toast.error(error.response?.data?.detail || "Failed to extract audio");
    },
    onSettled: () => {
      setIsDownloading(false);
    },
  });

  const handleExtractAudio = () => {
    if (!youtubeUrl) {
      toast.error("Invalid YouTube URL");
      return;
    }
    extractAudio({ url: youtubeUrl, maxDuration: 600 });
  };

  return (
    <Card className="overflow-hidden">
      <div className="relative aspect-video overflow-hidden">
        <img
          src={videoInfo.thumbnail_url}
          alt={videoInfo.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute bottom-2 right-2 bg-black/75 text-white px-2 py-1 rounded text-xs">
          {formatDuration(videoInfo.length_seconds)}
        </div>
      </div>
      <CardHeader>
        <CardTitle className="line-clamp-2 text-xl">
          {videoInfo.title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">By {videoInfo.author}</p>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button
          variant="outline"
          onClick={() => {
            if (youtubeUrl) {
              window.open(youtubeUrl, "_blank");
            } else {
              toast.error("Invalid YouTube URL");
            }
          }}
          disabled={!youtubeUrl}
        >
          View on YouTube
        </Button>
        <Button
          onClick={handleExtractAudio}
          disabled={isDownloading || !youtubeUrl}
        >
          {isDownloading ? "Processing..." : "Download Audio"}
        </Button>
      </CardFooter>
    </Card>
  );
}
