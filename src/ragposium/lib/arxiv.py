from pydantic import BaseModel


class Version(BaseModel):
    version: str
    created: str


class Author(BaseModel):
    last_name: str
    first_name: str
    middle_name: str | None = None


class ArxivPaper(BaseModel):
    id: str | None
    submitter: str | None
    authors: str | None
    title: str | None
    comments: str | None
    journal_ref: str | None = None
    doi: str | None = None
    report_no: str | None = None
    categories: str | None
    license: str | None = None
    abstract: str | None
    versions: list[Version] | None
    update_date: str | None
    authors_parsed: list[list[str]] | None
