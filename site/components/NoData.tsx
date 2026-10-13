import { LICENSE_NEEDED, LICENSE_REASON, isLicenseReason } from "@/lib/license";

// "no data" with the reason. Never a placeholder value.
// Session 215: a reason that begins "license needed: " is not a failed read but a table held under its publisher's
// terms (lib/license.ts, lib/supabase.ts LicenseNeeded). It is drawn as the data catalogue draws it: the words
// "license needed", with the publishers in the hover, in the place the numbers would have been.
export function NoData({ reason, what }: { reason: string; what?: string }) {
  if (isLicenseReason(reason)) {
    return (
      <span className="text-muted" role="status" data-license-held={what ?? ""} title={reason.slice(LICENSE_REASON.length)}>{LICENSE_NEEDED}</span>
    );
  }
  return (
    <div className="border border-dashed border-rule bg-panel px-3 py-2 text-sm text-muted" role="status">
      <span className="font-semibold text-ink">no data</span>
      {what ? <> for {what}</> : null}: {reason}
    </div>
  );
}
