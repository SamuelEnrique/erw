// "no data" with the reason. Never a placeholder value.
export function NoData({ reason, what }: { reason: string; what?: string }) {
  return (
    <div className="border border-dashed border-rule bg-panel px-3 py-2 text-sm text-muted" role="status">
      <span className="font-semibold text-ink">no data</span>
      {what ? <> for {what}</> : null}: {reason}
    </div>
  );
}
