// Lightweight local advertising rules enforcement helpers
// Usage:
//   const policy = loadPolicyForLocale('GB'); // returns policy JSON
//   const reason = validateAd(ad, userContext, policy);
//   if (!reason) renderAd(ad); else renderFallback(reason);

export function loadPolicyForLocale(locale, policies = {}) {
  // policies is optional map of locale -> policy; otherwise defaultPolicy used
  return policies[locale] || defaultPolicy;
}

const defaultPolicy = {
  disallowedCategories: [], // e.g. ["gambling"]
  requireConsent: false,
  maxImpressionsPerHour: 1000,
  language: null,
};

export function validateAd(ad, userContext = {}, policy = defaultPolicy) {
  // ad: { id, category, language, metadata }
  // userContext: { locale, impressionsLastHour, consentGiven }
  if (!ad || !ad.id) return { blocked: true, reason: 'invalid_ad' };

  if (policy.disallowedCategories && policy.disallowedCategories.includes(ad.category)) {
    return { blocked: true, reason: 'category_disallowed' };
  }

  if (policy.requireConsent && !userContext.consentGiven) {
    return { blocked: true, reason: 'consent_required' };
  }

  if (
    typeof policy.maxImpressionsPerHour === 'number' &&
    typeof userContext.impressionsLastHour === 'number' &&
    userContext.impressionsLastHour >= policy.maxImpressionsPerHour
  ) {
    return { blocked: true, reason: 'frequency_cap' };
  }

  if (policy.language && ad.language && policy.language !== ad.language) {
    return { blocked: true, reason: 'language_mismatch' };
  }

  return null; // not blocked
}
