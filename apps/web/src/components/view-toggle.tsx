"use client";

import { Button } from "@/components/ui/button";
import { LayoutGrid, List } from "lucide-react";
import { cn } from "@/lib/utils";

interface ViewToggleProps {
  viewMode: "list" | "grid";
  onViewModeChange: (mode: "list" | "grid") => void;
  className?: string;
}

export function ViewToggle({ viewMode, onViewModeChange, className }: ViewToggleProps) {
  return (
    <div className={cn("flex items-center bg-muted rounded-md p-1", className)}>
      <Button
        variant={viewMode === "list" ? "default" : "ghost"}
        size="sm"
        onClick={() => onViewModeChange("list")}
        className={cn(
          "h-8 px-3 transition-all duration-200",
          viewMode === "list" 
            ? "bg-background shadow-sm text-foreground hover:bg-background/90 hover:shadow-md" 
            : "hover:bg-background/80 hover:text-foreground text-muted-foreground"
        )}
      >
        <List className="w-4 h-4 mr-1" />
        List
      </Button>
      <Button
        variant={viewMode === "grid" ? "default" : "ghost"}
        size="sm"
        onClick={() => onViewModeChange("grid")}
        className={cn(
          "h-8 px-3 transition-all duration-200",
          viewMode === "grid" 
            ? "bg-background shadow-sm text-foreground hover:bg-background/90 hover:shadow-md" 
            : "hover:bg-background/80 hover:text-foreground text-muted-foreground"
        )}
      >
        <LayoutGrid className="w-4 h-4 mr-1" />
        Grid
      </Button>
    </div>
  );
}