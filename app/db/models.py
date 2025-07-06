
from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()

class SVGRecord(Base):
    __tablename__ = "svg_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    hash: Mapped[str] = mapped_column(String)
    svg: Mapped[str] = mapped_column(String)
    mask_contours: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
