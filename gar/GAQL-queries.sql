GAQL queries

-- account, general
SELECT
  customer.descriptive_name,
  customer.id,
  metrics.clicks,
  metrics.impressions,
  metrics.ctr,
  metrics.average_cpc,
  metrics.cost_micros,
  metrics.absolute_top_impression_percentage,
  metrics.top_impression_percentage,
  metrics.average_cpm
FROM customer
WHERE segments.date DURING LAST_7_DAYS

-- label scope, ad group+campaign
SELECT 
  ad_group.id, 
  ad_group.labels, 
  label.id, 
  label.status, 
  label.name, 
  ad_group.name, 
  campaign.id, 
  campaign.name, 
  campaign.labels, 
  customer.id, 
  customer.descriptive_name 
FROM ad_group_label 
WHERE 
  label.status = 'ENABLED' 
ORDER BY 
  ad_group.id ASC, 
  campaign.id ASC 

-- campaign group w/o metrics
SELECT
campaign_group.name,
campaign_group.id,
customer.descriptive_name
FROM campaign_group
WHERE
campaign_group.status = 'ENABLED'
ORDER BY
customer.descriptive_name  

-- ad group scope, w/metrics, last calendar month / TESTING
SELECT
segments.date,
customer.descriptive_name,
campaign.name,
campaign.campaign_group,
campaign.labels,
ad_group.name,
ad_group.labels,
campaign.advertising_channel_type,
metrics.cost_micros,
metrics.impressions,
metrics.clicks,
metrics.interactions,
metrics.conversions,
metrics.conversions_value,
customer.id,
campaign.id,
ad_group.id
FROM ad_group 
WHERE 
metrics.average_cost > 0 
AND segments.date DURING LAST_MONTH
ORDER BY 
segments.date DESC,
customer.descriptive_name DESC,
campaign.name DESC,
ad_group.name DESC

-- ad_group scope, dynamic single date
SELECT
segments.{time_seg},
customer.descriptive_name,
campaign.name,
campaign.campaign_group,
campaign.labels,
ad_group.name,
ad_group.labels,
campaign.advertising_channel_type,
metrics.cost_micros,
metrics.impressions,
metrics.clicks,
metrics.interactions,
metrics.conversions,
metrics.conversions_value,
customer.id,
campaign.id,
ad_group.id
FROM ad_group 
WHERE 
metrics.clicks > 0
AND segments.{time_seg} {time_condition} {start_date}
ORDER BY 
segments.{time_seg} ASC,
customer.descriptive_name ASC,
campaign.name ASC,
ad_group.name ASC

-- click_view
SELECT
segments.date,
customer.id,
customer.descriptive_name,
campaign.id,
campaign.name,
campaign.advertising_channel_type, 
ad_group.id,
ad_group.name,
click_view.ad_group_ad,
click_view.gclid,
click_view.keyword,
click_view.keyword_info.match_type,
click_view.keyword_info.text,
click_view.page_number,
click_view.location_of_presence.country,
click_view.location_of_presence.region,
click_view.location_of_presence.metro,
click_view.location_of_presence.city,
click_view.location_of_presence.most_specific,
click_view.location_of_presence.country,
click_view.location_of_presence.region,
click_view.location_of_presence.metro,
click_view.location_of_presence.city,
click_view.location_of_presence.most_specific,
segments.device,
segments.click_type,
metrics.clicks
FROM click_view
WHERE 
metrics.clicks > 0 
AND segments.date = {start_date}
ORDER BY 
segments.date ASC, 
customer.descriptive_name DESC, 
campaign.name DESC, 
ad_group.name DESC

-- reporting breakdown, w/campaign group
SELECT 
  segments.date, 
  customer.id, 
  customer.descriptive_name, 
  campaign.id, 
  campaign.name, 
  campaign.advertising_channel_type, 
  campaign.labels, 
  ad_group.id, 
  ad_group.name, 
  ad_group.labels, 
  ad_group.type, 
  ad_group_ad.ad.id, 
  ad_group_ad.ad.type, 
  ad_group_ad.labels, 
  metrics.cost_micros, 
  metrics.impressions, 
  metrics.clicks, 
  metrics.video_views, 
  metrics.conversions, 
  metrics.conversions_value, 
  campaign.campaign_group 
FROM ad_group_ad 
WHERE 
  metrics.clicks > 0 
  AND segments.date BETWEEN '2025-01-01' AND '2025-01-31' 
ORDER BY 
  segments.date ASC, 
  customer.descriptive_name ASC, 
  campaign.name ASC, 
  ad_group.name ASC

-- customer_resource_query, sub accounts scope
    SELECT
    customer.id, 
    customer.descriptive_name 
    FROM customer

-- customer_client_query, mcc accounts scope
    SELECT
    customer_client.client_customer,
    customer_client.level,
    customer_client.manager,
    customer_client.descriptive_name,
    customer_client.id
    FROM customer_client
    WHERE customer_client.level <= 10
"""