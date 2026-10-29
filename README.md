# Internal Workspace (Jira Clone Enterprise)

Platform manajemen kerja, backlog, dan pelacak sprint multi-tim internal bergaya Jira Enterprise.

* **Frontend**: Vue 3 (Composition API) + Tailwind CSS + Vite
* **Backend**: Python Flask + SQLAlchemy (ORM) + SQLite (relasional lokal)
* **Autentikasi**: Microsoft Entra ID (Azure AD SSO) + OAuth 2.0 (Google & GitHub)
* **Email & Notifikasi**: Background SMTP Mailer (@mention email notifikasi otomatis)

---

## ✨ Fitur Utama

1. **Desain & Tema Korporat Modern**:
   - Skema warna modern: *Primary Cobalt Blue* (`#1226AA`), *Dark Corporate Navy* (`#080E2F`), dan *Soft Blue Accent* (`#EEF2FF`).
   - Halaman login modern dengan kartu SSO Microsoft terintegrasi.
2. **Autentikasi Multi-Provider (Enterprise SSO)**:
   - **Microsoft Entra ID (SSO)** via MSAL Browser asli (tanpa mock user).
   - **OAuth 2.0 Google & GitHub** dengan Authorization Code Flow dan penerbitan JWT sesi internal.
3. **Workspace Multi-Tim & Manajemen Tim**:
   - Pembuatan tim baru otomatis menjadikan pembuatnya sebagai **Admin** tim.
   - Generate kode invite tim unik (`INVITE-KEY-XXXX`) dengan masa berlaku yang dapat diatur (1–30 hari).
   - Tim dapat diedit (nama, key prefix, deskripsi) atau dihapus oleh Admin.
4. **Manajemen Sprint Otomatis & Fleksibel**:
   - Sprint 1–4 otomatis diinisialisasi saat tim dibuat (Sprint 1 langsung `active`).
   - Admin dapat membuat sprint baru, mengubah nama/goal/tanggal, memulai (*start*), menyelesaikan (*complete*), serta menghapus sprint.
   - Aturan proteksi: Hanya boleh 1 sprint aktif dalam satu waktu. Issue yang belum selesai saat sprint selesai otomatis dialihkan ke Backlog.
5. **Papan Kanban Interaktif & Filter**:
   - Kolom status: `TO DO`, `IN PROGRESS`, `IN REVIEW`, dan `DONE`.
   - Drag-and-drop kartu tiket antar kolom.
   - Filter lengkap: pencarian teks, avatar assignee, tipe issue (*Story, Task, Bug, Epic*), prioritas, dan filter tiket pribadi (*Only My Issues*).
6. **Detail Tiket, Subtask & Komentar Real-Time**:
   - **Subtask Real-Time**: Tambah subtask langsung muncul tanpa reload, ceklis selesai/belum selesai seketika (*optimistic update*), serta hapus subtask.
   - **Komentar & @Mention Rekan Tim**: Autocomplete anggota tim saat mengetik `@`, format badge mention biru, dan pengiriman pesan instan via tombol `Enter`.
   - **Notifikasi Email Otomatis**: Backend otomatis mendeteksi email yang di-mention dan mengirim notifikasi email berformat HTML profesional via background thread (asynchronous). Dilengkapi mode simulasi aman jika kredensial SMTP belum diisi.
   - **Background Auto-Sync**: Sinkronisasi data latar belakang setiap 4 detik saat tab aktif.
7. **Bagikan Papan Tim (Public Read-Only Board)**:
   - Link publik permanen (`/share/<token>`) yang tetap dan tidak berubah-ubah.
   - Memungkinkan klien atau stakeholder memantau progres sprint secara *read-only* tanpa perlu login.
8. **Pengalaman Pengguna Tanpa Popup Browser**:
   - Seluruh konfirmasi (hapus tim, hapus tiket, hapus sprint, logout) menggunakan modal kustom modern. Tidak ada popup browser default (*"localhost says"*).

---

## 🛠️ Prasyarat Sistem

* **Python 3.11+**
* **Node.js 18+** & **npm**
* **Akun Microsoft Azure / Entra ID** (untuk konfigurasi SSO)

---

## 🚀 Panduan Menjalankan Proyek

