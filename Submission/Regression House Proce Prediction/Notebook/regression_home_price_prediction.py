# -*- coding: utf-8 -*-
"""regression-home-price-prediction.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KAQoiFbpXDpESRSnbUyjWcdrfAxH26w-

# **Mount to Drive**
"""

from google.colab import drive
drive.mount('/content/drive')

"""# **Import Libraries**"""

import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import (StandardScaler, MinMaxScaler, PolynomialFeatures, RobustScaler)
from sklearn.model_selection import (train_test_split, GridSearchCV, KFold, RandomizedSearchCV, StratifiedKFold, cross_val_score)
from sklearn.linear_model import (LinearRegression, Lasso, Ridge, ElasticNet, LassoCV, RidgeCV, ElasticNetCV)
from sklearn.feature_selection import RFE
from sklearn.metrics import (r2_score, mean_squared_error)
from sklearn.pipeline import make_pipeline
from sklearn.svm import SVR
from sklearn.ensemble import (GradientBoostingRegressor, RandomForestRegressor, AdaBoostRegressor, BaggingRegressor, ExtraTreesRegressor)
from xgboost import XGBRFRegressor, XGBRegressor
from lightgbm import LGBMRegressor
from mlxtend.regressor import StackingCVRegressor

# Setting options and context
warnings.filterwarnings('ignore')
sns.set_context("paper", font_scale=1, rc={"grid.linewidth": 3})
pd.set_option('display.max_rows', 100, 'display.max_columns', 400)

"""# **Load Dataset**"""

train= pd.read_csv('/content/drive/MyDrive/Kuliah/Dicoding/Submission/Regression House Price Prediction/Dataset/train.csv')
test=pd.read_csv('/content/drive/MyDrive/Kuliah/Dicoding/Submission/Regression House Price Prediction/Dataset/test.csv')

"""# **Data Understanding**"""

train.info()

train.head()

test.info()

test.head()

print(train.shape)
print(test.shape)

train.describe()

"""# **Check Missing Values**

cek missing values di `train dataset`
"""

missing_num = train[train.columns].isna().sum().sort_values(ascending=False)
missing_perc = (train[train.columns].isna().sum()/len(train)*100).sort_values(ascending=False)
missing = pd.concat([missing_num,missing_perc],keys=['Total','Percentage'],axis=1)
missing_train = missing[missing['Percentage']>0]
missing_train

"""cek missing values di `test dataset`"""

missing_num = test[test.columns].isna().sum().sort_values(ascending=False)
missing_perc = (test[test.columns].isna().sum()/len(test)*100).sort_values(ascending=False)
missing = pd.concat([missing_num,missing_perc],keys=['Total','Percentage'],axis=1)
missing_test = missing[missing['Percentage']>0]
missing_test

"""#### _Ada 19 attributes punya missing values and 5 features (PoolQC, MiscFeature, Alley, Fence, FireplaceQu) punya missing values lebih besar dari 45%_

# **Feature**

<b>`Numerical features`</b>: 1stFlrSF, 2ndFlrSF, 3SsnPorch, BedroomAbvGr, BsmtFinSF1, BsmtFinSF2, BsmtFullBath, BsmtHalfBath, BsmtUnfSF, EnclosedPorch, Fireplaces, FullBath, GarageArea, GarageCars, GarageYrBlt, GrLivArea, HalfBath, KitchenAbvGr, LotArea, LotFrontage, LowQualFinSF, MSSubClass, MasVnrArea, MiscVal, MoSold, OpenPorchSF, OverallCond, OverallQual, PoolArea, ScreenPorch, TotRmsAbvGrd, TotalBsmtSF, WoodDeckSF, YearBuilt, YearRemodAdd, YrSold

<b>`Categorical features`</b>: Alley, BldgType, BsmtCond, BsmtExposure, BsmtFinType1, BsmtFinType2, BsmtQual, CentralAir, Condition1, Condition2, Electrical, ExterCond, ExterQual, Exterior1st, Exterior2nd, Fence, FireplaceQu, Foundation, Functional, GarageCond, GarageFinish, GarageQual, GarageType, Heating, HeatingQC, HouseStyle, KitchenQual, LandContour, LandSlope, LotConfig, LotShape, MSZoning, MasVnrType, MiscFeature, Neighborhood, PavedDrive, PoolQC, RoofMatl, RoofStyle, SaleCondition, SaleType, Street, Utilities,
"""

