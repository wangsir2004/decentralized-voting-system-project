type ShowcaseMetricProps = {
  label: string;
  value: string | number;
  detail?: string;
  tone?: "cyan" | "gold" | "danger";
};

export function ShowcaseMetric({ label, value, detail, tone = "cyan" }: ShowcaseMetricProps) {
  // tone 只映射 CSS 类名，避免每个指标组件重复写颜色逻辑。
  return (
    <div className={`showcase-metric metric-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </div>
  );
}
