// Session 25: the ERW wordmark (docs/brand/erw-wordmark.svg), inline: a cardinal square whose white stem and three bars
// make an E that is also a bar chart, beside "ERW" in Georgia. No external assets.
export function Wordmark({ height = 26 }: { height?: number }) {
  return (
    <svg viewBox="0 0 104 32" height={height} width={(height * 104) / 32} role="img" aria-label="ERW" className="block">
      <rect width="32" height="32" rx="3" fill="#8C1515" />
      <rect x="8" y="7" width="3" height="18" fill="#FFFFFF" />
      <rect x="8" y="7" width="14" height="3" fill="#FFFFFF" />
      <rect x="8" y="14" width="11" height="3" fill="#FFFFFF" />
      <rect x="8" y="22" width="17" height="3" fill="#FFFFFF" />
      <text x="40" y="24" fontFamily="Georgia, 'Times New Roman', serif" fontSize="22" letterSpacing="1.5" fill="#8C1515">
        ERW
      </text>
    </svg>
  );
}
