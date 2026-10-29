# Complete Delivery Package: In-App Affiliate Integration & Educator Growth Engine
**Client:** Ritesh (@ritzkumar)  
**Project:** Integrate Link with affiliate link to software tool & Boost Sales  
**Tech Stack:** Electron, React, HTML/CSS, Lemon Squeezy  

---

## 1. Native Electron / React Dashboard Component (`AffiliateBanner.tsx`)
```tsx
import React from 'react';

interface AffiliateBannerProps {
  checkoutUrl?: string;
  partnerUrl?: string;
}

export const AffiliateBanner: React.FC<AffiliateBannerProps> = ({
  checkoutUrl = 'https://your-store.lemonsqueezy.com/buy/your-product-id',
  partnerUrl = 'https://your-store.lemonsqueezy.com/affiliates',
}) => {
  const openExternalLink = (url: string) => {
    // Uses Electron's native shell to safely open default OS browser without breaking window
    if (window.require) {
      try {
        const { shell } = window.require('electron');
        shell.openExternal(url);
        return;
      } catch (err) {
        console.warn('Electron shell not available, falling back to window.open', err);
      }
    }
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  return (
    <div style={{
      margin: '16px 0',
      padding: '16px 20px',
      borderRadius: '12px',
      background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      border: '1px solid #334155',
      color: '#f8fafc',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <div style={{ maxWidth: '65%' }}>
        <span style={{
          display: 'inline-block',
          backgroundColor: '#3b82f6',
          color: '#ffffff',
          fontSize: '11px',
          fontWeight: 700,
          padding: '2px 8px',
          borderRadius: '9999px',
          textTransform: 'uppercase',
          marginBottom: '6px'
        }}>
          Pro Classroom Suite
        </span>
        <h4 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: 600 }}>
          Save 3+ Hours of Classroom Prep Every Week
        </h4>
        <p style={{ margin: 0, fontSize: '13px', color: '#94a3b8', lineHeight: 1.4 }}>
          Unlock automated grading, interactive lesson tools, and priority educator support with a verified educator license.
        </p>
      </div>

      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <button
          onClick={() => openExternalLink(partnerUrl)}
          style={{
            padding: '8px 14px',
            fontSize: '12px',
            fontWeight: 500,
            borderRadius: '8px',
            border: '1px solid #475569',
            backgroundColor: 'transparent',
            color: '#cbd5e1',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
          onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#334155')}
          onMouseOut={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
        >
          Earn 30% as Partner
        </button>

        <button
          onClick={() => openExternalLink(checkoutUrl)}
          style={{
            padding: '8px 18px',
            fontSize: '13px',
            fontWeight: 600,
            borderRadius: '8px',
            border: 'none',
            backgroundColor: '#2563eb',
            color: '#ffffff',
            cursor: 'pointer',
            boxShadow: '0 2px 6px rgba(37, 99, 235, 0.4)',
            transition: 'background 0.2s ease'
          }}
          onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#1d4ed8')}
          onMouseOut={(e) => (e.currentTarget.style.backgroundColor = '#2563eb')}
        >
          Upgrade Now →
        </button>
      </div>
    </div>
  );
};
```

---

## 2. Educator & Distributor Copy Bank

### Headline Variations (A/B Test Options):
- **Option A (Time-Saving Focus):** "Save 3+ Hours of Classroom Prep Every Week with Pro."
- **Option B (Student Engagement Focus):** "Turn Every Lesson into an Interactive Experience with Zero Extra Work."
- **Option C (Partner / Reseller):** "Are You a Teacher or Tutor? Earn 30% Recurring Commission by Sharing this Tool with Fellow Educators."

### Body Copy:
"Designed specifically for modern educators, our Pro tools automate your repetitive lesson workflows and student tracking so you can spend less time on paperwork and more time inspiring students. Upgrade your classroom license today or partner with us to share the revenue."

---

## 3. 30-Day Launch & Distributor Acquisition Plan

### Phase 1: In-App & Organic Grassroots (Days 1–10)
- **In-App Referral Loop:** Deploy the dashboard component. Prompt active educators to invite colleagues ("Give a Fellow Teacher 15% Off, Earn 30% Recurring").
- **Community Value Sharing:** Share free interactive lesson templates in teacher communities (Reddit `r/Teachers`, `r/EdTech`, Facebook Private Tutor Groups, and EdTech LinkedIn groups). Always link the free resource first with an optional upgrade path.

### Phase 2: Direct Distributor / Coaching Institute Outreach (Days 11–20)
- **Target:** 50 independent tutoring centers and EdTech YouTube/Instagram creators who create software tutorials for teachers.
- **Offer:** Dedicated 30% revenue-share and custom discount coupon codes (e.g., `ACADEMY20`) for their students.
- **Distributor Starter Kit:** Pre-made demo videos, email templates, and banner assets.

### Phase 3: Targeted Paid Acquisition (Days 21–30)
- **Channel:** Meta Ads (Instagram & Facebook).
- **Audience Targeting:** 
  - Job Titles: High School Teacher, Primary School Teacher, Private Tutor, Academic Coach.
  - Interests: EdTech, Google Classroom, Canvas LMS, Khan Academy.
- **Budget Split:** 70% direct lead generation to free trial / sample lesson, 30% retargeting to checkout.
- **Target KPIs:** <$1.50 Cost per Free User, >8% Free-to-Paid Upgrade Rate, >$15 Average Customer Value.
