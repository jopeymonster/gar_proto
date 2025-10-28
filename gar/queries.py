# -*- coding: utf-8 -*-
"""GAQL query templates used by the Google Ads Reporter prototype."""


# query builder
def build_query(
    resource: str,
    select_fields: list[str],
    start_date: str,
    end_date: str,
    where_clauses: list[str] | None = None,
    order_by: list[str] | None = None,
) -> str:
    """Construct a GAQL query with basic filtering and ordering.

    Args:
        resource (str): GAQL resource name (for example 'campaign').
        select_fields (list[str]): Field selection for the query.
        start_date (str): Inclusive start date ('YYYY-MM-DD').
        end_date (str): Inclusive end date ('YYYY-MM-DD').
        where_clauses (list[str] | None): Additional predicates for the WHERE
            clause.
        order_by (list[str] | None): Optional ordering instructions.

    Returns:
        str: Fully assembled GAQL query string.
    """
    # SELECT
    query = "SELECT\n    " + ",\n    ".join(select_fields)
    query += f"\nFROM {resource}\n"
    # WHERE
    where_parts = [f"segments.date BETWEEN '{start_date}' AND '{end_date}'"]
    if where_clauses:
        where_parts.extend(where_clauses)
    query += "WHERE " + " AND ".join(where_parts) + "\n"
    # ORDER BY
    if order_by:
        query += "ORDER BY " + ", ".join(order_by) + "\n"
    return query.strip()


# customer/account info
def customer_client_query():
    """Return a GAQL query listing non-manager customer accounts."""

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
    """Return a GAQL query fetching enabled labels."""

    return """
    SELECT
        label.name,
        label.id
    FROM label
    WHERE label.status = 'ENABLED'
    ORDER BY label.name ASC
    """


def camp_group_query():
    """Return a GAQL query fetching enabled campaign groups."""

    return """
    SELECT
        campaign_group.name,
        campaign_group.id
    FROM campaign_group
    WHERE campaign_group.status = 'ENABLED'
    ORDER BY campaign_group.name ASC 
    """


def label_audit_query():
    """Return a GAQL query joining campaigns, ad groups, and labels."""

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
def arc_report_query(start_date, end_date, time_seg_string, **kwargs):
    """Return a GAQL query for the ARC performance report."""

    select_fields = [
        time_seg_string,
        "customer.descriptive_name",
        "customer.id",
        "campaign.name",
        "campaign.advertising_channel_type",
        "metrics.cost_micros",
    ]
    where_clauses = []
    return build_query(
        resource="campaign",
        select_fields=select_fields,
        start_date=start_date,
        end_date=end_date,
        where_clauses=where_clauses,
        order_by=[f"{time_seg_string} ASC"],
    )


def account_report_query(start_date, end_date, time_seg_string, **kwargs):
    """Return a GAQL query for the account performance report."""

    select_fields = [
        time_seg_string,
        "customer.descriptive_name",
        "customer.id",
        "metrics.clicks",
        "metrics.invalid_clicks",
        "metrics.impressions",
        "metrics.interactions",
        "metrics.ctr",
        "metrics.average_cpc",
        "metrics.cost_micros",
        "metrics.absolute_top_impression_percentage",
        "metrics.top_impression_percentage",
        "metrics.average_cpm",
    ]
    where_clauses = ["customer.status = 'ENABLED'"]
    order_by = [f"{time_seg_string} ASC", "customer.descriptive_name DESC"]
    return build_query(
        resource="customer",
        select_fields=select_fields,
        start_date=start_date,
        end_date=end_date,
        where_clauses=where_clauses,
        order_by=order_by,
    )


# ad_level, does not include PMax (pmax technically doesn't have 'ad groups')
def ad_group_ad_query(start_date, end_date, time_seg_string, **kwargs):
    """Return a GAQL query retrieving ad-level performance details."""

    select_fields = [
        time_seg_string,
        "customer.id",
        "customer.descriptive_name",
        "campaign.id",
        "campaign.name",
        "campaign.advertising_channel_type",
        "ad_group.id",
        "ad_group.name",
        "ad_group.type",
        "ad_group_ad.ad.id",
        "ad_group_ad.ad.type",
        "metrics.cost_micros",
        "metrics.impressions",
        "metrics.absolute_top_impression_percentage",
        "metrics.top_impression_percentage",
        "metrics.video_views",
        "metrics.average_cpm",
        "metrics.clicks",
        "metrics.average_cpc",
        "metrics.interactions",
        "metrics.conversions",
        "metrics.conversions_value",
    ]
    where_clauses = ["customer.status = 'ENABLED'"]
    order_by = [
        f"{time_seg_string} ASC",
        "customer.descriptive_name ASC",
        "campaign.name ASC",
    ]
    return build_query(
        resource="ad_group_ad",
        select_fields=select_fields,
        start_date=start_date,
        end_date=end_date,
        where_clauses=where_clauses,
        order_by=order_by,
    )


