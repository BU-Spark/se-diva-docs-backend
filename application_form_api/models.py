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


# dummy_applicant = Applicant(
#     universal_applicant_id="123456",
#     first_name="John",
#     middle_name="Doe",
#     last_name="Smith",
#     suffix="Jr.",
#     primary_email="john.smith@example.com",
#     secondary_email="j.smith@example.com",
#     phone_number="555-123-4567",
#     address=Address(
#         street="123 Main St",
#         apartment="Apt 2",
#         city="Anytown",
#         state="CA",
#         zip_code="12345",
#         country="USA"
#     ),
#     address_type=AddressType.personal,
#     current_academic_affiliation="University of Anytown",
#     current_hospital_company="Anytown General Hospital",
#     current_position="Resident",
#     specialty="Internal Medicine",
#     areas_of_work="Primary Care, Inpatient Care",
#     geographic_region="West Coast",
#     bwmdn_chapter_question=BWMDNChapterQuestion.no,
#     membership_directory_agreement=YesNoDontKnowResponse.yes,
#     resume_included_question=YesNoDontKnowResponse.yes,
#     divadocs_boston_member=DivaDocsBostonMember(
#         divadocs_boston_member_question=DivaDocsBostonMemberQuestion.no,
#         years="3"
#     ),
#     race_ethnicity="White",
#     gender_identity="Male",
#     pronouns="He/Him",
#     will_sponsor_question=SponsorQuestion(
#         sponsor_question_answer=SponsorQuestionAnswers.yes,
#         activities_interested=["Networking", "Mentorship"]
#     ),
#     applicant_status=ApplicantStatus(
#         subscription_tier="",
#         approved=True,
#         paid=False,
#         payment_link="",
#         account_password=""
#     )
# )

# print(dummy_applicant.json())

# #print(m.json())
