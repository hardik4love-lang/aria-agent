// Professional Services Marketplace Booking & Escrow Data Schema
export interface ServiceProvider {
  id: string;
  name: string;
  profession: 'LEGAL' | 'ACCOUNTING' | 'CONSULTING';
  hourlyRateUsd: number;
  verifiedCredentials: boolean;
  rating: number;
}

export interface ServiceContract {
  contractId: string;
  clientId: string;
  providerId: string;
  agreedAmountUsd: number;
  escrowStatus: 'FUNDED' | 'IN_PROGRESS' | 'RELEASED' | 'DISPUTED';
  deliverableDeadline: string;
}

export function releaseEscrowMilestone(contract: ServiceContract): { success: boolean; payoutStatus: string } {
  if (contract.escrowStatus !== 'FUNDED') {
    return { success: false, payoutStatus: 'ESCROW_NOT_FUNDED' };
  }
  contract.escrowStatus = 'RELEASED';
  return { success: true, payoutStatus: 'PAYOUT_INITIATED_TO_PROVIDER' };
}