### 1. Setup Backend (Python Flask)

Buka terminal di root proyek:

```bash
cd backend

# Buat virtual environment
python -m venv .venv

# Aktivasi virtual environment:
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (Command Prompt):
.venv\Scripts\activate.bat
# Linux / macOS:
source .venv/bin/activate

# Install dependensi
pip install -r requirements.txt

# Salin file konfigurasi environment
cp .env.example .env
```

Sesuaikan isi file `backend/.env`:
```env
FLASK_ENV=development
FLASK_PORT=5000
DATABASE_URL="sqlite:///jiravue.db"
SECRET_KEY="ganti-dengan-string-rahasia-acak-minimal-32-karakter"

# Microsoft Entra ID (Azure AD)
AZURE_TENANT_ID="<your-azure-tenant-id>"
AZURE_CLIENT_ID="<your-azure-client-id>"

# (Opsional) Google & GitHub OAuth
GOOGLE_CLIENT_ID=""
GOOGLE_CLIENT_SECRET=""
GITHUB_CLIENT_ID=""
GITHUB_CLIENT_SECRET=""

# (Opsional) Konfigurasi Pengiriman Email SMTP (Contoh Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=emailanda@gmail.com
SMTP_PASS=xxxx xxxx xxxx xxxx       # 16-digit Google App Password
SMTP_FROM="Internal Workspace <emailanda@gmail.com>"
SMTP_USE_TLS=true
APP_BASE_URL=http://localhost:5173

# (Opsional) Gemini API Key untuk AI Agent
GEMINI_API_KEY=""
```

Jalankan server backend:
```bash
python app.py
```
> Server backend berjalan di `http://localhost:5000`. Database SQLite otomatis dibuat pada `backend/instance/jiravue.db`.

---

### 2. Setup Frontend (Vue 3 + Vite)

Buka terminal baru di folder frontend:

```bash
cd frontend

# Install package npm
npm install

# Salin konfigurasi environment jika diperlukan
cp .env.example .env 2>/dev/null || true
```

Isi `frontend/.env`:
```env
VITE_FLASK_API_URL=http://localhost:5000/api/v1
VITE_AZURE_CLIENT_ID="<your-azure-client-id>"
VITE_AZURE_TENANT_ID="<your-azure-tenant-id>"
```

Jalankan server development frontend:
```bash
npm run dev
```

Atau lakukan build produksi:
```bash
npm run build
```
> Aplikasi frontend dapat diakses melalui browser di `http://localhost:5173`.

---

## 🔒 Konfigurasi Microsoft Entra ID (Azure Portal)

