"""College registry and invite code store - manages multi-tenant data."""

import json
import logging
import re
import uuid
from datetime import datetime
from pathlib import Path

from app.models.schemas import CollegeInfo, InviteCodeInfo

logger = logging.getLogger(__name__)

REGISTRY_FILE = Path("/app/data/colleges.json")
INVITE_CODES_FILE = Path("/app/data/invite_codes.json")


# ─── Invite Code Store ───────────────────────────────────────


class InviteCodeStore:
    """Manages invite codes for college registration gating."""

    def __init__(self):
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Create invite codes file if it doesn't exist."""
        INVITE_CODES_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not INVITE_CODES_FILE.exists():
            INVITE_CODES_FILE.write_text(json.dumps({"codes": {}}, indent=2))

    def _load(self) -> dict:
        """Load codes from disk."""
        return json.loads(INVITE_CODES_FILE.read_text())

    def _save(self, data: dict) -> None:
        """Save codes to disk."""
        INVITE_CODES_FILE.write_text(json.dumps(data, indent=2, default=str))

    def generate(self, count: int = 1) -> list[str]:
        """Generate new invite codes.

        Args:
            count: Number of codes to generate (1-20).

        Returns:
            List of generated code strings.
        """
        data = self._load()
        generated = []

        for _ in range(count):
            code = f"INV-{uuid.uuid4().hex[:6]}"
            # Ensure uniqueness
            while code in data["codes"]:
                code = f"INV-{uuid.uuid4().hex[:6]}"

            data["codes"][code] = {
                "status": "available",
                "used_by": None,
                "created_at": datetime.now().isoformat(),
                "used_at": None,
            }
            generated.append(code)

        self._save(data)
        logger.info(f"Generated {count} invite codes: {generated}")
        return generated

    def validate(self, code: str) -> bool:
        """Check if an invite code is valid and available.

        Args:
            code: The invite code to validate.

        Returns:
            True if the code exists and hasn't been used.
        """
        data = self._load()
        code_data = data["codes"].get(code)
        if not code_data:
            return False
        return code_data["status"] == "available"

    def consume(self, code: str, college_code: str) -> bool:
        """Mark an invite code as used.

        Args:
            code: The invite code to consume.
            college_code: The college that used it.

        Returns:
            True if consumed successfully.
        """
        data = self._load()
        if code not in data["codes"]:
            return False
        if data["codes"][code]["status"] != "available":
            return False

        data["codes"][code]["status"] = "used"
        data["codes"][code]["used_by"] = college_code
        data["codes"][code]["used_at"] = datetime.now().isoformat()
        self._save(data)

        logger.info(f"Invite code {code} consumed by {college_code}")
        return True

    def revoke(self, code: str) -> bool:
        """Revoke/delete an invite code.

        Args:
            code: The invite code to revoke.

        Returns:
            True if revoked successfully.
        """
        data = self._load()
        if code not in data["codes"]:
            return False

        del data["codes"][code]
        self._save(data)
        logger.info(f"Invite code {code} revoked")
        return True

    def list_all(self) -> list[InviteCodeInfo]:
        """List all invite codes with their status."""
        data = self._load()
        codes = []
        for code, info in data["codes"].items():
            codes.append(InviteCodeInfo(
                code=code,
                status=info["status"],
                used_by=info.get("used_by"),
                created_at=info.get("created_at", ""),
            ))
        return codes

    def count_available(self) -> int:
        """Count available (unused) invite codes."""
        data = self._load()
        return sum(1 for c in data["codes"].values() if c["status"] == "available")

    def count_used(self) -> int:
        """Count used invite codes."""
        data = self._load()
        return sum(1 for c in data["codes"].values() if c["status"] == "used")


# ─── College Registry ────────────────────────────────────────


