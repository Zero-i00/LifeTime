from database.models import LinkModel
from modules.link.schema import LinkSchemaOut


class LinkService:

    @staticmethod
    def to_schema(obj: LinkModel) -> LinkSchemaOut:
        return LinkSchemaOut(
            id=obj.id,
            url=obj.url,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


link_service = LinkService()
