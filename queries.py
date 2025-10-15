# customer/account info
def customer_client_query(): 
    return """
    SELECT
        customer_client.client_customer,
        customer_client.level,
        customer_client.manager,
        customer_client.descriptive_name,
        customer_client.id
    FROM customer_client
    WHERE customer_client.level <= 10
    AND customer_client.status = 'ENABLED'
    AND customer_client.hidden = FALSE
    ORDER BY customer_client.descriptive_name ASC
    """

# audting
def label_query():
    return """
    SELECT 
        label.name, 
        label.id
    FROM label
    WHERE label.status = 'ENABLED'
    ORDER BY label.name ASC
    """

def camp_group_query():
    return """
    SELECT
        campaign_group.name,
        campaign_group.id
    FROM campaign_group
    WHERE campaign_group.status = 'ENABLED'
    ORDER BY campaign_group.name ASC 
    """

def label_audit_query():
    return """
    SELECT
        customer.id,
        customer.descriptive_name,
        campaign.id,
        campaign.name,
        campaign.advertising_channel_type,
        campaign.campaign_group,
        campaign.labels,
        ad_group.id,
        ad_group.name,
        ad_group.type,
        ad_group.labels
    FROM ad_group
    WHERE ad_group.status != 'REMOVED'
    ORDER BY customer.descriptive_name ASC, campaign.name ASC, ad_group.name ASC
    """

# arc
def arc_campaign_query(start_date, end_date, time_seg_string):
    return f"""
        SELECT
            {time_seg_string},
            customer.descriptive_name,
            customer.id,
            campaign.name,
            campaign.advertising_channel_type,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY {time_seg_string} ASC
    """

# account
def account_report_query(start_date, end_date, time_seg_string):
    return f"""
        SELECT
            {time_seg_string},
            customer.descriptive_name,
            customer.id,
            metrics.clicks,
            metrics.invalid_clicks,
            metrics.impressions,
            metrics.interactions,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_micros,
            metrics.absolute_top_impression_percentage,
            metrics.top_impression_percentage,
            metrics.average_cpm
        FROM customer
        WHERE customer.status = 'ENABLED'
        AND segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY {time_seg_string} ASC, customer.descriptive_name DESC
        """ 

# ad_level, does not include PMax (pmax technically doesn't have 'ad groups')
def ad_group_ad_query(start_date, end_date, time_seg_string):
    return f"""
        SELECT
            {time_seg_string},
            customer.id,
            customer.descriptive_name,
            campaign.id,
            campaign.name,
            campaign.advertising_channel_type,
            ad_group.id,
            ad_group.name,
            ad_group.type,
            ad_group_ad.ad.id,
            ad_group_ad.ad.type,
            metrics.cost_micros,
            metrics.impressions,
            metrics.absolute_top_impression_percentage,
            metrics.top_impression_percentage,
            metrics.video_views,
            metrics.average_cpm,
            metrics.clicks,
            metrics.average_cpc,
            metrics.interactions,
            metrics.conversions,
            metrics.conversions_value
        FROM ad_group_ad
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY {time_seg_string} ASC, campaign.name ASC
    """
# pmax query for ads_report
def pmax_campaign_query(start_date, end_date, time_seg_string):
    return f"""
        SELECT
            {time_seg_string},
            customer.id,
            customer.descriptive_name,
            campaign.id,
            campaign.name,
            campaign.advertising_channel_type,
            metrics.cost_micros,
            metrics.impressions,
            metrics.absolute_top_impression_percentage,
            metrics.top_impression_percentage,
            metrics.video_views,
            metrics.average_cpm,
            metrics.clicks,
            metrics.invalid_clicks,
            metrics.average_cpc,
            metrics.interactions,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.advertising_channel_type = 'PERFORMANCE_MAX'
        ORDER BY {time_seg_string} ASC, campaign.name ASC
    """

# click_view
def click_view_query(start_date, end_date, time_seg_string):
    return f"""
        SELECT
            {time_seg_string},
            customer.descriptive_name,
            customer.id,
            campaign.name,
            campaign.id,
            campaign.advertising_channel_type, 
            ad_group.name,
            ad_group.id,
            click_view.ad_group_ad,
            click_view.gclid,
            click_view.keyword,
            click_view.keyword_info.match_type,
            click_view.keyword_info.text,
            click_view.page_number,
            click_view.area_of_interest.country,
            click_view.area_of_interest.region,
            click_view.area_of_interest.metro,
            click_view.area_of_interest.city,
            click_view.area_of_interest.most_specific,
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
            AND segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY 
            {time_seg_string} ASC, 
            customer.descriptive_name DESC
        """

# paid_organic_search_term_view
def paid_organic_search_term_view_query(start_date, end_date, time_seg_string):
    return f"""
        SELECT
            {time_seg_string},
            segments.search_engine_results_page_type,
            segments.keyword.info.match_type,
            segments.keyword.info.text,
            segments.device,
            customer.id,
            customer.descriptive_name,
            campaign.id,
            campaign.name,
            campaign.advertising_channel_type,
            ad_group.id,
            ad_group.name,
            metrics.organic_clicks,
            metrics.organic_clicks_per_query,
            metrics.organic_impressions,
            metrics.organic_impressions_per_query,
            metrics.organic_queries,
            metrics.impressions,
            metrics.combined_queries,
            metrics.combined_clicks_per_query,
            metrics.combined_clicks,
            metrics.clicks,
            metrics.average_cpc,
            metrics.ctr
        FROM paid_organic_search_term_view
        WHERE
            segments.date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY
            {time_seg_string} ASC, 
            customer.descriptive_name DESC,
            campaign.name ASC,
            metrics.clicks DESC
        """