numerical = train.select_dtypes(include=['int64','float64']).drop(['SalePrice','Id'],axis=1)
numerical.head()

categorical = train.select_dtypes(exclude=['int64','float64'])
categorical.head()

"""# **Exploratory Data Analysis**

### Plotting missing value pada train and test data
"""

def showvalues(ax,m=None):
    for p in ax.patches:
        ax.annotate("%.1f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),\
                    ha='center', va='center', fontsize=14, color='k', rotation=0, xytext=(0, 7),\
                    textcoords='offset points',fontweight='light',alpha=0.9)

plt.figure(figsize=(20,20))
plt.subplot(2,1,1)
ax1=sns.barplot(x=missing_train.index,y='Percentage',data=missing_train)
showvalues(ax1)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, horizontalalignment='right')
ax1.set_title('Missing Values in Train Data')
plt.subplot(2,1,2)
ax2=sns.barplot(x=missing_test.index,y='Percentage',data=missing_test)
showvalues(ax2)
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, horizontalalignment='right')
ax2.set_title('Missing Values in Test Data')
plt.show()

# Drop Id column from train and test test
train.drop('Id',axis=1,inplace=True)
test.drop('Id',axis=1,inplace=True)
print(train.shape)
print(test.shape)

#Visualising numerical predictor variables with Target Variables
train_num = train.select_dtypes(include=['int64','float64'])
fig,axs= plt.subplots(12,3,figsize=(20,80))
#adjust horizontal space between plots
fig.subplots_adjust(hspace=0.6)
for i,ax in zip(train_num.columns,axs.flatten()):
    sns.scatterplot(x=i, y='SalePrice', hue='SalePrice',data=train_num,ax=ax,palette='viridis_r')
    plt.xlabel(i,fontsize=12)
    plt.ylabel('SalePrice',fontsize=12)
    #ax.set_yticks(np.arange(0,900001,100000))
    ax.set_title('SalePrice'+' - '+str(i),fontweight='bold',size=20)

# Visualising Categorical predictor variables with Target Variables
def facetgrid_boxplot(x, y, **kwargs):
    sns.boxplot(x=x, y=y)
    x=plt.xticks(rotation=90)

f = pd.melt(train, id_vars=['SalePrice'], value_vars=sorted(train[categorical.columns]))
g = sns.FacetGrid(f, col="variable", col_wrap=3, sharex=False, sharey=False, height=5)
g = g.map(facetgrid_boxplot, "value", "SalePrice")

"""_<b>bisa dilihat dari boxplots, pada SalePrice fullbath=3 lebih tinggi dari 0,1, atau 2. untuk SalePrice OverallQual=10 lebih tinggi daripada yang lain._"""

# Distribution of Target variable (SalePrice)
plt.figure(figsize=(8,6))
sns.distplot(train['SalePrice'],hist_kws={"edgecolor": (1,0,0,1)})

# Skew and kurtosis for SalePrice
print("Skewness: %f" % train['SalePrice'].skew())
print("Kurtosis: %f" % train['SalePrice'].kurt())

#Applying log transformation to remove skewness and make target variable normally distributed
train['SalePrice'] = np.log1p(train['SalePrice'])

#Plotting graph again to see if its normally distributed or not and see outliers
# Distribution of Target variable (SalePrice)
plt.figure(figsize=(8,6))
sns.distplot(train['SalePrice'],hist_kws={"edgecolor": (1,0,0,1)})

