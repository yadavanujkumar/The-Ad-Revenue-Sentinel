"""
Natural Language Query Interface using LangChain
Converts plain English queries to SQL and visualizations
"""
import re
import pandas as pd
from typing import Dict, Any, Optional, List
import plotly.express as px
import plotly.graph_objects as go


class NLQueryEngine:
    """
    Natural Language Query Interface for ad revenue data
    Supports queries like:
    - "Show me the uplift for the summer campaign vs. the baseline"
    - "What's the revenue by region?"
    - "Show click-through rate by device type"
    """
    
    def __init__(self):
        self.query_templates = {
            'uplift': self._handle_uplift_query,
            'revenue_by_region': self._handle_revenue_by_region,
            'revenue_by_device': self._handle_revenue_by_device,
            'click_through_rate': self._handle_ctr_query,
            'conversion_rate': self._handle_conversion_rate,
            'top_campaigns': self._handle_top_campaigns,
            'performance': self._handle_performance_query
        }
        
    def parse_query(self, query: str) -> str:
        """
        Parse natural language query to determine intent
        """
        query_lower = query.lower()
        
        if 'uplift' in query_lower or 'vs' in query_lower or 'compare' in query_lower:
            return 'uplift'
        elif 'revenue' in query_lower and 'region' in query_lower:
            return 'revenue_by_region'
        elif 'revenue' in query_lower and 'device' in query_lower:
            return 'revenue_by_device'
        elif ('click' in query_lower and 'rate' in query_lower) or 'ctr' in query_lower:
            return 'click_through_rate'
        elif 'conversion' in query_lower and 'rate' in query_lower:
            return 'conversion_rate'
        elif 'top' in query_lower and 'campaign' in query_lower:
            return 'top_campaigns'
        elif 'performance' in query_lower:
            return 'performance'
        else:
            return 'unknown'
    
    def process_query(self, 
                     query: str,
                     data: pd.DataFrame) -> Dict[str, Any]:
        """
        Process natural language query and return results
        
        Args:
            query: Natural language query
            data: DataFrame with ad event data
            
        Returns:
            Dictionary with SQL query, results, and visualization
        """
        intent = self.parse_query(query)
        
        if intent == 'unknown':
            return {
                'query': query,
                'intent': 'unknown',
                'error': 'Could not understand the query. Try asking about revenue, uplift, CTR, or conversion rates.',
                'suggestions': [
                    'Show me revenue by region',
                    'What is the click-through rate by device type?',
                    'Show top performing campaigns',
                    'What is the conversion rate?'
                ]
            }
        
        handler = self.query_templates[intent]
        return handler(query, data)
    
    def _handle_uplift_query(self, query: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Handle campaign uplift queries"""
        
        # Extract campaign names from query
        campaigns = data['campaign_id'].unique() if 'campaign_id' in data.columns else []
        
        if len(campaigns) < 2:
            return {
                'query': query,
                'intent': 'uplift',
                'error': 'Need at least 2 campaigns for comparison',
                'available_campaigns': list(campaigns)
            }
        
        # Calculate revenue by campaign
        campaign_revenue = data.groupby('campaign_id')['revenue'].agg(['sum', 'mean', 'count']).reset_index()
        campaign_revenue.columns = ['campaign_id', 'total_revenue', 'avg_revenue', 'impressions']
        campaign_revenue = campaign_revenue.sort_values('total_revenue', ascending=False)
        
        # Generate SQL equivalent
        sql_query = """
        SELECT 
            campaign_id,
            SUM(revenue) as total_revenue,
            AVG(revenue) as avg_revenue,
            COUNT(*) as impressions
        FROM ad_events
        GROUP BY campaign_id
        ORDER BY total_revenue DESC
        """
        
        # Create visualization
        fig = px.bar(
            campaign_revenue,
            x='campaign_id',
            y='total_revenue',
            title='Campaign Revenue Comparison',
            labels={'total_revenue': 'Total Revenue ($)', 'campaign_id': 'Campaign'},
            text='total_revenue'
        )
        fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
        
        # Calculate uplift
        baseline_revenue = campaign_revenue.iloc[-1]['avg_revenue'] if len(campaign_revenue) > 0 else 0
        uplifts = []
        
        for _, row in campaign_revenue.iterrows():
            uplift_pct = ((row['avg_revenue'] - baseline_revenue) / baseline_revenue * 100) if baseline_revenue > 0 else 0
            uplifts.append({
                'campaign_id': row['campaign_id'],
                'avg_revenue': float(row['avg_revenue']),
                'uplift_vs_baseline_pct': float(uplift_pct)
            })
        
        return {
            'query': query,
            'intent': 'uplift',
            'sql_query': sql_query,
            'results': campaign_revenue.to_dict('records'),
            'uplifts': uplifts,
            'visualization': fig,
            'interpretation': f"Found {len(campaigns)} campaigns. Top performer: {campaign_revenue.iloc[0]['campaign_id']} with ${campaign_revenue.iloc[0]['total_revenue']:.2f} total revenue."
        }
    
    def _handle_revenue_by_region(self, query: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Handle revenue by region queries"""
        
        if 'region' not in data.columns or 'revenue' not in data.columns:
            return {
                'query': query,
                'intent': 'revenue_by_region',
                'error': 'Required columns (region, revenue) not found in data'
            }
        
        # Calculate revenue by region
        region_revenue = data.groupby('region')['revenue'].agg(['sum', 'mean', 'count']).reset_index()
        region_revenue.columns = ['region', 'total_revenue', 'avg_revenue', 'impressions']
        region_revenue = region_revenue.sort_values('total_revenue', ascending=False)
        
        sql_query = """
        SELECT 
            region,
            SUM(revenue) as total_revenue,
            AVG(revenue) as avg_revenue,
            COUNT(*) as impressions
        FROM ad_events
        GROUP BY region
        ORDER BY total_revenue DESC
        """
        
        # Create visualization
        fig = px.bar(
            region_revenue,
            x='region',
            y='total_revenue',
            title='Revenue by Region',
            labels={'total_revenue': 'Total Revenue ($)', 'region': 'Region'},
            color='total_revenue',
            color_continuous_scale='Viridis'
        )
        
        return {
            'query': query,
            'intent': 'revenue_by_region',
            'sql_query': sql_query,
            'results': region_revenue.to_dict('records'),
            'visualization': fig,
            'interpretation': f"Top region: {region_revenue.iloc[0]['region']} with ${region_revenue.iloc[0]['total_revenue']:.2f} total revenue."
        }
    
    def _handle_revenue_by_device(self, query: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Handle revenue by device type queries"""
        
        if 'device_type' not in data.columns or 'revenue' not in data.columns:
            return {
                'query': query,
                'intent': 'revenue_by_device',
                'error': 'Required columns (device_type, revenue) not found in data'
            }
        
        # Calculate revenue by device
        device_revenue = data.groupby('device_type')['revenue'].agg(['sum', 'mean', 'count']).reset_index()
        device_revenue.columns = ['device_type', 'total_revenue', 'avg_revenue', 'impressions']
        
        sql_query = """
        SELECT 
            device_type,
            SUM(revenue) as total_revenue,
            AVG(revenue) as avg_revenue,
            COUNT(*) as impressions
        FROM ad_events
        GROUP BY device_type
        """
        
        # Create pie chart
        fig = px.pie(
            device_revenue,
            values='total_revenue',
            names='device_type',
            title='Revenue Distribution by Device Type'
        )
        
        return {
            'query': query,
            'intent': 'revenue_by_device',
            'sql_query': sql_query,
            'results': device_revenue.to_dict('records'),
            'visualization': fig,
            'interpretation': f"Analyzed revenue across {len(device_revenue)} device types."
        }
    
    def _handle_ctr_query(self, query: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Handle click-through rate queries"""
        
        if 'clicked' not in data.columns:
            return {
                'query': query,
                'intent': 'click_through_rate',
                'error': 'Click data not available'
            }
        
        # Calculate CTR by device type
        if 'device_type' in data.columns:
            ctr_by_device = data.groupby('device_type')['clicked'].agg(['mean', 'sum', 'count']).reset_index()
            ctr_by_device.columns = ['device_type', 'ctr', 'total_clicks', 'total_impressions']
            ctr_by_device['ctr_pct'] = ctr_by_device['ctr'] * 100
            
            sql_query = """
            SELECT 
                device_type,
                AVG(clicked) * 100 as ctr_pct,
                SUM(clicked) as total_clicks,
                COUNT(*) as total_impressions
            FROM ad_events
            GROUP BY device_type
            """
            
            fig = px.bar(
                ctr_by_device,
                x='device_type',
                y='ctr_pct',
                title='Click-Through Rate by Device Type',
                labels={'ctr_pct': 'CTR (%)', 'device_type': 'Device Type'},
                text='ctr_pct'
            )
            fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            
            return {
                'query': query,
                'intent': 'click_through_rate',
                'sql_query': sql_query,
                'results': ctr_by_device.to_dict('records'),
                'visualization': fig,
                'interpretation': f"Overall CTR: {data['clicked'].mean()*100:.2f}%"
            }
        else:
            overall_ctr = data['clicked'].mean() * 100
            return {
                'query': query,
                'intent': 'click_through_rate',
                'results': {'overall_ctr_pct': float(overall_ctr)},
                'interpretation': f"Overall CTR: {overall_ctr:.2f}%"
            }
    
    def _handle_conversion_rate(self, query: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Handle conversion rate queries"""
        
        if 'revenue' not in data.columns:
            return {
                'query': query,
                'intent': 'conversion_rate',
                'error': 'Conversion data not available'
            }
        
        # Calculate conversion rate
        total_events = len(data)
        conversions = (data['revenue'] > 0).sum()
        conversion_rate = (conversions / total_events * 100) if total_events > 0 else 0
        
        return {
            'query': query,
            'intent': 'conversion_rate',
            'results': {
                'total_events': total_events,
                'conversions': int(conversions),
                'conversion_rate_pct': float(conversion_rate)
            },
            'interpretation': f"Conversion Rate: {conversion_rate:.2f}% ({conversions} conversions out of {total_events} events)"
        }
    
    def _handle_top_campaigns(self, query: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Handle top campaigns queries"""
        
        if 'campaign_id' not in data.columns or 'revenue' not in data.columns:
            return {
                'query': query,
                'intent': 'top_campaigns',
                'error': 'Campaign data not available'
            }
        
        # Get top campaigns by revenue
        top_campaigns = data.groupby('campaign_id').agg({
            'revenue': ['sum', 'mean'],
            'event_id': 'count'
        }).reset_index()
        top_campaigns.columns = ['campaign_id', 'total_revenue', 'avg_revenue', 'impressions']
        top_campaigns = top_campaigns.sort_values('total_revenue', ascending=False).head(10)
        
        sql_query = """
        SELECT 
            campaign_id,
            SUM(revenue) as total_revenue,
            AVG(revenue) as avg_revenue,
            COUNT(*) as impressions
        FROM ad_events
        GROUP BY campaign_id
        ORDER BY total_revenue DESC
        LIMIT 10
        """
        
        fig = px.bar(
            top_campaigns,
            x='campaign_id',
            y='total_revenue',
            title='Top 10 Campaigns by Revenue',
            labels={'total_revenue': 'Total Revenue ($)', 'campaign_id': 'Campaign'}
        )
        
        return {
            'query': query,
            'intent': 'top_campaigns',
            'sql_query': sql_query,
            'results': top_campaigns.to_dict('records'),
            'visualization': fig,
            'interpretation': f"Top campaign: {top_campaigns.iloc[0]['campaign_id']} with ${top_campaigns.iloc[0]['total_revenue']:.2f}"
        }
    
    def _handle_performance_query(self, query: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Handle general performance queries"""
        
        summary = {
            'total_impressions': len(data),
            'total_revenue': float(data['revenue'].sum()) if 'revenue' in data.columns else 0,
            'avg_revenue_per_impression': float(data['revenue'].mean()) if 'revenue' in data.columns else 0,
        }
        
        if 'clicked' in data.columns:
            summary['total_clicks'] = int(data['clicked'].sum())
            summary['ctr_pct'] = float(data['clicked'].mean() * 100)
        
        return {
            'query': query,
            'intent': 'performance',
            'results': summary,
            'interpretation': f"Total Revenue: ${summary['total_revenue']:.2f} from {summary['total_impressions']} impressions"
        }
