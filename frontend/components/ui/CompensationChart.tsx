'use client';

import { useState, useMemo } from 'react';
import { cn } from '@/lib/utils/cn';

export interface SalaryDataPoint {
  grade: string;
  min: number;
  mid: number;
  max: number;
}

interface CompensationChartProps {
  data: SalaryDataPoint[];
  className?: string;
  height?: number;
  showTooltip?: boolean;
  colorScheme?: 'green' | 'blue' | 'purple';
}

export function CompensationChart({
  data,
  className,
  height = 280,
  showTooltip = true,
  colorScheme = 'green',
}: CompensationChartProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });

  // Chart dimensions
  const padding = { top: 20, right: 30, bottom: 40, left: 60 };
  const chartWidth = 600;
  const chartHeight = height;
  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  // Color schemes
  const colors = {
    green: {
      min: 'rgba(74, 222, 128, 0.3)', // green-400/30
      mid: 'rgba(34, 197, 94, 0.5)',  // green-500/50
      max: 'rgba(22, 163, 74, 0.7)',  // green-600/70
      line: 'rgb(22, 163, 74)',       // green-600
      stroke: 'rgb(34, 197, 94)',     // green-500
    },
    blue: {
      min: 'rgba(96, 165, 250, 0.3)', // blue-400/30
      mid: 'rgba(59, 130, 246, 0.5)', // blue-500/50
      max: 'rgba(37, 99, 235, 0.7)',  // blue-600/70
      line: 'rgb(37, 99, 235)',       // blue-600
      stroke: 'rgb(59, 130, 246)',    // blue-500
    },
    purple: {
      min: 'rgba(192, 132, 252, 0.3)', // purple-400/30
      mid: 'rgba(168, 85, 247, 0.5)',  // purple-500/50
      max: 'rgba(147, 51, 234, 0.7)',  // purple-600/70
      line: 'rgb(147, 51, 234)',       // purple-600
      stroke: 'rgb(168, 85, 247)',     // purple-500
    },
  };

  const currentColors = colors[colorScheme];

  // Calculate scales
  const { minSalary, maxSalary, yTicks, xScale, yScale } = useMemo(() => {
    const allValues = data.flatMap((d) => [d.min, d.mid, d.max]);
    const minVal = Math.min(...allValues);
    const maxVal = Math.max(...allValues);
    
    // Round to nice numbers
    const minRounded = Math.floor(minVal / 100) * 100;
    const maxRounded = Math.ceil(maxVal / 100) * 100;
    
    // Generate Y-axis ticks
    const tickCount = 5;
    const tickStep = (maxRounded - minRounded) / (tickCount - 1);
    const ticks = Array.from({ length: tickCount }, (_, i) => minRounded + i * tickStep);

    // X scale (band scale)
    const xBandWidth = innerWidth / data.length;
    const xScaleFn = (index: number) => padding.left + index * xBandWidth + xBandWidth / 2;

    // Y scale (linear)
    const yScaleFn = (value: number) => {
      const ratio = (value - minRounded) / (maxRounded - minRounded);
      return padding.top + innerHeight - ratio * innerHeight;
    };

    return {
      minSalary: minRounded,
      maxSalary: maxRounded,
      yTicks: ticks,
      xScale: xScaleFn,
      yScale: yScaleFn,
    };
  }, [data, innerWidth, innerHeight, padding]);

  // Generate area paths
  const { minAreaPath, midAreaPath, maxAreaPath, midLinePath } = useMemo(() => {
    if (data.length === 0) return { minAreaPath: '', midAreaPath: '', maxAreaPath: '', midLinePath: '' };

    // Max area (top band)
    const maxPoints = data.map((d, i) => `${xScale(i)},${yScale(d.max)}`).join(' L');
    const midPointsRev = [...data].reverse().map((d, i) => `${xScale(data.length - 1 - i)},${yScale(d.mid)}`).join(' L');
    const maxArea = `M${maxPoints} L${midPointsRev} Z`;

    // Mid area (middle band)
    const midPoints = data.map((d, i) => `${xScale(i)},${yScale(d.mid)}`).join(' L');
    const minPointsRev = [...data].reverse().map((d, i) => `${xScale(data.length - 1 - i)},${yScale(d.min)}`).join(' L');
    const midArea = `M${midPoints} L${minPointsRev} Z`;

    // Min area (bottom band - for gradient effect)
    const minPoints = data.map((d, i) => `${xScale(i)},${yScale(d.min)}`).join(' L');
    const baseLineRev = [...data].reverse().map((_, i) => `${xScale(data.length - 1 - i)},${yScale(minSalary)}`).join(' L');
    const minArea = `M${minPoints} L${baseLineRev} Z`;

    // Mid line
    const midLine = `M${data.map((d, i) => `${xScale(i)},${yScale(d.mid)}`).join(' L')}`;

    return {
      minAreaPath: minArea,
      midAreaPath: midArea,
      maxAreaPath: maxArea,
      midLinePath: midLine,
    };
  }, [data, xScale, yScale, minSalary]);

  const handleMouseMove = (event: React.MouseEvent<SVGElement>, index: number) => {
    const svg = event.currentTarget.ownerSVGElement || event.currentTarget;
    const rect = svg.getBoundingClientRect();
    setTooltipPosition({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    });
    setHoveredIndex(index);
  };

  return (
    <div className={cn('relative', className)}>
      <svg
        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
        className="w-full h-auto"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Grid lines */}
        <g className="grid-lines">
          {yTicks.map((tick) => (
            <line
              key={tick}
              x1={padding.left}
              y1={yScale(tick)}
              x2={chartWidth - padding.right}
              y2={yScale(tick)}
              stroke="#e2e8f0"
              strokeWidth="1"
              strokeDasharray="4,4"
            />
          ))}
        </g>

        {/* Y-axis labels */}
        <g className="y-axis">
          {yTicks.map((tick) => (
            <text
              key={tick}
              x={padding.left - 10}
              y={yScale(tick)}
              textAnchor="end"
              alignmentBaseline="middle"
              className="text-xs fill-slate-500"
              fontSize="11"
            >
              {tick}万
            </text>
          ))}
        </g>

        {/* Area bands */}
        <g className="area-bands">
          {/* Max area (top - darkest) */}
          <path
            d={maxAreaPath}
            fill={currentColors.max}
            className="transition-opacity duration-200"
          />
          {/* Mid area (middle) */}
          <path
            d={midAreaPath}
            fill={currentColors.mid}
            className="transition-opacity duration-200"
          />
          {/* Min area (bottom - lightest) */}
          <path
            d={minAreaPath}
            fill={currentColors.min}
            className="transition-opacity duration-200"
          />
        </g>

        {/* Mid line */}
        <path
          d={midLinePath}
          fill="none"
          stroke={currentColors.line}
          strokeWidth="2"
          strokeDasharray="6,4"
        />

        {/* Data points for interaction */}
        <g className="data-points">
          {data.map((d, i) => (
            <g key={d.grade}>
              {/* Hover area */}
              <rect
                x={xScale(i) - innerWidth / data.length / 2}
                y={padding.top}
                width={innerWidth / data.length}
                height={innerHeight}
                fill="transparent"
                className="cursor-pointer"
                onMouseMove={(e) => handleMouseMove(e, i)}
                onMouseLeave={() => setHoveredIndex(null)}
              />
              {/* Points */}
              <circle
                cx={xScale(i)}
                cy={yScale(d.max)}
                r={hoveredIndex === i ? 6 : 4}
                fill={currentColors.line}
                className="transition-all duration-150"
              />
              <circle
                cx={xScale(i)}
                cy={yScale(d.mid)}
                r={hoveredIndex === i ? 5 : 3}
                fill="white"
                stroke={currentColors.line}
                strokeWidth="2"
                className="transition-all duration-150"
              />
              <circle
                cx={xScale(i)}
                cy={yScale(d.min)}
                r={hoveredIndex === i ? 6 : 4}
                fill={currentColors.stroke}
                className="transition-all duration-150"
              />
            </g>
          ))}
        </g>

        {/* X-axis labels */}
        <g className="x-axis">
          {data.map((d, i) => (
            <text
              key={d.grade}
              x={xScale(i)}
              y={chartHeight - padding.bottom + 25}
              textAnchor="middle"
              className={cn(
                'text-sm font-bold transition-colors duration-150',
                hoveredIndex === i ? 'fill-slate-800' : 'fill-slate-600'
              )}
              fontSize="12"
            >
              {d.grade}
            </text>
          ))}
        </g>
      </svg>

      {/* Tooltip */}
      {showTooltip && hoveredIndex !== null && (
        <div
          className="absolute pointer-events-none z-10 px-3 py-2 bg-slate-800 text-white text-xs rounded-lg shadow-lg transform -translate-x-1/2 -translate-y-full"
          style={{
            left: tooltipPosition.x,
            top: tooltipPosition.y - 10,
          }}
        >
          <div className="font-bold mb-1">{data[hoveredIndex].grade}</div>
          <div className="space-y-0.5">
            <div className="flex justify-between gap-4">
              <span className="text-slate-400">Max:</span>
              <span className="font-mono">{data[hoveredIndex].max.toLocaleString()}万</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-slate-400">Mid:</span>
              <span className="font-mono">{data[hoveredIndex].mid.toLocaleString()}万</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-slate-400">Min:</span>
              <span className="font-mono">{data[hoveredIndex].min.toLocaleString()}万</span>
            </div>
          </div>
          {/* Arrow */}
          <div className="absolute left-1/2 bottom-0 transform -translate-x-1/2 translate-y-full">
            <div className="border-8 border-transparent border-t-slate-800" />
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-4 rounded"
            style={{ backgroundColor: currentColors.max }}
          />
          <span className="text-slate-600">Max (上限)</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-4 rounded"
            style={{ backgroundColor: currentColors.mid }}
          />
          <span className="text-slate-600">Mid (中間)</span>
        </div>
        <div className="flex items-center gap-2">
          <div
            className="w-4 h-4 rounded"
            style={{ backgroundColor: currentColors.min }}
          />
          <span className="text-slate-600">Min (下限)</span>
        </div>
      </div>
    </div>
  );
}

export default CompensationChart;
