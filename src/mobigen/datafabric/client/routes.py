
from generated.schema.entity.data.glossary import Glossary
from generated.schema.entity.data.glossaryTerm import GlossaryTerm
from generated.schema.api.data.createGlossary import CreateGlossaryRequest
from generated.schema.api.data.createGlossaryTerm import (
    CreateGlossaryTermRequest,
)

ROUTES = {
    # Glossaries
    Glossary.__name__: "/glossaries",
    CreateGlossaryRequest.__name__: "/glossaries",
    GlossaryTerm.__name__: "/glossaryTerms",
    CreateGlossaryTermRequest.__name__: "/glossaryTerms",
}