"""<b>`Now SalePrice is normally distributed`"""

#Correlation between variables to check multicollinearity
# Generate a mask for the upper triangle (taken from seaborn example gallery)
plt.subplots(figsize = (30,20))
# Changed np.bool to bool
mask = np.zeros_like(train_num.corr(), dtype=bool)
mask[np.triu_indices_from(mask)] = True
#Plotting heatmap
sns.heatmap(train_num.corr(), cmap=sns.diverging_palette(20, 220, n=200), mask = mask, annot=True, center = 0)

"""* Terdapat korelasi sebesar 0,83 atau 83% antara **GarageYrBlt** dan **TahunDibangun**.
* Korelasi 83% antara **TotRmsAbvGrd** dan **GrLivArea**.
* Korelasi 89% antara **GarasiMobil** dan **GarasiArea**.
* Demikian pula banyak fitur lain seperti **BsmtUnfSF**, **FullBath** memiliki korelasi yang baik dengan fitur independen lainnya.

# **Data Preparation**

Penanganan pada Outliers
"""

## Deleting those two values with outliers.
train = train[train.GrLivArea < 4500]
train.reset_index(drop = True, inplace = True)

"""<b>`Menggabungkan train and test data untuk menghandle missing values pada train and test data, datatype issues, skewness dan transformation.`"""

y=train['SalePrice']
train_df=train.drop('SalePrice',axis=1)
test_df = test
df_all= pd.concat([train_df,test_df]).reset_index(drop=True)

df_all['age']=df_all['YrSold']-df_all['YearBuilt']
# Some of the non-numeric predictors are stored as numbers; convert them into strings
#will convert those columns into dummy variables later.
df_all[['MSSubClass']] = df_all[['MSSubClass']].astype(str)
df_all['YrSold'] = df_all['YrSold'].astype(str) #year
df_all['MoSold'] = df_all['MoSold'].astype(str) #month

"""Menghandle missing values dari 19 feature yang sudah dijelaskan diatas"""

#Functional: Home functionality (Assume typical unless deductions are warranted)
df_all['Functional'] = df_all['Functional'].fillna('Typ')
df_all['Electrical'] = df_all['Electrical'].fillna('SBrkr') #Filling with modef
# data description states that NA refers to "No Pool"
df_all["PoolQC"] = df_all["PoolQC"].fillna("None")
# Replacing the missing values with 0, since no garage = no cars in garage inferred from data dictionary
df_all['GarageYrBlt'] = df_all['GarageYrBlt'].fillna(0)
df_all['KitchenQual'] = df_all['KitchenQual'].fillna("TA")
df_all['Exterior1st'] = df_all['Exterior1st'].fillna(df_all['Exterior1st'].mode()[0])
df_all['Exterior2nd'] = df_all['Exterior2nd'].fillna(df_all['Exterior2nd'].mode()[0])
df_all['SaleType'] = df_all['SaleType'].fillna(df_all['SaleType'].mode()[0])
# Replacing the missing values with None inferred from data dictionary
for col in ['GarageType', 'GarageFinish', 'GarageQual', 'GarageCond']:
    df_all[col] = df_all[col].fillna('None')
# Replacing the missing values with None
# NaN values for these categorical basement df_all, means there's no basement
for col in ('BsmtQual', 'BsmtCond', 'BsmtExposure', 'BsmtFinType1', 'BsmtFinType2'):
    df_all[col] = df_all[col].fillna('None')
#Replacing missing value it with median beacuse of outliers
df_all['LotFrontage'] = df_all.groupby('Neighborhood')['LotFrontage'].transform(lambda x: x.fillna(x.median()))
# Replacing the missing values with None
# We have no particular intuition around how to fill in the rest of the categorical df_all
# So we replace their missing values with None
objects = []
for i in df_all.columns:
    if df_all[i].dtype == object:
        objects.append(i)
