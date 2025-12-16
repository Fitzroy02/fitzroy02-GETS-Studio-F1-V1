/**
 * Ad Rules Engine - Client-Side Policy Validation
 * 
 * IMPORTANT: These client-side checks are for UX purposes only.
 * Server-side validation and secure impression counting are still required
 * for actual policy enforcement, billing, and compliance.
 */

/**
 * Default advertising policy
 * This serves as a fallback when no locale-specific policy is found
 */
const DEFAULT_POLICY = {
  disallowedCategories: ['tobacco', 'gambling', 'adult-content', 'weapons'],
  requireConsent: true,
  maxImpressionsPerHour: 6,
  language: 'en'
};

/**
 * Load policy for a specific locale
 * @param {string} locale - User's locale (e.g., 'en-US', 'fr-FR', 'de-DE')
 * @param {Object} policies - Map of locale to policy objects
 * @returns {Object} Policy object for the locale or default policy
 */
function loadPolicyForLocale(locale, policies = {}) {
  // Return locale-specific policy if available
  if (policies && policies[locale]) {
    return policies[locale];
  }
  
  // Try base language if full locale not found (e.g., 'en' from 'en-US')
  const baseLanguage = locale ? locale.split('-')[0] : null;
  if (baseLanguage && policies && policies[baseLanguage]) {
    return policies[baseLanguage];
  }
  
  // Fall back to default policy
  return DEFAULT_POLICY;
}

/**
 * Validate an advertisement against policy rules
 * @param {Object} ad - Advertisement object to validate
 * @param {Object} userContext - User context including locale, consent, history
 * @param {Object} policy - Policy object with rules to enforce
 * @returns {Object|null} null if ad is allowed, or { blocked: true, reason: string } if blocked
 */
function validateAd(ad, userContext, policy) {
  // Validate ad object exists and has required fields
  if (!ad || typeof ad !== 'object') {
    return { blocked: true, reason: 'Invalid ad object' };
  }
  
  // Check for disallowed category
  if (ad.category && policy.disallowedCategories && 
      policy.disallowedCategories.includes(ad.category)) {
    return { 
      blocked: true, 
      reason: `Category '${ad.category}' is disallowed in this region` 
    };
  }
  
  // Check consent requirement
  if (policy.requireConsent && userContext && !userContext.hasConsent) {
    return { 
      blocked: true, 
      reason: 'User consent required for personalized ads' 
    };
  }
  
  // Check frequency cap
  if (policy.maxImpressionsPerHour && userContext && userContext.impressionHistory) {
    const hourAgo = Date.now() - (60 * 60 * 1000);
    const recentImpressions = userContext.impressionHistory.filter(
      impression => impression.adId === ad.id && impression.timestamp > hourAgo
    );
    
    if (recentImpressions.length >= policy.maxImpressionsPerHour) {
      return { 
        blocked: true, 
        reason: `Frequency cap exceeded: ${recentImpressions.length} impressions in last hour` 
      };
    }
  }
  
  // Check language match
  if (policy.language && ad.language && ad.language !== policy.language) {
    // Also check if user context has a preferred language
    const userLanguage = userContext && userContext.language ? userContext.language : policy.language;
    if (ad.language !== userLanguage) {
      return { 
        blocked: true, 
        reason: `Ad language '${ad.language}' does not match user language '${userLanguage}'` 
      };
    }
  }
  
  // Ad passes all validation checks
  return null;
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    DEFAULT_POLICY,
    loadPolicyForLocale,
    validateAd
  };
}
