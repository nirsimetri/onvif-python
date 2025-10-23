# ONVIF Python

[![License](https://img.shields.io/badge/License-MIT-blue)](https://github.com/nirsimetri/onvif-python?tab=MIT-1-ov-file)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/nirsimetri/onvif-python)
[![PyPI](https://img.shields.io/badge/PyPI-0.1.4-orange?logo=archive)](https://pypi.org/project/onvif-python/)
[![Downloads](https://img.shields.io/pypi/dm/onvif-python?label=PyPI%20Downloads&color=red)](https://clickpy.clickhouse.com/dashboard/onvif-python)
<br>
[![Build](https://github.com/nirsimetri/onvif-python/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/nirsimetri/onvif-python/actions/workflows/python-app.yml)
[![Upload Python Package](https://github.com/nirsimetri/onvif-python/actions/workflows/python-publish.yml/badge.svg)](https://github.com/nirsimetri/onvif-python/actions/workflows/python-publish.yml)

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

## Persyaratan

- **Python**: 3.9 atau lebih tinggi
- **Dependencies**:
  - [`zeep>=4.3.0`](https://github.com/mvantellingen/python-zeep) - Klien SOAP untuk komunikasi ONVIF
  - [`requests>=2.32.0`](https://github.com/psf/requests) - Library HTTP untuk permintaan jaringan

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

# Koneksi dasar
client = ONVIFClient("192.168.1.17", 8000, "admin", "admin123")

# Dengan direktori WSDL kustom (opsional)
client = ONVIFClient(
    "192.168.1.17", 8000, "admin", "admin123",
    wsdl_dir="/path/to/custom/wsdl"  # Gunakan direktori WSDL kustom
)
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

## ONVIF CLI

> [!NOTE]
> CLI secara otomatis terinstal saat Anda menginstal paket `onvif-python`, lihat [Instalasi](#instalasi). Fitur ini telah tersedia sejak `onvif-python` versi [`0.1.1`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.1).

![Windows](https://img.shields.io/badge/Windows-0078D6?style=plastic&logo=gitforwindows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=plastic&logo=linux&logoColor=black)
![macOS](https://img.shields.io/badge/macOS-1A9FEE?style=plastic&logo=apple&logoColor=black)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846?style=plastic&logo=raspberrypi&logoColor=black)

Pustaka ini menyertakan antarmuka baris perintah (CLI) yang kuat untuk berinteraksi dengan perangkat ONVIF langsung dari terminal Anda. CLI ini mendukung eksekusi perintah langsung dan mode shell interaktif, menyediakan cara yang fleksibel dan efisien untuk mengelola dan men-debug perangkat ONVIF.

### Fitur

- **Shell Interaktif:** Shell yang ramah pengguna dengan pelengkapan tab, riwayat perintah, dan output berwarna.
- **Eksekusi Perintah Langsung:** Jalankan perintah ONVIF langsung dari terminal untuk skrip dan otomatisasi.
- **Penemuan Otomatis:** Secara otomatis mendeteksi layanan yang tersedia di perangkat.
- **Manajemen Koneksi:** Mendukung HTTP/HTTPS, timeout kustom, dan verifikasi SSL.
- **Manajemen Data:** Simpan hasil dari perintah dan gunakan sebagai parameter dalam perintah berikutnya.
- **Lintas Platform:** Bekerja di Windows, macOS, Linux, dan Raspberry Pi.

### Tangkapan layar

<table>
  <tr>
    <td width="34.2%">
      <a href="https://github.com/nirsimetri/onvif-python">
        <img src="https://raw.githubusercontent.com/nirsimetri/onvif-python/refs/heads/main/assets/onvif_cli.png" />
      </a>
    </td>
    <td width="65.8%">
        <a href="https://github.com/nirsimetri/onvif-python">
        <img src="https://raw.githubusercontent.com/nirsimetri/onvif-python/refs/heads/main/assets/onvif_operations.png" />
        </a>
    </td>
  </tr>
  <tr>
    <th align="center">
      Tampilan pertama
    </th>
    <th align="center">
      Daftar operasi yang tersedia
    </th>
  </tr>
</table>

### Perintah Bantuan

<details>
<summary><b>1. CLI Langsung</b></summary> 

```bash
usage: onvif [-h] [--host HOST] [--port PORT] [--username USERNAME] [--password PASSWORD] [--discover] [--timeout TIMEOUT] [--https] [--no-verify]
             [--no-patch] [--interactive] [--debug] [--wsdl WSDL] [--cache {all,db,mem,none}] [--version]
             [service] [method] [params ...]

ONVIF Terminal Client — v0.1.4
https://github.com/nirsimetri/onvif-python

positional arguments:
  service               ONVIF service name (e.g., devicemgmt, media, ptz)
  method                Service method name (e.g., GetCapabilities, GetProfiles)
  params                Method parameters as Simple Parameter or JSON string

options:
  -h, --help            show this help message and exit
  --host HOST, -H HOST  ONVIF device IP address or hostname
  --port PORT, -P PORT  ONVIF device port (default: 80)
  --username USERNAME, -u USERNAME
                        Username for authentication
  --password PASSWORD, -p PASSWORD
                        Password for authentication
  --discover, -d        Discover ONVIF devices on the network using WS-Discovery
  --timeout TIMEOUT     Connection timeout in seconds (default: 10)
  --https               Use HTTPS instead of HTTP
  --no-verify           Disable SSL certificate verification
  --no-patch            Disable ZeepPatcher
  --interactive, -i     Start interactive mode
  --debug               Enable debug mode with XML capture
  --wsdl WSDL           Custom WSDL directory path
  --cache {all,db,mem,none}
                        Caching mode for ONVIFClient (default: all). 'all': memory+disk, 'db': disk-only, 'mem': memory-only, 'none': disabled.
  --version, -v         Show ONVIF CLI version and exit

Examples:
  # Discover ONVIF devices on network
  onvif --discover --username admin --password admin123 --interactive
  onvif media GetProfiles --discover --username admin
  onvif -d -i

  # Direct command execution
  onvif devicemgmt GetCapabilities Category=All --host 192.168.1.17 --port 8000 --username admin --password admin123
  onvif ptz ContinuousMove ProfileToken=Profile_1 Velocity={"PanTilt": {"x": -0.1, "y": 0}} --host 192.168.1.17 --port 8000 --username admin --password admin123

  # Interactive mode
  onvif --host 192.168.1.17 --port 8000 --username admin --password admin123 --interactive

  # Prompting for username and password
  # (if not provided)
  onvif -H 192.168.1.17 -P 8000 -i

  # Using HTTPS
  onvif media GetProfiles --host camera.example.com --port 443 --username admin --password admin123 --https
```

</details>

<details>
<summary><b>2. Shell Interaktif</b></summary> 


```bash
ONVIF Interactive Shell Commands - v0.1.4
https://github.com/nirsimetri/onvif-python

Basic Commands:
  capabilities, caps       - Show device capabilities
  services                 - Show available services with details
  info                     - Show connection and device information
  exit, quit               - Exit the shell
  shortcuts                - Show available shortcuts

Navigation Commands:
  <service>                - Enter service mode (e.g., devicemgmt, media)
  cd <service>             - Enter service mode (alias)
  ls                       - List commands/services/methods in grid format
  up                       - Exit current service mode (go up one level)
  pwd                      - Show current service context
  clear                    - Clear terminal screen
  help <command>           - Show help for a specific command

Service Mode Commands:
  desc <method>            - Show method documentation
  type <method>            - Show input/output types from WSDL

Method Execution:
  <method>                 - Execute method without parameters
  <method> {"param": "value"}  - Execute method with JSON parameters
  <method> param=value     - Execute method with simple parameters

Data Management:
  store <name>             - Store last result with a name
  show <name>              - Show stored data
  show <name>.attribute    - Show specific attribute
  show                     - List all stored data
  rm <name>                - Remove stored data by name
  cls                      - Clear all stored data

Using Stored Data in Methods:
  Use $variable syntax to reference stored data in method parameters:
  - $profiles[0].token                    - Access list element and attribute
  - $profiles[0].VideoSourceConfiguration.SourceToken

  Example:
    GetProfiles                           - Get profiles
    store profiles                        - Store result
    show profiles[0].token                - Show first profile token
    GetImagingSettings VideoSourceToken=$profiles[0].VideoSourceConfiguration.SourceToken

Debug Commands:
  debug                    - Show last SOAP request & response (if --debug enabled)

Tab Completion:
  Use TAB key for auto-completion of commands, services, and methods
  Type partial commands to see suggestions

Examples:
  192.168.1.17:8000 > caps                # Show capabilities
  192.168.1.17:8000 > dev<TAB>            # Completes to 'devicemgmt'
  192.168.1.17:8000 > cd devicemgmt       # Enter device management
  192.168.1.17:8000/devicemgmt > Get<TAB> # Show methods starting with 'Get'
  192.168.1.17:8000/devicemgmt > GetServices {"IncludeCapability": true}
  192.168.1.17:8000/devicemgmt > GetServices IncludeCapability=True
  192.168.1.17:8000/devicemgmt > store services_info
  192.168.1.17:8000/devicemgmt > up       # Exit service mode
  192.168.1.17:8000 >                     # Back to root context
```

</details>

### Penggunaan

**1. Mode Interaktif**

Shell interaktif direkomendasikan untuk eksplorasi dan debugging. Ini menyediakan cara intuitif untuk menavigasi layanan, memanggil metode, dan melihat hasil.

Untuk memulai shell interaktif, berikan detail koneksi:

```bash
onvif --host 192.168.1.17 --port 8000 --username admin --password admin123 -i
```

Jika Anda tidak menyertakan nama pengguna atau kata sandi, Anda akan diminta untuk memasukkannya secara aman.

**Perintah Shell Interaktif:**
| Perintah | Deskripsi |
|---|---|
| `help` | Tampilkan informasi bantuan |
| `ls` | Daftar layanan atau metode yang tersedia dalam konteks saat ini |
| `cd <service>` | Masuk ke mode layanan (mis., `cd devicemgmt`) |
| `up` | Kembali ke konteks root |
| `pwd` | Tampilkan konteks layanan saat ini |
| `desc <method>` | Tampilkan dokumentasi untuk sebuah metode |
| `store <name>` | Simpan hasil terakhir dengan nama variabel |
| `show <name>` | Tampilkan variabel yang disimpan |
| `exit` / `quit` | Keluar dari shell |

> [!IMPORTANT]
> Anda dapat melihat semua perintah lainnya yang tersedia di shell interaktif dengan mencobanya langsung. Shell interaktif menjalankan pemeriksaan kesehatan latar belakang secara berkala untuk mendeteksi kehilangan koneksi. Shell ini menggunakan ping TCP diam-diam agar tidak mengganggu pekerjaan Anda dan akan otomatis keluar jika perangkat tidak dapat dijangkau, mirip dengan sesi SSH.

**2. Penemuan Perangkat (WS-Discovery)**

CLI menyertakan fitur penemuan perangkat ONVIF otomatis menggunakan protokol WS-Discovery. Fitur ini memungkinkan Anda menemukan semua perangkat yang sesuai dengan ONVIF di jaringan lokal Anda tanpa perlu mengetahui alamat IP mereka terlebih dahulu.

**Temukan dan Terhubung Secara Interaktif:**
```bash
# Temukan perangkat dan masuk ke mode interaktif
onvif --discover --username admin --password admin123 --interactive

# Bentuk singkat
onvif -d -u admin -p admin123 -i

# Temukan dan interaktif (akan meminta kredensial)
onvif -d -i
```

**Temukan dan Eksekusi Perintah:**
```bash
# Temukan perangkat dan eksekusi perintah pada perangkat yang dipilih
onvif media GetProfiles --discover --username admin --password admin123

# Bentuk singkat
onvif media GetProfiles -d -u admin -p admin123
```

**Cara Kerja Penemuan Perangkat:**

1. **Pemindaian Jaringan Otomatis**: Mengirim pesan WS-Discovery Probe ke alamat multicast `239.255.255.250:3702`
2. **Deteksi Perangkat**: Mendengarkan respons ProbeMatch dari perangkat ONVIF (timeout default: 4 detik)
3. **Pemilihan Interaktif**: Menampilkan daftar bernomor dari perangkat yang ditemukan dengan detail mereka:
   - UUID Perangkat (Endpoint Reference)
   - XAddrs (URL layanan ONVIF)
   - Tipe Perangkat (mis., NetworkVideoTransmitter)
   - Scopes (informasi nama, lokasi, hardware, profil)
4. **Koneksi**: Setelah Anda memilih perangkat, CLI otomatis terhubung menggunakan host dan port yang ditemukan

**Contoh Output Penemuan:**
```
Discovering ONVIF devices on network...
Network interface: 192.168.1.100
Timeout: 4s

Found 2 ONVIF device(s):

[1] 192.168.1.14:2020
    [id] uuid:3fa1fe68-b915-4053-a3e1-a8294833fe3c
    [xaddrs] http://192.168.1.14:2020/onvif/device_service
    [types] tdn:NetworkVideoTransmitter
    [scopes] [name/C210] [hardware/C210] [Profile/Streaming] [location/Hong Kong] [type/NetworkVideoTransmitter]

[2] 192.168.1.17:8000
    [id] urn:uuid:7d04ff31-61e6-11f0-a00c-6056eef47207
    [xaddrs] http://192.168.1.17:8000/onvif/device_service
    [types] dn:NetworkVideoTransmitter tds:Device
    [scopes] [type/NetworkVideoTransmitter] [location/unknown] [name/IPC_123465959]

Select device number 1-2 or q to quit: 1

Selected: 192.168.1.14:2020
```

**Catatan:**

- Penemuan hanya bekerja di jaringan lokal (subnet yang sama)
- Beberapa jaringan mungkin memblokir lalu lintas multicast (periksa pengaturan firewall)
- Argumen `--host` dan `--port` tidak diperlukan saat menggunakan `--discover`
- Anda masih dapat memberikan `--username` dan `--password` di awal untuk menghindari prompt

**3. Eksekusi Perintah Langsung**

Anda juga dapat mengeksekusi satu perintah ONVIF secara langsung. Ini berguna untuk skrip atau pengecekan cepat.

**Sintaks:**
```bash
onvif <service> <method> [parameters...] -H <host> -P <port> -u <user> -p <pass>
```

**Contoh:**
```bash
# Dapatkan kapabilitas perangkat
onvif devicemgmt GetCapabilities Category=All -H 192.168.1.17 -P 8000 -u admin -p admin123

# Gerakkan kamera PTZ
onvif ptz ContinuousMove ProfileToken=Profile_1 Velocity='{"PanTilt": {"x": 0.1}}' -H 192.168.1.17 -P 8000 -u admin -p admin123
```

### Parameter CLI

Semua parameter `ONVIFClient` (seperti `--timeout`, `--https`, `--cache`, dll.) tersedia sebagai argumen baris perintah. Gunakan `onvif --help` untuk melihat semua opsi yang tersedia.

## Parameter ONVIFClient

Kelas `ONVIFClient` menyediakan berbagai opsi konfigurasi untuk menyesuaikan perilaku koneksi, strategi caching, pengaturan keamanan, dan kemampuan debugging. Berikut adalah deskripsi detail dari semua parameter yang tersedia:

<details>
<summary><b>Parameter Dasar</b></summary>

| Parameter | Tipe | Wajib | Default | Deskripsi |
|-----------|------|-------|---------|-----------|
| `host` | `str` | ✅ Ya | - | Alamat IP atau hostname perangkat ONVIF (mis., `"192.168.1.17"`) |
| `port` | `int` | ✅ Ya | - | Nomor port untuk layanan ONVIF (port umum: `80`, `8000`, `8080`) |
| `username` | `str` | ✅ Ya | - | Nama pengguna untuk autentikasi perangkat (menggunakan digest authentication) |
| `password` | `str` | ✅ Ya | - | Kata sandi untuk autentikasi perangkat |

</details>

<details>
<summary><b>Parameter Koneksi</b></summary>

| Parameter | Tipe | Wajib | Default | Deskripsi |
|-----------|------|-------|---------|-----------|
| `timeout` | `int` | ❌ Tidak | `10` | Timeout koneksi dalam detik untuk permintaan SOAP |
| `use_https` | `bool` | ❌ Tidak | `False` | Gunakan HTTPS sebagai pengganti HTTP untuk komunikasi aman |
| `verify_ssl` | `bool` | ❌ Tidak | `True` | Verifikasi sertifikat SSL saat menggunakan HTTPS (set ke `False` untuk sertifikat self-signed) |

</details>

<details>
<summary><b>Parameter Caching</b></summary>

| Parameter | Tipe | Wajib | Default | Deskripsi |
|-----------|------|-------|---------|-----------|
| `cache` | `CacheMode` | ❌ Tidak | `CacheMode.ALL` | Strategi caching WSDL (lihat **Mode Cache** di bawah) |

</details>

<details>
<summary><b>Parameter Fitur</b></summary>

| Parameter | Tipe | Wajib | Default | Deskripsi |
|-----------|------|-------|---------|-----------|
| `apply_patch` | `bool` | ❌ Tidak | `True` | Aktifkan patching zeep untuk parsing field xsd:any yang lebih baik dan flattening otomatis, diterapkan pada ([`>=v0.0.4`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.0.4)) |
| `capture_xml` | `bool` | ❌ Tidak | `False` | Aktifkan plugin XML capture untuk debugging permintaan/respons SOAP, diterapkan pada ([`>=v0.0.6`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.0.6)) |
| `wsdl_dir`    | `str`  | ❌ Tidak | `None` | Path direktori WSDL kustom untuk menggunakan file WSDL eksternal sebagai pengganti yang built-in (mis., `/path/to/custom/wsdl`), diterapkan pada ([`>=v0.1.0`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.0)) |

</details>

<details>
<summary><b>Mode Cache</b></summary>

Pustaka menyediakan empat strategi caching melalui enum `CacheMode`:

| Mode | Deskripsi | Cocok Untuk | Kecepatan Startup | Penggunaan Disk | Penggunaan Memori |
|------|-----------|-------------|-------------------|-----------------|-------------------|
| `CacheMode.ALL` | Cache in-memory + disk (SQLite) | Server produksi, aplikasi multi-device | Cepat | Tinggi | Tinggi |
| `CacheMode.DB` | Cache disk saja (SQLite) | Batch jobs, CLI tools | Sedang | Sedang | Rendah |
| `CacheMode.MEM` | Cache in-memory saja | Script singkat, demo | Sedang | Tidak ada | Sedang |
| `CacheMode.NONE` | Tanpa caching | Testing, debugging | Lambat | Tidak ada | Rendah |

**Rekomendasi:** Gunakan `CacheMode.ALL` (default) untuk aplikasi produksi guna memaksimalkan performa.

</details>

<details>
<summary><b>Contoh Penggunaan</b></summary> 

**Koneksi Dasar:**
```python
from onvif import ONVIFClient

# Konfigurasi minimal
client = ONVIFClient("192.168.1.17", 80, "admin", "password")
```

**Koneksi Aman (HTTPS):**
```python
from onvif import ONVIFClient

# Koneksi via HTTPS dengan timeout kustom
client = ONVIFClient(
    "your-cctv-node.viewplexus.com", 
    443,  # Port HTTPS
    "admin", 
    "password",
    timeout=30,
    use_https=True
)
```

**Optimasi Performa (Cache Memori):**
```python
from onvif import ONVIFClient, CacheMode

# Gunakan cache memory-only untuk script cepat
client = ONVIFClient(
    "192.168.1.17", 
    80, 
    "admin", 
    "password",
    cache=CacheMode.MEM
)
```

**Tanpa Caching dan Zeep Patching (Testing):**
```python
from onvif import ONVIFClient, CacheMode

# Nonaktifkan semua caching untuk testing
client = ONVIFClient(
    "192.168.1.17", 
    80, 
    "admin", 
    "password",
    cache=CacheMode.NONE,
    apply_patch=False  # Gunakan perilaku zeep original
)
```

**Mode Debugging (XML Capture):**
```python
from onvif import ONVIFClient

# Aktifkan XML capture untuk debugging
client = ONVIFClient(
    "192.168.1.17", 
    80, 
    "admin", 
    "password",
    capture_xml=True  # Menangkap semua permintaan/respons SOAP
)

# Lakukan beberapa pemanggilan ONVIF
device = client.devicemgmt()
info = device.GetDeviceInformation()
services = device.GetCapabilities()

# Akses plugin XML capture
if client.xml_plugin:
    # Dapatkan request/response terakhir yang ditangkap
    print("XML Permintaan Terakhir:")
    print(client.xml_plugin.last_sent_xml)
    
    print("\nXML Respons Terakhir:")
    print(client.xml_plugin.last_received_xml)
    
    print(f"\nOperasi Terakhir: {client.xml_plugin.last_operation}")
    
    # Dapatkan riwayat lengkap semua permintaan/respons
    print(f"\nTotal operasi yang ditangkap: {len(client.xml_plugin.history)}")
    for item in client.xml_plugin.history:
        print(f"  - {item['operation']} ({item['type']})")
    
    # Simpan captured XML ke file
    client.xml_plugin.save_to_file(
        request_file="last_request.xml",
        response_file="last_response.xml"
    )
    
    # Bersihkan riwayat setelah selesai
    client.xml_plugin.clear_history()
```

> **Metode XML Capture Plugin:**
> - `last_sent_xml` - Dapatkan XML permintaan SOAP terakhir
> - `last_received_xml` - Dapatkan XML respons SOAP terakhir
> - `last_operation` - Dapatkan nama operasi terakhir
> - `history` - Daftar semua permintaan/respons yang ditangkap dengan metadata
> - `get_last_request()` - Metode untuk mendapatkan permintaan terakhir
> - `get_last_response()` - Metode untuk mendapatkan respons terakhir
> - `get_history()` - Metode untuk mendapatkan semua riwayat
> - `save_to_file(request_file, response_file)` - Simpan XML ke file
> - `clear_history()` - Bersihkan riwayat yang ditangkap

**Direktori WSDL Kustom:**
```python
from onvif import ONVIFClient

# Gunakan file WSDL kustom sebagai pengganti yang built-in
client = ONVIFClient(
    "192.168.1.17", 
    80, 
    "admin", 
    "password",
    wsdl_dir="/path/to/custom/wsdl"  # Direktori WSDL kustom
)

# Semua layanan akan otomatis menggunakan file WSDL kustom
device = client.devicemgmt()
media = client.media()
ptz = client.ptz()

# Direktori WSDL kustom harus memiliki struktur flat:
# /path/to/custom/wsdl/
# ├── devicemgmt.wsdl
# ├── media.wsdl
# ├── ptz.wsdl
# ├── imaging.wsdl
# └── ... (file WSDL lainnya)
```

</details>

<details>
<summary><b>Konfigurasi Produksi</b></summary> 

```python
from onvif import ONVIFClient, CacheMode

# Pengaturan produksi yang direkomendasikan
client = ONVIFClient(
    host="192.168.1.17",
    port=80,
    username="admin",
    password="secure_password",
    timeout=15,
    cache=CacheMode.ALL,        # Performa maksimal (default)
    use_https=True,             # Komunikasi aman
    verify_ssl=True,            # Verifikasi sertifikat (default)
    apply_patch=True,           # Enhanced parsing (default)
    capture_xml=False,          # Nonaktifkan mode debug (default)
    wsdl_dir=None               # Gunakan WSDL files bawaan (default)
)
```
</details>

### Catatan

- **Autentikasi:** Pustaka ini menggunakan autentikasi **WS-UsernameToken with Digest** secara default, yang merupakan standar untuk perangkat ONVIF.
- **Patching:** `apply_patch=True` (default) mengaktifkan custom zeep patching yang meningkatkan parsing field `xsd:any`. Ini direkomendasikan untuk kompatibilitas yang lebih baik dengan respons ONVIF.
- **XML Capture:** Hanya gunakan `capture_xml=True` selama development/debugging karena meningkatkan penggunaan memori dan dapat mengekspos data sensitif di log.
- **WSDL Kustom:** Gunakan parameter `wsdl_dir` untuk menentukan direktori kustom yang berisi file WSDL. Direktori harus memiliki struktur flat dengan file WSDL langsung di root (mis., `/path/to/custom/wsdl/devicemgmt.wsdl`, `/path/to/custom/wsdl/media.wsdl`, dll.).
- **Lokasi Cache:** Cache disk (saat menggunakan `CacheMode.DB` atau `CacheMode.ALL`) disimpan di `~/.onvif-python/onvif_zeep_cache.sqlite`.

## Penemuan Layanan: Memahami Kapabilitas Perangkat

> [!WARNING]
> Sebelum melakukan operasi apa pun pada perangkat ONVIF, sangat disarankan untuk menemukan layanan mana yang tersedia dan didukung oleh perangkat. Pustaka ini secara otomatis melakukan penemuan layanan yang komprehensif selama inisialisasi menggunakan mekanisme fallback yang kuat.

**Mengapa menemukan layanan perangkat?**

- **Keanekaragaman Perangkat:** Tidak semua perangkat ONVIF mendukung setiap layanan. Layanan yang tersedia dapat bervariasi berdasarkan produsen, model, firmware, atau konfigurasi.
- **Pencegahan Kesalahan:** Mencoba menggunakan layanan yang tidak didukung dapat mengakibatkan permintaan gagal, pengecualian, atau perilaku yang tidak terdefinisi.
- **Deteksi Fitur Dinamis:** Perangkat dapat mengaktifkan atau menonaktifkan layanan dari waktu ke waktu (misalnya, setelah pembaruan firmware atau perubahan konfigurasi).
- **Integrasi yang Dioptimalkan:** Dengan memeriksa layanan yang tersedia, aplikasi Anda dapat menyesuaikan alur kerja dan UI untuk mencocokkan fitur perangkat yang sebenarnya.

**Cara kerja penemuan layanan di pustaka ini:**

`ONVIFClient` menggunakan **pendekatan penemuan 3-tingkat** untuk memaksimalkan kompatibilitas perangkat:

1. **GetServices (Preferensi)** - Mencoba `GetServices` terlebih dahulu untuk informasi layanan yang detail
2. **GetCapabilities (Fallback)** - Menggunakan `GetCapabilities` jika `GetServices` tidak didukung
3. **URL Default (Fallback Akhir)** - Menggunakan URL ONVIF standar sebagai pilihan terakhir

```python
from onvif import ONVIFClient

client = ONVIFClient("192.168.1.17", 8000, "admin", "admin123")

# Periksa metode penemuan mana yang digunakan
if client.services:
    print("Penemuan layanan: GetServices (preferensi)")
    print("Layanan yang ditemukan:", len(client.services))
    print("Peta layanan:", client._service_map)
elif client.capabilities:
    print("Penemuan layanan: GetCapabilities (fallback)")
    print("Kapabilitas yang tersedia:", client.capabilities)
else:
    print("Penemuan layanan: Menggunakan URL default")
```

**Mengapa pendekatan ini?**

- **GetServices** memberikan informasi layanan yang paling akurat dan detail, tetapi bersifat **opsional** dalam spesifikasi ONVIF
- **GetCapabilities** bersifat **wajib** untuk semua perangkat yang sesuai dengan ONVIF, memastikan kompatibilitas yang lebih luas
- **URL Default** menjamin konektivitas dasar bahkan dengan perangkat yang tidak sesuai

> [!TIP]
> Pustaka menangani penemuan layanan secara otomatis dengan fallback yang cerdas. Anda biasanya tidak perlu memanggil metode penemuan secara manual kecuali Anda memerlukan informasi kapabilitas detail atau ingin menyegarkan daftar layanan setelah perubahan konfigurasi perangkat.

## Perangkat yang Diuji

Pustaka ini telah diuji dengan berbagai perangkat yang sesuai dengan ONVIF. Untuk daftar terbaru dan paling lengkap dari perangkat yang telah diverifikasi bekerja dengan pustaka ini, silakan merujuk ke:

- [Daftar perangkat yang diuji (device-test)](https://github.com/nirsimetri/onvif-products-directory/blob/main/device-test)

Jika perangkat Anda belum terdaftar saat ini, jangan ragu untuk menyumbangkan hasil pengujian atau umpan balik Anda melalui Issues atau Discussions di [onvif-products-directory](https://github.com/nirsimetri/onvif-products-directory). Kontribusi Anda akan sangat berharga bagi komunitas dan publik.

> [!IMPORTANT]
> Kontribusi pengujian perangkat harus dilakukan dengan perangkat nyata dan menggunakan skrip yang disediakan di repositori [onvif-products-directory](https://github.com/nirsimetri/onvif-products-directory). Pastikan untuk berkontribusi menggunakan model perangkat yang belum terdaftar.

## Profil ONVIF yang Didukung

Pustaka ini sepenuhnya mendukung semua Profil ONVIF utama yang tercantum di bawah ini. Setiap profil mewakili serangkaian fitur dan kasus penggunaan standar, memastikan interoperabilitas antara perangkat dan klien yang sesuai dengan ONVIF. Anda dapat menggunakan pustaka ini untuk berintegrasi dengan perangkat dan sistem yang mengimplementasikan salah satu profil ini.

<details>
<summary><b>Daftar profil ONVIF</b></summary>

| Nama      | Spesifikasi | Fitur Utama | Kasus Penggunaan Umum | Dukungan |
|-----------|----------------|---------------|------------------|---------|
| Profile_S | [Dokumen](https://www.onvif.org/wp-content/uploads/2019/12/ONVIF_Profile_-S_Specification_v1-3.pdf) | Streaming video, PTZ, audio, multicasting | Pemancar video jaringan (kamera) dan penerima (perekam, VMS) | ✅ Ya |
| Profile_G | [Dokumen](https://www.onvif.org/wp-content/uploads/2017/01/ONVIF_Profile_G_Specification_v1-0.pdf) | Perekaman, pencarian, pemutaran ulang, penyimpanan video | Perekam video, perangkat penyimpanan | ✅ Ya |
| Profile_T | [Dokumen](https://www.onvif.org/wp-content/uploads/2018/09/ONVIF_Profile_T_Specification_v1-0.pdf) | Streaming video lanjutan (H.265, metadata analitik, deteksi gerakan) | Kamera modern dan klien | ✅ Ya |
| Profile_C | [Dokumen](https://www.onvif.org/wp-content/uploads/2017/01/2013_12_ONVIF_Profile_C_Specification_v1-0.pdf) | Kontrol akses, pemantauan pintu | Pengontrol pintu, sistem akses | ✅ Ya |
| Profile_A | [Dokumen](https://www.onvif.org/wp-content/uploads/2017/06/ONVIF_Profile_A_Specification_v1-0.pdf) | Konfigurasi kontrol akses lanjutan, manajemen kredensial | Klien dan perangkat kontrol akses | ✅ Ya |
| Profile_D | [Dokumen](https://www.onvif.org/wp-content/uploads/2021/06/onvif-profile-d-specification-v1-0.pdf) | Periferal kontrol akses (kunci, sensor, relai) | Perangkat periferal untuk kontrol akses | ✅ Ya |
| Profile_M | [Dokumen](https://www.onvif.org/wp-content/uploads/2024/04/onvif-profile-m-specification-v1-1.pdf) | Metadata, analitik event, deteksi objek | Perangkat analitik, klien metadata | ✅ Ya |

</details>

Untuk deskripsi lengkap setiap profil dan fiturnya, kunjungi [Profil ONVIF](https://www.onvif.org/profiles/).

## Layanan ONVIF yang Diimplementasikan

> [!NOTE]
> Untuk detail tentang fungsi dan metode layanan yang tersedia yang telah diimplementasikan dalam pustaka ini, lihat kode sumber di [`onvif/services/`](./onvif/services). Atau jika Anda ingin membaca dalam format yang lebih baik, kunjungi [onvif-python AI Wiki](https://deepwiki.com/nirsimetri/onvif-python).

Berikut adalah daftar layanan ONVIF yang diimplementasikan dan didukung oleh pustaka ini, bersama dengan tautan ke spesifikasi resmi, definisi layanan, dan berkas skema seperti yang dirujuk dari [Spesifikasi Pengembang ONVIF](https://developer.onvif.org/pub/specs/branches/development/doc/index.html). Tabel ini memberikan gambaran cepat tentang fitur ONVIF yang tersedia dan dokumentasi teknisnya untuk tujuan integrasi dan pengembangan.

<details>
<summary><b>Daftar layanan ONVIF</b></summary>

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

</details>

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
   client.notification()              # sub-binding accessor
   ```

2. **Security (Advanced Security)**
   - **Root:** `AdvancedSecurityServiceBinding`
   - **Sub-binding:**
     - `AuthorizationServerBinding`
     - `KeystoreBinding`
     - `JWTBinding`
     - `Dot1XBinding`
     - `TLSServerBinding`
     - `MediaSigningBinding`

   Penggunaan di pustaka:
   ```python
   client.security()                  # root binding
   client.authorizationserver(xaddr)  # sub-binding accessor (memerlukan xAddr)
   client.keystore(xaddr)             # ..
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

- [x] ~~Menambahkan mode debugging dengan raw XML pada permintaan dan respons SOAP.~~ ([c258162](https://github.com/nirsimetri/onvif-python/commit/c258162))
- [x] ~~Menambahkan fungsionalitas agar `ONVIFClient` dapat menerima layanan `wsdl_dir` kustom.~~ ([65f2570](https://github.com/nirsimetri/onvif-python/commit/65f2570))
- [x] ~~Menambahkan program `ONVIF CLI` untuk berinteraksi langsung dengan perangkat ONVIF melalui terminal.~~ ([645be01](https://github.com/nirsimetri/onvif-python/commit/645be01))
- [ ] Menambahkan dukungan asynchronous (async/await) untuk operasi ONVIF non-blocking dan komunikasi perangkat secara bersamaan.
- [ ] Mengimplementasikan model data terstruktur untuk Skema ONVIF menggunakan [xsdata](https://github.com/tefra/xsdata).
- [ ] Mengintegrasikan [xmltodict](https://github.com/martinblech/xmltodict) untuk parsing dan konversi XML yang lebih sederhana.
- [ ] Meningkatkan dokumentasi dengan referensi API dan diagram (bukan dari [AI Wiki](https://deepwiki.com/nirsimetri/onvif-python)).
- [ ] Menambahkan lebih banyak contoh penggunaan untuk fitur lanjutan.
- [ ] Menambahkan benchmarking dan metrik performa.
- [ ] Menambahkan template konfigurasi perangkat yang dikontribusikan oleh komunitas.
- [ ] Mengimplementasikan layanan ONVIF yang hilang atau masih parsial.
- [ ] Menambahkan fungsi untuk mengekspos perangkat ONVIF (untuk tujuan debugging oleh komunitas).

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

## Lisensi

Proyek ini dilisensikan di bawah Lisensi MIT. Lihat [LICENSE](./LICENSE.md) untuk detailnya.