class CollegeRegistry:
    """Manages college registrations and their metadata."""

    def __init__(self):
        self._ensure_registry_file()

    def _ensure_registry_file(self) -> None:
        """Create registry file if it doesn't exist."""
        REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not REGISTRY_FILE.exists():
            REGISTRY_FILE.write_text(json.dumps({"colleges": {}}, indent=2))

    def _load(self) -> dict:
        """Load registry from disk."""
        return json.loads(REGISTRY_FILE.read_text())

    def _save(self, data: dict) -> None:
        """Save registry to disk."""
        REGISTRY_FILE.write_text(json.dumps(data, indent=2, default=str))

    def _generate_code(self, college_name: str) -> str:
        """Generate a unique short code from college name.

        Takes first letters of words + random suffix.
        e.g., 'St Pauls College' -> 'SPC-a3b2'
        """
        words = re.findall(r"[A-Za-z]+", college_name)
        initials = "".join(w[0].upper() for w in words[:4])
        suffix = uuid.uuid4().hex[:4]
        return f"{initials}-{suffix}"

    def register(
        self, college_name: str, openai_api_key: str = ""
    ) -> CollegeInfo:
        """Register a new college.

        Args:
            college_name: Full name of the college.
            openai_api_key: Optional OpenAI API key for faster responses.

        Returns:
            CollegeInfo with generated code.
        """
        data = self._load()
        code = self._generate_code(college_name)

        # Ensure uniqueness
        while code in data["colleges"]:
            code = self._generate_code(college_name)

        college = CollegeInfo(
            college_name=college_name,
            college_code=code,
            total_chunks=0,
            is_indexed=False,
            has_openai_key=bool(openai_api_key),
            created_at=datetime.now(),
        )

        college_data = college.model_dump(mode="json")
        # Store OpenAI key separately (not in the public CollegeInfo model)
        college_data["_openai_api_key"] = openai_api_key

        data["colleges"][code] = college_data
        self._save(data)

        logger.info(f"Registered college: {college_name} -> {code}")
        return college

    def get(self, college_code: str) -> CollegeInfo | None:
        """Get college info by code (public info only, no API key).

        Args:
            college_code: The unique college code.

        Returns:
            CollegeInfo or None if not found.
        """
        data = self._load()
        college_data = data["colleges"].get(college_code)
        if not college_data:
            return None
        # Filter out private fields
        filtered = {k: v for k, v in college_data.items() if not k.startswith("_")}
        return CollegeInfo(**filtered)

    def get_openai_key(self, college_code: str) -> str:
        """Get the OpenAI API key for a college (internal use only).

        Args:
            college_code: The unique college code.

        Returns:
            OpenAI API key string (empty if not set).
        """
        data = self._load()
        college_data = data["colleges"].get(college_code)
        if not college_data:
            return ""
        return college_data.get("_openai_api_key", "")

    def update(self, college_code: str, **kwargs) -> CollegeInfo | None:
        """Update college metadata.

        Args:
            college_code: The unique college code.
            **kwargs: Fields to update.

        Returns:
            Updated CollegeInfo or None.
        """
        data = self._load()
        if college_code not in data["colleges"]:
            return None

        data["colleges"][college_code].update(kwargs)
        self._save(data)

        filtered = {k: v for k, v in data["colleges"][college_code].items() if not k.startswith("_")}
        return CollegeInfo(**filtered)

    def list_all(self) -> list[CollegeInfo]:
        """List all registered colleges (public info only)."""
        data = self._load()
        colleges = []
        for college_data in data["colleges"].values():
            filtered = {k: v for k, v in college_data.items() if not k.startswith("_")}
            colleges.append(CollegeInfo(**filtered))
        return colleges

    def get_collection_name(self, college_code: str) -> str:
        """Get the Qdrant collection name for a college.

        Args:
            college_code: The unique college code.

        Returns:
            Collection name (e.g., 'handbook_spc_a3b2').
        """
        return f"handbook_{college_code.lower().replace('-', '_')}"

    def exists(self, college_code: str) -> bool:
        """Check if a college code exists."""
        data = self._load()
        return college_code in data["colleges"]
