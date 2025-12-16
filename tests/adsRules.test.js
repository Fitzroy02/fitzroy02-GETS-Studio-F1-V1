/**
 * Ad Rules Unit Tests
 * 
 * Jest-style unit tests for ad validation logic
 */

const { validateAd, loadPolicyForLocale, DEFAULT_POLICY } = require('../src/utils/adsRules');

describe('adsRules', () => {
  describe('loadPolicyForLocale', () => {
    it('should return locale-specific policy when available', () => {
      const policies = {
        'en-US': { disallowedCategories: ['tobacco'], requireConsent: false },
        'fr-FR': { disallowedCategories: ['gambling'], requireConsent: true }
      };
      
      const policy = loadPolicyForLocale('fr-FR', policies);
      expect(policy).toEqual(policies['fr-FR']);
    });

    it('should return base language policy when full locale not found', () => {
      const policies = {
        'en': { disallowedCategories: ['tobacco'], requireConsent: false }
      };
      
      const policy = loadPolicyForLocale('en-GB', policies);
      expect(policy).toEqual(policies['en']);
    });

    it('should return default policy when locale not found', () => {
      const policies = {
        'fr-FR': { disallowedCategories: ['gambling'], requireConsent: true }
      };
      
      const policy = loadPolicyForLocale('de-DE', policies);
      expect(policy).toEqual(DEFAULT_POLICY);
    });

    it('should return default policy when policies object is empty', () => {
      const policy = loadPolicyForLocale('en-US', {});
      expect(policy).toEqual(DEFAULT_POLICY);
    });

    it('should return default policy when policies is null', () => {
      const policy = loadPolicyForLocale('en-US', null);
      expect(policy).toEqual(DEFAULT_POLICY);
    });
  });

  describe('validateAd', () => {
    const defaultPolicy = {
      disallowedCategories: ['tobacco', 'gambling'],
      requireConsent: true,
      maxImpressionsPerHour: 6,
      language: 'en'
    };

    describe('invalid ad scenarios', () => {
      it('should block null ad', () => {
        const result = validateAd(null, {}, defaultPolicy);
        expect(result).toEqual({ blocked: true, reason: 'Invalid ad object' });
      });

      it('should block undefined ad', () => {
        const result = validateAd(undefined, {}, defaultPolicy);
        expect(result).toEqual({ blocked: true, reason: 'Invalid ad object' });
      });

      it('should block non-object ad', () => {
        const result = validateAd('not an object', {}, defaultPolicy);
        expect(result).toEqual({ blocked: true, reason: 'Invalid ad object' });
      });
    });

    describe('disallowed category scenarios', () => {
      it('should block ad with disallowed category', () => {
        const ad = { id: 'ad1', category: 'tobacco', title: 'Cigarette Ad' };
        const userContext = { locale: 'en-US', hasConsent: true };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toEqual({ 
          blocked: true, 
          reason: "Category 'tobacco' is disallowed in this region" 
        });
      });

      it('should block gambling ad when gambling is disallowed', () => {
        const ad = { id: 'ad2', category: 'gambling', title: 'Casino Ad' };
        const userContext = { locale: 'en-US', hasConsent: true };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toEqual({ 
          blocked: true, 
          reason: "Category 'gambling' is disallowed in this region" 
        });
      });

      it('should allow ad with allowed category', () => {
        const ad = { id: 'ad3', category: 'retail', title: 'Store Sale' };
        const userContext = { locale: 'en-US', hasConsent: true };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toBeNull();
      });
    });

    describe('consent required scenarios', () => {
      it('should block ad when consent required but not given', () => {
        const ad = { id: 'ad4', category: 'retail', title: 'Store Sale' };
        const userContext = { locale: 'en-US', hasConsent: false };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toEqual({ 
          blocked: true, 
          reason: 'User consent required for personalized ads' 
        });
      });

      it('should allow ad when consent required and given', () => {
        const ad = { id: 'ad5', category: 'retail', title: 'Store Sale' };
        const userContext = { locale: 'en-US', hasConsent: true };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toBeNull();
      });

      it('should allow ad when consent not required', () => {
        const ad = { id: 'ad6', category: 'retail', title: 'Store Sale' };
        const userContext = { locale: 'en-US', hasConsent: false };
        const policy = { ...defaultPolicy, requireConsent: false };
        
        const result = validateAd(ad, userContext, policy);
        expect(result).toBeNull();
      });
    });

    describe('frequency cap scenarios', () => {
      it('should block ad when frequency cap exceeded', () => {
        const ad = { id: 'ad7', category: 'retail', title: 'Store Sale' };
        const now = Date.now();
        const userContext = { 
          locale: 'en-US', 
          hasConsent: true,
          impressionHistory: [
            { adId: 'ad7', timestamp: now - 1000 },      // 1 second ago
            { adId: 'ad7', timestamp: now - 60000 },     // 1 minute ago
            { adId: 'ad7', timestamp: now - 120000 },    // 2 minutes ago
            { adId: 'ad7', timestamp: now - 180000 },    // 3 minutes ago
            { adId: 'ad7', timestamp: now - 240000 },    // 4 minutes ago
            { adId: 'ad7', timestamp: now - 300000 }     // 5 minutes ago
          ]
        };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toEqual({ 
          blocked: true, 
          reason: 'Frequency cap exceeded: 6 impressions in last hour' 
        });
      });

      it('should allow ad when frequency cap not exceeded', () => {
        const ad = { id: 'ad8', category: 'retail', title: 'Store Sale' };
        const now = Date.now();
        const userContext = { 
          locale: 'en-US', 
          hasConsent: true,
          impressionHistory: [
            { adId: 'ad8', timestamp: now - 1000 },      // 1 second ago
            { adId: 'ad8', timestamp: now - 60000 }      // 1 minute ago
          ]
        };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toBeNull();
      });

      it('should ignore old impressions beyond 1 hour', () => {
        const ad = { id: 'ad9', category: 'retail', title: 'Store Sale' };
        const now = Date.now();
        const userContext = { 
          locale: 'en-US', 
          hasConsent: true,
          impressionHistory: [
            { adId: 'ad9', timestamp: now - 3700000 },   // 61 minutes ago (old)
            { adId: 'ad9', timestamp: now - 7200000 },   // 2 hours ago (old)
            { adId: 'ad9', timestamp: now - 1000 }       // 1 second ago (recent)
          ]
        };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toBeNull();
      });

      it('should only count impressions for the same ad', () => {
        const ad = { id: 'ad10', category: 'retail', title: 'Store Sale' };
        const now = Date.now();
        const userContext = { 
          locale: 'en-US', 
          hasConsent: true,
          impressionHistory: [
            { adId: 'ad10', timestamp: now - 1000 },     // Same ad
            { adId: 'ad10', timestamp: now - 60000 },    // Same ad
            { adId: 'different-ad', timestamp: now - 120000 },  // Different ad
            { adId: 'different-ad', timestamp: now - 180000 },  // Different ad
            { adId: 'different-ad', timestamp: now - 240000 },  // Different ad
            { adId: 'different-ad', timestamp: now - 300000 }   // Different ad
          ]
        };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toBeNull();
      });
    });

    describe('language mismatch scenarios', () => {
      it('should block ad when language does not match policy language', () => {
        const ad = { id: 'ad11', category: 'retail', language: 'fr', title: 'Store Sale' };
        const userContext = { locale: 'en-US', hasConsent: true };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toEqual({ 
          blocked: true, 
          reason: "Ad language 'fr' does not match user language 'en'" 
        });
      });

      it('should block ad when language does not match user context language', () => {
        const ad = { id: 'ad12', category: 'retail', language: 'fr', title: 'Store Sale' };
        const userContext = { locale: 'en-US', hasConsent: true, language: 'es' };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toEqual({ 
          blocked: true, 
          reason: "Ad language 'fr' does not match user language 'es'" 
        });
      });

      it('should allow ad when language matches policy language', () => {
        const ad = { id: 'ad13', category: 'retail', language: 'en', title: 'Store Sale' };
        const userContext = { locale: 'en-US', hasConsent: true };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toBeNull();
      });

      it('should allow ad when language matches user context language', () => {
        const ad = { id: 'ad14', category: 'retail', language: 'es', title: 'Store Sale' };
        const userContext = { locale: 'en-US', hasConsent: true, language: 'es' };
        const policy = { ...defaultPolicy, language: 'en' };
        
        const result = validateAd(ad, userContext, policy);
        expect(result).toBeNull();
      });
    });

    describe('multiple validation checks', () => {
      it('should block on first failing check (disallowed category)', () => {
        const ad = { 
          id: 'ad15', 
          category: 'tobacco',  // Disallowed
          language: 'fr',        // Wrong language
          title: 'Tobacco Ad' 
        };
        const userContext = { 
          locale: 'en-US', 
          hasConsent: false      // No consent
        };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result.blocked).toBe(true);
        expect(result.reason).toContain('tobacco');
      });

      it('should allow ad when all checks pass', () => {
        const ad = { 
          id: 'ad16', 
          category: 'retail',
          language: 'en',
          title: 'Store Sale' 
        };
        const userContext = { 
          locale: 'en-US', 
          hasConsent: true,
          impressionHistory: []
        };
        
        const result = validateAd(ad, userContext, defaultPolicy);
        expect(result).toBeNull();
      });
    });
  });
});
