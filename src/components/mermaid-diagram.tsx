"use client";

import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

interface MermaidDiagramProps {
  chart: string;
  className?: string;
}

export default function MermaidDiagram({ chart, className = '' }: MermaidDiagramProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chartRef.current && chart) {
      // Initialize mermaid with configuration
      mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'inherit',
        flowchart: {
          useMaxWidth: true,
          htmlLabels: true,
        },
      });

      const renderChart = async () => {
        if (chartRef.current) {
          try {
            chartRef.current.innerHTML = '';
            const { svg } = await mermaid.render(`mermaid-${Date.now()}`, chart);
            chartRef.current.innerHTML = svg;
          } catch (error) {
            console.error('Mermaid rendering error:', error);
            chartRef.current.innerHTML = `
              <div class="p-4 border border-red-200 rounded-lg bg-red-50 text-red-700">
                <p class="font-semibold">Error rendering diagram</p>
                <p class="text-sm">There was an issue rendering this mermaid diagram.</p>
              </div>
            `;
          }
        }
      };

      renderChart();
    }
  }, [chart]);

  if (!chart) {
    return null;
  }

  return (
    <div className={`mermaid-container ${className}`}>
      <div ref={chartRef} className="mermaid w-full overflow-x-auto" />
    </div>
  );
}