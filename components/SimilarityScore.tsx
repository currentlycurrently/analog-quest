interface SimilarityScoreProps {
  score: number; // 0-1
  showBar?: boolean;
  showLabel?: boolean;
}

function getScoreColor(score: number): string {
  if (score >= 0.7) return 'text-green-600';
  if (score >= 0.6) return 'text-yellow-600';
  if (score >= 0.5) return 'text-orange-600';
  return 'text-red-600';
}

function getBarColor(score: number): string {
  if (score >= 0.7) return 'bg-green-500';
  if (score >= 0.6) return 'bg-yellow-500';
  if (score >= 0.5) return 'bg-orange-500';
  return 'bg-red-500';
}

export default function SimilarityScore({
  score,
  showBar = false,
  showLabel = true,
}: SimilarityScoreProps) {
  const percentage = Math.round(score * 100);
  const colorClass = getScoreColor(score);
  const barColorClass = getBarColor(score);

  return (
    <div className="flex items-center gap-2">
      {showLabel && (
        <span className={`font-semibold ${colorClass}`}>
          {score.toFixed(2)}
        </span>
      )}
      {showBar && (
        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden max-w-[200px]">
          <div
            className={`h-full ${barColorClass} transition-all duration-300`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      )}
      {showBar && (
        <span className="text-sm text-gray-600">
          {percentage}%
        </span>
      )}
    </div>
  );
}
