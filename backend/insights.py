import pandas as pd
import numpy as np

def identify_columns(df):
    """
    Identify which columns correspond to Income, Spending, Frequency based on names.
    """
    cols = df.columns
    mapping = {
        'income': None,
        'spending': None,
        'frequency': None
    }
    
    for c in cols:
        lower_c = c.lower()
        if 'income' in lower_c:
            mapping['income'] = c
        elif 'spending' in lower_c or 'score' in lower_c:
            # Prefer 'Total Spending' or 'Spending Score'
            # If both exist, maybe use Total Spending for value calculation?
            # Prompt lists 'Spending Score' and 'Total Spending'.
            # Usually Spending Score is for segmentation, Total Spending for value.
            # Let's prioritize 'Total Spending' for value, 'Spending Score' for nature?
            # Actually, clusters are formed on both usually.
            # Let's just pick one representing spending behavior.
            if mapping['spending'] is None:
                mapping['spending'] = c
            elif 'total' in lower_c:
                mapping['spending'] = c # prefer total spending
        elif 'frequency' in lower_c:
            mapping['frequency'] = c
            
    return mapping

def generate_cluster_insights(df, cluster_col='Cluster'):
    """
    Generate insights for each cluster.
    Returns a dict of cluster_id -> {label, description, stats}
    """
    mapping = identify_columns(df)
    income_col = mapping['income']
    spending_col = mapping['spending']
    freq_col = mapping['frequency']
    
    # Calculate means
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    stats = df.groupby(cluster_col)[numeric_cols].mean()
    
    insights = {}
    
    # Global means for comparison
    global_means = df[numeric_cols].mean()
    
    for cluster_id in stats.index:
        cluster_stats = stats.loc[cluster_id]
        
        # Determine label based on relative values
        label = "Standard Customer"
        desc_parts = []
        
        # Spending logic
        spending_val = cluster_stats.get(spending_col, 0) if spending_col else 0
        global_spending = global_means.get(spending_col, 0) if spending_col else 0
        
        # Income logic
        income_val = cluster_stats.get(income_col, 0) if income_col else 0
        global_income = global_means.get(income_col, 0) if income_col else 0
        
        # Freq logic
        freq_val = cluster_stats.get(freq_col, 0) if freq_col else 0
        global_freq = global_means.get(freq_col, 0) if freq_col else 0
        
        is_high_spending = spending_val > global_spending * 1.1
        is_low_spending = spending_val < global_spending * 0.9
        
        is_high_income = income_val > global_income * 1.1
        is_low_income = income_val < global_income * 0.9
        
        if is_high_spending and is_high_income:
            label = "High Value Customer"
            desc_parts.append("High income and high spending.")
        elif is_low_spending and is_high_income:
            label = "Potential Saver" # Or "High Risk" if we consider churn risk?
            # Prompt says "High Risk Customers" based on Spending, Income, Frequency.
            # Usually Low Spending + High Income = High Potential/Savers.
            # High Spending + Low Income = "Careless" / "High Risk" (credit risk).
            desc_parts.append("High income but low spending.")
        elif is_high_spending and is_low_income:
            label = "High Risk Customer" # Spending beyond means?
            desc_parts.append("Low income but high spending.")
        elif is_low_spending and is_low_income:
            label = "Low Value Customer"
            desc_parts.append("Low income and low spending.")
        else:
            label = "Medium Value Customer"
            desc_parts.append("Average income and spending.")
            
        if freq_col:
            if freq_val > global_freq * 1.1:
                desc_parts.append("Frequent buyer.")
            elif freq_val < global_freq * 0.9:
                desc_parts.append("Infrequent buyer.")
                
        # Construct full description
        description = f"Cluster {cluster_id} contains {label.lower()}s. {' '.join(desc_parts)}"
        
        insights[int(cluster_id)] = {
            "label": label,
            "description": description,
            "stats": cluster_stats.to_dict()
        }
        
    return insights
