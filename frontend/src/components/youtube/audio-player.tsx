"use client";

import { useState, useRef, useEffect } from "react";
import { StreamUrlResponse } from "@/types";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { toast } from "sonner";
import { API_BASE_URL, API_ROUTES } from "@/config/routes";
import {
  Play,
  Pause,
  Volume1,
  Volume2,
  ExternalLink,
  Download,
} from "lucide-react";
import Image from "next/image";

interface AudioPlayerProps {
  streamData: StreamUrlResponse;
  onClose: () => void;
}

export function AudioPlayer({ streamData, onClose }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [error, setError] = useState<string | null>(null);
  const [useProxy, setUseProxy] = useState(false);

  // We'll use the proxy URL instead of the direct stream URL
  const getAudioUrl = () => {
    if (useProxy) {
      // Use our backend proxy to stream the audio
      return `${API_BASE_URL}${
        API_ROUTES.YOUTUBE_PROXY_AUDIO
      }?url=${encodeURIComponent(streamData.youtube_url)}`;
    } else {
      // Try direct stream URL first (which may expire)
      return streamData.stream_url;
    }
  };

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => setCurrentTime(audio.currentTime);
    const handleDurationChange = () => setDuration(audio.duration);
    const handleEnded = () => setIsPlaying(false);
    const handleError = () => {
      if (!useProxy) {
        // If direct URL fails, try using proxy
        setUseProxy(true);
        setError(null);

        // Force reload of audio element with new URL
        setTimeout(() => {
          if (audioRef.current) {
            audioRef.current.load();
            if (isPlaying) {
              audioRef.current.play().catch(() => {
                setError(
                  "Error playing audio even with proxy. Please try downloading instead."
                );
              });
            }
          }
        }, 500);

        toast.info("Trying alternative streaming method...");
      } else {
        setError(
          "Error playing audio. Please try downloading the file instead."
        );
        toast.error(
          "Error playing audio. Please try downloading the file instead."
        );
      }
    };

    audio.addEventListener("timeupdate", handleTimeUpdate);
    audio.addEventListener("durationchange", handleDurationChange);
    audio.addEventListener("ended", handleEnded);
    audio.addEventListener("error", handleError);

    return () => {
      audio.removeEventListener("timeupdate", handleTimeUpdate);
      audio.removeEventListener("durationchange", handleDurationChange);
      audio.removeEventListener("ended", handleEnded);
      audio.removeEventListener("error", handleError);
    };
  }, [useProxy, isPlaying, streamData]);

  const togglePlayPause = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play().catch((err) => {
        console.error("Error playing audio", err);
        if (!useProxy) {
          setUseProxy(true);
          toast.info("Trying alternative streaming method...");
          setTimeout(() => {
            if (audioRef.current) {
              audioRef.current.load();
              audioRef.current.play().catch(() => {
                setError(
                  "Error playing audio. Please try downloading instead."
                );
                toast.error(
                  "Error playing audio. Please try downloading instead."
                );
              });
            }
          }, 500);
        } else {
          setError("Error playing audio. Please try downloading instead.");
          toast.error("Error playing audio. Please try downloading instead.");
        }
      });
    }
    setIsPlaying(!isPlaying);
  };

  const handleVolumeChange = (value: number[]) => {
    const newVolume = value[0];
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  const handleProgressChange = (value: number[]) => {
    const newTime = value[0];
    setCurrentTime(newTime);
    if (audioRef.current) {
      audioRef.current.currentTime = newTime;
    }
  };

  const formatTime = (time: number) => {
    if (isNaN(time)) return "0:00";
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")}`;
  };

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="line-clamp-1 text-lg">
          {streamData.title}
        </CardTitle>
        <Button variant="ghost" size="sm" onClick={onClose}>
          Close
        </Button>
      </CardHeader>
      <CardContent>
        <div className="w-full h-[160px] mb-4 bg-muted rounded-md overflow-hidden">
          <Image
            src={streamData.thumbnail}
            alt={streamData.title}
            className="w-full h-full object-cover"
            fill
          />
        </div>

        <audio
          ref={audioRef}
          src={getAudioUrl()}
          preload="auto"
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          className="hidden"
        />

        {error ? (
          <div className="text-center py-4 text-destructive">
            {error}
            <div className="mt-2 flex flex-col sm:flex-row justify-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.open(streamData.youtube_url, "_blank")}
              >
                <ExternalLink className="mr-2 h-4 w-4" />
                Open on YouTube
              </Button>
              <Button
                variant="default"
                size="sm"
                onClick={() => {
                  // Trigger a direct download
                  window.location.href = `${API_BASE_URL}${
                    API_ROUTES.YOUTUBE_EXTRACT_AUDIO
                  }?url=${encodeURIComponent(streamData.youtube_url)}`;
                  toast.success("Download started!");
                }}
              >
                <Download className="mr-2 h-4 w-4" />
                Download Audio
              </Button>
            </div>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-1 mt-4">
              <span className="text-xs">{formatTime(currentTime)}</span>
              <span className="text-xs">{formatTime(duration)}</span>
            </div>
            <Slider
              value={[currentTime]}
              max={duration || 100}
              step={1}
              onValueChange={handleProgressChange}
              className="my-2"
            />

            <div className="flex items-center justify-between mt-4">
              <div className="flex items-center gap-2">
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={togglePlayPause}
                  className="h-10 w-10"
                >
                  {isPlaying ? (
                    <Pause className="h-5 w-5" />
                  ) : (
                    <Play className="h-5 w-5" />
                  )}
                </Button>
              </div>

              <div className="flex items-center gap-2">
                <Volume1 className="h-4 w-4 text-muted-foreground" />
                <Slider
                  value={[volume]}
                  max={1}
                  min={0}
                  step={0.01}
                  onValueChange={handleVolumeChange}
                  className="w-20"
                />
                <Volume2 className="h-4 w-4 text-muted-foreground" />
              </div>
            </div>

            <div className="flex justify-center mt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setUseProxy(!useProxy);
                  toast.info(
                    `Switching to ${useProxy ? "direct" : "proxy"} streaming`
                  );
                }}
              >
                {useProxy ? "Use Direct Stream" : "Use Proxy Stream"}
              </Button>
            </div>
          </>
        )}
      </CardContent>
      <CardFooter className="text-xs text-muted-foreground pt-0">
        <p>
          {useProxy
            ? "Using proxy streaming to avoid URL expiration"
            : streamData.note}
        </p>
      </CardFooter>
    </Card>
  );
}
