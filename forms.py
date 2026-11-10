"""Modul Validasi Formulir (Forms) Aplikasi SI Peringatan Dini.

Menggunakan Flask-WTF dan WTForms untuk validasi data input di sisi server (server-side).
Seluruh pesan galat (error message) disajikan dalam Bahasa Indonesia yang informatif.
"""

from flask_wtf import FlaskForm
from wtforms import (
    FloatField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    AnyOf,
    DataRequired,
    Email,
    InputRequired,
    Length,
    NoneOf,
    NumberRange,
    Optional,
    Regexp,
    ValidationError,
)
from models import Mahasiswa, db


# -----------------------------------------------------------------------------
# 1. Formulir Mahasiswa (MahasiswaForm)
# -----------------------------------------------------------------------------
class MahasiswaForm(FlaskForm):
    """Formulir input data mahasiswa dengan validasi ketat di sisi server."""

    def __init__(self, *args, current_id: int | None = None, **kwargs):
        """Inisialisasi form.

        Parameter current_id digunakan jika form dipakai untuk edit data,
        agar validasi unik NIM tidak memblokir record miliknya sendiri.
        """
        super().__init__(*args, **kwargs)
        self.current_id = current_id

    # Kolom NIM: Wajib diisi & sesuai pola regex (format A11.2023.00001)
    nim = StringField(
        "Nomor Induk Mahasiswa (NIM)",
        validators=[
            DataRequired(message="NIM wajib diisi dan tidak boleh kosong."),
            Regexp(
                regex=r"^[A-Z]\d{2}\.\d{4}\.\d{5}$",
                message="Format NIM tidak valid. Gunakan format standar institusi (contoh: A11.2023.00001).",
            ),
        ],
        render_kw={"placeholder": "Contoh: A11.2023.00001"},
    )

    # Kolom Nama: Wajib diisi & panjang 3-100 karakter
    nama = StringField(
        "Nama Lengkap Mahasiswa",
        validators=[
            DataRequired(message="Nama lengkap mahasiswa wajib diisi."),
            Length(
                min=3,
                max=100,
                message="Nama lengkap harus memiliki panjang antara 3 hingga 100 karakter.",
            ),
        ],
        render_kw={"placeholder": "Masukkan nama lengkap sesuai KTP/KTM"},
    )

    # Kolom Prodi: Wajib diisi & harus salah satu dari SI, TI, MI (AnyOf)
    prodi = SelectField(
        "Program Studi",
        choices=[
            ("", "-- Pilih Program Studi --"),
            ("SI", "SI - Sistem Informasi"),
            ("TI", "TI - Teknik Informatika"),
            ("MI", "MI - Manajemen Informatika"),
        ],
        validators=[
            DataRequired(message="Program studi wajib dipilih."),
            AnyOf(
                values=["SI", "TI", "MI"],
                message="Pilihan Program Studi harus salah satu dari: SI, TI, atau MI.",
            ),
        ],
    )

    # Kolom IPK: Menggunakan InputRequired (agar angka 0 sah) & rentang 0.00 - 4.00
    ipk = FloatField(
        "Indeks Prestasi Kumulatif (IPK)",
        validators=[
            InputRequired(message="Nilai IPK wajib diisi (gunakan angka desimal)."),
            NumberRange(
                min=0.0,
                max=4.0,
                message="Nilai IPK harus berada pada rentang skala 0.00 hingga 4.00.",
            ),
        ],
        render_kw={"step": "0.01", "placeholder": "Rentang 0.00 - 4.00"},
    )

    # Kolom Kehadiran: Menggunakan InputRequired (agar angka 0 sah) & rentang 0 - 100%
    kehadiran = IntegerField(
        "Tingkat Kehadiran (%)",
        validators=[
            InputRequired(message="Persentase kehadiran perkuliahan wajib diisi."),
            NumberRange(
                min=0,
                max=100,
                message="Tingkat kehadiran harus berada pada rentang 0 sampai 100 persen.",
            ),
        ],
        render_kw={"placeholder": "Rentang 0 - 100"},
    )

    # Kolom Email: Bersifat opsional, namun jika diisi harus valid
    email = StringField(
        "Alamat Email Mahasiswa",
        validators=[
            Optional(),
            Email(message="Format alamat email tidak valid. Masukkan email yang benar (misal: mhs@kampus.ac.id)."),
        ],
        render_kw={"placeholder": "nama@domain.ac.id (opsional)"},
    )

    submit = SubmitField("Simpan Data Mahasiswa")

    # Validator Khusus untuk NIM (Pengecekan Duplikasi ke Basis Data)
    def validate_nim(self, field):
        """Mengecek apakah NIM sudah terdaftar di basis data.

        Menggunakan sintaks SQLAlchemy 2.x untuk eksekusi query.
        """
        nim_input = field.data.strip() if field.data else ""

        # Query pengecekan NIM duplikat (SQLAlchemy 2.x style)
        stmt = db.select(Mahasiswa).filter_by(nim=nim_input)
        mahasiswa_ada = db.session.execute(stmt).scalar_one_or_none()

        if mahasiswa_ada:
            # Jika sedang mode edit, perbolehkan jika NIM adalah milik data yang sedang diedit
            if self.current_id and mahasiswa_ada.id == self.current_id:
                return

            raise ValidationError(
                f"NIM '{nim_input}' sudah terdaftar dalam sistem. Mohon periksa kembali atau gunakan NIM yang berbeda."
            )


# -----------------------------------------------------------------------------
# 2. Formulir Catatan (CatatanForm)
# -----------------------------------------------------------------------------
class CatatanForm(FlaskForm):
    """Formulir penambahan catatan bimbingan atau konseling akademik mahasiswa."""

    # Kolom Jenis: SelectField dengan opsi Akademik, Keuangan, Pribadi
    jenis = SelectField(
        "Kategori / Jenis Catatan",
        choices=[
            ("", "-- Pilih Jenis Catatan --"),
            ("Akademik", "Akademik"),
            ("Keuangan", "Keuangan"),
            ("Pribadi", "Pribadi"),
        ],
        validators=[
            DataRequired(message="Kategori jenis catatan wajib dipilih."),
        ],
    )

    # Kolom Isi: TextAreaField dengan DataRequired, Length (10-500), dan NoneOf ('tes', 'test', '-')
    isi = TextAreaField(
        "Isi Catatan Bimbingan / Konseling",
        validators=[
            DataRequired(message="Isi catatan bimbingan wajib diisi."),
            Length(
                min=10,
                max=500,
                message="Isi catatan harus memiliki panjang antara 10 hingga 500 karakter.",
            ),
            NoneOf(
                values=["tes", "test", "-", "Tes", "Test", "TES", "TEST"],
                message="Isi catatan tidak boleh hanya berupa teks uji coba (seperti 'tes', 'test', atau tanda strip '-'). Berikan deskripsi yang jelas.",
            ),
        ],
        render_kw={
            "rows": 4,
            "placeholder": "Tuliskan rincian hasil bimbingan, konseling, atau peringatan akademik di sini...",
        },
    )

    submit = SubmitField("Simpan Catatan")
