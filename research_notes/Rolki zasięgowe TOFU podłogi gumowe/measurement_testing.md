# Measuring and testing TOFU short-form video (Reels/Shorts/TikTok) for a small manufacturer/e-shop

Method note: Research ran 2026-10-10 using web search. Direct page fetches of socialinsider.io, metricool.com and support.google.com failed (DNS errors in the sandbox), so some findings come from search-result summaries of those pages or from press and secondary write-ups. These are marked "(secondary)". Labels used: **[OFFICIAL]** = platform statement or documentation; **[DATA]** = benchmark with stated methodology; **[OPINION]** = practitioner or vendor view, no controlled data.

## 1. Which leading metrics predict that a reel works for reach, and what the platforms expose

### Takeaway
The clearest early signals of reach are the **opening-decision metric** (YouTube "viewed vs swiped away", Instagram 3-second "skip rate", TikTok/Meta ads "hook rate"), **watch time/retention**, and **sends/shares per reach**. Instagram's head of platform named watch time, likes per reach and sends per reach as the top ranking signals. Sends matter more for reaching non-followers, which is the TOFU goal. Raw "views" are now a weak metric on every platform: since 2025, Meta and YouTube count every start or replay as a view.

### Cited Findings
**Instagram / Facebook (Meta)**
- **[OFFICIAL]** Adam Mosseri (Jan 2025): "The top three signals that matter most for ranking are watch time, likes and sends." He advised tracking average watch time, likes per reach and sends per reach. He also said "Likes are slightly more important for connected content, and sends are slightly more important for unconnected content" (i.e., reaching non-followers). — [Social Media Today](https://www.socialmediatoday.com/news/instagram-shares-algorithm-2025/738034/); [Social Samosa](https://www.socialsamosa.com/news-2/instagram-reveals-key-factors-for-boosting-reach-8646916)
- **[OPINION, unverified]** The claim that "sends weigh 3–5× likes" is widely credited to Mosseri, but it traces to a third-party analysis (CreatorFlow), not to Mosseri himself. — [search summary of posteverywhere.ai / eclincher](https://posteverywhere.ai/blog/how-the-instagram-algorithm-works)
- **[OFFICIAL]** Instagram added **Skip Rate** (share of viewers who leave within the first 3 seconds) and a **Retention chart** to Reels Insights in Aug 2025. Skip Rate replaced the older "View Rate". — [Social Samosa](https://www.socialsamosa.com/news-2/instagram-retention-chart-skip-rate-new-performance-metrics-reels-9730992); [Metricool](https://metricool.com/instagram-reel-analytics/) (secondary)
- **[OFFICIAL]** In Dec 2025 Meta added Reels Skip Rate to the Instagram Marketing API Insights endpoint, with a fixed 3-second window. — [exchange4media](https://www.exchange4media.com/digital-news/instagram-expands-marketing-api-with-new-metrics-and-content-management-tools-149985.html); [Storrito](https://storrito.com/resources/how-instagrams-updated-marketing-api-metrics-work/) (secondary)
- **[OFFICIAL]** Meta made **Views** the primary metric. On Reels, "Plays" were renamed Views. Impressions were deprecated on Instagram, fully by 21 Apr 2025. Facebook followed and Page Insights API impressions are being retired. Repeat viewings count, so Views can exceed old impression counts. — [Social Media Today](https://www.socialmediatoday.com/news/facebook-switches-views-primary-metric/732979/); [Social Media Today – API](https://www.socialmediatoday.com/news/meta-deprecates-impressions-in-favor-of-views-api/757958/); [Lindsey Gamble](https://www.lindseygamble.com/blog/facebook-follows-instagram-and-moves-to-views-as-the-primary-metric-for-all-formats)
- Instagram Reel insights also show reach (accounts reached), likes, comments, shares/sends, saves, follows, and average watch time. Trial reels show views, likes, comments and shares about 24h after posting. — [Inro](https://www.inro.social/blog/what-is-a-reel-trial-and-how-does-it-work); [Business Today](https://www.businesstoday.in/amp/technology/news/story/instagram-launches-trial-reels-letting-creators-test-content-before-reaching-followers-457022-2024-12-12)

**YouTube Shorts**
- **[OFFICIAL, via press]** From **31 Mar 2025**, a Shorts "view" counts every start or replay, with no minimum watch time. The old metric survives as **"engaged views"** under Advanced Mode, and YPP and earnings stay on engaged views. YouTube advises using engaged views when comparing Shorts published before 31 Mar 2025. One example showed total views rising more than a third after the change. — [MobileSyrup](https://mobilesyrup.com/2025/03/27/youtube-changes-how-it-counts-shorts-views/); [Search Engine Journal](https://beta.searchenginejournal.com/youtube-changes-shorts-view-counts-no-change-to-monetization/543005/); [Creator Handbook](https://www.creatorhandbook.net/youtube-is-changing-how-its-counting-shorts-views/)
- **[OFFICIAL, via secondary]** "Viewed vs swiped away" in the Shorts feed (shown with "Shown in feed") is the share of viewers who encountered the Short in the feed and chose to watch rather than swipe. YouTube's positive label "Stayed to watch" does not mean the viewer finished the Short. It is a different measure from thumbnail CTR. — [ContentStudio](https://contentstudio.io/blog/youtube-shorts-analytics-guide); [Lindsey Gamble](https://lindseygamble.com/blog/youtube-offers-creators-detailed-insights-into-their-content-performance-with-new-shorts-audience-demographic-metrics); [Subscribr](https://subscribr.ai/p/youtube-shorts-analytics-metrics-growth)
- YouTube also exposes average percentage viewed, an audience-retention curve, and subscribers gained per Short (standard Studio metrics). — [ContentStudio](https://contentstudio.io/blog/youtube-shorts-analytics-guide)

**TikTok**
- TikTok post analytics include total and average watch time, "watched full video" (completion rate), a retention curve, and traffic source breakdown. — [Sotrender (Sep 2025)](https://www.sotrender.com/blog/2025/09/tiktok-post-analytics/); [Sociality](https://sociality.io/blog/tiktok-analytics/)
- **[OFFICIAL via secondary]** TikTok's own guidance (as relayed) says shares expand distribution by introducing a video to new viewers. — [Sociality](https://sociality.io/blog/tiktok-analytics/)

**Paid-side equivalents**
- **[OPINION]** Ad testers split the opening into **hook rate** (3-second views / impressions: did people stop?) and **hold rate** (ThruPlays or longer views / 3-second views: did the right people stay?). Judging on one alone "kills good concepts for the wrong reason." — [Selzee](https://selzee.com/blog/hook-rate-vs-hold-rate)

### Inferences
- A practical TOFU scorecard per reel: (1) opening metric (IG skip rate / YT stayed-to-watch % / TikTok 2–3s retention from the curve), (2) average watch time or % viewed, (3) **shares/sends per 1,000 reach**, (4) **follows per 1,000 reach**, (5) saves per 1,000 reach, (6) profile visits / link clicks. Normalising per reach, not per follower, makes non-follower reach comparable.
- For a product like rubber gym flooring, saves and sends are the likely signals of buying intent (e.g., someone sending it to a partner or gym owner). That is a hypothesis to test, not a sourced finding.
- Because views count every replay, use **reach / accounts reached** (IG/FB), **engaged views** (YT) or **unique viewers** as the denominator, not views.

### Gaps
- No official Instagram, YouTube or TikTok documentation was retrieved directly. Fetches to support.google.com and help.instagram.com failed, so definitions rely on press and secondary guides.
- No source showed which metric best predicts *downstream inquiries*, as opposed to reach. That link has to be built from the company's own data.
- Not confirmed: whether TikTok shows a new vs returning viewer split for each post.

## 2. Benchmarks 2025–2026 (with methodology), especially for small accounts

### Takeaway
Credible public benchmarks exist for **engagement rate and reach by follower tier**. There are almost none for skip rate, viewed-vs-swiped, or retention, and most of those numbers are vendor rules of thumb. The best approach is to benchmark each reel against **the account's own median over its last 10–20 reels of similar length**.

### Cited Findings
- **[DATA]** Metricool + HypeAuditor "2025 Instagram Content Playbook" (Jan–Jun 2025 data; six follower tiers; the press release says 700M posts across 28M accounts, while Lia Haberman's preview says up to 70M, a conflict). For accounts **<1,000 followers**, Reels' median reach was **134**, against 56 for carousels and 23 for images. Reels lead on reach in every follower tier, and for accounts under 50k followers Reels consistently out-reach other formats. — [Metricool press release](https://metricool.com/press-release-instagram-content-playbook/); [Net Influencer](https://www.netinfluencer.com/instagram-carousels-outperform-reels-for-larger-accounts-content-performance-benchmarks-show/); [Lia Haberman](https://liahaberman.substack.com/p/the-best-instagram-content-formats)
- **[DATA]** Metricool 2025 short-form study: average views per video were Facebook 15,334, Instagram 14,422, TikTok 11,447 and YouTube 9,921 (all account sizes; skewed by large accounts). It reported Reels views falling 59%, while accounts under 1,000 followers saw engagement rise 30%. — [Social Media Today press release](https://socialmediatoday.com/press-release/20250908-metricool-2025-study-unveils-70-surge-in-short-form-video-as-tiktok-conti) (secondary summary)
- **[DATA]** Socialinsider 2026 Instagram benchmarks: average Reels engagement rate **0.52%** (carousels 0.55%). Socialinsider's Instagram-wide reach rate was **3.50%** (May 2024–May 2025 dataset; not Reels-specific). A third-party roundup's "1.23% Reels ER (Socialinsider)" could not be matched to Socialinsider's own page, so treat it with caution. — [Socialinsider](https://www.socialinsider.io/instagram-benchmarks) (via search summary); conflicting: [Colorlib](https://colorlib.com/wp/instagram-engagement-rate/)
- **[DATA]** Instagram engagement benchmarks differ by formula: Rival IQ median about 0.30% versus Socialinsider average about 0.48% (by followers). Comparing a company's numbers to a benchmark needs the same formula. — [search summary of postplanify / blckalpaca](https://postplanify.com/blog/social-media-engagement-rate-benchmarks-2026)
- **[DATA, secondary]** Influencer Marketing Hub: for 10k–50k-follower accounts, Reels reach rate 7.10% versus 6.40% for carousels and 5.50% for images (source dataset not stated). — [Influencer Marketing Hub](https://influencermarketinghub.com/Instagram-reels-stats)
- **[OPINION]** Instagram Skip Rate: Instagram publishes no official benchmark. Trackers suggest under about 30–40% is healthy and over about 50% signals a weak hook. — [BabbleBoxx](https://www.babbleboxx.com/post/instagram-adds-reels-retention-skip-rate-what-influencer-marketers-should-do-next)
- **[OPINION]** YouTube "viewed vs swiped away": one guide says to aim for 75–80% viewed. Another shows a real channel at 26.6% viewed over 90 days and recommends benchmarking against your own channel. No official threshold exists. — [Subscribr](https://subscribr.ai/p/youtube-shorts-analytics-metrics-growth); [Social Media Examiner](https://www.socialmediaexaminer.com/?p=251758)
- **[OPINION]** Shorts retention bands (ClipIQ framework): 50–64% average, 65–79% strong, 80%+ top. vidIQ's own channel averages 73.6% viewed. Dash Social's 2025 "99% retention for Shorts" looks like a definitional artefact. Bytecap calls its guide "evidence synthesis" and recommends comparing against same-length Shorts on the same channel. — [GoFaceless](https://www.gofaceless.ai/blog/youtube-shorts-retention-rate-benchmarks); [Dash Social](https://www.dashsocial.com/social-media-benchmarks/youtube); [Bytecap](https://www.bytecap.io/research/youtube-shorts-retention-benchmarks)
- **[OPINION]** TikTok: average watch time over 50% of the video's length is "excellent", 30–50% "good". Completion targets vary: 40–60% "solid" and 70%+ for strong reach. The sources disagree. — [HEC Digital](https://digital.hec.ca/en/blog/tiktok-analytics-to-optimize-your-reach/); [Dataslayer](https://dataslayer.ai/blog/tiktok-algorithm-2025-complete-guide-for-marketers)

### Inferences
- For a new B2B/niche account, expect reach per reel in the low hundreds to low thousands (Metricool median of 134 for <1k-follower accounts). A reel that clearly beats the account's own median (e.g., 2–3× median reach with share and follow rates above median) counts as a "winner" in relative terms. Universal thresholds mislead.
- Treat skip-rate and swipe benchmarks as directional only. Vertical, video length and audience change them a lot.

### Gaps
- No independent 2025–2026 benchmark for shares/sends per reach, saves per reach, or follows per reach for small or B2B accounts was found.
- No Polish or CEE-specific benchmarks were found.
- Emplifi, Hootsuite and Sprout Social 2025–2026 reports were not retrieved, as time was spent on other sources.

## 3. Connecting reach to pipeline (inquiries, sales)

### Takeaway
Short-form reach is largely "dark": views happen in-app, and later visits show up as direct, brand search or email. **Self-reported attribution** ("how did you hear about us", already used in the scorecard) is the main tool, backed by UTM links where clicks are possible, **video-viewer retargeting audiences**, and small-budget **boosting of proven organic winners**. Treat self-reports as directional, since recall bias is a real limit.

### Cited Findings
**Self-reported attribution**
- **[DATA, vendor]** Refine Labs (2023, 620 conversions): software attribution credited web search (direct + organic) with 78% of conversions. Customer self-reports credited web search with only 12% and "dark social" (social, podcasts, word of mouth, communities) with 85%. Refine Labs says software attribution "does not reveal where a prospect became aware". It also says self-reporting is not necessarily *better*, just a different view. — [Refine Labs – The Attribution Mirage](https://www.refinelabs.com/article/attribution-mirage)
- **[OPINION]** The main weakness of "How did you hear about us?" is inaccuracy and recency bias. Combine it with software attribution. — [Blend B2B](https://www.blendb2b.com/blog/self-reported-attribution)
- **[Unverified]** Accuracy claims like "self-reported 72–88% accurate" (GrowthSpree) have no traceable source. Do not use them. — [GrowthSpree](https://www.growthspreeofficial.com/blogs/b2b-saas-attribution-model-accuracy-benchmarks-2026-first-touch-last-touch-multi-touch-self-reported-comparison)

**UTM / analytics limits (dark social)**
- **[DATA]** SparkToro + Really Good Data (2023; 1,000+ visits across 11 networks): **100% of visits from TikTok**, Slack, Discord, Mastodon and WhatsApp were labelled "direct" in Google Analytics with no referrer. Facebook Messenger lost referrer data in 75% of visits. Secondary write-ups give Instagram DMs about 30%. (2023, older than the preferred range.) — [SparkToro](https://sparktoro.com/blog/new-research-dark-social-falsely-attributes-significant-percentages-of-web-traffic-as-direct)

**Retargeting audiences from video viewers**
- **Meta:** video engagement custom audiences can be built from viewers at several watch levels (e.g., 3s, ThruPlay, 25/50/75/95%), with a lookback of 1–365 days, updated dynamically. — [Jon Loomer](https://www.jonloomer.com/facebook-video-engagement-custom-audiences/); [Agorapulse](https://www.agorapulse.com/blog/facebook-content-strategy/video-custom-audiences-facebook-ads/). Note: Meta's own docs were not retrieved, so verify the options in Ads Manager.
- **[OPINION]** Use about 30-day windows for high-intent segments (95% viewers) rather than 365 days. A practical minimum audience size of about 5,000 is also suggested. — [NovaPixel](https://novapixeldev.com/blog/pick-meta-audience-manually-engagement-retargeting-system); [MHI Growth Engine](https://mhigrowthengine.com/blog/video-view-retargeting-meta/)
- **[OFFICIAL]** Google Ads "your data segments" (formerly remarketing lists) can target people based on past interactions with your YouTube videos or channel. The initial list can backfill the last 30 days of channel activity. The Shorts view-count change does not affect remarketing: views must reach **10 seconds** to qualify. Segments can be combined (e.g., viewed X but not Y). — [Google Ads Help](https://support.google.com/google-ads/answer/2545661?hl=en) (via search summary)

**Boosting organic winners**
- **TikTok Spark Ads:** these run an existing organic post as an ad, keeping the account handle and engagement. For your own account, link it to Ads Manager. For a creator's post, use an authorization code (7/30/60 days). Expired codes stop delivery. The "$20/day ad group minimum" is third-party and unverified. — [Vamp](https://vamp.com/blog/everything-you-need-to-know-about-tiktok-spark-ads/); [Relevant Audience](https://www.relevantaudience.com/tiktok-ads/tiktok-spark-ads-guide/); [MegaDigital](https://megadigital.ai/en/blog/tiktok-spark-ads/)
- **Meta boost:** boosting reels from about $1/day for 1–30 days is reported. iOS in-app boosts may add an Apple service fee (reported as 30%), so boost from the web. Review is usually minutes and can take up to 24h. **[OPINION]** Agencies suggest Ads Manager over boost and about £10–20/day. $5/day won't exit the learning phase on short campaigns. — [Hootsuite](https://blog.hootsuite.com/boost-instagram-reels/); [Lilach Bullock](https://www.lilachbullock.com/run-ads-using-instagram-reels/). Note: costs come from third parties, so verify in Meta Business Help Center.
- Partnership ads (Meta) and YouTube "Promote" for Shorts: no reliable 2025–2026 source on small-budget mechanics was retrieved.

### Inferences
- **Recommended tie-in for this company:**
  1. Keep the self-reported source field and make it structured, not free text. Ask "Where did you first hear about us?" with options (YouTube / Instagram / Facebook / TikTok / Google / recommendation / other) plus an optional "what did you see?" field. Ask it in every email reply template and in the Shoper checkout or contact form.
  2. Log **every** inquiry, including ones with no source. Then compute the share of inquiries per week that cite short-form, which turns the existing ~7 YouTube mentions in 3 weeks into a trend line.
  3. Add UTM-tagged links where links exist (YT description or pinned comment, IG bio link, link stickers). Expect most short-form influence to show up as direct traffic or brand search, not as UTM clicks (SparkToro).
  4. Track proxy lift weekly: branded search (Google Search Console for "Elevate"/brand names), direct sessions on Shoper, and email inquiries. Compare these against weekly reach.
  5. Start building **viewer audiences now**, at no cost: Meta video viewers and Google Ads YouTube data segments. These pools are used later with small retargeting budgets (e.g., testimonial, offer or product-detail videos to 50–95% viewers).
- For B2B (gyms, clubs), relevant deals are few, so analysis per inquiry (a qualitative note on "which video did you see?") is worth more than statistical attribution.

### Gaps
- No independent (non-vendor) validation of self-reported attribution accuracy was found.
- No SMB or e-commerce-specific evidence was found on what share of short-form-driven buyers recall the source correctly.
- Meta Partnership ads and YouTube Shorts promotion minimum budgets were not verified from official sources.

## 4. Testing cadence: volume, variants, hooks, kill/scale rules, Trial Reels, sustainable output for one person

### Takeaway
A sustainable cadence for one marketer is about **3–5 reels per week**, cross-posted to IG/FB/YT Shorts (and TikTok if used). Test **one variable at a time**, usually the hook or first 3 seconds, and judge each reel against the account's own median after a fixed window. **Instagram Trial Reels** give a free way to A/B hooks on non-followers. Paid kill and scale rules from ads work fine once a small boost budget is used.

### Cited Findings
- **[DATA]** Buffer (over 2M posts from 100k Instagram accounts; all feed formats, not reels-only): **3–5 posts/week** is the "sweet spot". Moving from 1–2 to 3–5 per week lifts reach per post by about 12%. Follower growth per week rises with volume (1–2: +0.12%; 3–5: +0.26%; 6–9: +0.44%; 10+: +0.66%), with diminishing returns. — [Buffer](https://buffer.com/resources/how-often-to-post-on-instagram/); [Social Media Today](https://www.socialmediatoday.com/news/study-shows-posting-more-instagram-leads-to-more-reach/757633/)
- **[OFFICIAL]** **Instagram Trial Reels** (launched Dec 2024) are shown only to non-followers and are hidden from the profile grid and followers' feeds. Insights arrive about 24h after posting. Instagram can auto-share a trial to followers "if we determine it's performing well based on the views it receives within the first 72 hours". Manual sharing is possible at any time. No threshold is published. Third-party claims of a 1,000-follower minimum and about 20 trials/day are unverified. — [9to5Mac](https://9to5mac.com/2024/12/10/instagrams-new-trial-reels-feature-lets-creators-test-content-with-non-followers); [Inro](https://www.inro.social/blog/what-is-a-reel-trial-and-how-does-it-work); [Storrito](https://storrito.com/resources/how-instagram-trial-reels-work-72-hours/)
- **[OPINION]** Hook testing: keep the body, visual and copy the same and change only the first 3 seconds. — [Madgicx](https://madgicx.com/blog/ad-testing)
- **[OPINION]** Keep tests separate from scaling (champion/challenger) so data isn't skewed. — [Madgicx](https://madgicx.com/blog/ad-testing)
- **[OPINION]** Paid kill rule: pause underperformers after about 48h or about 1,000 impressions. Scale by cloning proven hooks into new angles, not only by raising budget. Spreading a small budget across many ads (e.g., $500 / 10 ads) fails to reach significance. — [Chatterbuzz](https://chatterbuzzmedia.com/blog/ad-creative-testing/)
- **[OPINION, anecdotal]** Micro-testing about 100 hooks at about $10 each, then moving the top 10–20 to scale (a single LinkedIn practitioner post; not applicable at this budget). — [LinkedIn](https://si.linkedin.com/in/matejocepek)
- **[OPINION]** Spark Ads test budgets of about $50/day per creative for 5–7 days (music-promo context). — [Dynamoi](https://dynamoi.com/nl/learn/tiktok-music-promotion/tiktok-spark-ads-for-music-promotion)

### Inferences
- **Proposed weekly system for one marketer (synthesis, not sourced as a whole):**
  - **Produce:** 4 reels/week from 1–2 filming sessions. Batch footage, since factory, installation and product drop or impact tests yield many clips. Cross-post each reel to IG + FB + YT Shorts (+ TikTok) to get 3–4 reads per edit.
  - **Test:** for 1–2 of the 4 reels, publish 2 hook variants (Trial Reel on IG, or the variant on a different platform). Change only the first 1–3 seconds or the on-screen text.
  - **Read at fixed windows:** 72h (Trial Reels logic) and 7 days. Log each reel in a sheet with: topic/format, hook type, length, reach (unique), skip rate / stayed-to-watch %, avg watch %, shares, saves, follows, profile visits per 1k reach, and inquiries citing it.
  - **Kill/keep rule (organic):** after 7 days, a reel is a "winner" if it is in the top 25% of the last 20 reels on reach **and** on shares or follows per 1k reach. Make 2–3 follow-up variants of winning topics or hooks. Retire a hook type after 3 bottom-quartile results.
  - **Scale:** put a small budget (e.g., €5–10/day for 5–7 days) behind 1 winner per fortnight via Meta (Ads Manager, not iOS boost) or Spark Ads. Target a lookalike or a broad audience in Poland, then retarget 50–95% viewers with an offer or proof video.
  - **Monthly review:** reach trend versus inquiry trend (self-reported) and branded search. Decide which 2–3 formats to double down on.

### Gaps
- No controlled study of reels-per-week output for one-person teams was found. The 3–5/week figure is from Buffer (all formats) plus inference.
- No official YouTube equivalent of Trial Reels was found in this research. YouTube has "A/B test thumbnails" for long-form, but nothing for Shorts hooks was verified.

## 5. Common measurement mistakes

### Takeaway
The main traps are counting **views** (now inflated by replays), comparing reels of different length or format, judging too early or on too few posts, ignoring the shift from per-follower to per-reach metrics, and reading UTM or GA traffic as the full impact of short-form.

### Cited Findings
- Views are inflated by design: YouTube counts every start or replay from 31 Mar 2025 (one example showed over +33% more views), and Meta Views include repeat viewings. Critics flagged inflation from brief or accidental views. — [MobileSyrup](https://mobilesyrup.com/2025/03/27/youtube-changes-how-it-counts-shorts-views/); [Movavi](https://movavi.com/news/youtube-revamps-shorts-metrics-what-creators-need-to-know); [Social Media Today](https://www.socialmediatoday.com/news/facebook-switches-views-primary-metric/732979/)
- Period comparisons across the metric change break: use engaged views for Shorts before 31 Mar 2025. — [Creator Handbook](https://www.creatorhandbook.net/youtube-is-changing-how-its-counting-shorts-views/)
- Comparing different formats or lengths: retention should be compared against similar-length Shorts on the same channel. — [Bytecap](https://www.bytecap.io/research/youtube-shorts-retention-benchmarks)
- Benchmarks using different engagement formulas (by followers vs by reach; median vs average) aren't comparable. — [Postplanify](https://postplanify.com/blog/social-media-engagement-rate-benchmarks-2026)
- Judging on hook rate alone, without hold rate, kills good concepts. — [Selzee](https://selzee.com/blog/hook-rate-vs-hold-rate)
- Too little budget spread across too many paid variants fails to reach significance. — [Chatterbuzz](https://chatterbuzzmedia.com/blog/ad-creative-testing/)
- Trusting GA or UTM alone: TikTok and messaging traffic arrives as "direct". — [SparkToro](https://sparktoro.com/blog/new-research-dark-social-falsely-attributes-significant-percentages-of-web-traffic-as-direct)
- Over-trusting software attribution leaves out where awareness started. — [Refine Labs](https://www.refinelabs.com/article/attribution-mirage)

### Inferences
- With about 7 YouTube-sourced inquiries in 3 weeks, week-to-week swings are noise. Judge attribution trends on a 4–8-week rolling basis. Judge individual reels on 7-day metrics against the account median, never on 24h numbers alone, except the 72h Trial Reels read.
- Retail and B2B inquiries should be split in the scorecard, because a reel can drive retail e-shop interest without moving B2B pipeline (or the reverse).

### Gaps
- No source quantifies a "minimum test window" for organic reels. The 72h (Trial Reels) and 7-day windows are practical conventions, not evidence-based thresholds.
