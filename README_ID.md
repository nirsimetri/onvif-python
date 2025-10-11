# ONVIF Python

[![Lisensi](https://img.shields.io/badge/License-MIT-blue)](https://github.com/nirsimetri/onvif-python?tab=MIT-1-ov-file)
[![DeepWiki](https://img.shields.io/badge/DeepWiki-AI%20Wiki-orange)](https://deepwiki.com/nirsimetri/onvif-python)
[![Rilis](https://img.shields.io/badge/Release-v0.0.4-red?logo=archive)](https://github.com/nirsimetri/onvif-python/releases)
<br>
[![PyPI](https://img.shields.io/badge/PyPI-0.0.4-yellow?logo=archive)](https://pypi.org/project/onvif-python/)
[![Unduhan](https://img.shields.io/pypi/dm/onvif-python?label=PyPI%20Downloads)](https://clickpy.clickhouse.com/dashboard/onvif-python)

Apakah Anda kesulitan menemukan pustaka Python ONVIF yang mendukung perangkat Anda?  
Apakah Anda bingung dengan kompatibilitas berbagai versi ONVIF yang diperbarui setiap enam bulan?

**Proyek ini menyediakan pustaka Python yang komprehensif dan ramah pengembang untuk bekerja dengan perangkat yang sesuai dengan ONVIF.** Pustaka ini dirancang agar andal, mudah diintegrasikan, dan cukup fleksibel untuk mendukung berbagai profil dan layanan ONVIF.  

**[ONVIF](https://www.onvif.org) (Open Network Video Interface Forum)** adalah standar global untuk antarmuka produk keamanan fisik berbasis IP, termasuk kamera jaringan, perekam video, dan sistem terkait.  

Di balik layar, komunikasi ONVIF bergantung pada **[SOAP](https://en.wikipedia.org/wiki/SOAP) (Simple Object Access Protocol)** — protokol pesan berbasis [XML](https://en.wikipedia.org/wiki/XML) dengan definisi skema yang ketat ([WSDL](https://en.wikipedia.org/wiki/Web_Services_Description_Language)/[XSD](https://en.wikipedia.org/wiki/XML_Schema_(W3C))). SOAP memastikan interoperabilitas, tetapi jika digunakan secara langsung dapat menjadi verbose, kompleks, dan rentan terhadap kesalahan.  

Pustaka ini menyederhanakan proses tersebut dengan membungkus komunikasi SOAP ke dalam API Python yang bersih. Anda tidak perlu lagi menangani parsing XML tingkat rendah, namespace, atau token keamanan secara manual — pustaka ini menangani semuanya, memungkinkan Anda untuk fokus pada pembangunan fungsionalitas.  

## Fitur Utama
- Implementasi penuh layanan inti dan profil ONVIF  
- Dukungan untuk penemuan perangkat, streaming media, kontrol PTZ, manajemen event, dan lainnya  
- Abstraksi Pythonic atas permintaan dan respons SOAP (tidak perlu membuat XML secara manual)  
- Arsitektur yang dapat diperluas untuk ekstensi ONVIF khusus  
- Kompatibel dengan beberapa versi spesifikasi ONVIF  
- Skrip contoh dan pengujian disertakan  

## Untuk Siapa Pustaka Ini?
- **Pengembang individu** yang menjelajahi ONVIF atau membangun proyek hobi  
- **Perusahaan** yang membangun platform intelijen video, analitik, atau VMS  
- **Integrator keamanan** yang membutuhkan interoperabilitas ONVIF yang andal di berbagai perangkat

## Instalasi

Dari [PyPI](https://pypi.org/project/onvif-python/) resmi:
```bash
pip install onvif-python
```
Atau klon repositori ini dan instal secara lokal:
```bash
git clone https://github.com/nirsimetri/onvif-python
cd onvif-python
pip install .
```

## Contoh Penggunaan

> [!TIP]
> Anda dapat melihat dokumentasi lengkap yang dihasilkan secara otomatis oleh DeepWiki melalui tautan [onvif-python AI Wiki](https://deepwiki.com/nirsimetri/onvif-python). Saat ini kami belum memiliki situs dokumentasi resmi. Bantu kami membuat lebih banyak contoh dan dokumentasi yang bermanfaat dengan [berkontribusi](https://github.com/nirsimetri/onvif-python?tab=contributing-ov-file).

Berikut adalah contoh sederhana untuk membantu Anda memulai dengan pustaka ONVIF Python. Contoh ini menunjukkan cara menghubungkan ke perangkat yang sesuai dengan ONVIF dan mengambil informasi dasar perangkat.

**1. Inisialisasi ONVIFClient**

Buat instance `ONVIFClient` dengan memberikan alamat IP perangkat Anda, port, nama pengguna, dan kata sandi:

```python
from onvif import ONVIFClient

client = ONVIFClient("192.168.1.17", 8000, "admin", "admin123")
```

**2. Buat Instance Layanan**

`ONVIFClient` menyediakan beberapa layanan utama yang dapat diakses melalui metode berikut:

- `client.devicemgmt()` — Manajemen Perangkat
- `client.events()` — Events
- `client.imaging()` — Imaging
- `client.media()` — Media
- `client.ptz()` — PTZ (Pan-Tilt-Zoom)
- `client.analytics()` — Analytics

...dan seterusnya, periksa [Layanan ONVIF yang Diimplementasikan](https://github.com/nirsimetri/onvif-python?tab=readme-ov-file#implemented-onvif-services) untuk detail lebih lanjut

Contoh penggunaan:
```python
device = client.devicemgmt()      # Manajemen Perangkat (Inti)
media = client.media()            # Media
```

**3. Dapatkan Informasi Perangkat**

Ambil informasi dasar tentang perangkat, seperti produsen, model, versi firmware, dan nomor seri menggunakan layanan `devicemgmt()`:

```python
info = device.GetDeviceInformation()
print(info)
# Contoh: {'Manufacturer': '..', 'Model': '..', 'FirmwareVersion': '..', 'SerialNumber': '..'}
```

**4. Dapatkan URL RTSP**

Ambil URL aliran RTSP untuk streaming video langsung dari perangkat menggunakan layanan `media()`:

```python
profile = media.GetProfiles()[0]  # gunakan profil pertama
stream = media.GetStreamUri(
    ProfileToken=profile.token, 
	StreamSetup={"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}}
)
print(stream)
# Contoh: {'Uri': 'rtsp://192.168.1.17:8554/Streaming/Channels/101', ...}
```

Jelajahi penggunaan lanjutan dan operasi spesifik layanan di folder [`examples/`](./examples/).

> [!IMPORTANT]
> Jika Anda baru mengenal ONVIF dan ingin mempelajari lebih lanjut, kami sangat menyarankan untuk mengikuti kursus online gratis resmi yang disediakan oleh ONVIF di [Kursus Pengantar ONVIF](https://www.onvif.org/about/introduction-to-onvif-course). Harap dicatat bahwa kami tidak didukung atau disponsori oleh ONVIF, lihat [Pemberitahuan Hukum](#legal-notice) untuk detailnya.

## Verifikasi Perangkat: Mengapa Menggunakan GetCapabilities Terlebih Dahulu?

> [!WARNING]
> Sebelum melakukan operasi apa pun pada perangkat ONVIF, sangat disarankan untuk memverifikasi kemampuan dan layanan apa yang tersedia dan didukung oleh perangkat menggunakan metode `GetCapabilities` dari instance layanan `devicemgmt()`. Langkah ini memastikan bahwa aplikasi Anda hanya berinteraksi dengan fitur yang benar-benar diimplementasikan oleh perangkat, mencegah kesalahan, dan meningkatkan kompatibilitas.

**Mengapa memverifikasi kemampuan perangkat dengan GetCapabilities?**

- **Keanekaragaman Perangkat:** Tidak semua perangkat ONVIF mendukung setiap kemampuan atau layanan. Kemampuan dapat bervariasi berdasarkan produsen, model, firmware, atau konfigurasi.
- **Pencegahan Kesalahan:** Mencoba menggunakan fitur yang tidak didukung dapat mengakibatkan permintaan gagal, pengecualian, atau perilaku yang tidak terdefinisi.
- **Deteksi Fitur Dinamis:** Perangkat dapat mengaktifkan atau menonaktifkan kemampuan dari waktu ke waktu (misalnya, setelah pembaruan firmware atau perubahan konfigurasi).
- **Integrasi yang Dioptimalkan:** Dengan memeriksa kemampuan yang tersedia, aplikasi Anda dapat menyesuaikan alur kerja dan UI untuk mencocokkan fitur perangkat yang sebenarnya.

**Cara memverifikasi kemampuan perangkat:**

Panggil `GetCapabilities` pada instance `devicemgmt()` Anda:

```python
from onvif import ONVIFClient

client = ONVIFClient("192.168.1.17", 8000, "admin", "admin123")
capabilities = client.devicemgmt().GetCapabilities()
print(capabilities)
# Contoh: {'Media': {'XAddr': 'http://192.168.1.17:8000/onvif/media_service', ...}, 'PTZ': {...}, ...}
```

Tinjau kamus yang dikembalikan untuk menentukan kemampuan dan layanan (misalnya, Media, PTZ, Analitik) yang tersedia sebelum melakukan operasi lebih lanjut.

## Perangkat yang Diuji

Pustaka ini telah diuji dengan berbagai perangkat yang sesuai dengan ONVIF. Untuk daftar terbaru dan paling lengkap dari perangkat yang telah diverifikasi bekerja dengan pustaka ini, silakan merujuk ke:

- [Daftar perangkat yang diuji (device-test)](https://github.com/nirsimetri/onvif-products-directory/blob/main/device-test)

Jika perangkat Anda belum terdaftar saat ini, jangan ragu untuk menyumbangkan hasil pengujian atau umpan balik Anda melalui Issues atau Discussions di [onvif-products-directory](https://github.com/nirsimetri/onvif-products-directory). Kontribusi Anda akan sangat berharga bagi komunitas dan publik.

> [!IMPORTANT]
> Kontribusi pengujian perangkat harus dilakukan dengan perangkat nyata dan menggunakan skrip yang disediakan di repositori [onvif-products-directory](https://github.com/nirsimetri/onvif-products-directory). Pastikan untuk berkontribusi menggunakan model perangkat yang belum terdaftar.

## Profil ONVIF yang Didukung

Pustaka ini sepenuhnya mendukung semua Profil ONVIF utama yang tercantum di bawah ini. Setiap profil mewakili serangkaian fitur dan kasus penggunaan standar, memastikan interoperabilitas antara perangkat dan klien yang sesuai dengan ONVIF. Anda dapat menggunakan pustaka ini untuk berintegrasi dengan perangkat dan sistem yang mengimplementasikan salah satu profil ini.

| Nama      | Spesifikasi | Fitur Utama | Kasus Penggunaan Umum | Dukungan |
|-----------|----------------|---------------|------------------|---------|
| Profile_S | [Dokumen](https://www.onvif.org/wp-content/uploads/2019/12/ONVIF_Profile_-S_Specification_v1-3.pdf) | Streaming video, PTZ, audio, multicasting | Pemancar video jaringan (kamera) dan penerima (perekam, VMS) | ✅ Ya |
| Profile_G | [Dokumen](https://www.onvif.org/wp-content/uploads/2017/01/ONVIF_Profile_G_Specification_v1-0.pdf) | Perekaman, pencarian, pemutaran ulang, penyimpanan video | Perekam video, perangkat penyimpanan | ✅ Ya |
| Profile_T | [Dokumen](https://www.onvif.org/wp-content/uploads/2018/09/ONVIF_Profile_T_Specification_v1-0.pdf) | Streaming video lanjutan (H.265, metadata analitik, deteksi gerakan) | Kamera modern dan klien | ✅ Ya |
| Profile_C | [Dokumen](https://www.onvif.org/wp-content/uploads/2017/01/2013_12_ONVIF_Profile_C_Specification_v1-0.pdf) | Kontrol akses, pemantauan pintu | Pengontrol pintu, sistem akses | ✅ Ya |
| Profile_A | [Dokumen](https://www.onvif.org/wp-content/uploads/2017/06/ONVIF_Profile_A_Specification_v1-0.pdf) | Konfigurasi kontrol akses lanjutan, manajemen kredensial | Klien dan perangkat kontrol akses | ✅ Ya |
| Profile_D | [Dokumen](https://www.onvif.org/wp-content/uploads/2021/06/onvif-profile-d-specification-v1-0.pdf) | Periferal kontrol akses (kunci, sensor, relai) | Perangkat periferal untuk kontrol akses | ✅ Ya |
| Profile_M | [Dokumen](https://www.onvif.org/wp-content/uploads/2024/04/onvif-profile-m-specification-v1-1.pdf) | Metadata, analitik event, deteksi objek | Perangkat analitik, klien metadata | ✅ Ya |

Untuk deskripsi lengkap setiap profil dan fiturnya, kunjungi [Profil ONVIF](https://www.onvif.org/profiles/).

## Layanan ONVIF yang Diimplementasikan

> [!NOTE]
> Untuk detail tentang fungsi dan metode layanan yang tersedia yang telah diimplementasikan dalam pustaka ini, lihat kode sumber di [`onvif/services/`](./onvif/services). Atau jika Anda ingin membaca dalam format yang lebih baik, kunjungi [onvif-python AI Wiki](https://deepwiki.com/nirsimetri/onvif-python).

Berikut adalah daftar layanan ONVIF yang diimplementasikan dan didukung oleh pustaka ini, bersama dengan tautan ke spesifikasi resmi, definisi layanan, dan berkas skema seperti yang dirujuk dari [Spesifikasi Pengembang ONVIF](https://developer.onvif.org/pub/specs/branches/development/doc/index.html). Tabel ini memberikan gambaran cepat tentang fitur ONVIF yang tersedia dan dokumentasi teknisnya untuk tujuan integrasi dan pengembangan.

| Layanan                | Spesifikasi                | Definisi Layanan         | Skema                               | Status     |
|------------------------|----------------------------|--------------------------|-------------------------------------|------------|
| Device Management      | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Core.xml) | [devicemgmt.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/device/wsdl/devicemgmt.wsdl) | [onvif.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schema/onvif.xsd) <br> [common.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schema/common.xsd) | ✅ Lengkap |
| Events                 | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Core.xml) | [event.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/events/wsdl/event.wsdl) | [onvif.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schema/onvif.xsd) <br> [common.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schema/common.xsd) | ⚠️ Parsial |
| Access Control         | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/AccessControl.xml) | [accesscontrol.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/pacs/accesscontrol.wsdl) | [types.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/pacs/types.xsd) | ✅ Lengkap |
| Access Rules           | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/AccessRules.xml) | [accessrules.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/accessrules/wsdl/accessrules.wsdl) | - | ✅ Lengkap |
| Action Engine          | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/ActionEngine.xml) | [actionengine.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/actionengine.wsdl) | - | ✅ Lengkap |
| Analytics              | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Analytics.xml) | [analytics.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/wsdl/analytics.wsdl) | [rules.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/rules.xsd) <br> [humanbody.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/humanbody.xsd) <br> [humanface.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/humanface.xsd) | ✅ Lengkap |
| Application Management | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/AppMgmt.xml) | [appmgmt.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/appmgmt/wsdl/appmgmt.wsdl) | - | ✅ Lengkap |
| Authentication Behavior| [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/AuthenticationBehavior.xml) | [authenticationbehavior.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/authenticationbehavior/wsdl/authenticationbehavior.wsdl) | - | ✅ Lengkap |
| Cloud Integration      | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/CloudIntegration.xml) | [cloudintegration.yaml](https://developer.onvif.org/pub/specs/branches/development/doc/yaml.php?yaml=cloudintegration.yaml) | - | ❌ Belum |
| Credential             | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Credential.xml) | [credential.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/credential/wsdl/credential.wsdl) | - | ✅ Lengkap |
| Device IO              | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/DeviceIo.xml) | [deviceio.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/deviceio.wsdl) | - | ✅ Lengkap |
| Display                | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Display.xml) | [display.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/display.wsdl) | - | ✅ Lengkap |
| Door Control           | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/DoorControl.xml) | [doorcontrol.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/pacs/doorcontrol.wsdl) | - | ✅ Lengkap |
| Imaging                | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Imaging.xml) | [imaging.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/imaging/wsdl/imaging.wsdl) | - | ✅ Lengkap |
| Media                  | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Media.xml) | [media.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/media/wsdl/media.wsdl) | - | ✅ Lengkap |
| Media 2                | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Media2.xml) | [media2.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/media/wsdl/media.wsdl) | - | ✅ Lengkap |
| Provisioning           | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Provisioning.xml) | [provisioning.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/provisioning/wsdl/provisioning.wsdl) | - | ✅ Lengkap |
| PTZ                    | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/PTZ.xml) | [ptz.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/ptz/wsdl/ptz.wsdl) | - | ✅ Lengkap |
| Receiver               | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Receiver.xml) | [receiver.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/receiver.wsdl) | - | ✅ Lengkap |
| Recording Control      | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/RecordingControl.xml) | [recording.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/recording.wsdl) | - | ✅ Lengkap |
| Recording Search       | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/RecordingSearch.xml) | [search.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/search.wsdl) | - | ✅ Lengkap |
| Replay Control         | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Replay.xml) | [replay.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/replay.wsdl) | - | ✅ Lengkap |
| Resource Query         | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/ResourceQuery.xml) | - | - | ❌ Ada ide? |
| Schedule               | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Schedule.xml) | [schedule.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schedule/wsdl/schedule.wsdl) | - | ✅ Lengkap |
| Security               | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Security.xml) | [advancedsecurity.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl) | - | ✅ Lengkap |
| Thermal                | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Thermal.xml) | [thermal.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/thermal/wsdl/thermal.wsdl) | [radiometry.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/radiometry.xsd) | ✅ Lengkap |
| Uplink                 | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/Uplink.xml) | [uplink.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/uplink/wsdl/uplink.wsdl) | - | ✅ Lengkap |
| WebRTC                 | [Dokumen](https://developer.onvif.org/pub/specs/branches/development/doc/WebRTC.xml) | - | - | ❌ Ada ide? |

## Pengikatan Layanan (Service Bindings) di ONVIF

Layanan ONVIF didefinisikan oleh binding WSDL. Di pustaka ini, ada dua pola utama:

### 1. Layanan Single Binding

Sebagian besar layanan ONVIF menggunakan satu binding, dipetakan langsung ke satu endpoint. Layanan ini diakses melalui metode klien yang sederhana, dan binding/xAddr selalu diketahui dari kapabilitas perangkat.

<details>
<summary>Contoh:</summary>

```python
client.devicemgmt()   # DeviceBinding
client.media()        # MediaBinding
client.ptz()          # PTZBinding
...
```

✅ Layanan ini dianggap tetap (fixed) dan selalu diakses langsung.

</details>

### 2. Layanan Multi-Binding

Beberapa layanan ONVIF memiliki banyak binding dalam WSDL yang sama. Biasanya mencakup:
- Binding **root** (titik masuk utama)
- Satu atau lebih **sub-binding**, yang ditemukan atau dibuat secara dinamis (misalnya setelah pembuatan subscription/konfigurasi)

<details>
<summary>Contoh:</summary>

1. **Events**
   - **Root:** `EventBinding`
   - **Sub-binding:**
     - `PullPointSubscriptionBinding` (dibuat via `CreatePullPointSubscription`)
     - `SubscriptionManagerBinding` (mengelola subscription yang ada)
     - `NotificationProducerBinding`

   Penggunaan di pustaka:
   ```python
   client.events()                    # root binding
   client.pullpoint(subscription)     # sub-binding (dinamis, via SubscriptionReference.Address)
   client.subscription(subscription)  # sub-binding (dinamis, via SubscriptionReference.Address)
   ```

2. **Security (Advanced Security)**
   - **Root:** `AdvancedSecurityServiceBinding`
   - **Sub-binding:**
     - `AuthorizationServerBinding`
     - `KeystoreBinding`
     - `CredentialBinding`
     - `JWTBinding`
     - `Dot1XBinding`
     - `TLSServerBinding`
     - `MediaSigningBinding`

   Penggunaan di pustaka:
   ```python
   client.security()                  # root binding
   client.authorizationserver(xaddr)  # sub-binding accessor (memerlukan xAddr)
   client.keystore(xaddr)
   client.jwt(xaddr)
   client.dot1x(xaddr)
   client.tlsserver(xaddr)
   client.mediasigning(xaddr)
   ```

3. **Analytics (Analitik)**
   - **Root:** `AnalyticsEngineBinding`
   - **Sub-binding:**
     - `RuleEngineBinding`

   Penggunaan di pustaka:
   ```python
   client.analytics()   # root binding
   client.ruleengine()  # sub-binding accessor
   ```
</details>

### Ringkasan

- **Layanan single binding:** Selalu diakses langsung (mis. `client.media()`).
- **Layanan multi-binding:** Memiliki root + sub-binding. Root bersifat tetap; sub-binding mungkin memerlukan pembuatan dinamis atau xAddr eksplisit (mis. `client.pullpoint(subscription)`, `client.authorizationserver(xaddr)`).

## Peningkatan Mendatang (Pantau dan beri bintang ⭐ repo ini)

- [ ] Mengimplementasikan model data terstruktur untuk Skema ONVIF menggunakan [xsdata](https://github.com/tefra/xsdata).
- [ ] Integrasi [xmltodict](https://github.com/martinblech/xmltodict) untuk parsing dan konversi XML yang lebih sederhana.
- [ ] Menambahkan kemampuan agar `ONVIFClient` menerima layanan `wsdl_path` kustom.
- [ ] Menambahkan mode debugging dengan raw XML pada permintaan dan respons SOAP.
- [ ] Meningkatkan dokumentasi dengan referensi API dan diagram (bukan dari [AI Wiki](https://deepwiki.com/nirsimetri/onvif-python)).
- [ ] Menambah lebih banyak contoh penggunaan untuk fitur lanjutan.
- [ ] Menambah benchmarking dan metrik performa.
- [ ] Menambah template konfigurasi perangkat dari komunitas.
- [ ] Mengimplementasikan layanan ONVIF yang hilang atau masih parsial.
- [ ] Menambahkan fungsi untuk mengekspos perangkat ONVIF (untuk tujuan debug oleh komunitas).

## Proyek Terkait

- [onvif-products-directory](https://github.com/nirsimetri/onvif-products-directory):
	Proyek ini adalah suite agregasi dan manajemen data ONVIF yang komprehensif, dirancang untuk membantu pengembang menelusuri, menganalisis, dan memproses informasi produk yang sesuai ONVIF dari ratusan produsen di seluruh dunia. Menyediakan struktur terpadu untuk data perangkat, klien, dan perusahaan, sehingga mempermudah riset, membangun integrasi, dan menghasilkan statistik untuk analisis ekosistem ONVIF.

- (segera) [onvif-rest-server](https://github.com/nirsimetri/onvif-rest-server):
	Server API RESTful untuk perangkat ONVIF, memungkinkan integrasi mudah manajemen perangkat ONVIF, streaming media, dan kemampuan lainnya ke aplikasi dan layanan web.

- (segera) [onvif-mcp](https://github.com/nirsimetri/onvif-mcp):
	Server Model Context Protocol (MCP) untuk ONVIF, menyediakan API terpadu dan integrasi berbasis konteks untuk perangkat, klien, dan layanan ONVIF. Memungkinkan otomatisasi tingkat lanjut, orkestrasi, dan interoperabilitas di seluruh perangkat dan klien yang sesuai ONVIF.

## Alternatif

Jika Anda mencari pustaka Python ONVIF lainnya, berikut beberapa alternatif:

- [python-onvif-zeep](https://github.com/FalkTannhaeuser/python-onvif-zeep):
	Pustaka klien ONVIF sinkron untuk Python, menggunakan Zeep untuk komunikasi SOAP. Berfokus pada kompatibilitas dan kemudahan penggunaan untuk operasi perangkat ONVIF standar. Cocok untuk skrip dan aplikasi yang tidak memerlukan async.

- [python-onvif-zeep-async](https://github.com/openvideolibs/python-onvif-zeep-async):
	Pustaka klien ONVIF asinkron untuk Python, berbasis Zeep dan asyncio. Cocok untuk aplikasi yang memerlukan operasi non-blok dan komunikasi perangkat secara konkuren. Mendukung banyak layanan ONVIF dan aktif dipelihara.

## Referensi
- [Spesifikasi Resmi ONVIF](https://www.onvif.org/profiles/specifications/specification-history/)
- [Repositori Resmi ONVIF Specs](https://github.com/onvif/specs)
- [Indeks Operasi Layanan ONVIF 2.0](https://www.onvif.org/onvif/ver20/util/operationIndex.html)
- [Contoh Penggunaan](./examples/)

## Pernyataan Hukum

Proyek ini adalah **implementasi open-source independen** dari spesifikasi [ONVIF](https://www.onvif.org). Proyek ini **tidak berafiliasi, tidak didukung, dan tidak disponsori oleh ONVIF** atau perusahaan anggotanya.

- Nama **“ONVIF”** dan logo ONVIF adalah merek dagang terdaftar milik organisasi ONVIF.  
- Setiap referensi ke ONVIF dalam proyek ini dibuat semata-mata untuk tujuan menjelaskan interoperabilitas dengan perangkat dan layanan yang sesuai ONVIF.  
- Penggunaan merek ONVIF di repositori ini murni nominatif dan tidak menyiratkan kemitraan, sertifikasi, atau status resmi apa pun.
- Proyek ini menyertakan berkas WSDL/XSD/HTML dari spesifikasi resmi ONVIF.
- Berkas-berkas tersebut adalah © ONVIF dan didistribusikan ulang di sini untuk tujuan interoperabilitas.
- Semua hak atas spesifikasi ONVIF adalah milik ONVIF.

Jika Anda memerlukan perangkat atau klien yang tersertifikasi sesuai ONVIF, silakan merujuk ke [daftar produk konforman ONVIF](https://www.onvif.org/conformant-products/). Untuk referensi otoritatif dan spesifikasi ONVIF resmi terbaru, silakan lihat [Spesifikasi Resmi ONVIF](https://www.onvif.org/profiles/specifications/specification-history/).

Penggunaan pustaka ini merupakan risiko Anda sendiri. Penulis dan kontributor tidak bertanggung jawab atas kerusakan apa pun, langsung maupun tidak langsung, yang timbul dari penggunaannya.

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT. Lihat [LICENSE](./LICENSE.md) untuk detailnya.