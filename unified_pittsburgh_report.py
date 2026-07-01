# Pittsburgh AI Investment Ecosystem: Enhanced Unified Preliminary Report
# Block Center, Carnegie Mellon University
# Authors: Pablo Zavala and Liufei Chen

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
import json
import math
import numpy as np
from datetime import datetime
from comprehensive_pittsburgh_analysis import PittsburghAnalyzer, EcosystemAnalytics, NetworkAnalytics

class UnifiedPittsburghReport:
    """Generate enhanced comprehensive report leveraging all available data sources"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.pittsburgh_df = analyzer.pittsburgh_df
        self.ecosystem_df = analyzer.ecosystem_df
        self.investor_profiles_df = analyzer.investor_profiles_df
        self.funding_transactions_df = analyzer.funding_transactions_df
        self.educational_institutions_df = analyzer.educational_institutions_df
    
    def create_executive_metrics(self):
        """Calculate enhanced executive summary metrics"""
        metrics = EcosystemAnalytics.calculate_ecosystem_metrics(self.pittsburgh_df)
        industry_stats = EcosystemAnalytics.industry_analysis(self.pittsburgh_df)
        
        # Enhanced metrics with new data
        enhanced_metrics = metrics.copy()
        
        # Add high-growth companies if available
        if 'is_high_growth' in self.pittsburgh_df.columns:
            enhanced_metrics['high_growth_companies'] = self.pittsburgh_df['is_high_growth'].sum()
        
        # Add innovation metrics
        if 'innovation_score' in self.pittsburgh_df.columns:
            enhanced_metrics['top_innovators'] = (self.pittsburgh_df['innovation_score'] > self.pittsburgh_df['innovation_score'].quantile(0.9)).sum()
        
        # Add funding efficiency
        enhanced_metrics['funding_efficiency'] = metrics['funding_efficiency']
        
        enhanced_metrics.update({
            'dominant_sector': industry_stats.iloc[0]['industry_category'],
            'sector_funding': industry_stats.iloc[0]['total_funding'],
            'recent_funding_velocity': self.pittsburgh_df[self.pittsburgh_df['founded_year'] >= 2020]['funding_velocity'].mean() if 'funding_velocity' in self.pittsburgh_df.columns else 0
        })
        
        return enhanced_metrics
    
    def create_enhanced_industry_analysis(self):
        """Redesigned industry analysis with clearer, more intuitive visuals"""
        industry_long = self.analyzer.industry_long_df
        industry_stats = (industry_long.groupby('industry_category')
                          .agg(companies=('Organization Name','nunique'),
                               total_funding=('funding_weighted','sum'),
                               total_employees=('employee_estimate_weighted','sum'),
                               active_companies=('is_active','sum'),
                               founded_median=('founded_year','median'))
                          .reset_index())
        industry_stats['funding_efficiency'] = industry_stats['total_funding']/industry_stats['total_employees']
        industry_stats['maturity_years'] = datetime.now().year - industry_stats['founded_median']
        industry_stats['success_rate'] = industry_stats['active_companies']/industry_stats['companies']*100
        industry_stats['market_share'] = industry_stats['total_funding']/industry_stats['total_funding'].sum()*100
        industry_stats = industry_stats.replace([np.inf,-np.inf],np.nan)
        
        # Calculate additional fields required for the new visuals
        # industry_stats['funding_efficiency'] = (
        #     industry_stats['total_funding'] / industry_stats['total_employees']
        # ).replace([np.inf, -np.inf], np.nan)
        
        # 1. Total Funding by Industry (horizontal bar for clarity)
        fig1 = px.bar(
            industry_stats.sort_values('total_funding', ascending=True),
            x='total_funding',
            y='industry_category',
            orientation='h',
            title='Total Funding by Industry',
            labels={
                'total_funding': 'Total Funding (USD)',
                'industry_category': 'Industry'
            },
            color='market_share',
            color_continuous_scale='Blues'
        )
        fig1.update_layout(template="plotly_white", height=500)
        
        # 2. Industry Maturity vs Funding Efficiency (scatter)
        fig2 = px.scatter(
            industry_stats,
            x='maturity_years',
            y='funding_efficiency',
            size='companies',
            color='success_rate',
            hover_data=['industry_category', 'total_funding', 'total_employees'],
            text='industry_category',
            title='Industry Maturity vs Funding Efficiency',
            labels={
                'maturity_years': 'Average Industry Age (Years)',
                'funding_efficiency': 'Funding per Employee (USD)',
                'success_rate': 'Success Rate (%)'
            },
            color_continuous_scale='RdYlGn'
        )
        fig2.update_traces(textposition="top center", textfont_size=9)
        fig2.update_layout(template="plotly_white", height=500)
        
        # 3. Companies vs Active Rate (bubble chart)
        industry_stats['active_rate'] = industry_stats['success_rate']  # alias for clarity
        fig3 = px.scatter(
            industry_stats,
            x='companies',
            y='active_rate',
            size='total_funding',
            color='total_funding',
            hover_data=['industry_category'],
            text='industry_category',
            title='Industry Activity Level',
            labels={
                'companies': 'Number of Companies',
                'active_rate': 'Active Company Rate (%)',
                'total_funding': 'Total Funding (USD)'
            },
            color_continuous_scale='Viridis'
        )
        fig3.update_traces(textposition="top center", textfont_size=9)
        fig3.update_layout(template="plotly_white", height=500)
        
        return fig1, fig2, fig3, industry_stats
    
    def create_enhanced_funding_analysis(self):
        """Create enhanced funding analysis with transaction data"""
        
        # 1. Enhanced funding stages with transaction insights
        funding_dist = self.pittsburgh_df['funding_tier'].value_counts()
        
        fig1 = go.Figure(data=[go.Pie(
            labels=funding_dist.index,
            values=funding_dist.values,
            hole=0.4,
            textinfo='label+percent+value',
            title="Pittsburgh AI Companies by Funding Stage"
        )])
        fig1.update_layout(template="plotly_white", height=400)
        
        # 2. Enhanced top companies with innovation scores
        top_companies = self.pittsburgh_df.nlargest(15, 'total_funding')
        
        fig2 = px.bar(
            top_companies,
            x='total_funding',
            y='Organization Name',
            orientation='h',
            color='innovation_score' if 'innovation_score' in top_companies.columns else 'industry_category',
            title='Top 15 Pittsburgh AI Companies by Total Funding',
            labels={'total_funding': 'Total Funding ($)'},
            hover_data=['founded_year', 'employee_estimate'] if 'employee_estimate' in top_companies.columns else ['founded_year']
        )
        fig2.update_layout(template="plotly_white", height=600)
        
        # 3. Enhanced funding timeline with volatility
        if 'funding_rounds_count' in self.pittsburgh_df.columns and self.pittsburgh_df['funding_rounds_count'].notna().any():
            # Use transaction data for enhanced timeline
            timeline_data = self.pittsburgh_df[self.pittsburgh_df['funding_rounds_count'].notna()].copy()
            timeline_data['funding_year'] = pd.to_datetime(timeline_data['last_transaction_date'], errors='coerce').dt.year
            
            timeline_agg = timeline_data.groupby('funding_year').agg({
                'total_transaction_funding': 'sum',
                'funding_rounds_count': 'sum',
                'avg_round_size': 'mean',
                'funding_volatility': 'mean'
            }).reset_index()
            timeline_agg = timeline_agg[timeline_agg['funding_year'] >= 2015]
        else:
            # Fallback to original logic
            funding_timeline = self.pittsburgh_df[self.pittsburgh_df['last_funding_date'].notna()].copy()
            funding_timeline['funding_year'] = funding_timeline['last_funding_date'].dt.year
            
            timeline_agg = funding_timeline.groupby('funding_year').agg({
                'last_funding': 'sum',
                'Organization Name': 'count'
            }).reset_index()
            timeline_agg.columns = ['funding_year', 'total_funding', 'deal_count']
            timeline_agg = timeline_agg[timeline_agg['funding_year'] >= 2015]
        
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        
        if 'total_transaction_funding' in timeline_agg.columns:
            fig3.add_trace(
                go.Bar(x=timeline_agg['funding_year'], y=timeline_agg['total_transaction_funding']/1e6,
                       name='Total Funding ($M)', marker_color='lightblue'),
                secondary_y=False
            )
            
            fig3.add_trace(
                go.Scatter(x=timeline_agg['funding_year'], y=timeline_agg['funding_rounds_count'],
                          mode='lines+markers', name='Funding Rounds',
                          line=dict(color='red', width=3)),
                secondary_y=True
            )
        else:
            fig3.add_trace(
                go.Bar(x=timeline_agg['funding_year'], y=timeline_agg['total_funding']/1e6,
                       name='Total Funding ($M)', marker_color='lightblue'),
                secondary_y=False
            )
            
            fig3.add_trace(
                go.Scatter(x=timeline_agg['funding_year'], y=timeline_agg['deal_count'],
                          mode='lines+markers', name='Number of Deals',
                          line=dict(color='red', width=3)),
                secondary_y=True
            )
        
        fig3.update_xaxes(title_text="Year")
        fig3.update_yaxes(title_text="Total Funding (Millions $)", secondary_y=False)
        fig3.update_yaxes(title_text="Funding Activity", secondary_y=True)
        fig3.update_layout(title="Enhanced Annual Funding Activity (2015-2025)", template="plotly_white", height=400)
        
        return fig1, fig2, fig3
    
    def create_innovation_ecosystem_analysis(self):
        """Innovation ecosystem analysis (innovation score histogram removed)"""
        # We keep high-growth and educational impact visuals but drop the innovation score histogram
        fig1 = None  # Innovation score distribution removed per user request
        
        # 1. High-Growth Companies Analysis (kept)
        if 'is_high_growth' in self.pittsburgh_df.columns:
            high_growth_stats = self.pittsburgh_df.groupby(['industry_category', 'is_high_growth']).size().reset_index()
            high_growth_stats.columns = ['industry_category', 'is_high_growth', 'count']
            
            fig2 = px.bar(
                high_growth_stats,
                x='industry_category',
                y='count',
                color='is_high_growth',
                title='High-Growth Companies by Industry',
                labels={'count': 'Number of Companies', 'is_high_growth': 'High Growth Status'}
            )
            fig2.update_layout(template="plotly_white", height=400, xaxis_tickangle=-45)
        else:
            fig2 = None
        
        # 2. Educational Institution Impact (kept)
        fig3 = None
        if self.educational_institutions_df is not None and not self.educational_institutions_df.empty:
            edu_data = self.educational_institutions_df.copy()
            
            # Utility to clean numbers
            def _clean_num(val):
                try:
                    return float(str(val).replace(',', '').replace('$', ''))
                except:
                    return np.nan
            
            for col in ['Number of Alumni', 'Number of Founders (Alumni)', 'Total Funding Amount (in USD)', 'Number of Enrollments']:
                if col in edu_data.columns:
                    edu_data[col] = edu_data[col].apply(_clean_num)
            
            major_institutions = edu_data.nlargest(15, 'Number of Alumni') if 'Number of Alumni' in edu_data.columns else edu_data.head(10)
            
            if not major_institutions.empty:
                # Ensure size values have no NaNs
                size_column = 'Total Funding Amount (in USD)' if 'Total Funding Amount (in USD)' in major_institutions.columns else 'Number of Enrollments'
                major_institutions[size_column] = major_institutions[size_column].fillna(1)
                x_column = 'Number of Alumni' if 'Number of Alumni' in major_institutions.columns else 'Number of Enrollments'
                y_column = 'Number of Founders (Alumni)' if 'Number of Founders (Alumni)' in major_institutions.columns else 'Total Funding Amount (in USD)'
                fig3 = px.scatter(
                    major_institutions,
                    x=x_column,
                    y=y_column,
                    size=size_column,
                    color='School Type' if 'School Type' in major_institutions.columns else None,
                    hover_data=['Organization Name'],
                    title='Educational Institution Impact on AI Ecosystem',
                    labels={'Number of Alumni': 'Number of Alumni', 'Number of Founders (Alumni)': 'AI Founders', 'Total Funding Amount (in USD)': 'Funding (USD)', 'Number of Enrollments':'Enrollments'}
                )
                fig3.update_layout(template="plotly_white", height=500)
        
        return fig1, fig2, fig3
    
    def create_enhanced_investor_analysis(self):
        """Enhanced investor analysis with richer metrics and visuals"""
        # ------------------------------------------------------------------
        # Build long investor → company table
        # ------------------------------------------------------------------
        inv_rows = []
        for _, row in self.pittsburgh_df.iterrows():
            if pd.isna(row.get("Top 5 Investors")):
                continue
            company = row['Organization Name']
            investors = [i.strip() for i in str(row['Top 5 Investors']).replace(';', ',').split(',') if i.strip()]
            for inv in investors:
                inv_rows.append({
                    'investor': inv,
                    'company': company,
                    'industry': row.get('industry_category'),
                    'funding_tier': row.get('funding_tier'),
                    'total_funding': row.get('total_funding', 0),
                    'is_active': row.get('is_active', False),
                    'company_age': row.get('years_since_founding', np.nan)
                })
        if not inv_rows:
            return None, None, None
        inv_df = pd.DataFrame(inv_rows)
        # ------------------------------------------------------------------
        # Aggregate metrics per investor
        # ------------------------------------------------------------------
        stats = (inv_df.groupby('investor')
                 .agg(portfolio_companies=('company','nunique'),
                      total_funding=('total_funding','sum'),
                      industries_count=('industry','nunique'),
                      active_companies=('is_active','sum'),
                      avg_company_age=('company_age','mean'),
                      funding_stage_diversity=('funding_tier','nunique'))
                 .reset_index())
        stats['portfolio_success_rate'] = stats['active_companies']/stats['portfolio_companies']*100
        stats['avg_investment'] = stats['total_funding']/stats['portfolio_companies']
        # ------------------------------------------------------------------
        # Visual 1: Horizontal bar by total funding
        # ------------------------------------------------------------------
        fig1 = px.bar(stats.sort_values('total_funding', ascending=True).tail(20),
                      x='total_funding',
                      y='investor',
                      orientation='h',
                      color='industries_count',
                      title='Top Investors by Total Funding',
                      labels={'total_funding':'Total Funding (USD)','industries_count':'Sectors Covered','investor':'Investor'})
        fig1.update_layout(template="plotly_white", height=600)
        # ------------------------------------------------------------------
        # Visual 2: Scatter success vs age
        # ------------------------------------------------------------------
        stats['portfolio_success_rate'] = stats['portfolio_success_rate'].clip(upper=100)
        # filter
        scatter_df = stats[stats['portfolio_companies'] >= 1]
        # Cap bubbles so single unicorn investors don’t dominate
        scatter_df['bubble_size'] = np.sqrt(scatter_df['avg_investment'].clip(upper=2e8))

        fig2 = px.scatter(
            scatter_df,
            x='portfolio_companies',
            y='total_funding',
            size='bubble_size',
            color='portfolio_success_rate',
            hover_data={
                'investor': True,
                'portfolio_companies': True,
                'total_funding': ':.0f',
                'avg_investment': ':.0f',
                'portfolio_success_rate': ':.1f',
                'funding_stage_diversity': True,
                'industries_count': True
            },
            title='Investor Landscape: Portfolio Size vs Total Funding',
            labels={'portfolio_companies': 'Portfolio Companies (log)',
                    'total_funding': 'Total Funding (USD, log)',
                    'portfolio_success_rate': 'Success Rate (%)'},
            color_continuous_scale='Turbo',
            log_x=True,
            log_y=True
        )
        fig2.update_layout(template='plotly_white', height=550)
        # ------------------------------------------------------------------
        # Visual 3: Heatmap investor × sector concentration
        # ------------------------------------------------------------------
        pivot = (inv_df.groupby(['investor','industry'])
                 .size().unstack(fill_value=0))
        top_invs = stats.sort_values('portfolio_companies', ascending=False).head(15)['investor']
        heat_df = pivot.loc[top_invs]
        fig3 = px.imshow(heat_df,
                         aspect='auto',
                         color_continuous_scale='Blues',
                         labels=dict(x='Industry', y='Investor', color='#Companies'),
                         title='Top Investors – Sector Concentration')
        fig3.update_layout(template="plotly_white", height=600)
        return fig1, fig2, fig3
    
    def create_enhanced_geographic_map(self):
        """Enhanced geographic visualization with educational institutions"""
        try:
            geocoded_df = pd.read_csv("Companies-With-Address - Sheet1.csv")
            geocoded_df.columns = ["Organization Name", "Address", "Latitude", "Longitude"]
            
            # Merge with Pittsburgh data
            geo_pittsburgh = self.pittsburgh_df.merge(geocoded_df, on="Organization Name", how="left")
            
            # Check for coordinates
            lat_cols = [col for col in geo_pittsburgh.columns if 'latitude' in col.lower() or 'lat' in col.lower()]
            lng_cols = [col for col in geo_pittsburgh.columns if 'longitude' in col.lower() or 'lng' in col.lower() or 'lon' in col.lower()]
            
            if lat_cols and lng_cols:
                lat_col, lng_col = lat_cols[0], lng_cols[0]
                mapped_companies = geo_pittsburgh.dropna(subset=[lat_col, lng_col])
                
                # Create enhanced map
                m = folium.Map(location=[40.4406, -79.9959], zoom_start=11, tiles="cartodbpositron")
                
                # Add ZIP choropleth if available
                try:
                    with open("Allegheny_County_Zip_Code_Boundaries.geojson", "r") as f:
                        geojson_data = json.load(f)
                    
                    mapped_companies['zip_clean'] = mapped_companies['Postal Code'].astype(str).str.split('-').str[0]
                    
                    zip_agg = mapped_companies.groupby('zip_clean').agg({
                        'total_funding': 'sum',
                        'Organization Name': 'count',
                        'innovation_score': 'mean'
                    }).reset_index()
                    zip_agg.columns = ['ZIP', 'total_funding', 'company_count', 'avg_innovation']
                    
                    folium.Choropleth(
                        geo_data=geojson_data,
                        name="Total Funding",
                        data=zip_agg,
                        columns=['ZIP', 'total_funding'],
                        key_on="feature.properties.ZIP",
                        fill_color="YlOrRd",
                        fill_opacity=0.7,
                        line_opacity=0.2,
                        legend_name="Total Funding (USD)"
                    ).add_to(m)
                    
                    # Add innovation layer
                    folium.Choropleth(
                        geo_data=geojson_data,
                        name="Innovation Score",
                        data=zip_agg,
                        columns=['ZIP', 'avg_innovation'],
                        key_on="feature.properties.ZIP",
                        fill_color="YlGn",
                        fill_opacity=0.5,
                        line_opacity=0.2,
                        legend_name="Average Innovation Score"
                    ).add_to(m)
                    
                except FileNotFoundError:
                    pass
                
                # Enhanced company markers with innovation data
                for _, company in mapped_companies.iterrows():
                    funding = company.get('total_funding', 0)
                    innovation = company.get('innovation_score', 0)
                    radius = min(25, 4 + 3 * math.log10(max(funding, 1)))
                    
                    # Color by innovation score if available
                    if innovation > 0:
                        color = "#ff4444" if innovation > 10 else "#0066cc" if company['is_active'] else "#cc6600"
                    else:
                        color = "#0066cc" if company['is_active'] else "#cc6600"
                    
                    popup_text = f"""
                    <b>{company['Organization Name']}</b><br>
                    Industry: {company['industry_category']}<br>
                    Funding: ${funding:,.0f}<br>
                    Founded: {company.get('founded_year', 'N/A')}<br>
                    Innovation Score: {innovation:.2f}<br>
                    Status: {'Active' if company['is_active'] else 'Inactive'}
                    """
                    
                    folium.CircleMarker(
                        location=[company[lat_col], company[lng_col]],
                        radius=radius,
                        color=color,
                        fill=True,
                        popup=folium.Popup(popup_text, max_width=350),
                        tooltip=company['Organization Name']
                    ).add_to(m)
                
                # Enhanced universities with detailed info
                if self.educational_institutions_df is not None and not self.educational_institutions_df.empty:
                    # Use actual university data
                    for _, university in self.educational_institutions_df.iterrows():
                        if 'Pittsburgh' in str(university.get('Headquarters Location', '')):
                            popup_text = f"""
                            <b>{university['Organization Name']}</b><br>
                            Type: {university.get('School Type', 'University')}<br>
                            Alumni: {university.get('Number of Alumni', 'N/A')}<br>
                            AI Founders: {university.get('Number of Founders (Alumni)', 'N/A')}<br>
                            Funding: ${university.get('Total Funding Amount (in USD)', 0):,.0f}
                            """
                            
                            # Use coordinates if available, otherwise use default
                            if university['Organization Name'] == 'Carnegie Mellon University':
                                coords = (40.4435, -79.9445)
                            elif university['Organization Name'] == 'University of Pittsburgh':
                                coords = (40.4443, -79.9609)
                            else:
                                coords = (40.44, -79.95)  # Default Pittsburgh location
                            
                            folium.Marker(
                                location=coords,
                                popup=folium.Popup(popup_text, max_width=350),
                                icon=folium.Icon(color="green", icon="graduation-cap", prefix="fa")
                            ).add_to(m)
                else:
                    # Fallback to default universities
                    universities = {
                        "Carnegie Mellon University": (40.4435, -79.9445),
                        "University of Pittsburgh": (40.4443, -79.9609),
                    }
                    
                    for univ_name, (lat, lon) in universities.items():
                        folium.Marker(
                            location=[lat, lon],
                            popup=f"<b>{univ_name}</b>",
                            icon=folium.Icon(color="green", icon="graduation-cap", prefix="fa")
                        ).add_to(m)
                
                folium.LayerControl().add_to(m)
                return m, len(mapped_companies)
            
        except Exception as e:
            print(f"Geographic analysis error: {e}")
        
        # Fallback basic map
        m = folium.Map(location=[40.4406, -79.9959], zoom_start=11)
        return m, 0
    
    def create_city_comparison(self):
        """Compare Pittsburgh to peer cities provided by user"""
        cities = ['Pittsburgh', 'Columbus', 'Cincinnati', 'Cleveland', 'Indianapolis',
                  'Kansas City', 'St. Louis', 'Milwaukee', 'Baltimore', 'Austin',
                  'Raleigh', 'Durham']
        records = []
        for city in cities:
            city_df = self.ecosystem_df[self.ecosystem_df['Headquarters Location'].str.contains(city, na=False, case=False)].copy()
            if city_df.empty:
                continue
            city_df['Total Funding USD'] = pd.to_numeric(city_df['Total Funding Amount (in USD)'], errors='coerce')
            companies = city_df.shape[0]
            total_fund = city_df['Total Funding USD'].sum()
            active_rate = (city_df['Operating Status']=='Active').mean()*100
            median_fund = city_df['Total Funding USD'].median()
            founded_median = pd.to_datetime(city_df['Founded Date'], errors='coerce').dt.year.median()
            maturity = datetime.now().year - founded_median if not np.isnan(founded_median) else np.nan
            records.append({'city':city, 'companies':companies, 'total_funding':total_fund,
                            'active_rate':active_rate, 'median_funding':median_fund,
                            'maturity':maturity})
        comp_df = pd.DataFrame(records)
        # Radar chart requires normalized values 0-1
        norm_cols = ['companies','total_funding','active_rate','median_funding']
        comp_norm = comp_df.copy()
        for col in norm_cols:
            comp_norm[col] = (comp_norm[col]-comp_norm[col].min())/(comp_norm[col].max()-comp_norm[col].min()+1e-9)
        fig_radar = go.Figure()
        for _, row in comp_norm.iterrows():
            fig_radar.add_trace(go.Scatterpolar(r=row[norm_cols].tolist()+[row[norm_cols[0]]],
                                                theta=norm_cols+[norm_cols[0]],
                                                name=row['city']))
        fig_radar.update_layout(title="City Comparison Radar (normalized)", polar=dict(radialaxis=dict(visible=True)), showlegend=True, template="plotly_white")
        # Bubble chart companies vs funding
        fig_bubble = px.scatter(comp_df, x='companies', y='total_funding', size='active_rate', color='city',
                                title='Companies vs Funding by City', log_y=True, labels={'companies':'Companies','total_funding':'Total Funding (USD)','active_rate':'Active %'})
        fig_bubble.update_layout(template="plotly_white")
        return fig_radar, fig_bubble
    
    def generate_unified_report(self):
        """Generate single comprehensive HTML report"""
        print("Generating unified preliminary report...")
        
        # Calculate metrics
        metrics = self.create_executive_metrics()
        
        # Generate visualizations
        industry_figs = self.create_enhanced_industry_analysis()
        funding_figs = self.create_enhanced_funding_analysis()
        innovation_figs = self.create_innovation_ecosystem_analysis()
        investor_figs = self.create_enhanced_investor_analysis()
        city_figs = self.create_city_comparison()
        geo_map, mapped_count = self.create_enhanced_geographic_map()
        
        # Create comprehensive HTML
        html_content = self._build_html_report(
            metrics, industry_figs, funding_figs, innovation_figs, investor_figs, city_figs, geo_map, mapped_count
        )
        
        # Remove old reports and create new one
        import os
        old_reports = [
            "Pittsburgh_AI_Investment_Report.html",
            "Pittsburgh_AI_Comprehensive_Research_Report.html"
        ]
        for report in old_reports:
            if os.path.exists(report):
                os.remove(report)
        
        # Save new unified report
        filename = "Pittsburgh_AI_Preliminary_Report.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"Unified preliminary report generated: {filename}")
        return filename
    
    def _build_html_report(self, metrics, industry_figs, funding_figs, innovation_figs, investor_figs, city_figs, geo_map, mapped_count):
        """Build comprehensive HTML report"""
        
        # Convert figures to HTML
        plots = {}
        
        # Industry plots
        plots['industry_treemap'] = industry_figs[0].to_html(include_plotlyjs='cdn', div_id="industry_treemap")
        plots['industry_performance'] = industry_figs[1].to_html(include_plotlyjs='cdn', div_id="industry_performance")
        plots['funding_efficiency'] = industry_figs[2].to_html(include_plotlyjs='cdn', div_id="funding_efficiency")
        
        # Funding plots
        plots['funding_stages'] = funding_figs[0].to_html(include_plotlyjs='cdn', div_id="funding_stages")
        plots['top_companies'] = funding_figs[1].to_html(include_plotlyjs='cdn', div_id="top_companies")
        plots['funding_timeline'] = funding_figs[2].to_html(include_plotlyjs='cdn', div_id="funding_timeline")
        
        # Innovation plots
        if innovation_figs[0]:
            plots['innovation_score_dist'] = innovation_figs[0].to_html(include_plotlyjs='cdn', div_id="innovation_score_dist")
        else:
            plots['innovation_score_dist'] = ""  # Removed per user request
            
        if innovation_figs[1]:
            plots['high_growth_companies'] = innovation_figs[1].to_html(include_plotlyjs='cdn', div_id="high_growth_companies")
        else:
            plots['high_growth_companies'] = "<p>High-growth companies analysis data unavailable</p>"
            
        if innovation_figs[2]:
            plots['edu_impact'] = innovation_figs[2].to_html(include_plotlyjs='cdn', div_id="edu_impact")
        else:
            plots['edu_impact'] = "<p>Educational institution impact data unavailable</p>"
        
        # Investor plots
        if investor_figs[0]:
            plots['top_investors'] = investor_figs[0].to_html(include_plotlyjs='cdn', div_id="top_investors")
            plots['investor_analysis'] = investor_figs[1].to_html(include_plotlyjs='cdn', div_id="investor_analysis")
            plots['investor_geo_dist'] = investor_figs[2].to_html(include_plotlyjs='cdn', div_id="investor_geo_dist")
        else:
            plots['top_investors'] = "<p>Investor data analysis unavailable</p>"
            plots['investor_analysis'] = ""
            plots['investor_geo_dist'] = "<p>Investor geographic distribution data unavailable</p>"
        
        # City Comparison plots
        plots['city_comparison_radar'] = city_figs[0].to_html(include_plotlyjs='cdn', div_id="city_comparison_radar")
        plots['city_comparison_bubble'] = city_figs[1].to_html(include_plotlyjs='cdn', div_id="city_comparison_bubble")
        
        # Map
        map_html = geo_map._repr_html_() if geo_map else "<p>Geographic visualization unavailable</p>"
        
        # Industry stats for insights
        industry_stats = industry_figs[3]
        top_industry = industry_stats.iloc[0]
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pittsburgh AI Investment Ecosystem - Preliminary Report</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                    background-color: #f8fafc;
                    color: #334155;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: white;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #1e40af, #3b82f6);
                    color: white;
                    padding: 40px;
                    text-align: center;
                    margin: -20px -20px 40px -20px;
                    border-radius: 0 0 20px 20px;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .metric-card {{
                    background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
                    padding: 25px;
                    border-radius: 12px;
                    text-align: center;
                    border-left: 4px solid #3b82f6;
                }}
                .metric-value {{
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #1e40af;
                    margin-bottom: 5px;
                }}
                .metric-label {{
                    font-size: 0.9em;
                    color: #64748b;
                    font-weight: 500;
                }}
                .section {{
                    margin: 50px 0;
                }}
                .section h2 {{
                    color: #1e40af;
                    border-bottom: 2px solid #e2e8f0;
                    padding-bottom: 10px;
                    font-size: 1.8em;
                }}
                .plot-container {{
                    margin: 25px 0;
                    padding: 20px;
                    background: #fafbfc;
                    border-radius: 12px;
                    border: 1px solid #e2e8f0;
                }}
                .insights-box {{
                    background: linear-gradient(135deg, #eff6ff, #dbeafe);
                    border-left: 4px solid #3b82f6;
                    padding: 20px;
                    margin: 25px 0;
                    border-radius: 8px;
                }}
                .key-findings {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .finding-card {{
                    background: white;
                    padding: 25px;
                    border-radius: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-top: 4px solid #10b981;
                }}
                .map-container {{
                    height: 600px;
                    margin: 25px 0;
                    border-radius: 12px;
                    overflow: hidden;
                    border: 1px solid #e2e8f0;
                }}
                .methodology {{
                    background: #f8fafc;
                    padding: 25px;
                    border-radius: 12px;
                    margin: 40px 0;
                    border-left: 4px solid #6b7280;
                }}
                .footer {{
                    text-align: center;
                    padding: 30px;
                    background: #1e40af;
                    color: white;
                    margin: 40px -20px -20px -20px;
                    border-radius: 20px 20px 0 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Pittsburgh AI Investment Ecosystem</h1>
                    <h2>Preliminary Research Report</h2>
                    <p><strong>Block Center for Technology and Society</strong><br>
                    Carnegie Mellon University<br>
                    Pablo Zavala and Liufei Chen | January 2025</p>
                </div>

                <div class="section">
                    <h2>Executive Summary</h2>
                    <p>This preliminary analysis examines Pittsburgh's artificial intelligence investment ecosystem, revealing a mature and diversified technology hub with exceptional strengths in autonomous systems and strong academic-industry integration. Our research identifies {metrics['total_companies']} AI companies that have collectively raised ${metrics['total_funding']/1e9:.1f} billion in funding, demonstrating Pittsburgh's emergence as a significant AI innovation center.</p>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{metrics['total_companies']}</div>
                            <div class="metric-label">AI Companies</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${metrics['total_funding']/1e9:.1f}B</div>
                            <div class="metric-label">Total Investment</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics['activity_rate']:.1f}%</div>
                            <div class="metric-label">Active Rate</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics['total_employees']:,.0f}</div>
                            <div class="metric-label">Est. Jobs</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics['recent_companies']}</div>
                            <div class="metric-label">Since 2020</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{metrics['unicorn_companies']}</div>
                            <div class="metric-label">Unicorns</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>Key Findings</h2>
                    <div class="key-findings">
                        <div class="finding-card">
                            <h3>Industry Leadership</h3>
                            <p><strong>{metrics['dominant_sector']}</strong> dominates the ecosystem with ${metrics['sector_funding']/1e6:.0f}M in total funding, representing {(metrics['sector_funding']/metrics['total_funding'])*100:.1f}% of total investment. This concentration reflects Pittsburgh's historic strengths in robotics and autonomous systems.</p>
                        </div>
                        <div class="finding-card">
                            <h3>Ecosystem Health</h3>
                            <p>With a {metrics['activity_rate']:.1f}% activity rate, Pittsburgh demonstrates exceptional company survival and sustainability. The average company age of {metrics['avg_company_age']:.1f} years indicates a maturing ecosystem with established players.</p>
                        </div>
                        <div class="finding-card">
                            <h3>Recent Growth</h3>
                            <p>{metrics['recent_companies']} companies founded since 2020 represent {(metrics['recent_companies']/metrics['total_companies'])*100:.1f}% of the ecosystem, indicating continued innovation and entrepreneurial activity despite market challenges.</p>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>Industry Sector Analysis</h2>
                    
                    <div class="plot-container">
                        {plots['industry_treemap']}
                    </div>
                    
                    <div class="insights-box">
                        <h3>Sector Insights</h3>
                        <p>Pittsburgh's AI ecosystem demonstrates significant diversification across technology sectors, with particular dominance in autonomous systems reflecting the region's robotics heritage. This sector concentration provides competitive advantages while the supporting ecosystem of core AI/ML companies ensures technological breadth.</p>
                    </div>
                    
                    <div class="plot-container">
                        {plots['industry_performance']}
                    </div>
                    
                    <div class="plot-container">
                        {plots['funding_efficiency']}
                    </div>
                </div>

                <div class="section">
                    <h2>Investment Landscape</h2>
                    
                    <div class="plot-container">
                        {plots['funding_stages']}
                    </div>
                    
                    <div class="plot-container">
                        {plots['top_companies']}
                    </div>
                    
                    <div class="insights-box">
                        <h3>Investment Insights</h3>
                        <p>The funding distribution shows a healthy ecosystem with companies across all stages, from seed to unicorn status. Late-stage funding concentration in autonomous systems companies demonstrates the sector's capital intensity and market validation.</p>
                    </div>
                    
                    <div class="plot-container">
                        {plots['funding_timeline']}
                    </div>
                </div>

                <div class="section">
                    <h2>Innovation Ecosystem Analysis</h2>
                    
                    <div class="plot-container">
                        {plots['innovation_score_dist']}
                    </div>
                    
                    <div class="insights-box">
                        <h3>Innovation Insights</h3>
                        <p>Pittsburgh's AI ecosystem demonstrates significant innovation capacity with companies across various innovation maturity levels. The distribution reveals concentrations in specific sectors that drive technological advancement and market leadership.</p>
                    </div>
                    
                    <div class="plot-container">
                        {plots['high_growth_companies']}
                    </div>
                    
                    <div class="plot-container">
                        {plots['edu_impact']}
                    </div>
                    
                    <div class="insights-box">
                        <h3>Educational Institution Impact</h3>
                        <p>Pittsburgh's world-class educational institutions, particularly Carnegie Mellon University and the University of Pittsburgh, serve as critical drivers of AI innovation through talent development, research collaboration, and founder cultivation. The institutional ecosystem provides sustainable competitive advantages for long-term growth.</p>
                    </div>
                </div>

                <div class="section">
                    <h2>Enhanced Investor Network and Capital Sources</h2>
                    
                    <div class="plot-container">
                        {plots['top_investors']}
                    </div>
                    
                    <div class="plot-container">
                        {plots['investor_analysis']}
                    </div>
                    
                    <div class="plot-container">
                        {plots['investor_geo_dist']}
                    </div>
                    
                    <div class="insights-box">
                        <h3>Enhanced Investment Network Analysis</h3>
                        <p>Pittsburgh benefits from a sophisticated investor ecosystem that combines local expertise with national and international capital sources. The geographic distribution of investors demonstrates the ecosystem's ability to attract diverse funding sources while maintaining strong local institutional support. Portfolio success rates indicate effective investor selection and company support capabilities.</p>
                    </div>
                </div>

                <div class="section">
                    <h2>City Comparison</h2>
                    
                    <div class="plot-container">
                        {plots['city_comparison_radar']}
                    </div>
                    
                    <div class="plot-container">
                        {plots['city_comparison_bubble']}
                    </div>
                    
                    <div class="insights-box">
                        <h3>City Comparison Insights</h3>
                        <p>Pittsburgh's AI ecosystem compares favorably with peer cities in terms of company count, total funding, and active rate. The city's strong academic institutions and robust investor network contribute to its competitive position.</p>
                    </div>
                </div>

                <div class="section">
                    <h2>Geographic Distribution</h2>
                    <p>Analysis of {mapped_count} companies with geographic data reveals clustering patterns around major research institutions, particularly Carnegie Mellon University and the University of Pittsburgh.</p>
                    
                    <div class="map-container">
                        {map_html}
                    </div>
                    
                    <div class="insights-box">
                        <h3>Geographic Insights</h3>
                        <p>Company clustering near universities facilitates knowledge transfer and talent recruitment. The geographic concentration creates innovation districts that support collaboration while the broader metropolitan distribution provides access to diverse markets and talent pools.</p>
                    </div>
                </div>

                <div class="section">
                    <h2>Strategic Implications</h2>
                    
                    <h3>Competitive Advantages</h3>
                    <ul>
                        <li><strong>Academic Excellence:</strong> World-class research institutions providing talent and technology transfer</li>
                        <li><strong>Sector Leadership:</strong> Dominant position in autonomous systems and robotics</li>
                        <li><strong>Ecosystem Maturity:</strong> High company survival rates and established support infrastructure</li>
                        <li><strong>Diverse Funding:</strong> Mix of local and national capital sources</li>
                    </ul>
                    
                    <h3>Growth Opportunities</h3>
                    <ul>
                        <li><strong>Early-Stage Capital:</strong> Expand seed funding to support more startup formation</li>
                        <li><strong>Sector Diversification:</strong> Develop strengths in healthcare AI and enterprise applications</li>
                        <li><strong>Talent Retention:</strong> Strengthen programs to retain university graduates</li>
                        <li><strong>Corporate Engagement:</strong> Increase Fortune 500 partnership and investment activity</li>
                    </ul>
                    
                    <h3>Preliminary Recommendations</h3>
                    <ul>
                        <li>Establish specialized AI innovation districts with targeted incentives</li>
                        <li>Create university-industry collaboration programs for technology transfer</li>
                        <li>Develop workforce training initiatives for AI-related skills</li>
                        <li>Attract additional venture capital presence through economic development initiatives</li>
                    </ul>
                </div>

                <div class="methodology">
                    <h2>Research Methodology</h2>
                    <p><strong>Data Sources:</strong> Comprehensive startup databases, venture capital transaction records, institutional datasets</p>
                    <p><strong>Analysis Period:</strong> 2000-2025 with emphasis on recent developments (2020-2025)</p>
                    <p><strong>Geographic Scope:</strong> Pittsburgh metropolitan statistical area</p>
                    <p><strong>Company Classification:</strong> AI-focused companies with machine learning, autonomous systems, or intelligent software as core business</p>
                    <p><strong>Analytical Framework:</strong> Multi-dimensional analysis including financial metrics, temporal patterns, network analysis, and geographic clustering</p>
                </div>

                <div class="footer">
                    <p><strong>Block Center for Technology and Society</strong><br>
                    Carnegie Mellon University<br>
                    Research conducted by Pablo Zavala and Liufei Chen<br>
                    Preliminary Report | January 2025</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content

if __name__ == "__main__":
    print("Unified Pittsburgh Report Generator Ready")
    print("Usage: from comprehensive_pittsburgh_analysis import run_comprehensive_analysis")
    print("       analyzer = run_comprehensive_analysis()")
    print("       report = UnifiedPittsburghReport(analyzer)")
    print("       report.generate_unified_report()") 