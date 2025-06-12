# from sqlalchemy import Column, Integer, String, DateTime, func, Date, ForeignKey, Boolean, Text
# from sqlalchemy.dialects.postgresql import UUID, ENUM, JSONB
# from sqlalchemy.orm import relationship
# from enum import Enum
# from llama_index.callbacks.schema import CBEventType
# from libs.models.base import Base


# class MessageRoleEnum(str, Enum):
#     user = "user"
#     assistant = "assistant"


# class MessageStatusEnum(str, Enum):
#     PENDING = "PENDING"
#     SUCCESS = "SUCCESS"
#     ERROR = "ERROR"


# class MessageSubProcessStatusEnum(str, Enum):
#     PENDING = "PENDING"
#     FINISHED = "FINISHED"


# # python doesn't allow enums to be extended, so we have to do this
# additional_message_subprocess_fields = {
#     "CONSTRUCTED_QUERY_ENGINE": "constructed_query_engine",
#     "SUB_QUESTIONS": "sub_questions",
# }

# MessageSubProcessSourceEnum = Enum(
#     "MessageSubProcessSourceEnum",
#     [(event_type.name, event_type.value) for event_type in CBEventType]
#     + list(additional_message_subprocess_fields.items()),
# )


# def to_pg_enum(enum_class) -> ENUM:
#     return ENUM(enum_class, name=enum_class.__name__)


# class Document(Base):
#     """
#         A table along with its metadata
#     """

#     # URL to the actual document (e.g. a PDF)
#     table_name = Column(String, nullable=False, unique=True)
#     metadata_map = Column(JSONB, nullable=True)
#     conversations = relationship(
#         "ConversationDocument", back_populates="document")


# class Conversation(Base):
#     """
#         A conversation with messages and linked documents
#     """

#     messages = relationship("Message", back_populates="conversation")
#     conversation_documents = relationship(
#         "ConversationDocument", back_populates="conversation"
#     )


# class ConversationDocument(Base):
#     """
#     A many-to-many relationship between a conversation and a document
#     """

#     conversation_id = Column(
#         UUID(as_uuid=True), ForeignKey("conversation.id"), index=True
#     )
#     document_id = Column(UUID(as_uuid=True),
#                          ForeignKey("document.id"), index=True)
#     conversation = relationship(
#         "Conversation", back_populates="conversation_documents")
#     document = relationship(
#         "Document", back_populates="conversations")


# class Message(Base):
#     """
#         A message in a conversation
#     """

#     conversation_id = Column(
#         UUID(as_uuid=True), ForeignKey("conversation.id"), index=True
#     )
#     content = Column(String)
#     role = Column(to_pg_enum(MessageRoleEnum))
#     status = Column(to_pg_enum(MessageStatusEnum),
#                     default=MessageStatusEnum.PENDING)
#     conversation = relationship("Conversation", back_populates="messages")
#     sub_processes = relationship("MessageSubProcess", back_populates="message")


# class MessageSubProcess(Base):
#     """
#     A record of a sub-process that occurred as part of the generation of a message from an AI assistant
#     """

#     message_id = Column(UUID(as_uuid=True),
#                         ForeignKey("message.id"), index=True)
#     source = Column(to_pg_enum(MessageSubProcessSourceEnum))
#     message = relationship("Message", back_populates="sub_processes")
#     status = Column(
#         to_pg_enum(MessageSubProcessStatusEnum),
#         default=MessageSubProcessStatusEnum.FINISHED,
#         nullable=False,
#     )
#     metadata_map = Column(JSONB, nullable=True)

# class Colleague(Base):
#     __tablename__ = 'colleagues'

#     id = Column(Integer, primary_key=True)
#     given_name = Column(String(255), nullable=False)
#     family_name = Column(String(255), nullable=False)
#     email = Column(String(255), nullable=False)
#     created_at = Column(Date, nullable=False,
#                         server_default='CURRENT_TIMESTAMP(6)')
#     updated_at = Column(
#         Date, nullable=False, server_default='CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)')
#     published_at = Column(Date, nullable=True)
#     respondent_id = Column(Integer, ForeignKey(
#         'respondents.id'), nullable=True)
#     # Relationships
#     respondent = relationship("Respondent")


# class Completion(Base):
#     __tablename__ = 'completions'

