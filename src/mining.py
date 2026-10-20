import sqlite3
from itertools import combinations
from collections import Counter
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from .config import DB_PATH, OUTPUTS


def eng():
    return sqlite3.connect(DB_PATH)


def rfm():
    q = """
        WITH x AS (
            SELECT f.customer_key, MAX(d.full_date) AS last_purchase,
                   COUNT(DISTINCT f.order_id) AS frequency,
                   SUM(f.sales_amount) AS monetary
            FROM fact_sales f JOIN dim_date d ON d.date_key=f.date_key
            GROUP BY f.customer_key
        ), anchor AS (SELECT MAX(full_date) AS max_date FROM dim_date)
        SELECT c.customer_id, c.name,
               CAST(julianday(anchor.max_date)-julianday(x.last_purchase) AS INTEGER) AS recency,
               x.frequency, ROUND(x.monetary, 2) AS monetary,
               c.city, c.state
        FROM x JOIN dim_customer c ON c.customer_key=x.customer_key
        CROSS JOIN anchor
    """
    with eng() as conn:
        df = pd.read_sql_query(q, conn)

    X = StandardScaler().fit_transform(df[['recency','frequency','monetary']])
    cluster_count = min(4, max(1, len(df)))
    km = KMeans(n_clusters=cluster_count, random_state=42, n_init=10)
    df['cluster'] = km.fit_predict(X)

    means = df.groupby('cluster')[['recency','frequency','monetary']].mean()
    score = (
        means['recency'].rank(ascending=False) +
        means['frequency'].rank(ascending=True) +
        means['monetary'].rank(ascending=True)
    )
    ordered = score.sort_values(ascending=False).index.tolist()
    labels = {}
    names = ['Premium', 'Loyal', 'Regular', 'At Risk']
    for i, cid in enumerate(ordered):
        labels[cid] = names[min(i, 3)]
    df['segment'] = df['cluster'].map(labels)
    df.to_csv(OUTPUTS / 'customer_segments.csv', index=False)
    return df


def repeat_purchase():
    q = """
        SELECT f.customer_key,
               COUNT(DISTINCT f.order_id) AS orders,
               SUM(f.sales_amount) AS spend,
               COUNT(*) AS items,
               AVG(f.sales_amount) AS avg_line,
               CAST(julianday((SELECT MAX(full_date) FROM dim_date))-julianday(MAX(d.full_date)) AS INTEGER) AS recency
        FROM fact_sales f JOIN dim_date d ON d.date_key=f.date_key
        GROUP BY f.customer_key
    """
    with eng() as conn:
        df = pd.read_sql_query(q, conn)

    df['will_repeat'] = (df['orders'] >= 2).astype(int)
    X = df[['orders','spend','items','avg_line','recency']]
    y = df['will_repeat']

    class_counts = y.value_counts()
    if y.nunique() < 2 or len(df) < 8 or class_counts.min() < 2:
        df['prediction'] = y
        print('Repeat-purchase model skipped: not enough rows in each class; using observed labels.')
    else:
        a, b, c, d = train_test_split(X, y, test_size=.25, random_state=42, stratify=y)
        model = RandomForestClassifier(n_estimators=150, random_state=42, class_weight='balanced')
        model.fit(a, c)
        df['prediction'] = model.predict(X)
        print('Repeat-purchase training accuracy:', round(accuracy_score(y, df['prediction']), 3))

    df.to_csv(OUTPUTS / 'repeat_purchase_predictions.csv', index=False)
    return df


def basket():
    """Apriori-style frequent itemset mining implemented with the Python standard library."""
    q = """
        SELECT f.order_id, p.product_name
        FROM fact_sales f JOIN dim_product p ON p.product_key=f.product_key
    """
    with eng() as conn:
        d = pd.read_sql_query(q, conn)

    transactions = d.groupby('order_id')['product_name'].apply(set).tolist()
    n_transactions = len(transactions)
    min_support = 0.01
    min_count = max(1, int(min_support * n_transactions))

    item_counts = Counter()
    for basket_items in transactions:
        for item in basket_items:
            item_counts[(item,)] += 1

    frequent = {k: v for k, v in item_counts.items() if v >= min_count}
    all_frequent = dict(frequent)
    previous = set(frequent)

    # Mine pairs and triples. This is enough for a practical college-scale demo.
    for size in (2, 3):
        if not previous:
            break
        candidate_items = sorted({item for fs in previous for item in fs})
        candidates = set(combinations(candidate_items, size))
        counts = Counter()
        for basket_items in transactions:
            for candidate in candidates:
                if set(candidate).issubset(basket_items):
                    counts[candidate] += 1
        current = {k: v for k, v in counts.items() if v >= min_count}
        all_frequent.update(current)
        previous = set(current)

    rule_rows = []
    for itemset, count in all_frequent.items():
        if len(itemset) < 2:
            continue
        itemset_support = count / n_transactions
        items = set(itemset)
        for r in range(1, len(items)):
            for antecedent_tuple in combinations(sorted(items), r):
                antecedent = set(antecedent_tuple)
                consequent = items - antecedent
                antecedent_count = all_frequent.get(tuple(sorted(antecedent)))
                consequent_count = all_frequent.get(tuple(sorted(consequent)))
                if not antecedent_count or not consequent_count:
                    continue
                confidence = count / antecedent_count
                consequent_support = consequent_count / n_transactions
                lift = confidence / consequent_support
                if lift >= 1.05:
                    rule_rows.append({
                        'antecedents': ', '.join(sorted(antecedent)),
                        'consequents': ', '.join(sorted(consequent)),
                        'support': itemset_support,
                        'confidence': confidence,
                        'lift': lift,
                    })

    rules = pd.DataFrame(rule_rows, columns=['antecedents','consequents','support','confidence','lift'])
    if not rules.empty:
        rules = rules.drop_duplicates().sort_values(['lift','confidence'], ascending=False)
    rules.to_csv(OUTPUTS / 'association_rules.csv', index=False)
    return rules


def run():
    rfm()
    repeat_purchase()
    basket()
    print('Data mining complete.')


if __name__ == '__main__':
    run()
