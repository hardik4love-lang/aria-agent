import { ImageResponse } from "next/og";
import { NextRequest } from "next/server";

export const runtime = "edge";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default async function handler(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const title = searchParams.get("title") || "ARIA Autonomous Assistant";
  const category = searchParams.get("category") || "High-Yield Bounties";

  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          justifyContent: "space-between",
          backgroundColor: "#090d16",
          padding: "80px",
          fontFamily: "Inter, sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div style={{ width: 18, height: 18, borderRadius: "50%", backgroundColor: "#10b981" }} />
          <span style={{ color: "#38bdf8", fontSize: 28, fontWeight: 700 }}>ARIA AGENT</span>
        </div>
        <div style={{ color: "#ffffff", fontSize: 64, fontWeight: 800, lineHeight: 1.2 }}>{title}</div>
        <div style={{ display: "flex", justifyContent: "space-between", width: "100%", color: "#94a3b8", fontSize: 24 }}>
          <span>{category}</span>
          <span style={{ color: "#10b981", fontWeight: 700 }}>$0.00 / mo TCO</span>
        </div>
      </div>
    ),
    { ...size }
  );
}
