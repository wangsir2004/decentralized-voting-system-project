import { useEffect, useRef } from "react";
import { BarChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import { graphic, init, use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";

use([BarChart, GridComponent, TooltipComponent, CanvasRenderer]);

type ResultsChartProps = {
  candidates: string[];
  counts: number[];
};

export function ResultsChart({ candidates, counts }: ResultsChartProps) {
  const chartRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // ECharts 实例随候选项或票数变化重建，确保图表与链上结果一致。
    const chart = init(chartRef.current);
    chart.setOption({
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        backgroundColor: "rgba(21, 20, 18, 0.96)",
        borderColor: "rgba(209, 150, 98, 0.42)",
        textStyle: { color: "#f4eee8" }
      },
      grid: { left: 18, right: 18, top: 42, bottom: 24, containLabel: true },
      xAxis: {
        type: "category",
        data: candidates,
        axisLabel: {
          color: "#bdb0a2",
          interval: 0,
          width: 128,
          overflow: "truncate"
        },
        axisLine: { lineStyle: { color: "rgba(105, 195, 170, 0.28)" } }
      },
      yAxis: {
        type: "value",
        minInterval: 1,
        axisLabel: { color: "#bdb0a2" },
        splitLine: { lineStyle: { color: "rgba(105, 195, 170, 0.12)" } }
      },
      series: [
        {
          type: "bar",
          data: counts,
          barMaxWidth: 48,
          itemStyle: {
            borderRadius: [6, 6, 0, 0],
            // 使用渐变色区分数据柱，与页面的链上证据视觉风格保持一致。
            color: new graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#69c3aa" },
              { offset: 1, color: "#d6aa61" }
            ])
          },
          label: { show: true, position: "top", color: "#f4eee8" }
        }
      ]
    });

    const handleResize = () => chart.resize();
    window.addEventListener("resize", handleResize);

    return () => {
      // 组件卸载或数据更新时释放实例，避免重复注册 resize 监听。
      window.removeEventListener("resize", handleResize);
      chart.dispose();
    };
  }, [candidates, counts]);

  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <span>结果可视化</span>
        <strong>链上读取</strong>
      </div>
      <h2>实时投票结果</h2>
      {candidates.length ? <div className="chart" ref={chartRef} /> : <div className="chart-empty">等待链上结果...</div>}
    </section>
  );
}
