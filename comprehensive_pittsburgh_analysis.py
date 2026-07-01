# Pittsburgh AI Investment Ecosystem: Comprehensive Research Analysis
# Block Center, Carnegie Mellon University
# Authors: Pablo Zavala and Liufei Chen
# Date: January 2025

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import folium
from folium.plugins import MarkerCluster, HeatMap
import warnings
from datetime import datetime
import json
import math
from collections import Counter
import itertools

warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

print("="*80)
print("PITTSBURGH AI INVESTMENT ECOSYSTEM: COMPREHENSIVE ANALYSIS")
print("Block Center, Carnegie Mellon University")
print("="*80)
print(f"Analysis initiated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =============================================================================
# 1. ENHANCED DATA LOADING AND PREPARATION
# =============================================================================

class PittsburghAnalyzer:
    """Comprehensive analysis framework for Pittsburgh AI ecosystem with enhanced data sources"""
    
    def __init__(self):
        self.ecosystem_df = None
        self.pittsburgh_df = None
        self.geocoded_df = None
        self.investor_profiles_df = None
        self.funding_transactions_df = None
        self.educational_institutions_df = None
        self.industry_mappings = self._define_industry_categories()
        
    def _define_industry_categories(self):
        """Return mapping of high-level categories to lists of keyword tokens"""
        return {
            # Core AI / Machine Learning
            'Core AI/ML': [
                'artificial intelligence', 'machine learning', 'deep learning', 'computer vision',
                'natural language processing', 'predictive analytics', 'data science', 'neural network'
            ],
            # Autonomous Systems & Robotics
            'Autonomous Systems': [
                'autonomous vehicle', 'self-driving', 'robotics', 'drone', 'unmanned', 'automation',
                'industrial automation'
            ],
            # Healthcare & Life Sciences
            'Healthcare AI': [
                'healthcare', 'medical', 'biotech', 'pharmaceutical', 'digital health', 'medical device',
                'precision medicine', 'drug discovery', 'life science'
            ],
            # Enterprise Software & Services
            'Enterprise Software': [
                'enterprise software', 'saas', 'business intelligence', 'workflow automation',
                'customer service', 'human resources', 'productivity', 'collaboration', 'crm'
            ],
            # Financial Technology
            'Fintech': [
                'fintech', 'financial service', 'payment', 'lending', 'insurance', 'insurtech',
                'wealth management', 'trading', 'blockchain'
            ],
            # Security & Privacy
            'Cybersecurity': [
                'cybersecurity', 'network security', 'data security', 'privacy', 'fraud detection',
                'identity management', 'compliance'
            ],
            # Infrastructure & Hardware
            'AI Infrastructure': [
                'semiconductor', 'cloud computing', 'edge computing', 'hardware', 'chip', 'processor', 'gpu'
            ],
            # Applied AI Verticals
            'Applied AI': [
                'logistics', 'supply chain', 'agriculture', 'energy', 'manufacturing', 'retail',
                'telecommunication', 'real estate', 'transportation'
            ]
        }
    
    def load_data(self):
        """Load all available datasets with enhanced error handling"""
        print("Loading comprehensive datasets...")
        
        # Core company datasets
        try:
            self.ecosystem_df = pd.concat([
                pd.read_csv("austin-companies-7-18-2025.csv"),
                pd.read_csv("all-minus-austin-companies-7-18-2025.csv")
            ], ignore_index=True)
            print(f"✓ Loaded {len(self.ecosystem_df)} companies from ecosystem data")
        except Exception as e:
            print(f"Error loading ecosystem data: {e}")
            return False
        
        # Geographic data
        try:
            self.geocoded_df = pd.read_csv("Companies-With-Address - Sheet1.csv")
            self.geocoded_df.columns = ["Organization Name", "Address", "Latitude", "Longitude"]
            print(f"✓ Loaded geographic data for {len(self.geocoded_df)} companies")
        except Exception as e:
            print(f"Warning: Geographic data not available: {e}")
        
        # Enhanced datasets
        try:
            # Load investor profiles (sample for memory efficiency)
            self.investor_profiles_df = pd.read_csv("investor_profiles_unique (1).csv", nrows=50000)
            print(f"✓ Loaded {len(self.investor_profiles_df)} investor profiles")
        except Exception as e:
            print(f"Warning: Investor profiles not available: {e}")
        
        try:
            # Load funding transactions (sample for memory efficiency)
            self.funding_transactions_df = pd.read_csv("funding_transactions_full.csv", nrows=100000)
            print(f"✓ Loaded {len(self.funding_transactions_df)} funding transactions")
        except Exception as e:
            print(f"Warning: Funding transactions not available: {e}")
        
        try:
            # Load educational institutions
            self.educational_institutions_df = pd.read_csv("pittsburgh-schools-7-23-2025.csv")
            print(f"✓ Loaded {len(self.educational_institutions_df)} educational institutions")
        except Exception as e:
            print(f"Warning: Educational institutions data not available: {e}")
        
        return True
    
    def process_pittsburgh_data(self):
        """Enhanced Pittsburgh data processing with additional insights"""
        print("Processing Pittsburgh data with enhanced analytics...")
        
        # Filter Pittsburgh companies
        pittsburgh_companies = self.ecosystem_df[
            self.ecosystem_df['Headquarters Location'].str.contains('Pittsburgh', na=False, case=False)
        ].copy()
        
        print(f"Found {len(pittsburgh_companies)} Pittsburgh AI companies")
        
        # Enhanced data processing
        self.pittsburgh_df = pittsburgh_companies.copy()
        self._clean_financial_data()
        self._process_temporal_data()
        self._parse_employee_data()
        self._process_funding_stages()
        self._categorize_industries()
        self._enhance_with_transaction_data()
        self._calculate_company_metrics()
        
        print(f"✓ Processed Pittsburgh dataset: {len(self.pittsburgh_df)} companies")
        return True
    
    def _clean_financial_data(self):
        """Clean monetary columns"""
        def clean_monetary(series):
            if series.dtype == 'object':
                cleaned = (
                    series.astype(str)
                    .str.replace(r'[\$,]', '', regex=True)
                    .str.replace(r'[kK]$', '000', regex=True)
                    .str.replace(r'[mM]$', '000000', regex=True)
                    .str.replace(r'[bB]$', '000000000', regex=True)
                )
                return pd.to_numeric(cleaned, errors='coerce')
            return series
        
        self.pittsburgh_df['total_funding'] = clean_monetary(self.pittsburgh_df['Total Funding Amount (in USD)'])
        self.pittsburgh_df['last_funding'] = clean_monetary(self.pittsburgh_df['Last Funding Amount (in USD)'])
        
    def _process_temporal_data(self):
        """Process date and temporal information"""
        self.pittsburgh_df['founded_date'] = pd.to_datetime(
            self.pittsburgh_df['Founded Date'], errors='coerce'
        )
        self.pittsburgh_df['founded_year'] = self.pittsburgh_df['founded_date'].dt.year
        self.pittsburgh_df['company_age'] = 2025 - self.pittsburgh_df['founded_year']
        
        self.pittsburgh_df['last_funding_date'] = pd.to_datetime(
            self.pittsburgh_df['Last Funding Date'], errors='coerce'
        )
        self.pittsburgh_df['last_funding_year'] = self.pittsburgh_df['last_funding_date'].dt.year
        
    def _categorize_industries(self):
        """Categorize industries using comprehensive mapping"""
        def categorize_company_industries(industries_str):
            if pd.isna(industries_str):
                return []
            industries_str = str(industries_str).lower()
            matched = []
            for category, keywords in self.industry_mappings.items():
                for kw in keywords:
                    if kw in industries_str:
                        matched.append(category)
                        break
            return matched if matched else ['Other Technology']
        
        self.pittsburgh_df['industry_list'] = self.pittsburgh_df['Industries'].apply(categorize_company_industries)
        # Legacy single-label column so downstream code (executive metrics, etc.) still works
        self.pittsburgh_df['industry_category'] = self.pittsburgh_df['industry_list'].apply(
            lambda lst: lst[0] if isinstance(lst, list) and len(lst) > 0 else 'Other Technology'
        )
        
        # Explode into long format with funding weighting
        base_cols = self.pittsburgh_df.drop(columns=['industry_category']).copy()
        exploded = base_cols.explode('industry_list').rename(columns={'industry_list':'industry_category'}).copy()
        exploded['category_count'] = exploded.groupby('Organization Name')['industry_category'].transform('count')
        exploded['funding_weighted'] = exploded['total_funding'] / exploded['category_count']
        exploded['employee_estimate_weighted'] = exploded['employee_estimate'].fillna(0) / exploded['category_count']
        self.industry_long_df = exploded
        
    def _parse_employee_data(self):
        """Parse employee range strings"""
        def parse_employee_range(emp_str):
            if pd.isna(emp_str):
                return np.nan
            
            emp_mapping = {
                "1-10": 5.5, "11-50": 30.5, "51-100": 75.5, "101-250": 175.5,
                "251-500": 375.5, "501-1000": 750.5, "1001-5000": 3000.5,
                "5001-10000": 7500.5, "10000+": 12000
            }
            
            return emp_mapping.get(str(emp_str), np.nan)
        
        self.pittsburgh_df['employee_estimate'] = self.pittsburgh_df['Number of Employees'].apply(
            parse_employee_range
        )
        
    def _process_funding_stages(self):
        """Categorize funding stages"""
        def categorize_funding_stage(funding_amount):
            if pd.isna(funding_amount) or funding_amount == 0:
                return 'Undisclosed'
            elif funding_amount >= 1e9:
                return 'Unicorn ($1B+)'
            elif funding_amount >= 100e6:
                return 'Scaleup ($100M-$1B)'
            elif funding_amount >= 10e6:
                return 'Growth ($10M-$100M)'
            elif funding_amount >= 1e6:
                return 'Early Stage ($1M-$10M)'
            else:
                return 'Seed (<$1M)'
        
        self.pittsburgh_df['funding_tier'] = self.pittsburgh_df['total_funding'].apply(
            categorize_funding_stage
        )
        
        # Status processing
        self.pittsburgh_df['is_active'] = self.pittsburgh_df['Operating Status'] == 'Active'

    def _enhance_with_transaction_data(self):
        """Enhance Pittsburgh companies with detailed transaction data"""
        if self.funding_transactions_df is not None:
            print("Enhancing with transaction-level data...")
            
            # Filter Pittsburgh transactions
            pgh_transactions = self.funding_transactions_df[
                self.funding_transactions_df['Organization Location'].str.contains('Pittsburgh', na=False, case=False)
            ].copy()
            
            if len(pgh_transactions) > 0:
                # Calculate transaction metrics per company
                transaction_metrics = pgh_transactions.groupby('Organization Name').agg({
                    'Money Raised (in USD)': ['sum', 'count', 'mean', 'std'],
                    'Announced Date': ['min', 'max'],
                    'Number of Investors': ['sum', 'mean'],
                    'Funding Type': lambda x: ', '.join(x.unique())
                }).round(2)
                
                # Flatten column names
                transaction_metrics.columns = [
                    'total_transaction_funding', 'funding_rounds_count', 'avg_round_size', 'funding_volatility',
                    'first_funding_date', 'last_transaction_date', 'total_unique_investors', 'avg_investors_per_round',
                    'funding_types_history'
                ]
                
                # Merge with Pittsburgh companies
                self.pittsburgh_df = self.pittsburgh_df.merge(
                    transaction_metrics, 
                    left_on='Organization Name', 
                    right_index=True, 
                    how='left'
                )
                
                print(f"✓ Enhanced {len(transaction_metrics)} companies with transaction data")
    
    def _calculate_company_metrics(self):
        """Calculate advanced company performance metrics"""
        print("Calculating advanced company metrics...")
        
        # Funding efficiency metrics
        self.pittsburgh_df['funding_per_employee'] = (
            self.pittsburgh_df['total_funding'] / self.pittsburgh_df['employee_estimate']
        ).replace([np.inf, -np.inf], np.nan)
        
        # Growth metrics
        current_year = datetime.now().year
        self.pittsburgh_df['years_since_founding'] = current_year - self.pittsburgh_df['founded_year']
        self.pittsburgh_df['funding_velocity'] = (
            self.pittsburgh_df['total_funding'] / self.pittsburgh_df['years_since_founding']
        ).replace([np.inf, -np.inf], np.nan)
        
        # Market position metrics
        self.pittsburgh_df['is_unicorn'] = self.pittsburgh_df['total_funding'] >= 1e9
        self.pittsburgh_df['is_high_growth'] = (
            (self.pittsburgh_df['years_since_founding'] <= 10) & 
            (self.pittsburgh_df['total_funding'] >= 10e6)
        )
        
        # Innovation metrics (based on founding recency and funding)
        self.pittsburgh_df['innovation_score'] = (
            (self.pittsburgh_df['total_funding'] / 1e6) * 
            (1 / (self.pittsburgh_df['years_since_founding'] + 1))
        ).fillna(0)

# =============================================================================
# 2. ENHANCED ANALYTICS MODULES
# =============================================================================

class EcosystemAnalytics:
    """Enhanced ecosystem-wide analysis with multi-source data integration"""
    
    @staticmethod
    def calculate_ecosystem_metrics(df):
        """Calculate comprehensive ecosystem KPIs with enhanced metrics"""
        print("Calculating enhanced ecosystem metrics...")
        
        # Core metrics
        total_companies = len(df)
        active_companies = df['is_active'].sum()
        total_funding = df['total_funding'].sum()
        avg_funding = df['total_funding'].mean()
        median_funding = df['total_funding'].median()
        
        # Enhanced metrics
        unicorn_companies = (df['total_funding'] >= 1e9).sum()
        decacorn_companies = (df['total_funding'] >= 10e9).sum()
        recent_companies = (df['founded_year'] >= 2020).sum()
        high_growth_companies = df['is_high_growth'].sum() if 'is_high_growth' in df.columns else 0
        
        # Temporal metrics
        avg_company_age = df['years_since_founding'].mean() if 'years_since_founding' in df.columns else None
        funding_per_year = total_funding / max(1, datetime.now().year - df['founded_year'].min())
        
        # Employment metrics  
        total_employees = df['employee_estimate'].sum()
        avg_employees = df['employee_estimate'].mean()
        
        # Innovation metrics
        avg_innovation_score = df['innovation_score'].mean() if 'innovation_score' in df.columns else 0
        
        # Financial efficiency
        funding_efficiency = total_funding / total_employees if total_employees > 0 else 0
        
        return {
            'total_companies': total_companies,
            'active_companies': active_companies,
            'activity_rate': (active_companies / total_companies * 100) if total_companies > 0 else 0,
            'total_funding': total_funding,
            'avg_funding': avg_funding,
            'median_funding': median_funding,
            'total_employees': total_employees,
            'avg_employees': avg_employees,
            'unicorn_companies': unicorn_companies,
            'decacorn_companies': decacorn_companies,
            'recent_companies': recent_companies,
            'high_growth_companies': high_growth_companies,
            'avg_company_age': avg_company_age,
            'funding_per_year': funding_per_year,
            'avg_innovation_score': avg_innovation_score,
            'funding_efficiency': funding_efficiency
        }
    
    @staticmethod
    def industry_analysis(df):
        """Enhanced industry sector analysis"""
        print("Performing enhanced industry analysis...")
        
        industry_stats = df.groupby('industry_category').agg({
            'Organization Name': 'count',
            'total_funding': ['sum', 'mean', 'median'],
            'employee_estimate': ['sum', 'mean'],
            'is_active': 'sum',
            'founded_year': ['min', 'max', 'mean'],
            'innovation_score': 'mean',
            'funding_per_employee': 'mean'
        }).round(2)
        
        # Flatten column names
        industry_stats.columns = [
            'companies', 'total_funding', 'avg_funding', 'median_funding',
            'total_employees', 'avg_employees', 'active_companies',
            'earliest_founded', 'latest_founded', 'avg_founding_year',
            'avg_innovation_score', 'avg_funding_efficiency'
        ]
        
        # Calculate additional metrics
        industry_stats['market_share'] = (industry_stats['total_funding'] / industry_stats['total_funding'].sum() * 100)
        industry_stats['success_rate'] = (industry_stats['active_companies'] / industry_stats['companies'] * 100)
        industry_stats['maturity_years'] = datetime.now().year - industry_stats['avg_founding_year']
        
        # Reset index to make industry_category a column
        industry_stats = industry_stats.reset_index()
        
        return industry_stats.sort_values('total_funding', ascending=False)
    
    @staticmethod
    def temporal_analysis(df):
        """Enhanced temporal analysis with funding velocity"""
        print("Performing enhanced temporal analysis...")
        
        temporal_data = df.groupby('founded_year').agg({
            'Organization Name': 'count',
            'total_funding': ['sum', 'mean'],
            'employee_estimate': 'sum',
            'is_active': 'sum',
            'innovation_score': 'mean'
        }).round(2)
        
        temporal_data.columns = ['companies_founded', 'total_funding', 'avg_funding', 'employees_added', 'active_companies', 'avg_innovation']
        temporal_data = temporal_data.reset_index()
        temporal_data['year'] = temporal_data['founded_year']
        
        # Calculate cumulative metrics
        temporal_data = temporal_data.sort_values('year')
        temporal_data['cumulative_companies'] = temporal_data['companies_founded'].cumsum()
        temporal_data['cumulative_funding'] = temporal_data['total_funding'].cumsum()
        temporal_data['cumulative_employees'] = temporal_data['employees_added'].cumsum()
        
        # Growth rates
        temporal_data['company_growth_rate'] = temporal_data['companies_founded'].pct_change() * 100
        temporal_data['funding_growth_rate'] = temporal_data['total_funding'].pct_change() * 100
        
        return temporal_data

    @staticmethod
    def funding_velocity_analysis(df):
        """Analyze time to funding and funding patterns"""
        print("Analyzing funding velocity patterns...")
        
        # Filter companies with funding data
        funded_companies = df[df['total_funding'] > 0].copy()
        
        if 'last_funding_date' in funded_companies.columns:
            funded_companies['time_to_last_funding'] = (
                funded_companies['last_funding_date'] - funded_companies['founded_date']
            ).dt.days / 365.25
            
            velocity_analysis = funded_companies.groupby('industry_category').agg({
                'time_to_last_funding': ['mean', 'median', 'std'],
                'total_funding': ['mean', 'sum'],
                'funding_velocity': ['mean', 'median']
            }).round(2)
            
            velocity_analysis.columns = [
                'avg_time_to_funding', 'median_time_to_funding', 'funding_time_volatility',
                'avg_total_funding', 'sector_total_funding', 'avg_funding_velocity', 'median_funding_velocity'
            ]
            
            return velocity_analysis.reset_index()
        
        return pd.DataFrame()

class NetworkAnalytics:
    """Enhanced network analysis with investor profiles and transaction data"""
    
    @staticmethod
    def create_investor_network(df):
        """Enhanced investor network with better parsing and validation"""
        print("Creating enhanced investor network...")
        
        # Parse investors with improved handling
        investor_edges = []
        
        for _, company in df.iterrows():
            if pd.notna(company.get('Top 5 Investors', '')):
                company_name = company['Organization Name']
                funding = company.get('total_funding', 0)
                industry = company.get('industry_category', 'Unknown')
                
                # Parse investors - handle both ; and , separators
                investors_str = str(company['Top 5 Investors'])
                investors = [inv.strip() for inv in investors_str.replace(';', ',').split(',') if inv.strip()]
                
                # Filter out invalid entries
                valid_investors = [inv for inv in investors if len(inv) > 2 and not inv.lower() in ['nan', 'none', 'n/a']]
                
                for investor in valid_investors:
                    investor_edges.append({
                        'investor': investor,
                        'company': company_name,
                        'funding': funding,
                        'industry': industry,
                        'is_active': company.get('is_active', True)
                    })
        
        if not investor_edges:
            print("No valid investor relationships found")
            return nx.Graph(), pd.DataFrame()
        
        edges_df = pd.DataFrame(investor_edges)
        
        # Create network graph
        G = nx.Graph()
        
        # Add investor nodes
        investor_stats = edges_df.groupby('investor').agg({
            'company': 'nunique',
            'funding': 'sum',
            'industry': lambda x: len(x.unique()),
            'is_active': 'sum'
        }).reset_index()
        
        for _, investor in investor_stats.iterrows():
            G.add_node(investor['investor'], 
                      node_type='investor',
                      portfolio_size=investor['company'],
                      total_funding=investor['funding'],
                      industries=investor['industry'])
        
        # Add company nodes and edges
        for _, edge in edges_df.iterrows():
            if not G.has_node(edge['company']):
                G.add_node(edge['company'], 
                          node_type='company',
                          funding=edge['funding'],
                          industry=edge['industry'])
            
            G.add_edge(edge['investor'], edge['company'], 
                      funding=edge['funding'],
                      industry=edge['industry'])
        
        print(f"✓ Created network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        return G, edges_df
    
    @staticmethod
    def analyze_co_investment_patterns(df):
        """Enhanced co-investment analysis"""
        print("Analyzing co-investment patterns...")
        
        company_investors = {}
        
        for _, company in df.iterrows():
            if pd.notna(company.get('Top 5 Investors', '')):
                investors = [inv.strip() for inv in str(company['Top 5 Investors']).replace(';', ',').split(',')]
                valid_investors = [inv for inv in investors if len(inv) > 2 and not inv.lower() in ['nan', 'none', 'n/a']]
                if len(valid_investors) > 1:
                    company_investors[company['Organization Name']] = valid_investors
        
        # Find co-investment pairs
        co_investments = []
        for company, investors in company_investors.items():
            for i, inv1 in enumerate(investors):
                for inv2 in investors[i+1:]:
                    co_investments.append({
                        'investor1': inv1,
                        'investor2': inv2,
                        'company': company
                    })
        
        if co_investments:
            co_invest_df = pd.DataFrame(co_investments)
            co_invest_counts = co_invest_df.groupby(['investor1', 'investor2']).size().reset_index()
            co_invest_counts.columns = ['investor1', 'investor2', 'co_investments']
            return co_invest_counts.sort_values('co_investments', ascending=False)
        
        return pd.DataFrame()
    
    @staticmethod
    def get_investor_portfolio_stats(df):
        """Enhanced investor portfolio statistics with transaction data"""
        print("Calculating enhanced investor portfolio statistics...")
        
        investor_data = []
        
        for _, company in df.iterrows():
            if pd.notna(company.get('Top 5 Investors', '')):
                company_name = company['Organization Name']
                funding = company.get('total_funding', 0)
                industry = company.get('industry_category', 'Unknown')
                is_active = company.get('is_active', True)
                
                investors_str = str(company['Top 5 Investors'])
                investors = [inv.strip() for inv in investors_str.replace(';', ',').split(',')]
                valid_investors = [inv for inv in investors if len(inv) > 2 and not inv.lower() in ['nan', 'none', 'n/a']]
                
                # Assume equal participation if co-investing
                funding_per_investor = funding / len(valid_investors) if valid_investors else 0
                
                for investor in valid_investors:
                    investor_data.append({
                        'investor': investor,
                        'company': company_name,
                        'funding_share': funding_per_investor,
                        'industry': industry,
                        'is_active': is_active
                    })
        
        if not investor_data:
            return pd.DataFrame()
        
        investor_df = pd.DataFrame(investor_data)
        
        # Calculate portfolio statistics
        portfolio_stats = investor_df.groupby('investor').agg({
            'company': 'nunique',
            'funding_share': 'sum',
            'industry': lambda x: len(x.unique()),
            'is_active': 'sum'
        }).reset_index()
        
        portfolio_stats.columns = ['investor', 'portfolio_companies', 'total_funding', 'industries_count', 'active_companies']
        
        # Calculate additional metrics
        portfolio_stats['avg_investment'] = portfolio_stats['total_funding'] / portfolio_stats['portfolio_companies']
        portfolio_stats['portfolio_success_rate'] = (portfolio_stats['active_companies'] / portfolio_stats['portfolio_companies'] * 100)
        
        return portfolio_stats.sort_values('portfolio_companies', ascending=False)

    @staticmethod
    def analyze_investor_geographic_distribution(investor_profiles_df):
        """Analyze geographic distribution of investors"""
        if investor_profiles_df is None or investor_profiles_df.empty:
            return pd.DataFrame()
        
        print("Analyzing investor geographic distribution...")
        
        # Extract location data
        investor_locations = investor_profiles_df['Location'].value_counts().head(20)
        
        # Analyze investment patterns by location
        location_analysis = investor_profiles_df.groupby('Location').agg({
            'Number of Investments': ['sum', 'mean'],
            'Number of Portfolio Organizations': ['sum', 'mean'],
            'Total Funding Amount (in USD)': ['sum', 'mean']
        }).round(2)
        
        return location_analysis

# =============================================================================
# 3. ENHANCED INTEGRATION AND RUNNER
# =============================================================================

def run_comprehensive_analysis():
    """Enhanced main analysis runner with error handling"""
    print("Starting comprehensive Pittsburgh AI ecosystem analysis...")
    
    # Initialize analyzer
    analyzer = PittsburghAnalyzer()
    
    # Load data
    if not analyzer.load_data():
        print("❌ Failed to load core data. Exiting.")
        return None
    
    # Process Pittsburgh data
    if not analyzer.process_pittsburgh_data():
        print("❌ Failed to process Pittsburgh data. Exiting.")
        return None
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE - Enhanced Pittsburgh AI Ecosystem Data Ready")
    print("="*60)
    print(f"✓ Companies analyzed: {len(analyzer.pittsburgh_df)}")
    print(f"✓ Data sources integrated: {3 + (1 if analyzer.investor_profiles_df is not None else 0) + (1 if analyzer.funding_transactions_df is not None else 0)}")
    print(f"✓ Enhanced metrics available: {len([col for col in analyzer.pittsburgh_df.columns if col in ['innovation_score', 'funding_velocity', 'funding_per_employee']])}")
    
    return analyzer

if __name__ == "__main__":
    print("Enhanced Pittsburgh AI Analysis Framework")
    print("Usage: analyzer = run_comprehensive_analysis()")
    analyzer = run_comprehensive_analysis() 