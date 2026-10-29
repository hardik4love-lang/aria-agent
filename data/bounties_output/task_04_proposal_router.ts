// New Proposal Router Architecture
// Decouples repository routing from static configuration and preserves user edits.

export interface ProposalRouteTarget {
  repository: string;
  category: string;
  handler: string;
}

export class ProposalRouter {
  private routes = new Map<string, ProposalRouteTarget>();

  registerRoute(category: string, target: ProposalRouteTarget) {
    this.routes.set(category.toLowerCase(), target);
  }

  resolveTarget(category: string, defaultRepo: string): ProposalRouteTarget {
    const route = this.routes.get(category.toLowerCase());
    if (route) return route;
    return {
      repository: defaultRepo,
      category: 'general',
      handler: 'DefaultProposalHandler'
    };
  }
}