# pmax query for ads_report
def pmax_campaign_query(start_date, end_date, time_seg_string, **kwargs):
    """Return a GAQL query focusing on Performance Max campaign metrics."""

    select_fields = [
        time_seg_string,
        "customer.id",
        "customer.descriptive_name",
        "campaign.id",
        "campaign.name",
        "campaign.advertising_channel_type",
        "metrics.cost_micros",
        "metrics.impressions",
        "metrics.absolute_top_impression_percentage",
        "metrics.top_impression_percentage",
        "metrics.video_views",
        "metrics.average_cpm",
        "metrics.clicks",
        "metrics.invalid_clicks",
        "metrics.average_cpc",
        "metrics.interactions",
        "metrics.conversions",
        "metrics.conversions_value",
    ]
    where_clauses = [
        "campaign.advertising_channel_type = 'PERFORMANCE_MAX'",
        "customer.status = 'ENABLED'",
    ]
    order_by = [
        f"{time_seg_string} ASC",
        "customer.descriptive_name ASC",
        "campaign.name ASC",
    ]
    return build_query(
        resource="campaign",
        select_fields=select_fields,
        start_date=start_date,
        end_date=end_date,
        where_clauses=where_clauses,
        order_by=order_by,
    )


# click_view
def click_view_query(start_date, end_date, time_seg_string, **kwargs):
    """Return a GAQL query retrieving ClickView performance data."""

    select_fields = [
        time_seg_string,
        "customer.descriptive_name",
        "customer.id",
        "campaign.name",
        "campaign.id",
        "campaign.advertising_channel_type,ad_group.name",
        "ad_group.id",
        "click_view.ad_group_ad",
        "click_view.gclid",
        "click_view.keyword",
        "click_view.keyword_info.match_type",
        "click_view.keyword_info.text",
        "click_view.page_number",
        "click_view.area_of_interest.country",
        "click_view.area_of_interest.region",
        "click_view.area_of_interest.metro",
        "click_view.area_of_interest.city",
        "click_view.area_of_interest.most_specific",
        "click_view.location_of_presence.country",
        "click_view.location_of_presence.region",
        "click_view.location_of_presence.metro",
        "click_view.location_of_presence.city",
        "click_view.location_of_presence.most_specific",
        "segments.device",
        "segments.click_type",
        "metrics.clicks",
    ]
    where_clauses = ["metrics.clicks > 0"]
    order_by = [
        f"{time_seg_string} ASC",
        "customer.descriptive_name ASC",
        "campaign.name ASC",
        "ad_group.name ASC",
    ]
    return build_query(
        resource="click_view",
        select_fields=select_fields,
        start_date=start_date,
        end_date=end_date,
        where_clauses=where_clauses,
        order_by=order_by,
    )


# paid_organic_search_term_view
def paid_organic_search_term_view_query(
    start_date, end_date, time_seg_string, **kwargs
):
    """Return a GAQL query for paid and organic search term metrics."""

    select_fields = [
        time_seg_string,
        "segments.search_engine_results_page_type",
        "segments.keyword.info.match_type",
        "segments.keyword.info.text",
        "segments.device",
        "customer.id",
        "customer.descriptive_name",
        "campaign.id",
        "campaign.name",
        "campaign.advertising_channel_type",
        "ad_group.id",
        "ad_group.name",
        "metrics.organic_clicks",
        "metrics.organic_clicks_per_query",
        "metrics.organic_impressions",
        "metrics.organic_impressions_per_query",
        "metrics.organic_queries",
        "metrics.impressions",
        "metrics.combined_queries",
        "metrics.combined_clicks_per_query",
        "metrics.combined_clicks",
        "metrics.clicks",
        "metrics.average_cpc",
        "metrics.ctr",
    ]
    where_clauses = []
    order_by = [
        f"{time_seg_string} ASC",
        "customer.descriptive_name DESC",
        "campaign.name ASC",
        "metrics.clicks DESC",
    ]
    return build_query(
        resource="paid_organic_search_term_view",
        select_fields=select_fields,
        start_date=start_date,
        end_date=end_date,
        where_clauses=where_clauses,
        order_by=order_by,
    )
