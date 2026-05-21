from datetime import date, datetime

from pydantic import BaseModel


class Detection(BaseModel):
    id: int
    date: date
    time: str
    sci_name: str
    com_name: str
    confidence: float
    lat: float
    lon: float
    cutoff: float
    week: int
    sens: float
    overlap: float
    file_name: str

    @property
    def datetime_str(self) -> str:
        return f"{self.date} {self.time}"

    @property
    def species_dir(self) -> str:
        return self.com_name.replace(" ", "_").replace("'", "")

    @property
    def audio_path(self) -> str:
        return f"Extracted/By_Date/{self.date}/{self.species_dir}/{self.file_name}"

    @property
    def spectrogram_path(self) -> str:
        return f"Extracted/By_Date/{self.date}/{self.species_dir}/{self.file_name}.png"

    @property
    def confidence_pct(self) -> int:
        return round(self.confidence * 100)


class SpeciesSummary(BaseModel):
    com_name: str
    sci_name: str
    detection_count: int
    avg_confidence: float
    last_detected: str
    first_detected: str


class DailyCount(BaseModel):
    date: str
    count: int


class HourlyCount(BaseModel):
    hour: int
    count: int


class DashboardStats(BaseModel):
    total_detections: int
    today_detections: int
    species_today: int
    total_species: int
    hourly_rate: float
