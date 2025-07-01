from dataclasses import dataclass
from functools import cache
from importlib import metadata
from typing import Literal, Self

type MetaValue = str | list['MetaValue'] | dict[str, 'MetaValue'] | None

MetaKey = Literal[
    "metadata_version",
    "name",
    "version",
    "summary",
    "author_email",
    "classifier",
    "requires_python",
    "description_content_type",
    "license_file",
    "requires_dist",
    "dynamic",
    "description",
]


@dataclass(slots=True, frozen=True)
class Meta:
    data: dict[MetaKey, MetaValue]

    @classmethod
    def load_from_installed_package(cls) -> Self:
        top_level_package = __package__.split('.')[0] if __package__ else None
        if not top_level_package:
            return cls._get_fallback_meta("Unknown (running as script)")

        try:
            if not (dist_names := metadata.packages_distributions().get(top_level_package)):
                return cls._get_fallback_meta(pkg_name=top_level_package)

            dist_name = dist_names[0]

            return cls(data=metadata.metadata(dist_name).json)  # noqa

        except metadata.PackageNotFoundError:
            return cls._get_fallback_meta(top_level_package)

    @staticmethod
    def _get_fallback_meta(pkg_name: str) -> dict[MetaKey, MetaValue]:
        return {
            "name": f"{pkg_name} (not installed)",
            "version": "0.0.0-dev",
            "description": "Project metadata unavailable.",
        }

    def __getitem__(self, item: MetaKey) -> MetaValue:
        return self.data.get(item)

    def __str__(self) -> str:
        return str(self.data)


@cache
def get_project_meta() -> Meta:
    """Fetches the project metadata using the Meta class."""
    return Meta.load_from_installed_package()
