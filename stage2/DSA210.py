import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu, spearmanr, wilcoxon


sales = []
with open('daily_sales_by_category_2021_2022.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sales.append({
            'date': datetime.strptime(row['date'], '%Y-%m-%d'),
            # Önce float’a, sonra int’e çeviriyoruz:
            'Sweet': int(float(row['Sweet'])),
            'Savory': int(float(row['Savory'])),
            'Other':  int(float(row['Other']))
        })

trends = []
with open('gogletrendsDATA.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        trends.append({
            'date': datetime.strptime(row['date'], '%Y-%m-%d'),
            'comment_maigrir': float(row['comment perdre du poids: (France)']),
            'regime':          float(row['régime: (France)'])
        })

# 2) Eksik Günleri Forward-Fill ile tamamlama modülüm
start = min(r['date'] for r in sales)
end   = max(r['date'] for r in sales)
all_dates = []
d = start
while d <= end:
    all_dates.append(d)
    d += timedelta(days=1)

tr_map = { r['date']: r for r in sorted(trends, key=lambda x: x['date']) }
filled_tr = {}
last = None
for d in all_dates:
    if d in tr_map:
        last = tr_map[d]
        filled_tr[d] = last
    else:
        filled_tr[d] = {
            'date': d,
            'comment_maigrir': last['comment_maigrir'],
            'regime': last['regime']
        }

# 3) Sales + Trends Birleştirme 
data = []
for rec in sales:
    d = rec['date']
    t = filled_tr[d]
    data.append({
        'date': d,
        'Sweet': rec['Sweet'],
        'Savory': rec['Savory'],
        'Other':  rec['Other'],
        'regime':          t['regime'],
        'comment_maigrir': t['comment_maigrir']
    })

# 4) EDA: Zaman Serisi Plot’ları
dates        = [r['date'] for r in data]
sweet_sales  = [r['Sweet'] for r in data]
regime_index = [r['regime'] for r in data]

plt.figure(figsize=(10,4))
plt.plot(dates, sweet_sales, label='Sweet Sales')
plt.title('Daily Sweet Sales')
plt.xlabel('Date')
plt.ylabel('Quantity')
plt.tight_layout()
plt.show()

plt.figure(figsize=(10,4))
plt.plot(dates, regime_index, label='Regime Search Index', color='orange')
plt.title('Daily "régime" Search Index')
plt.xlabel('Date')
plt.ylabel('Index')
plt.tight_layout()
plt.show()

# 5) Haftalık Ortalama Hesaplama
weekly = {}
for r in data:
    year, week, _ = r['date'].isocalendar()
    key = (year, week)
    weekly.setdefault(key, {'Sweet':0,'Savory':0,'Other':0,'regime':0,'count':0})
    weekly[key]['Sweet'] += r['Sweet']
    weekly[key]['Savory'] += r['Savory']
    weekly[key]['Other']  += r['Other']
    weekly[key]['regime'] += r['regime']
    weekly[key]['count']  += 1

weekly_avg = {
    k: { metric: v[metric]/v['count'] for metric in ('Sweet','Savory','Other','regime') }
    for k,v in weekly.items()
}

# 6) Hipotez Testleri 

# H1
regimes = sorted(r['regime'] for r in data)
cutoff = regimes[int(len(regimes)*0.75)]
high_sweet = [r['Sweet'] for r in data if r['regime'] > cutoff]
low_sweet  = [r['Sweet'] for r in data if r['regime'] <= cutoff]
U1, p1 = mannwhitneyu(high_sweet, low_sweet, alternative='two-sided')

# H3
high_sav = [r['Savory'] for r in data if r['regime'] > cutoff]
low_sav  = [r['Savory'] for r in data if r['regime'] <= cutoff]
U3, p3 = mannwhitneyu(high_sav, low_sav, alternative='two-sided')

# H2
rho, p_corr = spearmanr(
    [r['regime'] for r in data],
    [r['Sweet']  for r in data]
)
lag_corr = {}
for lag in (1,2,3):
    x = [data[i]['regime'] for i in range(len(data)-lag)]
    y = [data[i+lag]['Sweet'] for i in range(len(data)-lag)]
    lag_corr[lag] = spearmanr(x,y).correlation

print(f"H1 (Sweet vs regime): U={U1:.1f}, p={p1:.3f}")
print(f"H3 (Savory vs regime): U={U3:.1f}, p={p3:.3f}")
print(f"H2 Spearman: rho={rho:.3f}, p={p_corr:.3f}")
for lag, c in lag_corr.items():
    print(f"  Lag {lag} day corr = {c:.3f}")