df_all.update(df_all[objects].fillna('None'))

numeric_dtypes = [ 'int64','float64']
numerics = []
for i in df_all.columns:
    if df_all[i].dtype in numeric_dtypes:
        numerics.append(i)
df_all.update(df_all[numerics].fillna(0))

df_all['MSZoning'] = df_all.groupby('MSSubClass')['MSZoning'].transform(lambda x: x.fillna(x.mode()[0]))

#Checking percentage of null values present in dataset
missing_perc= (df_all[df_all.columns].isna().sum()/len(df_all)*100).sort_values(ascending=False)
print(missing_perc[missing_perc>0].sum()) #No missing values

"""### Menangani Skewness dalam variabel prediktor

Mengapa menghilangkan Skewness dari model dan variabel prediktor kita?
- Agar koefisien dapat ditafsirkan, regresi linier mengasumsikan beberapa hal
- 'Homoskedastisitas' (yaitu, kesalahan yang dilakukan model Anda harus memiliki varians yang sama) dan istilah kesalahan harus 'terdistribusi secara normal'.
- Mengikuti asumsi regresi linier adalah penting jika Anda ingin `menginterpretasikan koefisien` dan dapat digunakan dalam tujuan bisnis.
- Ketika variabel dependen memiliki kemiringan seperti data kita, maka residualnya juga akan demikian. maka dari itu melakukan`handling skewness` pada data.
- Model ini kemudian akan digunakan untuk memahami bagaimana tepatnya harga bervariasi dengan variabel.
"""

# menghilangkan skewness dari variabel target (Harga Jual) dan membuatnya terdistribusi secara normal.
# cari tahu apakah variabel prediktor numerik sebagian besar condong atau tidak
df_all_num = df_all.select_dtypes(include=['int64','float64'])
skew_features = df_all_num.apply(lambda x: skew(x)).sort_values(ascending=False)
high_skew = skew_features[skew_features > 0.5]
skew_index = high_skew.index
skewness = pd.DataFrame({'Skew' :high_skew})
skew_features

f, ax = plt.subplots(figsize=(8, 7))
ax.set_xscale("log")
ax = sns.boxplot(data=df_all_num , orient="h", palette="Set1")
ax.xaxis.grid(False)
ax.set(ylabel="Feature names")
ax.set(xlabel="Numeric values")
ax.set(title="Numeric Distribution of Features")
sns.despine(trim=True, left=True)

print(df_all[skew_index].min())

from sklearn.preprocessing import PowerTransformer

# Menggunakan Yeo-Johnson jika ada nilai negatif
transformer = PowerTransformer(method='yeo-johnson')
df_all[skew_index] = transformer.fit_transform(df_all[skew_index])

# Let's make sure we handled all the skewed values
f, ax = plt.subplots(figsize=(8, 7))
ax.set_xscale("log")
ax = sns.boxplot(data=df_all[skew_index] , orient="h", palette="Set1")
ax.xaxis.grid(False)
ax.set(ylabel="Feature names")
ax.set(xlabel="Numeric values")
ax.set(title="Numeric Distribution of Features")
sns.despine(trim=True, left=True)

"""<b>Feature terlihat terdistribusi secara normal sekarang, tidak ada banyak kemiringan dalam distribusi variabel prediktor.

### Menghapus fitur yang tidak memberikan informasi penting.
- Membuat fitur baru berdasarkan penggabungan atau transformasi dari beberapa kolom yang sudah ada.
- Fitur-fitur baru tersebut seperti `Total_sqr_footage, Total_Bathrooms, dan Total_porch_sf` bisa membantu meningkatkan performa model prediksi karena mereka memberikan gambaran yang lebih menyeluruh tentang kondisi fisik rumah, yang berhubungan langsung dengan harga rumah.
"""

print(df_all['Utilities'].value_counts())
print(df_all['Street'].value_counts())
print(df_all['PoolQC'].value_counts())

