import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from PIL import Image
sns.set(style='dark')

day_df = pd.read_csv("day_data.csv")

def create_monthly_sharing_df(df):
    monthly_sharing_df = df.resample(rule='M', on='dteday').agg({
        "cnt": "sum"
    })
    monthly_sharing_df.index = monthly_sharing_df.index.strftime('%Y-%m')
    monthly_sharing_df = monthly_sharing_df.reset_index()
    monthly_sharing_df.rename(columns={
        "dteday": "Bulan",
        "cnt": "Total_Peminjaman"
    }, inplace=True)
    return monthly_sharing_df

datetime_columns = ["dteday"]
 
for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

# Sidebar untuk pengaturan tanggal
with st.sidebar:
    # Membaca gambar dari folder lokal
    image_path = "1200px-Melbourne_City_Bikes.JPEG"  # Ganti dengan path gambar Anda
    image = Image.open(image_path)

    # Menampilkan gambar yang dibaca
    st.image(image, use_column_width=True)

    # Mengambil start_date dari date_input
    start_date = st.date_input(
        label='Start Date',
        min_value=min_date,
        max_value=max_date,
        value=min_date
    )

    # Mengambil end_date dari date_input
    end_date = st.date_input(
        label='End Date',
        min_value=min_date,
        max_value=max_date,
        value=max_date
    )

    # Membuat validasi agar end_date tidak bisa sebelum start_date
    if start_date > end_date:
        st.error('End date must fall after start date.')

# Filter data berdasarkan tanggal yang dipilih
main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

monthly_sharing_data_df = create_monthly_sharing_df(main_df)
st.header('Bike Sharing Data Analysis')

st.subheader('Tren Monthly Sharing')

monthly_sharing_data_df['Bulan'] = pd.to_datetime(monthly_sharing_data_df['Bulan'])
# Memisahkan data untuk tahun 2011 dan 2012
monthly_sharing_2011 = monthly_sharing_data_df[monthly_sharing_data_df['Bulan'].dt.year == 2011]
monthly_sharing_2012 = monthly_sharing_data_df[monthly_sharing_data_df['Bulan'].dt.year == 2012]

col1, col2 = st.columns(2)
 
with col1:
    total_sharing_2011 = monthly_sharing_2011["Total_Peminjaman"].sum()
    formatted_total_sharing_2011 = "{:,.0f}".format(total_sharing_2011)
    st.metric("Total sharing 2011", value=formatted_total_sharing_2011)

with col2:
    total_sharing_2012 = monthly_sharing_2012["Total_Peminjaman"].sum()
    formatted_total_sharing_2012 = "{:,.0f}".format(total_sharing_2012)
    st.metric("Total sharing 2012", value=formatted_total_sharing_2012)

# Membuat plot menggunakan Matplotlib
fig, ax = plt.subplots(figsize=(16, 8))

# Plot data untuk tahun 2011
ax.plot(
    monthly_sharing_2011["Bulan"].dt.month,
    monthly_sharing_2011["Total_Peminjaman"],
    marker='o', 
    linewidth=2,
    color="#FF5733",  # Warna untuk tahun 2011
    label="2011"  # Label untuk legenda
)

# Plot data untuk tahun 2012
ax.plot(
    monthly_sharing_2012["Bulan"].dt.month,
    monthly_sharing_2012["Total_Peminjaman"],
    marker='o', 
    linewidth=2,
    color="#0066FF",  # Warna untuk tahun 2012
    label="2012"  # Label untuk legenda
)

# Mengatur parameter tick untuk sumbu x dan y
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

# Menambahkan judul
ax.set_title('Total Peminjaman Sepeda per Bulan', fontsize=20)

# Menambahkan label sumbu x dan y
ax.set_xlabel('Bulan', fontsize=15)
ax.set_ylabel('Total Peminjaman', fontsize=15)

# Menambahkan legenda
ax.legend(fontsize=15)

