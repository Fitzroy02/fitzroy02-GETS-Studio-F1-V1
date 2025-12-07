import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(page_title="GETS Studio Art Gallery", page_icon="🎨", layout="wide")

st.title("🎨 GETS Studio F1 Art Gallery")
st.markdown("**Visual Arts Platform** — Paintings, Digital Art, Photography, Sculpture & Mixed Media")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Gallery Dashboard", 
    "🖼️ Submit Artwork", 
    "🎨 Browse Gallery",
    "💰 Revenue & Eco Impact",
    "📜 Certificates"
])

# ============================================================================
# TAB 1: GALLERY DASHBOARD
# ============================================================================
with tab1:
    st.header("Gallery Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Artworks", "1,245", "+87 this month")
    
    with col2:
        st.metric("Active Artists", "423", "+12 this month")
    
    with col3:
        st.metric("Total Sales", "£487,350", "+£23,450 this month")
    
    with col4:
        st.metric("Trees Planted", "2,437", "+117 this month")
    
    st.markdown("---")
    
    # Revenue Distribution
    st.subheader("Revenue Distribution Model")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **GETS Studio Art Gallery** follows the same transparent revenue model:
        
        - **70%** to Artists (creators)
        - **20%** to Platform Operations (infrastructure, gallery management, marketing)
        - **10%** to Ecological Anchors (trees + ocean conservation)
        
        **Engagement-Based Ecological Allocation:**
        - 10,000 likes/favorites = 1 tree planted
        - Every sale contributes 10% to environmental projects
        - Quarterly Eco Impact Certificates issued to all artists
        """)
    
    with col2:
        st.info("""
        **Current Month:**
        
        £23,450 revenue
        
        → £16,415 to Artists  
        → £4,690 to Platform  
        → £2,345 to Eco Anchors
        
        **117 trees planted**  
        **£937 ocean conservation**
        """)
    
    st.markdown("---")
    
    # Gallery Statistics
    st.subheader("Gallery Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Artwork by Medium:**")
        medium_data = {
            "Medium": ["Painting", "Digital Art", "Photography", "Sculpture", "Mixed Media", "Print"],
            "Count": [423, 387, 245, 98, 67, 25]
        }
        st.dataframe(pd.DataFrame(medium_data), hide_index=True)
    
    with col2:
        st.markdown("**Top Artists (Sales):**")
        artist_data = {
            "Artist": ["Sarah Mitchell", "David Chen", "Emma Rodriguez", "James O'Brien", "Aisha Patel"],
            "Sales (£)": ["£45,230", "£38,750", "£32,100", "£28,940", "£25,680"]
        }
        st.dataframe(pd.DataFrame(artist_data), hide_index=True)
    
    with col3:
        st.markdown("**Recent Activity:**")
        st.write("✅ New artwork: 'Urban Sunset' by Maria Santos")
        st.write("💰 Sale: 'Reflection' by Tom Harrison (£1,250)")
        st.write("🌳 Milestone: 1,000 likes = 1 tree planted")
        st.write("📜 Certificate issued: Sarah Mitchell")
        st.write("🎨 New artist joined: Alex Thompson")

# ============================================================================
# TAB 2: SUBMIT ARTWORK
# ============================================================================
with tab2:
    st.header("Submit Artwork to Gallery")
    
    st.markdown("""
    Register your artwork with **GETS Studio Art Gallery**. All submissions are reviewed, catalogued, 
    and distributed to partner galleries and online platforms.
    """)
    
    with st.form("artwork_submission"):
        st.subheader("Artist Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            artist_name = st.text_input("Artist Name *", placeholder="Your full name or artist pseudonym")
            artist_email = st.text_input("Email Address *", placeholder="your.email@example.com")
            artist_location = st.text_input("Location", placeholder="City, Country")
        
        with col2:
            artist_website = st.text_input("Website/Portfolio", placeholder="https://yourportfolio.com")
            artist_social = st.text_input("Social Media", placeholder="@yourusername or profile link")
            artist_bio = st.text_area("Artist Bio (50-200 words)", placeholder="Brief description of your artistic practice...")
        
        st.markdown("---")
        st.subheader("Artwork Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            artwork_title = st.text_input("Artwork Title *", placeholder="e.g., 'Sunrise Over Mountains'")
            artwork_medium = st.selectbox("Medium *", [
                "Select medium...",
                "Oil Painting",
                "Acrylic Painting",
                "Watercolor",
                "Digital Art",
                "Photography (Print)",
                "Photography (Digital)",
                "Sculpture (Bronze)",
                "Sculpture (Stone)",
                "Sculpture (Mixed Media)",
                "Mixed Media",
                "Ink/Pen Drawing",
                "Charcoal Drawing",
                "Collage",
                "Printmaking",
                "Textile Art",
                "Installation Art",
                "Other (specify in description)"
            ])
            artwork_year = st.number_input("Year Created *", min_value=1900, max_value=2025, value=2025)
        
        with col2:
            artwork_dimensions = st.text_input("Dimensions *", placeholder="e.g., 60cm x 80cm or 24in x 36in")
            artwork_edition = st.selectbox("Edition Type", [
                "Original (One-of-a-kind)",
                "Limited Edition (specify number below)",
                "Open Edition (Prints/Digital)",
                "Artist Proof"
            ])
            if "Limited Edition" in artwork_edition:
                edition_number = st.text_input("Edition Details", placeholder="e.g., 5/50 (5th of 50 prints)")
        
        st.markdown("---")
        
        artwork_description = st.text_area(
            "Artwork Description *", 
            placeholder="Describe your artwork: concept, inspiration, technique, materials used... (100-500 words)",
            height=150
        )
        
        st.markdown("---")
        st.subheader("Pricing & Sales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            sale_status = st.selectbox("Sale Status *", [
                "For Sale",
                "Not For Sale (Exhibition Only)",
                "Commission Available",
                "Sold (Archival Record)"
            ])
            
            if sale_status == "For Sale":
                sale_price = st.number_input("Sale Price (£) *", min_value=0, value=500, step=50)
                
                # Calculate ecological allocation
                eco_allocation = sale_price * 0.10
                trees = int(eco_allocation / 10)  # £10 = 1 tree
                oceans = eco_allocation * 0.40
                
                st.info(f"""
                **Revenue Distribution for £{sale_price:,.2f} sale:**
                
                → **£{sale_price * 0.70:,.2f}** to You (Artist)  
                → **£{sale_price * 0.20:,.2f}** to Platform Operations  
                → **£{eco_allocation:,.2f}** to Ecological Anchors
                
                **Ecological Impact:**  
                🌳 **{trees} trees** planted  
                🌊 **£{oceans:.2f}** to ocean conservation
                """)
        
        with col2:
            shipping_available = st.checkbox("Shipping Available")
            if shipping_available:
                shipping_regions = st.multiselect("Shipping Regions", [
                    "UK Only",
                    "Europe",
                    "North America",
                    "Worldwide"
                ])
            
            framing_options = st.checkbox("Framing Options Available")
            if framing_options:
                framing_details = st.text_input("Framing Details", placeholder="e.g., Museum-quality frame, £150 extra")
        
        st.markdown("---")
        st.subheader("Image Upload")
        
        st.markdown("""
        Upload high-resolution images of your artwork:
        - **Primary Image:** Main gallery display (required)
        - **Additional Images:** Detail shots, alternate angles, context photos (optional)
        - **Format:** JPG, PNG, WEBP
        - **Resolution:** Minimum 2000px on longest side recommended
        - **File Size:** Max 10MB per image
        """)
        
        primary_image = st.file_uploader("Primary Image *", type=["jpg", "jpeg", "png", "webp"])
        additional_images = st.file_uploader("Additional Images (up to 5)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
        
        st.markdown("---")
        st.subheader("Distribution & Exhibition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            online_galleries = st.multiselect("Online Gallery Platforms", [
                "GETS Studio Main Gallery (Default)",
                "Saatchi Art",
                "Artsy",
                "Artfinder",
                "Rise Art",
                "TurningArt"
            ], default=["GETS Studio Main Gallery (Default)"])
        
        with col2:
            physical_galleries = st.multiselect("Physical Gallery Interest", [
                "Local UK Galleries",
                "International Galleries",
                "Pop-up Exhibitions",
                "Art Fairs",
                "Museum Submissions"
            ])
        
        st.markdown("---")
        st.subheader("Terms & Submission")
        
        terms_accepted = st.checkbox("""
        **I confirm:**
        - I am the original creator and copyright holder of this artwork
        - All provided information is accurate
        - I understand the 70/20/10 revenue distribution model
        - I agree to 10% ecological allocation on all sales
        - I grant GETS Studio distribution rights (I retain copyright)
        - I accept the GETS Studio Art Gallery Terms & Conditions
        """)
        
        submitted = st.form_submit_button("Submit Artwork", type="primary", disabled=not terms_accepted)
        
        if submitted:
            if not all([artist_name, artist_email, artwork_title, artwork_medium != "Select medium...", artwork_description, primary_image]):
                st.error("Please fill in all required fields (*)")
            else:
                st.success("✅ Artwork Submitted Successfully!")
                st.balloons()
                
                st.info(f"""
                **Next Steps:**
                
                1. **Review (1-3 days):** Our curatorial team will review your submission
                2. **Approval Notification:** You'll receive email confirmation
                3. **Gallery Listing:** Artwork goes live on GETS Studio Art Gallery
                4. **Distribution:** Artwork distributed to selected partner platforms
                5. **Certificate Issued:** Digital certificate with artwork metadata + ecological commitment
                
                **Submission Details:**
                - Artist: {artist_name}
                - Title: {artwork_title}
                - Medium: {artwork_medium}
                - Year: {artwork_year}
                - Status: {sale_status}
                {f"- Price: £{sale_price:,.2f}" if sale_status == "For Sale" else ""}
                
                **Reference Number:** ART-{datetime.now().strftime('%Y%m%d')}-{hash(artwork_title) % 10000:04d}
                """)

# ============================================================================
# TAB 3: BROWSE GALLERY
# ============================================================================
with tab3:
    st.header("Browse Art Gallery")
    
    # Filters
    st.subheader("Filter Artworks")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_medium = st.multiselect("Medium", [
            "All", "Painting", "Digital Art", "Photography", "Sculpture", "Mixed Media", "Print"
        ], default=["All"])
    
    with col2:
        filter_price = st.selectbox("Price Range", [
            "All Prices",
            "Under £500",
            "£500 - £1,000",
            "£1,000 - £2,500",
            "£2,500 - £5,000",
            "Over £5,000"
        ])
    
    with col3:
        filter_status = st.selectbox("Status", [
            "All",
            "For Sale",
            "Sold",
            "Exhibition Only"
        ])
    
    with col4:
        sort_by = st.selectbox("Sort By", [
            "Recently Added",
            "Price: Low to High",
            "Price: High to Low",
            "Most Liked",
            "Artist Name"
        ])
    
    st.markdown("---")
    
    # Sample Gallery Grid
    st.subheader("Featured Artworks")
    
    # Sample artwork data
    artworks = [
        {"title": "Urban Sunset", "artist": "Maria Santos", "medium": "Oil Painting", "price": "£1,250", "likes": 2847, "image": "🌆"},
        {"title": "Digital Dreams", "artist": "Alex Chen", "medium": "Digital Art", "price": "£450", "likes": 3201, "image": "🎨"},
        {"title": "Ocean Whispers", "artist": "Emma Rodriguez", "medium": "Photography", "price": "£850", "likes": 1956, "image": "📸"},
        {"title": "Abstract Flow", "artist": "James O'Brien", "medium": "Acrylic", "price": "£2,100", "likes": 1432, "image": "🖼️"},
        {"title": "Nature's Geometry", "artist": "Sarah Mitchell", "medium": "Mixed Media", "price": "£1,800", "likes": 2134, "image": "🌿"},
        {"title": "City Lights", "artist": "David Park", "medium": "Digital Art", "price": "£600", "likes": 2689, "image": "🌃"},
    ]
    
    # Display in 3-column grid
    cols = st.columns(3)
    
    for idx, artwork in enumerate(artworks):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### {artwork['image']} {artwork['title']}")
                st.markdown(f"**Artist:** {artwork['artist']}")
                st.markdown(f"**Medium:** {artwork['medium']}")
                st.markdown(f"**Price:** {artwork['price']}")
                st.markdown(f"❤️ {artwork['likes']:,} likes | 🌳 {artwork['likes'] // 10000} trees")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.button("View Details", key=f"view_{idx}")
                with col_b:
                    st.button("❤️ Like", key=f"like_{idx}")
                
                st.markdown("---")

# ============================================================================
# TAB 4: REVENUE & ECO IMPACT
# ============================================================================
with tab4:
    st.header("Revenue & Ecological Impact")
    
    st.subheader("Artist Revenue Dashboard")
    
    st.markdown("""
    Track your earnings, sales history, and ecological contribution through the GETS Studio Art Gallery.
    """)
    
    # Sample artist revenue data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Earnings", "£12,450", "+£850 this month")
    
    with col2:
        st.metric("Artworks Sold", "17", "+2 this month")
    
    with col3:
        st.metric("Your Trees", "124", "+8 this month")
    
    with col4:
        st.metric("Your Ocean Fund", "£498", "+£34 this month")
    
    st.markdown("---")
    
    # Revenue Breakdown
    st.subheader("Revenue Breakdown (Last 12 Months)")
    
    revenue_data = {
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "Sales (£)": [450, 0, 1250, 850, 0, 2100, 600, 1800, 0, 450, 1250, 850],
        "Your Share (70%)": [315, 0, 875, 595, 0, 1470, 420, 1260, 0, 315, 875, 595],
        "Platform (20%)": [90, 0, 250, 170, 0, 420, 120, 360, 0, 90, 250, 170],
        "Eco (10%)": [45, 0, 125, 85, 0, 210, 60, 180, 0, 45, 125, 85]
    }
    
    st.dataframe(pd.DataFrame(revenue_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Ecological Impact
    st.subheader("Your Ecological Contribution")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **How Your Art Plants Trees:**
        
        - **Sales:** 10% of every sale → 60% trees / 40% oceans
        - **Engagement:** 10,000 likes = 1 tree planted
        - **Cumulative Impact:** All your artworks contribute to platform-wide ecological goals
        
        **Your Impact to Date:**
        - 17 artworks sold = £1,245 ecological allocation
        - 747 trees planted from your sales (60% of £1,245)
        - £498 ocean conservation from your sales (40% of £1,245)
        - 47,300 total likes across all artworks = 4.7 additional trees
        
        **Total Trees from Your Art:** 124 trees 🌳  
        **Total CO₂ Offset:** 12.4 tonnes (equivalent to 2.7 cars removed for 1 year)
        """)
    
    with col2:
        st.info("""
        **Top Artist Eco Leaders:**
        
        1. Sarah Mitchell: 487 trees
        2. David Chen: 356 trees
        3. Emma Rodriguez: 289 trees
        4. James O'Brien: 234 trees
        5. **YOU: 124 trees** 🎉
        
        Keep creating to climb the leaderboard!
        """)