df_all=df_all.drop(['Utilities', 'Street', 'PoolQC'], axis=1) # not useful df_all, evident from above
# vintage house with remodified version of it plays a important role in prediction(i.e. high price )
df_all['YrBltAndRemod']=df_all['YearBuilt']+df_all['YearRemodAdd']
#Overall area for all floors and basement plays an important role, hence creating total area in square foot column
df_all['Total_sqr_footage'] = (df_all['BsmtFinSF1'] + df_all['BsmtFinSF2'] +
                                 df_all['1stFlrSF'] + df_all['2ndFlrSF'])
# Creating derived column for total number of bathrooms column
df_all['Total_Bathrooms'] = (df_all['FullBath'] + (0.5 * df_all['HalfBath']) +
                               df_all['BsmtFullBath'] + (0.5 * df_all['BsmtHalfBath']))
#Creating derived column for total porch area
df_all['Total_porch_sf'] = (df_all['OpenPorchSF'] + df_all['3SsnPorch'] + df_all['EnclosedPorch'] + \
                              df_all['ScreenPorch'] + df_all['WoodDeckSF'])

"""- Membuat Fitur Biner: Fitur biner seperti ini memudahkan model dalam menangani atribut yang bersifat "ada atau tidak", yang membantu meningkatkan performa prediksi dengan memberikan informasi yang lebih mudah dipahami oleh model.

- Mengganti Nilai Nol: Penggantian nilai nol dengan angka yang lebih logis dilakukan karena nilai nol seringkali tidak mencerminkan kondisi sebenarnya. Misalnya, beberapa rumah mungkin tidak memiliki basement, tapi ada juga kemungkinan bahwa data untuk rumah dengan basement tidak tercatat dengan benar. Menggunakan nilai eksponensial seperti ini adalah cara untuk menghindari nilai nol yang dapat mengganggu distribusi fitur dan membuat model lebih robust.
"""

df_all['has_pool'] = df_all['PoolArea'].apply(lambda x: 1 if x > 0 else 0)
df_all['has_2ndfloor'] = df_all['2ndFlrSF'].apply(lambda x: 1 if x > 0 else 0)
df_all['has_garage'] = df_all['GarageArea'].apply(lambda x: 1 if x > 0 else 0)
df_all['has_bsmt'] = df_all['TotalBsmtSF'].apply(lambda x: 1 if x > 0 else 0)
df_all['has_fireplace'] = df_all['Fireplaces'].apply(lambda x: 1 if x > 0 else 0)
df_all['has_openporch'] =df_all['OpenPorchSF'].apply(lambda x: 1 if x > 0 else 0)
df_all['has_wooddeck'] =df_all['WoodDeckSF'].apply(lambda x: 1 if x > 0 else 0)
df_all['has_enclosedporch'] = df_all['EnclosedPorch'].apply(lambda x: 1 if x > 0 else 0)
df_all['has_3ssnporch']=df_all['3SsnPorch'].apply(lambda x: 1 if x > 0 else 0)
df_all['has_openporch'] = df_all['OpenPorchSF'].apply(lambda x: 1 if x > 0 else 0)
df_all['has_screenporch'] = df_all['ScreenPorch'].apply(lambda x: 1 if x > 0 else 0)

df_all['TotalBsmtSF'] = df_all['TotalBsmtSF'].apply(lambda x: np.exp(6) if x <= 0.0 else x)
df_all['2ndFlrSF'] = df_all['2ndFlrSF'].apply(lambda x: np.exp(6.5) if x <= 0.0 else x)
df_all['LotFrontage'] = df_all['LotFrontage'].apply(lambda x: np.exp(4.2) if x <= 0.0 else x)
df_all['MasVnrArea'] = df_all['MasVnrArea'].apply(lambda x: np.exp(4) if x <= 0.0 else x)
df_all['BsmtFinSF1'] = df_all['BsmtFinSF1'].apply(lambda x: np.exp(6.5) if x <= 0.0 else x)

