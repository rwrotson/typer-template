import re
import sys
from dataclasses import dataclass
from email.utils import parseaddr
from functools import cache
from importlib import metadata
from typing import Literal, Self

type MetaValue = str | list["MetaValue"] | dict[str, "MetaValue"] | None

MetaKey = Literal[
    "metadata_version",
    "name",
    "version",
    "summary",
    "authors",
    "classifier",
    "requires_python",
    "description_content_type",
    "license_file",
    "requires_dist",
    "dynamic",
    "description",
    "dependencies",
]


@dataclass(slots=True, frozen=True)
class Meta:
    data: dict[MetaKey, MetaValue]

    @classmethod
    def load_from_installed_package(cls) -> Self:
        if not (top_level_pkg := __package__.split(".")[0] if __package__ else None):
            return cls._get_fallback_meta("Unknown (running as script)")

        try:
            if not (dist_names := metadata.packages_distributions().get(top_level_pkg)):
                return cls._get_fallback_meta(pkg_name=top_level_pkg)

            dist_name = dist_names[0]

            meta = metadata.metadata(dist_name).json

            if author_email := meta.pop("author_email", None):
                authors = []
                for author_string in author_email.split(","):
                    name, email = parseaddr(author_string)
                    authors.append({"name": name, "email": email})
                meta["authors"] = authors

            meta["dependencies"] = cls._get_installed_dependencies(meta.pop("requires_dist", []))

            return cls(data=meta)

        except metadata.PackageNotFoundError:
            return cls._get_fallback_meta(top_level_pkg)

    @staticmethod
    def _get_installed_dependencies(requires_dist: list[str]) -> dict[str, str]:
        pkg_name_pattern = re.compile(r"^[a-zA-Z0-9._-]+")
        pkg_names = [pkg_name_pattern.match(s).group(0).lower() for s in requires_dist]

        installed = {}
        if sys.version_info >= (3, 8):
            for dist in metadata.distributions():
                if dist.name.lower() in pkg_names:
                    installed[dist.name] = dist.version

        return dict(sorted(installed.items()))

    @staticmethod
    def _get_fallback_meta(pkg_name: str) -> dict[MetaKey, MetaValue]:
        return {
            "name": f"{pkg_name} (not installed)",
            "version": "0.0.0-dev",
            "description": "Project metadata unavailable.",
            "dependencies": {},
        }

    def __getitem__(self, item: MetaKey) -> MetaValue:
        return self.data.get(item)

    def __str__(self) -> str:
        return str(self.data)


@cache
def get_project_meta() -> Meta:
    """Fetches the project metadata using the Meta class."""
    return Meta.load_from_installed_package()