# ============================================================================
# TAB 5: CERTIFICATES
# ============================================================================
with tab5:
    st.header("Certificates & Documentation")
    
    st.markdown("""
    All artists receive official certificates documenting artwork registration, distribution, 
    revenue transparency, and ecological impact.
    """)
    
    st.subheader("Available Certificates")
    
    # Artwork Registration Certificate
    with st.expander("🖼️ Artwork Registration Certificate", expanded=True):
        st.markdown("""
        **Certificate Type:** Artwork Registration & Distribution  
        **Artist:** Maria Santos  
        **Artwork:** Urban Sunset  
        **Date Registered:** November 15, 2025  
        
        **Artwork Details:**
        - **Medium:** Oil on Canvas
        - **Dimensions:** 60cm x 80cm
        - **Year:** 2025
        - **Edition:** Original (One-of-a-kind)
        - **Sale Price:** £1,250
        
        **Distribution Confirmed:**
        - GETS Studio Main Gallery ✓
        - Saatchi Art ✓
        - Artfinder ✓
        - Local UK Gallery Network ✓
        
        **Revenue Model:**
        - 70% (£875) to Artist
        - 20% (£250) to Platform Operations
        - 10% (£125) to Ecological Anchors
        
        **Ecological Commitment:**
        - Trees: 7 native UK trees planted (60% of £125)
        - Oceans: £50 to ocean conservation (40% of £125)
        - CO₂ Offset: 0.7 tonnes
        
        **Blockchain Verification:** SHA-256 Hash: a3f8b9c2...  
        **Certificate ID:** ART-REG-20251115-3847  
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("📄 Download PDF", key="cert1_pdf")
        with col2:
            st.button("✉️ Email Certificate", key="cert1_email")
    
    # Quarterly Eco Impact Certificate
    with st.expander("🌳 Quarterly Eco Impact Certificate"):
        st.markdown("""
        **Certificate Type:** Ecological Impact Report  
        **Period:** Q4 2025 (October - December)  
        **Artist:** Maria Santos  
        
        **Artwork Sales This Quarter:**
        - 2 artworks sold
        - Total sales: £2,050
        - Ecological allocation (10%): £205
        
        **Trees Planted:**
        - Sales contribution: 12 trees (60% of £205 = £123)
        - Engagement contribution: 3 trees (31,500 likes across portfolio)
        - **Total: 15 trees planted this quarter** 🌳
        
        **Ocean Conservation:**
        - Sales contribution: £82 (40% of £205)
        - Projects supported: Plastic removal, coastal cleanup
        
        **CO₂ Offset:**
        - 1.5 tonnes CO₂ offset this quarter
        - Cumulative: 12.4 tonnes total
        
        **Tree Planting Details:**
        - Species: Oak, birch, rowan (native UK)
        - Locations: Scotland, Wales, Northern England
        - Partners: Woodland Trust, Trees for Life
        
        **Verification:**
        - Blockchain hash: b7d4e1a9...
        - Third-party audit: Woodland Trust Confirmation #WT-2025-Q4-1847
        
        **Certificate ID:** ECO-IMP-20251231-3847  
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("📄 Download PDF", key="cert2_pdf")
        with col2:
            st.button("✉️ Email Certificate", key="cert2_email")
    
    # Artist Profile Certificate
    with st.expander("👤 Artist Profile Certificate"):
        st.markdown("""
        **Certificate Type:** Artist Registration & Verification  
        **Artist Name:** Maria Santos  
        **Location:** London, United Kingdom  
        **Registration Date:** March 12, 2024  
        **Artist ID:** ARTIST-20240312-MS-2847  
        
        **Portfolio Summary:**
        - **Total Artworks:** 23 registered
        - **Mediums:** Oil painting, watercolor, mixed media
        - **Sales:** 17 artworks sold (73% sell-through rate)
        - **Total Revenue:** £12,450
        
        **Platform Statistics:**
        - **Gallery Views:** 45,687
        - **Total Likes:** 47,300
        - **Followers:** 1,234
        - **Average Rating:** 4.8/5.0 (from 156 reviews)
        
        **Ecological Leadership:**
        - **Total Trees:** 124 trees planted
        - **CO₂ Offset:** 12.4 tonnes
        - **Rank:** #5 in Artist Eco Leaderboard
        
        **Certifications:**
        - ✓ Copyright holder verified
        - ✓ Payment details confirmed
        - ✓ Distribution agreements signed
        - ✓ GETS Studio Code of Conduct accepted
        
        **Certificate ID:** ARTIST-PROF-20240312-2847  
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("📄 Download PDF", key="cert3_pdf")
        with col2:
            st.button("✉️ Email Certificate", key="cert3_email")
    
    st.markdown("---")
    
    st.subheader("Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("📊 Export All Data (CSV)", use_container_width=True)
    
    with col2:
        st.button("📋 Export All Data (JSON)", use_container_width=True)
    
    with col3:
        st.button("📄 Generate Annual Report", use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
**GETS Studio F1 Art Gallery** — Unifying visual arts with ecological stewardship  
70% to Artists | 20% Platform | 10% Ecological Anchors | Every artwork leaves the world better
""")