"""### Melakukan normal transformation

"""

def log_transform(result, features):
    m = result.shape[1]
    for feature in features:
        result = result.assign(newcol=pd.Series(np.log(1.01+result[feature])).values)
        result.columns.values[m] = feature + '_log'
        m += 1
    return result

log_features = ['LotFrontage','LotArea','MasVnrArea','BsmtFinSF1','BsmtFinSF2','BsmtUnfSF',
                 'TotalBsmtSF','1stFlrSF','2ndFlrSF','LowQualFinSF','GrLivArea',
                 'BsmtFullBath','BsmtHalfBath','FullBath','HalfBath','BedroomAbvGr','KitchenAbvGr',
                 'TotRmsAbvGrd','Fireplaces','GarageCars','GarageArea','WoodDeckSF','OpenPorchSF',
                 'EnclosedPorch','3SsnPorch','ScreenPorch','PoolArea','MiscVal','YearRemodAdd']

df_all = log_transform(df_all, log_features)

"""Mengapa Menggunakan Log Transformation?: <br>
Log transformation sering digunakan dalam machine learning dan statistical modeling ketika distribusi fitur numerik sangat skewed (tidak normal). Log transformation membantu untuk:
1. Mengurangi skewness: Data yang memiliki distribusi skewed menjadi lebih mendekati distribusi normal setelah log transformation.
2. Mengurangi dampak outliers: Nilai yang sangat besar (outliers) menjadi lebih kecil dalam skala log, sehingga bisa membantu model dalam mempelajari pola lebih baik.
3. Meningkatkan performa model: Distribusi fitur yang lebih normal biasanya membuat algoritma machine learning bekerja lebih efisien dan akurat.

### Menangani kolom-kolom kategorikal dan mengubahnya menjadi fitur numerik melalui teknik one-hot encoding.
"""

df_all_num= df_all.select_dtypes(include=['float64','int64']).columns  # Numerical columns
df_all_temp = df_all.select_dtypes(exclude=['float64','int64']) # selecting object and categorical features only
df_all_dummy= pd.get_dummies(df_all_temp)
df_all=pd.concat([df_all,df_all_dummy],axis=1) # joining converted dummy feature and original df_all dataset
df_all= df_all.drop(df_all_temp.columns,axis=1) #removing original categorical columns
df_all.shape

X= df_all[:len(train)] #converted into train data
Z_test= df_all[len(train):] #test data
print('Train Data Shape:',X.shape) #train set shape
print('Test Data Shape:',Z_test.shape)  #test set shape

#based on describe method and scatter plot, removing outliers
outl_col = ['GrLivArea','GarageArea','TotalBsmtSF','LotArea']

def drop_outliers(x):
    list = []
    for col in outl_col:
        Q1 = x[col].quantile(.25)
        Q3 = x[col].quantile(.99)
        IQR = Q3-Q1
        x =  x[(x[col] >= (Q1-(1.5*IQR))) & (x[col] <= (Q3+(1.5*IQR)))]
    return x
X = drop_outliers(X)
outliers = [30, 88, 462, 631, 1322]
X = X.drop(X.index[outliers])
y = y.drop(y.index[outliers])
print(X.shape)

"""Menghapus outlier dari dataset X dan target y berdasarkan beberapa kolom yang mengandung nilai ekstrem dan juga berdasarkan indeks outlier yang telah ditentukan sebelumnya.

<b>`Jika ada satu nilai yang muncul hampir di semua baris (lebih dari 99.94% dari seluruh data), fitur tersebut dianggap tidak bermanfaat dalam proses pembelajaran model. Alasannya, jika hampir semua baris memiliki nilai yang sama untuk sebuah fitur, maka fitur tersebut tidak memberikan variasi atau informasi yang cukup bagi model untuk belajar. Dengan kata lain, fitur yang isinya hampir sama di seluruh dataset tidak membantu model membedakan antara contoh data yang satu dengan yang lain, sehingga dihapus karena dianggap tidak relevan untuk prediksi.`
"""