# Menambahkan xticks hanya untuk bulan 1-12
plt.xticks(range(1, 13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig)


with st.expander("See explanation"):
    st.write(
        """Berdasarkan grafik yang dihasilkan diatas, dapat dilihat bahwa tren peminjaman sepeda pada tahun 2012 jauh lebih banyak dibandingkan dengan tahun 2011. Selain itu, pada tahun 2012, peak month peminjaman ada pada bulan September dan terjadi penurunan cukup signifikan pada bulan-bulan selanjutnya. Pada tahun 2011, dari awal tahun mengalami peningkatan sampai pada bulan Mei. Namun, bulan-bulan selanjutnya mengalami tren penrurunan sampai akhir tahun. Hal ini menunjukkan bahwa kenaikan penyewaan sepeda dari tahun ke tahun cukup berhasil walaupun di tahun tersebut mengalami naik turun yang signifikan.
        """
    )

# Agregasi data
season_weather_stats = day_df.groupby(["season", "weathersit"]).agg({
    "cnt": ["max", "min", "mean", "std", "sum"]
})

# Ubah multiindex menjadi single index untuk memudahkan visualisasi
season_weather_stats.columns = ['_'.join(col).strip() for col in season_weather_stats.columns.values]
season_weather_stats.reset_index(inplace=True)

st.subheader('Bike Sharing by Season & Weather')

# Membuat plot menggunakan Matplotlib
fig2, ax2 = plt.subplots(figsize=(10, 6))

# Buat stacked bar plot
for weather_sit in season_weather_stats['weathersit'].unique():
    weather_sit_data = season_weather_stats[season_weather_stats['weathersit'] == weather_sit]
    ax2.bar(weather_sit_data['season'], weather_sit_data['cnt_sum'], label=f'Weather {weather_sit}')

# Konfigurasi plot
ax2.set_title('Total Peminjaman Sepeda Berdasarkan Musim dan Kondisi Cuaca')
ax2.set_xlabel('Musim')
ax2.set_ylabel('Total Peminjaman')
ax2.legend(title='Kondisi Cuaca')
ax2.set_xticks(range(1, 5))
ax2.set_xticklabels(['Spring', 'Summer', 'Fall', 'Winter'])

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig2)
with st.expander("See explanation"):
    st.write(
        """Berdasarkan grafik diatas, musim 3 atau musim gugur merupakan salah satu faktor meningkatnya penyewa sepeda. Selain itu, penyewaan tertinggi ketika cuaca sedang cerah sehingga memungkinkan banyak masyarakat menggunakan penyewaan sepeda. Berkebalikan dengan hal tersebut, di berbagai musim dapat dilihat bahwa ketika cuaca tidak mendukung, maka penyewaan sepeda juga ikut menurun. Bahkan, ketika cuaca 4 tidak terdapat penyewa sama sekali. Hal ini dapat disimpulkan bahwa musim dan cuaca pada hari tertentu berpengaruh terhadap tingkat penyewaan sepeda.
        """
    )

st.subheader('Correlation of Weather Factors')

# Menghitung korelasi antara variabel cuaca dan cnt
weather_correlation_matrix = day_df[['temp', 'atemp', 'hum', 'windspeed', 'cnt']].corr()

# Plot heatmap
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.heatmap(weather_correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax3)
ax3.set_title('Korelasi antara Faktor Cuaca dan Jumlah Penyewaan Sepeda')

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig3)
with st.expander("See explanation"):
    st.write(
        """Berdasarkan heatmap korelasi diatas, dapat dilihat faktor terbesar peningkatan penyewa sepeda ada pada faktor temperatur/suhu. Walaupun angka korelasi hanya 0.63, tetapi dapat dinyatakan bahwa semakin hangat/stabil suhunya maka semakin meningkat penyewaan sepeda. Berkebalikan dengan faktor humidity/kelembaban dan windspeed. Hal ini dapat disimpulkan bahwa faktor-faktor cuaca dapat berpengaruh terhadap tingkat penyewaan sepeda.
        """
    )

st.subheader('Segmentation Customer by Working Day')

# Membuat scatter plot
fig4, ax4 = plt.subplots(figsize=(10, 6))

# Scatter plot untuk hari kerja
ax4.scatter(day_df[day_df['workingday'] == 1]['temp'],
            day_df[day_df['workingday'] == 1]['cnt'],
            color='blue',
            label='Hari Kerja')

# Scatter plot untuk hari libur
ax4.scatter(day_df[day_df['workingday'] == 0]['temp'],
            day_df[day_df['workingday'] == 0]['cnt'],
            color='red',
            label='Hari Libur')

ax4.set_xlabel('Temperatur (Celsius)')
ax4.set_ylabel('Jumlah Peminjaman Sepeda')
ax4.set_title('Segmentasi Peminjaman Sepeda berdasarkan Hari Kerja & Hari Libur')
ax4.legend()

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig4)
with st.expander("See explanation"):
    st.write(
        """Berdasarkan grafik dapat dilihat bahwa persebaran penyewa sepeda pada hari kerja lebih banyak dibandingkan saat hari libur. Selain itu, ketika cuaca suhu normal (tidak terlalu panas/dingin), maka jumlah peminjaman juga semakin banyak. Hal ini dapat diartikan bahwa peminjaman sepeda dapat dibagi kedalam beberapa segmentasi, yaitu pelanggan yang bekerja, cuaca cerah, dan hari bekerja.
        """
    )