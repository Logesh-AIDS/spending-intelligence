'use client';

import { Card } from '@/components/ui/card';
import type { HealthScore } from '@/lib/hooks/useDashboard';

interface Props {
  data: HealthScore;
}

const gradeColor: Record<string, string> = {
  A: 'text-green-600',
  B: 'text-blue-600',
  C: 'text-yellow-600',
  D: 'text-orange-600',
  F: 'text-red-600',
};

const gradeBarColor: Record<string, string> = {
  A: 'bg-green-500',
  B: 'bg-blue-500',
  C: 'bg-yellow-500',
  D: 'bg-orange-500',
  F: 'bg-red-500',
};

export function HealthScoreCard({ data }: Props) {
  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold mb-4">Financial Health Score</h2>

      <div className="flex items-center gap-6 mb-4">
        <div className="text-center">
          <div className={`text-5xl font-bold ${gradeColor[data.grade] || 'text-slate-800'}`}>
            {data.grade}
          </div>
          <div className="text-sm text-slate-500 mt-1">Grade</div>
        </div>
        <div className="flex-1">
          <div className="flex justify-between text-sm mb-1">
            <span className="text-slate-600">Score</span>
            <span className="font-semibold">{data.score}/100</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${gradeBarColor[data.grade] || 'bg-slate-500'}`}
              style={{ width: `${data.score}%` }}
            />
          </div>
          <p className="text-sm text-slate-500 mt-2">{data.interpretation}</p>
        </div>
      </div>

      {data.improvement_tips?.length > 0 && (
        <div className="mt-3 border-t pt-3">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">
            Tips
          </p>
          <ul className="space-y-1">
            {data.improvement_tips.slice(0, 2).map((tip, i) => (
              <li key={i} className="text-sm text-slate-600 flex gap-2">
                <span className="text-blue-500">•</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}
    </Card>
  );
}
