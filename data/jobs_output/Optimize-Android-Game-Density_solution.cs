// Unity / Android Adaptive Ad Density Controller
// Implements intelligent frequency capping and session retention protection
using System;
using UnityEngine;

public class AdaptiveAdDensityManager : MonoBehaviour {
    [SerializeField] private int minSecondsBetweenInterstitials = 45;
    [SerializeField] private int levelsCompletedBeforeAd = 2;
    
    private float lastAdShownTime = -999f;
    private int sessionLevelCounter = 0;

    public bool CanShowInterstitial() {
        bool timeElapsed = (Time.time - lastAdShownTime) >= minSecondsBetweenInterstitials;
        bool levelMilestoneReached = sessionLevelCounter >= levelsCompletedBeforeAd;
        return timeElapsed && levelMilestoneReached;
    }

    public void OnLevelCompleted() {
        sessionLevelCounter++;
        if (CanShowInterstitial()) {
            ShowAdMobInterstitial();
        }
    }

    private void ShowAdMobInterstitial() {
        Debug.Log("[AdManager] Displaying Interstitial Ad");
        lastAdShownTime = Time.time;
        sessionLevelCounter = 0;
        // Trigger SDK call here
    }
}