#     id = Column(Integer, primary_key=True)
#     survey_year = Column(String(255), nullable=True)
#     is_complete = Column(Boolean, nullable=True)
#     created_at = Column(Date, nullable=True)
#     updated_at = Column(Date, nullable=True)
#     published_at = Column(Date, nullable=True)
#     respondent_id = Column(Integer, ForeignKey(
#         'respondents.id'), nullable=True)
#     # Relationships
#     respondent = relationship("Respondent")


# class Defect(Base):
#     __tablename__ = 'defects'

#     id = Column(Integer, primary_key=True)
#     created_at = Column(Date, nullable=False,
#                         server_default='CURRENT_TIMESTAMP(6)')
#     updated_at = Column(Date, nullable=False,
#                         server_default='CURRENT_TIMESTAMP(6)')
#     published_at = Column(Date, nullable=True)
#     number_of_patients = Column(Integer, nullable=True)
#     address_country = Column(String(255), nullable=True)
#     address_country_code = Column(String(255), nullable=True)
#     table_name = Column(String(255), nullable=True)
#     table_description = Column(String(255), nullable=True)
#     table_number = Column(Integer, nullable=True)
#     table_group_number = Column(Integer, nullable=True)
#     category_name = Column(String(255), nullable=True)
#     category_description = Column(String(255), nullable=True)
#     name = Column(String(255), nullable=True)
#     type = Column(String(255), nullable=True)
#     associated_features = Column(Text, nullable=True)
#     tcells = Column(Text, nullable=True)
#     bcells = Column(Text, nullable=True)
#     immunoglobulin = Column(Text, nullable=True)
#     affected_cells = Column(Text, nullable=True)
#     functional_defects = Column(Text, nullable=True)
#     affected_function = Column(Text, nullable=True)
#     laboratory_features = Column(Text, nullable=True)
#     major_category = Column(Text, nullable=True)
#     sub_category = Column(Text, nullable=True)
#     respondent_id = Column(Integer, ForeignKey(
#         'respondents.id'), nullable=True)
#     country_name = Column(String(255), nullable=True)
#     country_alternate_name = Column(String(255), nullable=True)
#     world_region_name = Column(String(255), nullable=True)
#     world_region_alternate_name = Column(String(255), nullable=True)
#     world_sub_region_name = Column(String(255), nullable=True)
#     world_sub_region_alternate_name = Column(String(255), nullable=True)
#     world_intermediate_region_name = Column(String(255), nullable=True)
#     world_intermediate_region_alternate_name = Column(
#         String(255), nullable=True)
#     # Relationships
#     respondent = relationship("Respondent")


# class Demographic(Base):
#     __tablename__ = 'demographics'

#     id = Column(Integer, primary_key=True)
#     created_at = Column(Date, nullable=False,
#                         server_default='CURRENT_TIMESTAMP(6)')
#     updated_at = Column(
#         Date, nullable=False, server_default='CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)')
#     published_at = Column(Date, nullable=True)
#     survey_year = Column(String(255), nullable=True)
#     patient_age_count = Column(Integer, nullable=True)
#     number_of_male_patients = Column(Integer, nullable=True)
#     number_of_female_patients = Column(Integer, nullable=True)
#     patient_age = Column(String(255), nullable=True)
#     respondent_id = Column(Integer, ForeignKey(
#         'respondents.id'), nullable=True)
#     country_name = Column(String(255), nullable=True)
#     country_alternate_name = Column(String(255), nullable=True)
#     world_region_name = Column(String(255), nullable=True)
#     world_region_alternate_name = Column(String(255), nullable=True)
#     world_sub_region_name = Column(String(255), nullable=True)
#     world_sub_region_alternate_name = Column(String(255), nullable=True)
#     world_intermediate_region_name = Column(String(255), nullable=True)
#     world_intermediate_region_alternate_name = Column(
#         String(255), nullable=True)
#     # Relationships
#     respondent = relationship("Respondent")


# class Login(Base):
#     __tablename__ = 'logins'

#     id = Column(Integer, primary_key=True)
#     ip_address = Column(String(255), nullable=True)
#     created_at = Column(Date, nullable=True)
#     updated_at = Column(Date, nullable=True)
#     published_at = Column(Date, nullable=True)
#     created_by_id = Column(Integer, nullable=True)
#     updated_by_id = Column(Integer, nullable=True)
#     user_agent = Column(String(255), nullable=True)
#     browser_name = Column(String(255), nullable=True)
#     browser_version = Column(String(255), nullable=True)
#     operating_system = Column(String(255), nullable=True)
#     operating_system_version = Column(String(255), nullable=True)
#     screen_resolution = Column(String(255), nullable=True)
#     language = Column(String(255), nullable=True)


