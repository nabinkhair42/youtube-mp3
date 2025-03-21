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
      toast.error(
        error.response?.data?.detail || "Failed to retrieve video information"
      );
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
