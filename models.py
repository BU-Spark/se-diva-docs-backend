from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class SponsorQuestionAnswers(str, Enum):
    no = "No"
    yes = "Yes"


class SponsorQuestion(BaseModel):
    sponsor_question_answer: SponsorQuestionAnswers
    activities_interested: Optional[List[str]]


class DivaDocsBostonMemberQuestion(str, Enum):
    no = "No"
    yes = "Yes"
    no_additional = "No, but I live in Greater Boston and would like to join"


class DivaDocsBostonMember(BaseModel):
    divadocs_boston_member_question: DivaDocsBostonMemberQuestion
    years: Optional[str]


class YesNoDontKnowResponse(str, Enum):
    no = "No"
    yes = "Yes"
    dont_know = "Don't Know"


class BWQuestion(str, Enum):
    no = "No"
    yes = "Yes"
    no_additional = "No, but I would like more information about starting a branch in my region"


class AddressType(str, Enum):
    work = "Work"
    personal = "Home"


class Address(BaseModel):
    street: str
    apartment: Optional[str]
    city: str
    state: str
    zip_code: str
    country: str


class ApplicantStatus(BaseModel):
    subscription_tier: Optional[str]
    approved: Optional[bool]
    paid: Optional[bool]
    stripe_customer_id: Optional[str]
    account_password: Optional[str]


class Applicant(BaseModel):
    id: str
    first_name: str
    middle_name: Optional[str]
    last_name: str
    suffix: Optional[str]
    primary_email: str
    secondary_email: Optional[str]
    phone_number: str
    address: Address
    address_type: AddressType
    current_academic_affiliation: str
    current_hospital_company: Optional[str]
    current_position: Optional[str]
    specialty: str
    areas_of_work: Optional[List[str]]
    geographic_region: str
    bwmdn_chapter_question: BWQuestion
    membership_directory_agreement: YesNoDontKnowResponse
    resume_included_question: YesNoDontKnowResponse
    divadocs_boston_member: DivaDocsBostonMember
    race: List[str]
    ethnicity: List[str]
    gender_identity: str
    pronouns: str
    will_sponsor_question: SponsorQuestion
    applicant_status: ApplicantStatus