# class NetPromoterScore(Base):
#     __tablename__ = 'net_promoter_scores'

#     id = Column(Integer, primary_key=True)
#     score = Column(Integer, nullable=True)
#     survey_year = Column(String(255), nullable=True)
#     is_survey_complete = Column(Boolean, nullable=True)
#     created_at = Column(Date, nullable=True)
#     updated_at = Column(Date, nullable=True)
#     published_at = Column(Date, nullable=True)
#     comments = Column(Text, nullable=True)
#     respondent_id = Column(Integer, ForeignKey(
#         'respondents.id'), nullable=True)
#     # Relationships
#     respondent = relationship("Respondent")


# class OtherDefect(Base):
#     __tablename__ = 'other_defects'

#     id = Column(Integer, primary_key=True)
#     name = Column(String(255), nullable=False)
#     gene_defect = Column(String(255), nullable=False)
#     gene_mutations = Column(String(255), nullable=False)
#     number_of_patients = Column(Integer, nullable=False)
#     created_at = Column(Date, nullable=False,
#                         server_default='CURRENT_TIMESTAMP(6)')
#     updated_at = Column(
#         Date, nullable=False, server_default='CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)')
#     published_at = Column(Date, nullable=True)
#     created_by_id = Column(Integer, nullable=True)
#     updated_by_id = Column(Integer, nullable=True)
#     survey_year = Column(String(255), nullable=False)
#     respondent_id = Column(Integer, ForeignKey(
#         'respondents.id'), nullable=True)
#     country_name = Column(String(255), nullable=True)
#     country_alternate_name = Column(String(255), nullable=True)
#     world_region_name = Column(String(255), nullable=True)
#     world_region_alternate_name = Column(String(255), nullable=True)
#     world_sub_region_name = Column(String(255), nullable=True)
#     world_sub_region_alternate_name = Column(String(255), nullable=True)
#     world_intermediate_region_name = Column(String(255), nullable=True)
#     world_intermediate_region_alternate_name = Column(
#         String(255), nullable=True)
#     # Relationships
#     respondent = relationship("Respondent")


# class ProxyRespondent(Base):
#     __tablename__ = 'proxy_respondents'

#     id = Column(Integer, primary_key=True)
#     given_name = Column(String(255), nullable=False)
#     family_name = Column(String(255), nullable=False)
#     email = Column(String(255), nullable=False)
#     created_at = Column(Date, nullable=False)
#     updated_at = Column(Date, nullable=False)
#     published_at = Column(Date, nullable=True)
#     full_name = Column(String(255), nullable=False)
#     respondent_id = Column(Integer, ForeignKey(
#         'respondents.id'), nullable=True)
#     # Relationships
#     respondent = relationship("Respondent")


# class Respondent(Base):
#     __tablename__ = 'respondents'