1. Buka [Azure Portal](https://portal.azure.com/) → **Microsoft Entra ID** → **App registrations** → **New registration**.
2. Berikan nama aplikasi (misal: `Internal Workspace`).
3. Pilih tipe akun: *Accounts in this organizational directory only (Single tenant)*.
4. Pada **Redirect URI**, pilih platform **Single-page application (SPA)** dan isi URI:
   ```
   http://localhost:5173
   ```
5. Pada menu **API permissions**, pastikan izin berikut aktif:
   - `openid`, `profile`, `email`, `User.Read`.
6. Salin **Application (client) ID** dan **Directory (tenant) ID** ke file `.env` di backend dan frontend.

---

## 📁 Struktur Direktori

```
JIRA/
├── .gitignore                   # Aturan pengabaian file sensitif Git
├── README.md                    # Dokumentasi resmi proyek
├── backend/
│   ├── app.py                   # Entry point Flask & registrasi Blueprint
│   ├── config.py                # Konfigurasi aplikasi & database
│   ├── models.py                # Schema ORM SQLAlchemy
│   ├── mailer.py                # Service asynchronous background email SMTP
│   ├── auth_microsoft.py        # Validasi JWT MSAL Entra ID
│   ├── auth_oauth.py            # Handler OAuth 2.0 Google & GitHub
│   ├── requirements.txt         # Daftar dependency Python
│   ├── .env.example             # Template variabel environment backend
│   └── routes/
│       ├── teams_bp.py          # Endpoint tim, anggota, invite, & sprint
│       ├── issues_bp.py         # Endpoint issue, subtask, & komentar
│       └── agent_bp.py          # Endpoint AI Agent prompt-to-action
└── frontend/
    ├── index.html               # Entry point HTML aplikasi
    ├── package.json             # Konfigurasi package & script npm
    ├── tailwind.config.js       # Konfigurasi Tailwind & tema warna modern
    ├── vite.config.js           # Konfigurasi Vite bundler
    └── src/
        ├── App.vue              # Main state orchestration
        ├── main.js              # Bootstrap aplikasi Vue 3
        ├── auth/                # Modul autentikasi MSAL & sesi OAuth
        ├── services/            # Service layer axios API backend
        ├── views/
        │   ├── HomeLoginView.vue         # Landing page & login internal
        │   ├── WelcomeWorkspaceView.vue  # Onboarding state (belum ada tim)
        │   ├── TeamSelectorView.vue      # Pilihan workspace tim
        │   └── ShareBoardView.vue        # Public read-only board
        └── components/
            ├── JiraNavbar.vue            # Top navigation bar
            ├── JiraSidebar.vue           # Sidebar daftar sprint & views
            ├── KanbanBoard.vue           # Papan kanban sprint aktif
            ├── KanbanCard.vue            # Kartu tiket issue
            ├── IssueDetailModal.vue      # Modal detail issue, subtask, komentar
            ├── TeamMembersPanel.vue      # Kelola anggota & kode invite tim
            ├── JiraAiAgent.vue           # Panel AI Agent chat
            ├── ToastNotification.vue     # Notifikasi toast sistem
            └── modals/                   # Modal dialog kustom
```

---

## 📡 Ringkasan Endpoint REST API

| Method | Endpoint | Deskripsi |
| :--- | :--- | :--- |
| `GET` | `/api/v1/me` | Profil pengguna aktif dan daftar membership tim |
| `GET` | `/api/v1/auth/<provider>/login` | Mulai alur OAuth Google / GitHub |
| `GET` | `/api/v1/auth/<provider>/callback`| Callback OAuth: tukar kode & terbitkan JWT |
| `GET` / `POST` | `/api/v1/teams` | Ambil daftar tim saya / buat tim baru |
| `POST` | `/api/v1/teams/join` | Bergabung ke tim dengan kode invite |
| `PUT` / `DELETE` | `/api/v1/teams/<teamId>` | Edit nama & info tim / hapus tim |
| `GET` | `/api/v1/teams/<teamId>/members` | Daftar anggota tim beserta rolenya |
| `GET` / `POST` | `/api/v1/teams/<teamId>/invites` | Lihat dan generate kode invite tim baru |
| `GET` / `POST` | `/api/v1/teams/<teamId>/sprints` | Ambil daftar sprint / buat sprint baru |
| `PUT` / `DELETE` | `/api/v1/teams/<teamId>/sprints/<sprintId>` | Update sprint / hapus sprint |
| `POST` | `/api/v1/teams/<teamId>/sprints/<sprintId>/complete` | Selesaikan sprint aktif |
| `GET` | `/api/v1/teams/<teamId>/share` | Ambil link publik read-only yang permanen |
| `POST` | `/api/v1/teams/<teamId>/share/reset` | Reset/regenerasi token share board |
| `GET` | `/api/v1/public/share/<token>` | Ambil data board publik untuk mode read-only |
| `GET` / `POST` | `/api/v1/teams/<teamId>/issues` | Ambil semua issue tim / buat issue baru |
| `PUT` / `DELETE` | `/api/v1/teams/<teamId>/issues/<key>` | Update detail issue / hapus issue |
| `POST` | `/api/v1/teams/<teamId>/issues/<key>/subtasks` | Tambah subtask pada issue |
| `PATCH` | `/api/v1/teams/<teamId>/issues/<key>/subtasks/<id>` | Ceklis / unceklis status selesai subtask |
| `DELETE` | `/api/v1/teams/<teamId>/issues/<key>/subtasks/<id>` | Hapus subtask |
| `POST` | `/api/v1/teams/<teamId>/issues/<key>/comments` | Tambah komentar & kirim email mention |
| `POST` | `/api/v1/agent/prompt` | Prompt-to-action AI Agent (Gemini) |

---

## 📄 Lisensi & Hak Cipta

© 2026 **Internal Workspace**. All rights reserved.
