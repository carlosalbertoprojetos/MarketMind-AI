try:
    from enum import StrEnum  # Python 3.11+
except ImportError:  # Python 3.10 compatibility
    from enum import Enum

    class StrEnum(str, Enum):
        pass


class Role(StrEnum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class MembershipStatus(StrEnum):
    active = "active"
    invited = "invited"
    disabled = "disabled"


class CampaignStage(StrEnum):
    awareness = "awareness"
    education = "education"
    solution = "solution"
    proof = "proof"
    conversion = "conversion"


class CampaignStatus(StrEnum):
    draft = "draft"
    active = "active"
    paused = "paused"
    completed = "completed"


class ContentType(StrEnum):
    linkedin_post = "linkedin_post"
    instagram_post = "instagram_post"
    x_thread = "x_thread"
    youtube_script = "youtube_script"
    carousel = "carousel"
    email_campaign = "email_campaign"


class PostStatus(StrEnum):
    draft = "draft"
    scheduled = "scheduled"
    published = "published"
    failed = "failed"


class MediaType(StrEnum):
    image = "image"
    video = "video"
    audio = "audio"
    document = "document"


class ScheduleStatus(StrEnum):
    scheduled = "scheduled"
    sent = "sent"
    cancelled = "cancelled"


class AnalyticsEventType(StrEnum):
    post_published = "post_published"
    post_viewed = "post_viewed"
    post_clicked = "post_clicked"
    post_engaged = "post_engaged"


class SocialPlatform(StrEnum):
    instagram = "instagram"
    linkedin = "linkedin"
    x = "x"
    youtube = "youtube"
    tiktok = "tiktok"


class IntegrationStatus(StrEnum):
    active = "active"
    disabled = "disabled"
    error = "error"


class AiRunStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