def redundant_feature(df):
    redundant = []
    for i in df.columns:
        counts = df[i].value_counts()
        count_max = counts.iloc[0]
        if count_max / len(df) * 100 > 99.94:
            redundant.append(i)
    redundant = list(redundant)
    return redundant


redundant_features = redundant_feature(X)

X = X.drop(redundant_features, axis=1)
Z_test = Z_test.drop(redundant_features, axis=1)

""" Menghapus fitur yang redundan atau tidak memberikan informasi yang signifikan dalam proses prediksi. Fitur-fitur tersebut dianggap redundan jika lebih dari 99.94% nilainya sama (konstan) di seluruh dataset. Dengan membuang fitur yang redundan dari X (train) dan Z_test (test), model akan lebih efisien dan tidak terganggu oleh fitur yang tidak bervariasi."""

print('Train Data Shape:',X.shape) #train set shape
print('Test Data Shape:',Z_test.shape)  #test set shape

"""# **Cross Validation**"""

kfold= KFold(n_splits=11,random_state=42,shuffle=True) #kfold cross validation

# Error function to compute error
def rmsle(y, y_pred):
    return np.sqrt(mean_squared_error(y, y_pred))

#Assigning scoring paramter to 'neg_mean_squared_error' beacause 'mean_squared_error' is not
# available inside cross_val_score method
def cv_rmse(model, X=X):
    rmse = np.sqrt(-cross_val_score(model, X, y, scoring="neg_mean_squared_error", cv=kfold))
    return (rmse)

"""# **Splitting Data Into Train and Test**"""

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

print(X_train.shape)
print(y_train.shape)
print(X_test.shape)

"""# **Modelling**"""

from sklearn.impute import SimpleImputer

# Menggunakan SimpleImputer untuk mengisi NaN dengan rata-rata kolom
imputer = SimpleImputer(strategy='mean')
X_train = imputer.fit_transform(X_train)
X_test = imputer.transform(X_test)

"""# Ridge Regression"""

# 1. Ridge Regression
ridge = Ridge()
params = {'alpha': [5, 8, 10, 10.1, 10.2, 10.3, 10.35, 10.36, 11, 12, 15]}
scaler = RobustScaler()

# Mengubah data
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Melakukan GridSearchCV
grid_ridge = GridSearchCV(ridge, param_grid=params, cv=kfold, scoring='neg_mean_squared_error')
grid_ridge.fit(X_train_scaled, y_train)

# Mendapatkan alpha terbaik
alpha = grid_ridge.best_params_['alpha']
ridge_score = -grid_ridge.best_score_  # Negasi karena scoring adalah negatif MSE

# Melatih model Ridge dengan alpha terbaik
ridge_alpha = Ridge(alpha=alpha)
ridge_alpha.fit(X_train_scaled, y_train)

# Melakukan prediksi
y_pred_train_ridge = ridge_alpha.predict(X_train_scaled)
y_pred_test_ridge = ridge_alpha.predict(X_test_scaled)

# Menghitung RMSE dan MSE
train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train_ridge))
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test_ridge))
train_mse = mean_squared_error(y_train, y_pred_train_ridge)
test_mse = mean_squared_error(y_test, y_pred_test_ridge)

print('RMSE Train (Ridge) =', train_rmse)
print('MSE Train (Ridge) =', train_mse)
print('RMSE Test (Ridge) =', test_rmse)
print('MSE Test (Ridge) =', test_mse)

"""# Lasso Regression"""

# 2. Lasso Regression
lasso = Lasso(alpha=0.001)  # Contoh alpha
lasso.fit(X_train_scaled, y_train)
y_pred_train_lasso = lasso.predict(X_train_scaled)
y_pred_test_lasso = lasso.predict(X_test_scaled)

