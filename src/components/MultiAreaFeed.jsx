import React from 'react';
import { loadPolicyForLocale, validateAd } from '../utils/adsRules';

/*
Props:
- areas: [{ id, type: 'global'|'region'|'neighborhood', items: [content|ad] }]
- userContext: { locale, impressionsLastHour, consentGiven }
- policies: optional locale->policy map
*/

export default function MultiAreaFeed({ areas = [], userContext = {}, policies = {} }) {
  const policy = loadPolicyForLocale(userContext.locale, policies);

  return (
    <div className="multi-area-feed">
      {areas.map(area => (
        <section key={area.id} className={`feed-area feed-area--${area.type}`}>
          <h3>{area.type.toUpperCase()}</h3>
          <div className="feed-items">
            {area.items.map(item => {
              if (item.type === 'ad') {
                const block = validateAd(item, userContext, policy);
                if (block) {
                  return (
                    <article key={item.id} className="feed-item ad blocked">
                      <div className="ad-placeholder">Ad blocked: {block.reason}</div>
                    </article>
                  );
                }
                return (
                  <article key={item.id} className="feed-item ad">
                    <div className="ad-content">{item.content}</div>
                  </article>
                );
              }
              return (
                <article key={item.id} className="feed-item content">
                  <div>{item.content}</div>
                </article>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}
