// Minimal tests for adsRules
import { validateAd } from '../src/utils/adsRules';

test('blocks disallowed category', () => {
  const policy = { disallowedCategories: ['gambling'], requireConsent: false };
  const ad = { id: 'a1', category: 'gambling' };
  const res = validateAd(ad, { locale: 'GB' }, policy);
  expect(res.reason).toBe('category_disallowed');
});

test('requires consent if policy says so', () => {
  const policy = { disallowedCategories: [], requireConsent: true };
  const ad = { id: 'a2', category: 'retail' };
  const res = validateAd(ad, { consentGiven: false }, policy);
  expect(res.reason).toBe('consent_required');
});
