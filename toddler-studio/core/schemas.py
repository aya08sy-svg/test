"""Pydantic models for every toddler-studio pipeline artifact.

All Gemini / Veo responses that are persisted or gated must use these models
(with response-schema enforcement). Creative content lives in YAML config;
this module only defines structure.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Run / segment state machine
# ---------------------------------------------------------------------------


class RunStatus(str, Enum):
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    ASSEMBLED = "ASSEMBLED"
    PUBLISH_PACKAGE_READY = "PUBLISH_PACKAGE_READY"
    ABORTED = "ABORTED"
    FAILED = "FAILED"


class SegmentStatus(str, Enum):
    PENDING = "PENDING"
    PROMPTS_READY = "PROMPTS_READY"
    CLIPS_RENDERED = "CLIPS_RENDERED"
    QC_PASSED = "QC_PASSED"
    QC_FAILED = "QC_FAILED"
    AWAITING_HUMAN = "AWAITING_HUMAN"
    SEGMENT_APPROVED = "SEGMENT_APPROVED"
    SEGMENT_REJECTED = "SEGMENT_REJECTED"
    ESCALATED = "ESCALATED"


# ---------------------------------------------------------------------------
# Series bible (loaded from YAML; validated here)
# ---------------------------------------------------------------------------


class CharacterReferenceSheet(BaseModel):
    """Canonical images — stored once, never regenerated."""

    front: str = Field(..., description="Path or Drive id for front view")
    three_quarter: str | None = None
    side: str | None = None
    expression_sheet: str | None = None
    extra: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def at_least_one_image(self) -> CharacterReferenceSheet:
        paths = [
            self.front,
            self.three_quarter,
            self.side,
            self.expression_sheet,
            *self.extra,
        ]
        if not any(p for p in paths if p):
            raise ValueError("reference sheet needs at least one image path")
        return self


class CharacterDescriptor(BaseModel):
    """Frozen descriptor block injected verbatim into every shot prompt."""

    height_ratio: str
    palette_hex: list[str]
    silhouette: str
    outfit: str
    hair: str
    distinguishing_marks: str
    verbatim_block: str = Field(
        ...,
        description="Exact text injected into prompts; never paraphrase",
    )


class Character(BaseModel):
    name: str
    role: str = ""
    reference_sheet: CharacterReferenceSheet
    descriptor: CharacterDescriptor
    seed: int | None = Field(
        default=None,
        description="Pinned generation seed when the API supports it",
    )


class SeriesBible(BaseModel):
    series_title: str
    target_audience: str = "preschool/toddler"
    characters: list[Character]
    world_rules: list[str] = Field(default_factory=list)
    voice: str = ""
    palette: list[str] = Field(default_factory=list)
    style_token: str = Field(
        ...,
        description="Fixed style string injected verbatim into every prompt",
    )
    negative_prompt: list[str] = Field(default_factory=list)
    banned_elements: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Episode / segment planning
# ---------------------------------------------------------------------------


class Beat(BaseModel):
    beat_id: str
    summary: str
    duration_hint_sec: float = Field(ge=1, le=60)
    focal_characters: list[str] = Field(default_factory=list)
    setting: str = ""
    learning_moment: str | None = None
    motion_notes: str = ""


class SegmentPlan(BaseModel):
    segment_index: int = Field(ge=1, le=10)
    title: str
    beats: list[Beat] = Field(min_length=1)
    structural_signature: list[str] = Field(
        default_factory=list,
        description="Ordered beat-type tags used by template_similarity_check",
    )


class EpisodePlan(BaseModel):
    episode_id: str
    title: str
    premise: str
    segments: list[SegmentPlan] = Field(min_length=10, max_length=10)
    originality_note: str = Field(
        default="",
        description="Per-episode note on what makes this structure unique",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("segments")
    @classmethod
    def segments_are_1_through_10(cls, segments: list[SegmentPlan]) -> list[SegmentPlan]:
        indices = [s.segment_index for s in segments]
        if indices != list(range(1, 11)):
            raise ValueError("segments must be indexed 1..10 in order")
        return segments


class EpisodeTemplate(BaseModel):
    """Validated form of episode_template.yaml — must vary per episode."""

    episode_title: str
    premise: str
    segments: list[SegmentPlan] = Field(min_length=10, max_length=10)
    structural_signature: list[str] = Field(
        ...,
        description="Episode-level beat structure for similarity checks",
    )


# ---------------------------------------------------------------------------
# Shot prompts / clips
# ---------------------------------------------------------------------------


class ClipPrompt(BaseModel):
    clip_index: int = Field(ge=0)
    prompt: str
    negative_prompt: str = ""
    duration_sec: float = Field(default=8.0, ge=1, le=8)
    characters_on_screen: list[str] = Field(default_factory=list)
    reference_image_paths: list[str] = Field(default_factory=list)
    seed: int | None = None
    use_image_to_video: bool = False
    corrective_notes: str = ""


class SegmentPrompts(BaseModel):
    segment_index: int = Field(ge=1, le=10)
    clips: list[ClipPrompt] = Field(min_length=1)
    target_duration_sec: float = 60.0


class ClipArtifact(BaseModel):
    clip_index: int
    path: str
    duration_sec: float
    model: str
    seed: int | None = None
    generation_id: str | None = None
    estimated_cost_usd: float = 0.0


class SegmentRender(BaseModel):
    segment_index: int
    clips: list[ClipArtifact]
    segment_path: str
    duration_sec: float


# ---------------------------------------------------------------------------
# QC agent (structured Gemini response)
# ---------------------------------------------------------------------------


class PerCharacterConsistency(BaseModel):
    name: str
    score: int = Field(ge=0, le=10)
    drift_notes: str = ""


class CharacterConsistencyScore(BaseModel):
    score: int = Field(ge=0, le=10)
    per_character: list[PerCharacterConsistency] = Field(default_factory=list)


class ScoredNotes(BaseModel):
    score: int = Field(ge=0, le=10)
    notes: str = ""


class SafetyVerdict(BaseModel):
    pass_: bool = Field(alias="pass")
    flags: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class QCVerdict(BaseModel):
    """Strict JSON schema enforced on Gemini multimodal QC responses."""

    character_consistency: CharacterConsistencyScore
    palette_consistency: ScoredNotes
    continuity: ScoredNotes
    toddler_attention: ScoredNotes
    safety: SafetyVerdict
    artifacts: ScoredNotes
    verdict: Literal["pass", "regenerate"]
    corrective_prompt_notes: str = ""

    def fails_thresholds(
        self,
        *,
        min_character_score: int = 7,
        min_artifacts_score: int = 6,
    ) -> bool:
        if self.verdict == "regenerate":
            return True
        if not self.safety.pass_:
            return True
        if self.artifacts.score < min_artifacts_score:
            return True
        for entry in self.character_consistency.per_character:
            if entry.score < min_character_score:
                return True
        return False


class QCRecord(BaseModel):
    segment_index: int
    attempt: int = Field(ge=1, le=3)
    frame_paths: list[str] = Field(default_factory=list)
    verdict: QCVerdict
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Human gate
# ---------------------------------------------------------------------------


class HumanReviewDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"


class HumanReviewEntry(BaseModel):
    segment_index: int = Field(ge=1, le=10)
    decision: HumanReviewDecision
    notes: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    qc_attempt: int | None = None


# ---------------------------------------------------------------------------
# Budget / cost
# ---------------------------------------------------------------------------


class CostEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    category: Literal[
        "script",
        "shot_prompt",
        "veo_clip",
        "qc",
        "other",
    ]
    model: str
    units: float = 1.0
    unit_label: str = "call"
    estimated_cost_usd: float = Field(ge=0)
    segment_index: int | None = None
    clip_index: int | None = None
    notes: str = ""


class CostLedger(BaseModel):
    max_run_cost_usd: float
    entries: list[CostEntry] = Field(default_factory=list)
    abort_threshold_ratio: float = 0.9

    @property
    def spent_usd(self) -> float:
        return round(sum(e.estimated_cost_usd for e in self.entries), 6)

    @property
    def remaining_usd(self) -> float:
        return round(self.max_run_cost_usd - self.spent_usd, 6)

    def would_exceed_abort_threshold(self, additional_usd: float = 0.0) -> bool:
        projected = self.spent_usd + additional_usd
        return projected >= self.max_run_cost_usd * self.abort_threshold_ratio


# ---------------------------------------------------------------------------
# Compliance / publish package
# ---------------------------------------------------------------------------


class ComplianceFlags(BaseModel):
    made_for_kids: bool = True
    altered_synthetic_content_disclosure: bool = True
    collect_viewer_data: bool = False
    external_links: bool = False
    ctas: bool = False
    product_marketing_to_children: bool = False
    comments_cards_endscreens_unavailable: bool = True
    personalized_ads_unavailable: bool = True


class LicenseProvenance(BaseModel):
    asset_path: str
    source: Literal["original", "licensed"]
    license_note: str = ""
    license_id: str | None = None


class FlashCheckResult(BaseModel):
    passed: bool
    max_luminance_delta: float | None = None
    notes: str = ""


class AudioNormalizeResult(BaseModel):
    target_lufs: float = -14.0
    measured_lufs: float | None = None
    true_peak_dbtp: float | None = None
    passed: bool = False
    notes: str = ""


class TemplateSimilarityResult(BaseModel):
    compared_episode_ids: list[str] = Field(default_factory=list)
    max_similarity: float = Field(ge=0, le=1)
    threshold: float = Field(ge=0, le=1)
    passed: bool
    notes: str = ""


class PublishPackage(BaseModel):
    episode_id: str
    title: str
    made_for_kids: bool = True
    altered_synthetic_content_disclosure: bool = True
    originality_note: str
    description: str = Field(
        default="",
        description="Must contain no CTAs, external links, or product marketing",
    )
    compliance: ComplianceFlags = Field(default_factory=ComplianceFlags)
    human_review_log: list[HumanReviewEntry]
    qc_records: list[QCRecord]
    cost_ledger: CostLedger
    license_provenance: list[LicenseProvenance] = Field(default_factory=list)
    flash_check: FlashCheckResult | None = None
    audio_normalize: AudioNormalizeResult | None = None
    template_similarity: TemplateSimilarityResult | None = None
    episode_path: str
    duration_sec: float
    resolution: str = "1920x1080"
    fps: int = 30


class EpisodeManifest(BaseModel):
    """Drive-archived manifest for an episode."""

    episode_id: str
    title: str
    status: RunStatus
    plan: EpisodePlan
    segment_statuses: dict[int, SegmentStatus]
    human_review_log: list[HumanReviewEntry]
    qc_records: list[QCRecord]
    cost_ledger: CostLedger
    compliance: ComplianceFlags = Field(default_factory=ComplianceFlags)
    license_provenance: list[LicenseProvenance] = Field(default_factory=list)
    publish_package: PublishPackage | None = None
    drive_folder_id: str | None = None
    created_at: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Runtime config thresholds (from YAML / env overlays)
# ---------------------------------------------------------------------------


class QCThresholds(BaseModel):
    min_character_score: int = 7
    min_artifacts_score: int = 6
    max_auto_regenerations: int = 2


class PipelineConfig(BaseModel):
    episode_duration_sec: int = 600
    segment_count: int = 10
    segment_duration_sec: int = 60
    width: int = 1920
    height: int = 1080
    fps: int = 30
    clip_duration_sec: float = 8.0
    target_lufs: float = -14.0
    max_true_peak_dbtp: float = -1.0
    max_run_cost_usd: float = 150.0
    cost_abort_ratio: float = 0.9
    template_similarity_threshold: float = 0.7
    template_similarity_lookback: int = 10
    gate_host: str = "127.0.0.1"
    gate_port: int = 7788
    qc: QCThresholds = Field(default_factory=QCThresholds)
