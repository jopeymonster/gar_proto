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

-- label scope w/o metrics
SELECT 
label.name, 
label.id, 
customer.descriptive_name 
FROM label
WHERE label.status = 'ENABLED'
ORDER BY 
  customer.descriptive_name DESC

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

-- click_view - TESTING
SELECT 
click_view.ad_group_ad, 
click_view.gclid, 
click_view.keyword, 
click_view.keyword_info.match_type, 
click_view.keyword_info.text, 
click_view.page_number, 
ad_group.campaign, 
ad_group.id, 
ad_group.labels, 
ad_group.name, 
ad_group.status, 
campaign.advertising_channel_type, 
campaign.campaign_group, 
campaign.id, 
campaign.labels, 
campaign.name, 
segments.date, 
segments.device, 
segments.click_type, 
customer.id, 
customer.descriptive_name, 
metrics.clicks 
FROM click_view 
WHERE 
metrics.clicks > 0 
AND segments.date = '2024-05-01' 
ORDER BY 
segments.date ASC, 
customer.descriptive_name ASC, 
campaign.name ASC, 
ad_group.name ASC 