#     id = Column(Integer, primary_key=True)
#     created_at = Column(DateTime, nullable=False,
#                         server_default='CURRENT_TIMESTAMP(6)')
#     updated_at = Column(DateTime, nullable=False,
#                         server_default='CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)')
#     published_at = Column(DateTime, nullable=True)
#     given_name = Column(String(255), nullable=True)
#     additional_name = Column(String(255), nullable=True)
#     family_name = Column(String(255), nullable=True)
#     honorific_prefix = Column(String(255), nullable=True)
#     honorific_suffix = Column(String(255), nullable=True)
#     job_title = Column(String(255), nullable=True)
#     organization = Column(String(255), nullable=True)
#     address_country = Column(String(255), nullable=True)
#     address_country_code = Column(String(255), nullable=True)
#     address_formatted = Column(String(255), nullable=True)
#     street_address = Column(String(255), nullable=True)
#     address_locality = Column(String(255), nullable=True)
#     address_region = Column(String(255), nullable=True)
#     postal_code = Column(String(255), nullable=True)
#     telephone = Column(String(255), nullable=True)
#     email = Column(String(255), nullable=True)
#     fax_number = Column(String(255), nullable=True)
#     international_dialing_code = Column(String(255), nullable=True)
#     post_office_box_number = Column(String(255), nullable=True)
#     mobile_phone_number = Column(String(255), nullable=True)
#     mobile_international_dialing_code = Column(String(255), nullable=True)
#     fax_international_dialing_code = Column(String(255), nullable=True)
#     password = Column(String(255), nullable=True)
#     full_name = Column(String(255), nullable=True)
#     latitude = Column(String(255), nullable=True)
#     longitude = Column(String(255), nullable=True)
#     is_approved = Column(Boolean, nullable=True)
#     is_newsletter_subscriber = Column(Boolean, nullable=True)
#     is_administrator = Column(Boolean, nullable=True)
#     # location
#     country_name = Column(String(255), nullable=True)
#     country_alternate_name = Column(String(255), nullable=True)
#     world_region_name = Column(String(255), nullable=True)
#     world_region_alternate_name = Column(String(255), nullable=True)
#     world_sub_region_name = Column(String(255), nullable=True)
#     world_sub_region_alternate_name = Column(String(255), nullable=True)
#     world_intermediate_region_name = Column(String(255), nullable=True)
#     world_intermediate_region_alternate_name = Column(
#         String(255), nullable=True)
#     # Relationships
#     completions = relationship("Completion")
#     colleagues = relationship("Colleague")
#     defects = relationship("Defect")
#     other_defects = relationship("OtherDefect")
#     treatment_patterns = relationship("TreatmentPattern")
#     demographics = relationship("Demographic")
#     net_promoter_scores = relationship("NetPromoterScore")
#     proxy_respondents = relationship("ProxyRespondent")


# class TreatmentPattern(Base):
#     __tablename__ = 'treatment_patterns'

#     id = Column(Integer, primary_key=True)
#     survey_year = Column(String(255), nullable=True)
#     patients_followed = Column(Integer, nullable=True)
#     patients_with_pi_defect = Column(Integer, nullable=True)
#     patients_receiving_ig_g_ivig_clinic = Column(Integer, nullable=True)
#     patients_receiving_ig_g_ivig_home = Column(Integer, nullable=True)
#     patients_receiving_ig_g_scig = Column(Integer, nullable=True)
#     patients_receiving_ig_g_other = Column(Integer, nullable=True)
#     patients_treated_with_gene_therapy = Column(Integer, nullable=True)
#     patients_treated_with_peg_ada = Column(Integer, nullable=True)
#     patients_treated_by_transplant_donor_type_mrd = Column(
#         Integer, nullable=True)
#     patients_treated_by_transplant_donor_type_mud = Column(
#         Integer, nullable=True)
#     patients_treated_by_transplant_donor_type_m_mud = Column(
#         Integer, nullable=True)
#     patients_treated_by_transplant_donor_type_haplo = Column(
#         Integer, nullable=True)
#     patients_treated_by_transplant_stem_cell_src_bm = Column(
#         Integer, nullable=True)
#     patients_treated_by_transplant_stem_cell_src_pbsc = Column(
#         Integer, nullable=True)
#     patients_treated_by_transplant_stem_cell_src_cord = Column(
#         Integer, nullable=True)
#     patients_treated_by_transplant_stem_cell_src_other_name = Column(
#         String(255), nullable=True)
#     patients_treated_by_transplant_stem_cell_src_other_count = Column(
#         Integer, nullable=True)
#     created_at = Column(Date, nullable=False)
#     updated_at = Column(Date, nullable=False)
#     published_at = Column(Date, nullable=True)
#     created_by = Column(String(255), nullable=True)
#     updated_by = Column(String(255), nullable=True)
#     patients_diagnosed_through_jeffrey_insights_program = Column(
#         Integer, nullable=True)
#     respondent_id = Column(Integer, ForeignKey(
#         'respondents.id'), nullable=True)
#     country_name = Column(String(255), nullable=True)
#     country_alternate_name = Column(String(255), nullable=True)
#     world_region_name = Column(String(255), nullable=True)
#     world_region_alternate_name = Column(String(255), nullable=True)
#     world_sub_region_name = Column(String(255), nullable=True)
#     world_sub_region_alternate_name = Column(String(255), nullable=True)
#     world_intermediate_region_name = Column(String(255), nullable=True)
#     world_intermediate_region_alternate_name = Column(
#         String(255), nullable=True)
#     # Relationships
#     respondent = relationship("Respondent")
