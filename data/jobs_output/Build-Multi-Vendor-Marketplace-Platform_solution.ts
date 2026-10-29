// Multi-Vendor Marketplace Commission Split & Payout Router
export function calculateVendorSplit(orderTotal: number, platformCommissionRate: number = 0.10) {
  const platformFee = Math.round(orderTotal * platformCommissionRate * 100) / 100;
  const vendorPayout = Math.round((orderTotal - platformFee) * 100) / 100;
  
  return {
    orderTotal,
    platformFee,
    vendorPayout,
    currency: "USD",
    settlementRail: "PayPal Instant Split"
  };
}

console.log(calculateVendorSplit(250.00, 0.12));
