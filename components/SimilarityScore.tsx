interface SimilarityScoreProps {
  score: number; // 0-1
  showBar?: boolean;
  showLabel?: boolean;
}

function getScoreColor(score: number): string {
  if (score >= 0.7) return 'text-brown-dark';
  if (score >= 0.6) return 'text-brown';
  if (score >= 0.5) return 'text-brown/80';
  return 'text-brown/60';
}

function getBarColor(score: number): string {
  if (score >= 0.7) return 'bg-brown-dark';
  if (score >= 0.6) return 'bg-brown';
  if (score >= 0.5) return 'bg-brown/80';
  return 'bg-brown/60';
}

export default function SimilarityScore({
  score,
  showBar = false,
  showLabel = true,
}: SimilarityScoreProps) {
  // Ensure score is a number (in case it comes as a string from DB)
  const numericScore = typeof score === 'string' ? parseFloat(score) : score;
  const percentage = Math.round(numericScore * 100);
  const colorClass = getScoreColor(numericScore);
  const barColorClass = getBarColor(numericScore);

  return (
    <div className="flex items-center gap-2">
      {showLabel && (
        <span className={`font-mono text-xs ${colorClass}`}>
          {numericScore.toFixed(2)}
        </span>
      )}
      {showBar && (
        <div className="flex-1 h-1.5 bg-brown/10 overflow-hidden max-w-[100px]">
          <div
            className={`h-full ${barColorClass} transition-all duration-300`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      )}
      {showBar && (
        <span className="text-xs font-mono text-brown/60">
          {percentage}%
        </span>
      )}
    </div>
  );
}
