"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { toast } from "sonner";
import { useMutation } from "@tanstack/react-query";
import { youtubeServices } from "@/services";
import { VideoInfo } from "@/types";
import { Input } from "../ui/input";

interface UrlInputProps {
  onVideoInfoReceived: (info: VideoInfo) => void;
}

interface ApiError {
  response?: {
    data?: {
      detail?: string;
    };
    status?: number;
  };
  message: string;
}

export function UrlInput({ onVideoInfoReceived }: UrlInputProps) {
  const [url, setUrl] = useState("");

  const { mutate: checkUrl, isPending } = useMutation({
    mutationFn: youtubeServices.getVideoInfo,
    onSuccess: (data) => {
      toast.success("Video information retrieved!");
      onVideoInfoReceived(data);
    },
    onError: (error: ApiError) => {
      const errorMessage = error.response?.data?.detail || 
        error.message || 
        "Failed to retrieve video information";
        
      // Check for rate limiting error or bot detection
      if (error.response?.status === 429 || 
          errorMessage.includes("Sign in to confirm") || 
          errorMessage.includes("bot")) {
        toast.error("YouTube Bot Protection Triggered", {
          description: "YouTube is blocking automated access right now. Try a different video, wait 15-20 minutes, or try from a different network.",
          duration: 8000
        });
      } else {
        toast.error(errorMessage);
      }
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      toast.error("Please enter a YouTube URL");
      return;
    }

    checkUrl(url);
  };

  return (
    <Card className="w-full">
      <CardContent className="pt-6">
        <form
          onSubmit={handleSubmit}
          className="flex flex-col sm:flex-row gap-3"
        >
          <Input
            type="text"
            placeholder="Enter YouTube URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <Button
            type="submit"
            disabled={isPending || !url.trim()}
            className="sm:w-auto w-full"
          >
            {isPending ? "Checking..." : "Extract Audio"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