lasso_mse_train = mean_squared_error(y_train, y_pred_train_lasso)
lasso_rmse_train = np.sqrt(lasso_mse_train)
lasso_mse_test = mean_squared_error(y_test, y_pred_test_lasso)
lasso_rmse_test = np.sqrt(lasso_mse_test)

print(f"Lasso - Train MSE: {lasso_mse_train}, Train RMSE: {lasso_rmse_train}")
print(f"Lasso - Test MSE: {lasso_mse_test}, Test RMSE: {lasso_rmse_test}")

"""# ElasticNet Regression"""

# 3. ElasticNet Regression
elasticnet = ElasticNet(alpha=0.001, l1_ratio=0.5)  # Contoh hyperparameter
elasticnet.fit(X_train_scaled, y_train)
y_pred_train_elastic = elasticnet.predict(X_train_scaled)
y_pred_test_elastic = elasticnet.predict(X_test_scaled)

elastic_mse_train = mean_squared_error(y_train, y_pred_train_elastic)
elastic_rmse_train = np.sqrt(elastic_mse_train)
elastic_mse_test = mean_squared_error(y_test, y_pred_test_elastic)
elastic_rmse_test = np.sqrt(elastic_mse_test)

print(f"ElasticNet - Train MSE: {elastic_mse_train}, Train RMSE: {elastic_rmse_train}")
print(f"ElasticNet - Test MSE: {elastic_mse_test}, Test RMSE: {elastic_rmse_test}")

"""# Support Vector Regressor"""

# 4. Support Vector Regression (SVR)
svr = SVR(C=19, epsilon=0.008, gamma=0.00015)
svr.fit(X_train_scaled, y_train)
y_pred_train_svr = svr.predict(X_train_scaled)
y_pred_test_svr = svr.predict(X_test_scaled)

svr_mse_train = mean_squared_error(y_train, y_pred_train_svr)
svr_rmse_train = np.sqrt(svr_mse_train)
svr_mse_test = mean_squared_error(y_test, y_pred_test_svr)
svr_rmse_test = np.sqrt(svr_mse_test)

print(f"SVR - Train MSE: {svr_mse_train}, Train RMSE: {svr_rmse_train}")
print(f"SVR - Test MSE: {svr_mse_test}, Test RMSE: {svr_rmse_test}")

"""# **Visualisasi Evaluasi**"""

# Data MSE dan RMSE dari model yang sudah dievaluasi
model_names = ['Ridge', 'Lasso', 'ElasticNet', 'SVR']

# Data untuk visualisasi
train_mse = [train_mse, lasso_mse_train, elastic_mse_train, svr_mse_train]  # MSE dari training
train_rmse = [train_rmse, lasso_rmse_train, elastic_rmse_train, svr_rmse_train]  # RMSE dari training
test_mse = [test_mse, lasso_mse_test, elastic_mse_test, svr_mse_test]  # MSE dari testing
test_rmse = [test_rmse, lasso_rmse_test, elastic_rmse_test, svr_rmse_test]  # RMSE dari testing

# Membuat line chart
plt.figure(figsize=(14, 7))

# Plot untuk Train RMSE
plt.plot(model_names, train_rmse, marker='o', label='Train RMSE', linestyle='-', color='b')
# Plot untuk Train MSE
plt.plot(model_names, train_mse, marker='o', label='Train MSE', linestyle='--', color='c')

# Plot untuk Test RMSE
plt.plot(model_names, test_rmse, marker='o', label='Test RMSE', linestyle='-', color='r')
# Plot untuk Test MSE
plt.plot(model_names, test_mse, marker='o', label='Test MSE', linestyle='--', color='m')

# Menambahkan judul dan label
plt.title('Perbandingan Kinerja Model: RMSE dan MSE', fontsize=16)
plt.xlabel('Model', fontsize=14)
plt.ylabel('Error', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend()
plt.grid(False)

# Menampilkan grafik
plt.show()