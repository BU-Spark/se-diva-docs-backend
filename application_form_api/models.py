from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class SponsorQuestionAnswers(str, Enum):
    no = "No"
    yes = "Yes"
    no_additional = "No, but I will consider in the future"

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

class BWMDNChapterQuestion(str, Enum):
    no = "No"
    yes = "Yes"
    no_additional = "No, but I would like more information about starting a branch in my region"

class AddressType(str, Enum):
    work = "work"
    personal = "personal"

class Address(BaseModel):
    street: str
    apartment: Optional[str]
    city: str
    state: str
    zip_code: str
    country: str
    
class Applicant(BaseModel):
    first_name: str
    middle_name: Optional[str]
    last_name: str
    suffix: str
    primary_email: str
    secondary_email: Optional[str]
    phone_number: str
    address: Address
    address_type: AddressType
    current_academic_affiliation: str
    current_hospital_company: Optional[str]
    current_position: Optional[str]
    specialty: str
    areas_of_work: str
    geographic_region: str
    bwmdn_chapter_question: BWMDNChapterQuestion
    membership_directory_agreement: YesNoDontKnowResponse
    resume_included_question: YesNoDontKnowResponse
    divadocs_boston_member: DivaDocsBostonMember
    race_ethnicity: str
    gender_identity: str
    pronouns: str
    will_sponsor_question: SponsorQuestion


m = Applicant(
    first_name="John",
    last_name="Doe",
    suffix="MD",
    primary_email="john.doe@gmail.com",
    phone_number="6171231111",
    address= Address(
        street="123 Fruit St",
        city="Boston",
        state="MA",
        zip_code="02119",
        country="USA"
    ),
    address_type=AddressType.work,
    specialty="Dermatology",
    areas_of_work="Academic",
    geographic_region="Region 1 - CT,ME,MA,NH,RI and VT",
    bwmdn_chapter_question=BWMDNChapterQuestion.yes,
    current_academic_affiliation="MA-Boston University School of Medicine",
    membership_directory_agreement=YesNoDontKnowResponse.yes,
    resume_included_question= YesNoDontKnowResponse.yes,
    divadocs_boston_member= DivaDocsBostonMember(
        divadocs_boston_member_question= DivaDocsBostonMemberQuestion.yes
    ),
    race_ethnicity= "Asian/Asian American",
    gender_identity="Male",
    pronouns="He/Him",
    will_sponsor_question= SponsorQuestion(
        sponsor_question_answer = SponsorQuestionAnswers.yes
    )
)
#print(m.json())


