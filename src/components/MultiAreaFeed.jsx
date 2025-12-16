/**
 * MultiAreaFeed Component
 * 
 * Displays a multi-area feed with global, regional, and neighborhood sections.
 * Applies client-side ad validation rules before rendering advertisements.
 * 
 * Note: Client-side validation is for UX only. Server-side validation required.
 */

import React from 'react';
import { loadPolicyForLocale, validateAd } from '../utils/adsRules';

/**
 * MultiAreaFeed - React component for rendering multi-area content feed
 * @param {Object} props - Component props
 * @param {Array} props.areas - Array of feed areas (global, regional, neighborhood)
 * @param {Object} props.userContext - User context (locale, consent, history)
 * @param {Object} props.policies - Map of locale-specific policies
 */
const MultiAreaFeed = ({ areas = [], userContext = {}, policies = {} }) => {
  // Load policy for user's locale
  const userLocale = userContext.locale || 'en-US';
  const policy = loadPolicyForLocale(userLocale, policies);

  /**
   * Render a single feed item (content or ad)
   * @param {Object} item - Feed item to render
   * @param {number} index - Item index for React key
   * @returns {JSX.Element} Rendered item or blocked placeholder
   */
  const renderItem = (item, index) => {
    // If item is an ad, validate before rendering
    if (item.type === 'ad') {
      const validationResult = validateAd(item, userContext, policy);
      
      // If ad is blocked, show placeholder
      if (validationResult && validationResult.blocked) {
        return (
          <div 
            key={`blocked-ad-${index}`} 
            className="feed-item blocked-ad-placeholder"
            role="status"
            aria-label="Advertisement blocked"
          >
            <p className="blocked-message">
              Ad blocked: {validationResult.reason}
            </p>
          </div>
        );
      }
      
      // Render valid ad
      return (
        <div 
          key={`ad-${item.id || index}`} 
          className="feed-item feed-ad"
          role="complementary"
          aria-label="Advertisement"
        >
          <div className="ad-label">Sponsored</div>
          <h3>{item.title}</h3>
          <p>{item.content}</p>
          {item.imageUrl && (
            <img 
              src={item.imageUrl} 
              alt={item.altText || item.title} 
              className="ad-image"
            />
          )}
          {item.ctaText && item.ctaUrl && (
            <a 
              href={item.ctaUrl} 
              className="ad-cta"
              target="_blank"
              rel="noopener noreferrer"
            >
              {item.ctaText}
            </a>
          )}
        </div>
      );
    }
    
    // Render regular content item
    return (
      <div 
        key={`content-${item.id || index}`} 
        className="feed-item feed-content"
        role="article"
      >
        <h3>{item.title}</h3>
        <p>{item.content}</p>
        {item.author && <p className="content-author">By {item.author}</p>}
        {item.timestamp && (
          <time className="content-timestamp">
            {new Date(item.timestamp).toLocaleString()}
          </time>
        )}
      </div>
    );
  };

  /**
   * Render a feed area section
   * @param {Object} area - Feed area object
   * @param {number} index - Area index for React key
   * @returns {JSX.Element} Rendered feed area section
   */
  const renderArea = (area, index) => {
    if (!area || !area.items || area.items.length === 0) {
      return null;
    }

    return (
      <section 
        key={`area-${area.type || index}`} 
        className={`feed-area feed-area-${area.type}`}
        aria-labelledby={`feed-area-heading-${area.type}`}
      >
        <h2 id={`feed-area-heading-${area.type}`} className="feed-area-heading">
          {area.title || area.type}
        </h2>
        <div className="feed-items">
          {area.items.map((item, itemIndex) => renderItem(item, itemIndex))}
        </div>
      </section>
    );
  };

  // Render the complete multi-area feed
  return (
    <div className="multi-area-feed" role="main">
      <h1 className="feed-title">Feed</h1>
      {areas.length === 0 ? (
        <p className="no-content-message">No content available</p>
      ) : (
        areas.map((area, index) => renderArea(area, index))
      )}
    </div>
  );
};

export default MultiAreaFeed;
