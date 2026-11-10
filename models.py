"""Model Basis Data SI Peringatan Dini.

Menggunakan Flask-SQLAlchemy dengan sintaks SQLAlchemy 2.x (Mapped & mapped_column).
Mendefinisikan entitas Mahasiswa dan Catatan dengan relasi One-to-Many dua arah.
"""

from datetime import datetime, timezone
from typing import List, Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

# -----------------------------------------------------------------------------
# Inisialisasi Instance Flask-SQLAlchemy
# -----------------------------------------------------------------------------
db = SQLAlchemy()


# -----------------------------------------------------------------------------
# Model Mahasiswa
# -----------------------------------------------------------------------------
class Mahasiswa(db.Model):
    """Model entitas Mahasiswa untuk pemantauan performa akademik."""

    __tablename__ = "mahasiswa"

    # Kolom Entitas Mahasiswa (SQLAlchemy 2.x)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nim: Mapped[str] = mapped_column(db.String(14), unique=True, nullable=False, index=True)
    nama: Mapped[str] = mapped_column(db.String(100), nullable=False)
    prodi: Mapped[str] = mapped_column(db.String(50), nullable=False)
    ipk: Mapped[float] = mapped_column(db.Float, nullable=False)
    kehadiran: Mapped[int] = mapped_column(db.Integer, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(db.String(120), nullable=True)

    # Relasi One-to-Many ke model Catatan (dua arah dengan back_populates)
    # cascade="all, delete-orphan" memastikan seluruh catatan terkait ikut terhapus jika mahasiswa dihapus
    catatan: Mapped[List["Catatan"]] = db.relationship(
        "Catatan",
        back_populates="mahasiswa",
        cascade="all, delete-orphan",
    )

    @property
    def is_berisiko(self) -> bool:
        """Menentukan apakah mahasiswa masuk kategori risiko peringatan dini.

        Kriteria: IPK < 2.75 ATAU tingkat kehadiran < 75%.
        """
        return self.ipk < 2.75 or self.kehadiran < 75

    def __repr__(self) -> str:
        return f"<Mahasiswa {self.nim} - {self.nama}>"


# -----------------------------------------------------------------------------
# Model Catatan
# -----------------------------------------------------------------------------
class Catatan(db.Model):
    """Model entitas Catatan Bimbingan / Konseling Akademik Mahasiswa."""

    __tablename__ = "catatan"

    # Kolom Entitas Catatan (SQLAlchemy 2.x)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    jenis: Mapped[str] = mapped_column(db.String(50), nullable=False)
    isi: Mapped[str] = mapped_column(db.Text, nullable=False)
    # Default waktu saat ini menggunakan func.now() atau UTC timestamp
    dibuat: Mapped[datetime] = mapped_column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )

    # Foreign Key merujuk ke primary key tabel mahasiswa (mahasiswa.id)
    mahasiswa_id: Mapped[int] = mapped_column(
        db.ForeignKey("mahasiswa.id"),
        nullable=False,
        index=True,
    )

    # Relasi Many-to-One: Akses dua arah kembali ke objek Mahasiswa
    mahasiswa: Mapped["Mahasiswa"] = db.relationship(
        "Mahasiswa",
        back_populates="catatan",
    )

    def __repr__(self) -> str:
        return f"<Catatan {self.jenis} [ID: {self.id}] - Mahasiswa ID: {self.mahasiswa_id}>"
