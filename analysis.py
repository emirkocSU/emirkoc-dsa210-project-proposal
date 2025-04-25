import csv
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# 1) CSV’den Veri Okuma ve Birleştirme
sales = []
with open('daily_sales_by_category_2021_2022.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        sales.append({
            'date': datetime.strptime(row['date'], '%Y-%m-%d'),
            'Sweet': float(row['Sweet']),
            'Savory': float(row['Savory']),
            'Other':  float(row['Other'])
        })

trends = []
with open('gogletrendsDATA.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        
        trends.append({
            'date': datetime.strptime(row['date'], '%Y-%m-%d'),
            'comment_maigrir': float(row['comment perdre du poids: (France)']),
            'regime':          float(row['régime: (France)'])
        })

# Eksik günleri forward-fill ile tamamlama
start = min(r['date'] for r in sales)
end   = max(r['date'] for r in sales)
# Tarih aralığı
all_dates = []
d = start
while d <= end:
    all_dates.append(d)
    d += timedelta(days=1)

# trends verisini tarihe göre sözlüğe koyuyorum
tr_map = { r['date']: r for r in sorted(trends, key=lambda x: x['date']) }
filled_tr = {}
last = None
for d in all_dates:
    if d in tr_map:
        last = tr_map[d]
    filled_tr[d] = {
        'date':            d,
        'comment_maigrir': last['comment_maigrir'],
        'regime':          last['regime']
    }

# sales ve trends birleştiriyorum
data = []
for rec in sales:
    d = rec['date']
    t = filled_tr[d]
    data.append({
        'date':            d,
        'Sweet':           rec['Sweet'],
        'Savory':          rec['Savory'],
        'Other':           rec['Other'],
        'regime':          t['regime'],
        'comment_maigrir': t['comment_maigrir']
    })

# İlk 5 kayıt kontrol
print("Sample merged records:")
for r in data[:5]:
    print(r)


# 2) Veri Dönüşümleri 
numeric_cols = ['Sweet','Savory','Other','regime','comment_maigrir']
# IQR hesaplayıp outlier flag ekleme
for col in numeric_cols:
    vals = np.array([r[col] for r in data])
    Q1, Q3 = np.percentile(vals, [25,75])
    IQR = Q3 - Q1
    low, high = Q1 - 1.5*IQR, Q3 + 1.5*IQR
    for r in data:
        r[f'{col}_outlier'] = (r[col] < low) or (r[col] > high)

# Tarih özellikleri
for r in data:
    wd = r['date'].weekday()  # 0=Mon,6=Sun
    r['weekday']    = r['date'].strftime('%A')
    r['is_weekend'] = wd >= 5
    r['month']      = r['date'].month

print("\nAfter transformations (first 3):")
for r in data[:3]:
    print({k: r[k] for k in ['date','weekday','is_weekend','month','Sweet_outlier']})


# 3)(Manuel Tatil Takvimi)
holiday_list = [
    "2021-01-01","2021-04-05","2021-05-01","2021-05-08","2021-05-13","2021-05-24",
    "2021-07-14","2021-08-15","2021-11-01","2021-11-11","2021-12-25",
    "2022-01-01","2022-04-18","2022-05-01","2022-05-08","2022-05-26","2022-06-06",
    "2022-07-14","2022-08-15","2022-11-01","2022-11-11","2022-12-25"
]
holidays = set(datetime.strptime(d, '%Y-%m-%d') for d in holiday_list)
for r in data:
    r['is_holiday'] = r['date'] in holidays

counts = sum(r['is_holiday'] for r in data), len(data)
print(f"\nHoliday flag counts: {counts[0]} true, {counts[1]-counts[0]} false")


# 4) MinMaxScaler
scaler = MinMaxScaler()
X = np.array([[r[col] for col in numeric_cols] for r in data])
X_scaled = scaler.fit_transform(X)
for i, r in enumerate(data):
    for j, col in enumerate(numeric_cols):
        r[f'{col}_scaled'] = X_scaled[i, j]

print("\nScaled features sample:")
for r in data[:2]:
    print({col+'_scaled': r[col+'_scaled'] for col in numeric_cols})


# 5) EDA: Korelasyon ve Görselleştirme
# 5.1 Korelasyon matrisi
all_keys = numeric_cols + ['is_holiday']
M = np.array([[r[k] for k in all_keys] for r in data], dtype=float)
corr = np.corrcoef(M, rowvar=False)

plt.figure(figsize=(6,6))
plt.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
plt.colorbar(label='Correlation')
plt.xticks(range(len(all_keys)), all_keys, rotation=90)
plt.yticks(range(len(all_keys)), all_keys)
plt.title('Correlation Heatmap')
plt.tight_layout()
plt.show()

# 5.2 Boxplot: Sweet by Weekday
groups = {}
for r in data:
    groups.setdefault(r['weekday'], []).append(r['Sweet'])

labels = list(groups.keys())
values = [groups[l] for l in labels]

plt.figure(figsize=(8,4))
plt.boxplot(values, labels=labels)
plt.title('Sweet Sales by Weekday')
plt.xlabel('Weekday')
plt.ylabel('Sweet Sales')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# 6) requirements.txt
deps = ["numpy","matplotlib","scikit-learn"]
with open("requirements.txt","w") as f:
    f.write("\n".join(deps))
print("\nrequirements.txt written.")
